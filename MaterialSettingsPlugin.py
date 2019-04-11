# Copyright (c) 2019 fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

from UM.Application import Application
from UM.Extension import Extension
from PyQt5.QtQml import qmlRegisterType
from . import MaterialSettingsPluginVisibilityHandler

class MaterialSettingsPlugin(Extension):
    def __init__(self):
        super().__init__()

        Application.getInstance().engineCreatedSignal.connect(self._onEngineCreated)

    def _onEngineCreated(self):
        qmlRegisterType(MaterialSettingsPluginVisibilityHandler.MaterialSettingsPluginVisibilityHandler, "Cura", 1, 0, "MaterialSettingsVisibilityHandler")
