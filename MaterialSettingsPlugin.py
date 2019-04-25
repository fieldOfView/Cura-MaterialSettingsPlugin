# Copyright (c) 2019 fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

from UM.Application import Application
from UM.Extension import Extension
from PyQt5.QtQml import qmlRegisterType
from . import MaterialSettingsPluginVisibilityHandler

class MaterialSettingsPlugin(Extension):
    def __init__(self):
        super().__init__()

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
        qmlRegisterType(MaterialSettingsPluginVisibilityHandler.MaterialSettingsPluginVisibilityHandler, "Cura", 1, 0, "MaterialSettingsVisibilityHandler")
