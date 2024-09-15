import inspect
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
from rich.console import Console

from cfmtoolbox.models import CFM

Importer: TypeAlias = Callable[[bytes], CFM]
Exporter: TypeAlias = Callable[[CFM], bytes]
CommandF = TypeVar("CommandF", bound=Callable[[CFM], CFM])


class CFMToolbox:
    def __init__(self) -> None:
        self.registered_importers: dict[str, Importer] = {}
        self.registered_exporters: dict[str, Exporter] = {}
        self.import_path: Path | None = None
        self.export_path: Path | None = None
        self.typer = typer.Typer(callback=self.prepare)
        self.err_console = Console(stderr=True)

    def __call__(self) -> None:
        return self.typer()

    def prepare(
        self,
        import_path: Annotated[Optional[Path], typer.Option("--import")] = None,
        export_path: Annotated[Optional[Path], typer.Option("--export")] = None,
    ) -> None:
        self.import_path = import_path
        self.export_path = export_path

    def import_model(self) -> CFM | None:
        if self.import_path is None:
            return None

        importer = self.registered_importers.get(self.import_path.suffix)

        if importer is None:
            message = f"Unsupported import format: {self.import_path.suffix}"
            raise typer.Abort(message)

        return importer(self.import_path.read_bytes())

    def export_model(self, model: CFM) -> None:
        if self.export_path is None:
            return

        exporter = self.registered_exporters.get(self.export_path.suffix)

        if exporter is None:
            message = f"Unsupported export format: {self.export_path.suffix}"
            raise typer.Abort(message)

        self.export_path.write_bytes(exporter(model))

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
        def decorator(internal_function: CommandF) -> CommandF:
            internal_signature = inspect.signature(internal_function)
            internal_params = list(internal_signature.parameters.values())
            external_params = internal_params[1:]  # Omit the first/CFM parameter
            external_signature = internal_signature.replace(parameters=external_params)

            def external_function(*args, **kwargs):
                original_model = self.import_model()

                if original_model is None:
                    self.err_console.print(
                        "Please provide a model via the --import option."
                    )
                    raise typer.Exit(code=1)

                modified_model = internal_function(original_model, *args, **kwargs)
                self.export_model(modified_model)

            external_function.__name__ = internal_function.__name__
            external_function.__module__ = internal_function.__module__
            external_function.__qualname__ = internal_function.__qualname__
            external_function.__doc__ = internal_function.__doc__
            external_function.__annotations__ = internal_function.__annotations__
            setattr(external_function, "__signature__", external_signature)

            self.typer.command(*args, **kwargs)(external_function)
            return internal_function

        return decorator

    @classmethod
    def load_plugins(cls) -> list[ModuleType]:
        plugin_entry_points = entry_points(group="cfmtoolbox.plugins")
        return [ep.load() for ep in plugin_entry_points]
