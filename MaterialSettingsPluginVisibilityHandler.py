# Copyright (c) 2019 fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

from UM.Settings.Models.SettingVisibilityHandler import SettingVisibilityHandler
from UM.Application import Application

class MaterialSettingsPluginVisibilityHandler(SettingVisibilityHandler):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent = parent, *args, **kwargs)

        self._preferences = Application.getInstance().getPreferences()
        self._preferences.preferenceChanged.connect(self._onPreferencesChanged)

        self._onPreferencesChanged("material_settings/visible_settings")


    def _onPreferencesChanged(self, name: str) -> None:
        if name != "material_settings/visible_settings":
            return

        visibility_string = self._preferences.getValue("material_settings/visible_settings")
        if not visibility_string:
            self._preferences.resetPreference("material_settings/visible_settings")
            return

        material_settings = set(visibility_string.split(";"))

        self.setVisible(material_settings)
