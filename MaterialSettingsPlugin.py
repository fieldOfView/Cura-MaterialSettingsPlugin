# Copyright (c) 2019 fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

import os.path

from UM.Application import Application
from UM.Extension import Extension
from PyQt5.QtQml import qmlRegisterType

from . import MaterialSettingsPluginVisibilityHandler

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

class MaterialSettingsPlugin(Extension):
    def __init__(self):
        super().__init__()

        self._settings_dialog = None

        self.setMenuName(catalog.i18nc("@item:inmenu", "Material Settings"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Configure Material Settings"), self.showSettingsDialog)

        default_material_settings = {
            "default_material_print_temperature",
            "default_material_bed_temperature",
            "material_standby_temperature",
            #"material_flow_temp_graph",
            "cool_fan_speed",
            "retraction_amount",
            "retraction_speed",
            "material_flow",
        }

        Application.getInstance().getPreferences().addPreference(
            "material_settings/visible_settings",
            ";".join(default_material_settings)
        )

        Application.getInstance().engineCreatedSignal.connect(self._onEngineCreated)

    def _onEngineCreated(self):
        qmlRegisterType(
            MaterialSettingsPluginVisibilityHandler.MaterialSettingsPluginVisibilityHandler,
            "Cura", 1, 0, "MaterialSettingsVisibilityHandler"
        )

    def showSettingsDialog(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SettingsDialog.qml")
        self._settings_dialog = Application.getInstance().createQmlComponent(path, {"manager": self})
        self._settings_dialog.show()
