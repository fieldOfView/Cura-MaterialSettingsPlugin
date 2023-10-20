# Copyright (c) 2023 Aldo Hoeben / fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

try:
    from cura.ApplicationMetadata import CuraSDKVersion
except ImportError:  # Cura <= 3.6
    CuraSDKVersion = "6.0.0"
if CuraSDKVersion >= "8.0.0":
    from PyQt6.QtCore import QObject, pyqtSlot
else:
    from PyQt5.QtCore import QObject, pyqtSlot

from cura.CuraApplication import CuraApplication

from typing import Any, Optional

from .MaterialSettingsPluginVisibilityHandler import (
    MaterialSettingsPluginVisibilityHandler
)
from .MaterialSettingDefinitionsModel import MaterialSettingDefinitionsModel
from .CustomStackProxy import CustomStackProxy


class MaterialSettingsProxy(QObject):
    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

        self._custom_stacks = []
        self._material_setting_definitions_models = []
        self._material_settings_visibility_handlers = []

    @pyqtSlot(result=QObject)
    def makeCustomStack(self) -> Optional["QObject"]:
        stack = CustomStackProxy()
        stack.destroyed.connect(self._forgetCustomStack)
        self._custom_stacks.append(stack)
        return stack

    def _forgetCustomStack(self, stack):
        stack.destroyed.disconnect(self._forgetCustomStack)
        try:
            self._custom_stacks.remove(stack)
        except ValueError:
            pass

    @pyqtSlot(result=QObject)
    def makeMaterialSettingDefinitionsModel(self) -> Optional["QObject"]:
        model = MaterialSettingDefinitionsModel()
        model.destroyed.connect(self._forgetMaterialSettingDefinitionsModel)
        self._material_setting_definitions_models.append(model)
        return model

    def _forgetMaterialSettingDefinitionsModel(self, model):
        model.destroyed.disconnect(self._forgetMaterialSettingDefinitionsModel)
        try:
            self._material_setting_definitions_models.remove(model)
        except ValueError:
            pass

    @pyqtSlot(result=QObject)
    def makeVisibilityHandler(self) -> Optional["QObject"]:
        visibility_handler = MaterialSettingsPluginVisibilityHandler()
        visibility_handler.destroyed.connect(self._forgetVisibilityHandler)
        self._material_settings_visibility_handlers.append(visibility_handler)
        return visibility_handler

    def _forgetVisibilityHandler(self, visibility_handler):
        visibility_handler.destroyed.disconnect(self._forgetVisibilityHandler)
        try:
            self._material_settings_visibility_handlers.remove(visibility_handler)
        except ValueError:
            pass

    @pyqtSlot(str, str, "QVariant")
    def setMaterialContainersPropertyValue(
        self, base_file: str, key: str, value: Any
    ) -> None:
        container_registry = CuraApplication.getInstance().getContainerRegistry()
        for container in container_registry.findInstanceContainers(base_file=base_file):
            container.setProperty(key, "value", value)
