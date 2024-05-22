from importlib.metadata import entry_points
from pathlib import Path
from types import ModuleType
from typing import Annotated, Callable, Optional, TypeAlias

import typer

from cfmtoolbox.models import CFM

Importer: TypeAlias = Callable[[], None]
Exporter: TypeAlias = Callable[[], None]


class CFMToolbox(typer.Typer):
    def __init__(self) -> None:
        self.registered_importers: dict[str, Importer] = {}
        self.registered_exporters: dict[str, Exporter] = {}
        self.model: CFM | None = None
        self.input_path: Path | None = None
        self.output_path: Path | None = None
        return super().__init__(callback=self.prepare, result_callback=self.cleanup)

    def prepare(
        self,
        input_path: Annotated[Optional[Path], typer.Option("--input")] = None,
        output_path: Annotated[Optional[Path], typer.Option("--output")] = None,
    ) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.import_model()

    def cleanup(self, *args: tuple[object], **kwargs: dict[str, object]) -> None:
        self.export_model()

    def import_model(self) -> None:
        if self.input_path:
            importer = self.registered_importers.get(self.input_path.suffix)

            if importer is None:
                print(f"Unsupported input format: {self.input_path.suffix}")
                raise typer.Abort()

            importer()

    def export_model(self) -> None:
        if self.output_path:
            exporter = self.registered_exporters.get(self.output_path.suffix)

            if exporter is None:
                print(f"Unsupported output format: {self.output_path.suffix}")
                raise typer.Abort()

            exporter()

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

    @classmethod
    def load_plugins(cls) -> list[ModuleType]:
        plugin_entry_points = entry_points(group="cfmtoolbox.plugins")
        return [ep.load() for ep in plugin_entry_points]
