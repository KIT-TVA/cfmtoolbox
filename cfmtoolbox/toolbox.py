import inspect
from functools import partial
from importlib.metadata import entry_points
from pathlib import Path
from types import ModuleType
from typing import (
    Annotated,
    Callable,
    Optional,
    TypeAlias,
    TypeVar,
)

import typer

from cfmtoolbox.models import CFM

Importer: TypeAlias = Callable[[bytes], CFM]
Exporter: TypeAlias = Callable[[CFM], bytes]
CommandF = TypeVar("CommandF", bound=Callable[[CFM | None], CFM | None])


class CFMToolbox:
    def __init__(self) -> None:
        self.registered_importers: dict[str, Importer] = {}
        self.registered_exporters: dict[str, Exporter] = {}
        self.model: CFM | None = None
        self.import_path: Path | None = None
        self.export_path: Path | None = None
        self.typer = typer.Typer(callback=self.prepare, result_callback=self.cleanup)

    def __call__(self) -> None:
        return self.typer()

    def prepare(
        self,
        import_path: Annotated[Optional[Path], typer.Option("--import")] = None,
        export_path: Annotated[Optional[Path], typer.Option("--export")] = None,
    ) -> None:
        self.import_path = import_path
        self.export_path = export_path
        self.import_model()

    def cleanup(self, *args: tuple[object], **kwargs: dict[str, object]) -> None:
        self.export_model()

    def import_model(self) -> None:
        if self.import_path:
            importer = self.registered_importers.get(self.import_path.suffix)

            if importer is None:
                message = f"Unsupported import format: {self.import_path.suffix}"
                raise typer.Abort(message)

            self.model = importer(self.import_path.read_bytes())

    def export_model(self) -> None:
        if self.export_path and self.model:
            exporter = self.registered_exporters.get(self.export_path.suffix)

            if exporter is None:
                message = f"Unsupported export format: {self.export_path.suffix}"
                raise typer.Abort(message)

            self.export_path.write_bytes(exporter(self.model))

    def importer(self, extension: str) -> Callable[[Importer], Importer]:
        def decorator(func: Importer) -> Importer:
            self.registered_importers[extension] = func
            return func

        return decorator

    def exporter(self, extension: str) -> Callable[[Exporter], Exporter]:
        def decorator(func: Exporter) -> Exporter:
            self.registered_exporters[extension] = func
            return func

        return decorator

    def command(self, *args, **kwargs) -> Callable[[CommandF], CommandF]:
        def decorator(func: CommandF) -> CommandF:
            partial_func = partial(func, self.model)

            def lazy_partial_func(*args, **kwargs):
                self.model = func(self.model, *args, **kwargs)

            lazy_partial_func.__name__ = func.__name__
            lazy_partial_func.__module__ = func.__module__
            lazy_partial_func.__qualname__ = func.__qualname__
            lazy_partial_func.__doc__ = func.__doc__
            lazy_partial_func.__annotations__ = func.__annotations__
            setattr(lazy_partial_func, "__signature__", inspect.signature(partial_func))

            self.typer.command(*args, **kwargs)(lazy_partial_func)
            return func

        return decorator

    @classmethod
    def load_plugins(cls) -> list[ModuleType]:
        plugin_entry_points = entry_points(group="cfmtoolbox.plugins")
        return [ep.load() for ep in plugin_entry_points]
