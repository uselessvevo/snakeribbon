from __feature__ import snake_case

import os
from typing import Union

from PySide6.QtWidgets import QWidget


class _RegistryConnector:

    def __init__(self, registry: Union[dict, "BaseRegistry"] = None):
        self._registry = registry or {}

    def set_registry(self, registry: Union[dict, "BaseRegistry"] = None):
        self._registry = registry

    def update_registry_data(self, *args, **kwargs):
        raise NotImplementedError(f"Method `{self.__qualname__}` must be implemented")

    def __call__(self, filename: str) -> None:
        if self._registry is None:
            raise ValueError("Attribute `registry` is not initialized")
        self._registry.get(filename, None)


class _DataFileConnector(_RegistryConnector):

    def update_registry_data(self, icons: dict[str, Union[str, os.PathLike]]):
        self._registry.update(**icons)


DataFile = _DataFileConnector()


class _ThemeFileConnector(_RegistryConnector):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_sheet = ""

    def update_registry_data(self, target: QWidget, filename: Union[str, os.PathLike]):
        with open(filename, "r", encoding="utf-8") as output:
            self._style_sheet += output.read()

        target.set_style_sheet(self._style_sheet)


ThemeFile = _ThemeFileConnector()
