# Copyright (c) 2019 fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

import UM.Settings.Models.SettingVisibilityHandler


class MaterialSettingsPluginVisibilityHandler(UM.Settings.Models.SettingVisibilityHandler.SettingVisibilityHandler):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)

        material_settings = {
            "default_material_print_temperature",
            "default_material_bed_temperature",
            "material_standby_temperature",
            #"material_flow_temp_graph",
            "cool_fan_speed",
            "retraction_amount",
            "retraction_speed",
            "material_flow",
        }

        self.setVisible(material_settings)
