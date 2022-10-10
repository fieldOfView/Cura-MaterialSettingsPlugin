# Copyright (c) 2022 Aldo Hoeben / fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

try:
    from cura.ApplicationMetadata import CuraSDKVersion
except ImportError: # Cura <= 3.6
    CuraSDKVersion = "6.0.0"
if CuraSDKVersion >= "8.0.0":
    from PyQt6.QtCore import QObject, pyqtSlot
else:
    from PyQt5.QtCore import QObject, pyqtSlot

from cura.CuraApplication import CuraApplication

from typing import Any

class HelperProxy(QObject):

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

    @pyqtSlot(str, str, "QVariant")
    def setMaterialContainersPropertyValue(self, base_file: str, key: str, value: Any) -> None:
        container_registry = CuraApplication.getInstance().getContainerRegistry()
        for container in container_registry.findInstanceContainers(base_file=base_file):
            container.setProperty(key, "value", value)