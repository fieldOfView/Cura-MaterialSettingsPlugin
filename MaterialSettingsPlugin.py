# Copyright (c) 2022 Aldo Hoeben / fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

import os.path

try:
    from cura.ApplicationMetadata import CuraSDKVersion
except ImportError: # Cura <= 3.6
    CuraSDKVersion = "6.0.0"
USE_QT5 = False
if CuraSDKVersion >= "8.0.0":
    from PyQt6.QtQml import qmlRegisterType
    from PyQt6.QtCore import QUrl
else:
    from PyQt5.QtQml import qmlRegisterType
    from PyQt5.QtCore import QUrl
    USE_QT5 = True

from UM.Extension import Extension
from UM.Resources import Resources
from UM.Logger import Logger
from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderManager import ExtruderManager
from cura.Settings.MaterialSettingsVisibilityHandler import MaterialSettingsVisibilityHandler

try:
    # Cura 3.6 and newer
    from cura.Settings.CuraFormulaFunctions import CuraFormulaFunctions
except ImportError:
    # Cura 3.5
    from cura.Settings.CustomSettingFunctions import CustomSettingFunctions as CuraFormulaFunctions  # type: ignore

from . import MaterialSettingsPluginVisibilityHandler

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

class MaterialSettingsPlugin(Extension):
    def __init__(self) -> None:
        super().__init__()

        default_material_settings = list(MaterialSettingsVisibilityHandler().getVisible()) # the default list
        default_material_settings.append("material_flow")

        CuraApplication.getInstance().getPreferences().addPreference(
            "material_settings/visible_settings",
            ";".join(default_material_settings)
        )

        CuraApplication.getInstance().engineCreatedSignal.connect(self._onEngineCreated)

        if hasattr(CuraFormulaFunctions, "getValueFromContainerAtIndex"):
            api = CuraApplication.getInstance().getCuraAPI()
            api.interface.settings.addContextMenuItem({
               "name": catalog.i18nc("@item:inmenu", "Use value from material"),
               "icon_name": "",
               "actions": ["__call__"],
               "menu_item": self.useValueFromMaterialContainer
            })

    def _onEngineCreated(self) -> None:
        qmlRegisterType(
            MaterialSettingsPluginVisibilityHandler.MaterialSettingsPluginVisibilityHandler,
            "Cura", 1, 0, "MaterialSettingsVisibilityHandler"
        )

        # Adding/removing pages from the preferences dialog is handles in QML
        # There is no way to access the preferences dialog directly, so we have to search for it
        preferencesDialog = None
        main_window = CuraApplication.getInstance().getMainWindow()
        if not main_window:
            Logger.log("e", "Could not replace Materials preferencepane with patched version because there is no main window")
            return
        for child in main_window.contentItem().children():
            try:
                test = child.setPage # only PreferencesDialog has a setPage function
                preferencesDialog = child
                break
            except:
                pass

        if preferencesDialog:
            Logger.log("d", "Replacing Materials preferencepane with patched version")

            qml_folder = "qml" if not USE_QT5 else "qml_qt5"
            materialPreferencesPage = QUrl.fromLocalFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), qml_folder, "MaterialsPage.qml"))
            if USE_QT5:
                materialPreferencesPage = materialPreferencesPage.toString()

            preferencesDialog.removePage(3)
            preferencesDialog.insertPage(3, catalog.i18nc("@title:tab", "Materials"), materialPreferencesPage)
        else:
            Logger.log("e", "Could not replace Materials preferencepane with patched version")

    def useValueFromMaterialContainer(self, kwargs) -> None:
        try:
            setting_key = kwargs["key"]
        except KeyError:
            return

        global_container_stack = CuraApplication.getInstance().getGlobalContainerStack()
        if not global_container_stack:
            return

        try:
            material_container_index = global_container_stack.getContainers().index(global_container_stack.material)
        except ValueError:
            return

        settable_per_extruder = global_container_stack.getProperty(setting_key, "settable_per_extruder")
        resolve_value = global_container_stack.getProperty(setting_key, "resolve")
        if not settable_per_extruder and resolve_value is None:
            # todo: notify user
            Logger.log("e", "Setting %s can not be set per material" % setting_key)
            return

        if settable_per_extruder:
            value_string = "=extruderValueFromContainer(extruder_nr,\"%s\",%d)" %(setting_key, material_container_index)
            ExtruderManager.getInstance().getActiveExtruderStack().userChanges.setProperty(setting_key, "value", value_string)
        else:
            active_extruder_index = ExtruderManager.getInstance().activeExtruderIndex
            value_string = "=extruderValueFromContainer(%d,\"%s\",%d)" %(active_extruder_index, setting_key, material_container_index)
            global_container_stack.userChanges.setProperty(setting_key, "value", value_string)
