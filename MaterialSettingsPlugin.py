# Copyright (c) 2023 Aldo Hoeben / fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

import os.path

try:
    from cura.ApplicationMetadata import CuraSDKVersion
except ImportError: # Cura <= 3.6
    CuraSDKVersion = "6.0.0"

USE_QT5 = False
# Cura 5.11 uses SDK 8.11.0 and has a new PreferencesDialog without removePage/insertPage
USE_NEW_PREFERENCES_DIALOG = CuraSDKVersion >= "8.11.0"

if CuraSDKVersion >= "8.0.0":
    from PyQt6.QtCore import QUrl, QObject, pyqtProperty, pyqtSignal, QTimer
    from PyQt6.QtGui import QGuiApplication
    from PyQt6.QtQml import qmlRegisterType
else:
    from PyQt5.QtCore import QUrl, QObject, pyqtProperty, pyqtSignal, QTimer
    from PyQt5.QtGui import QGuiApplication
    from PyQt5.QtQml import qmlRegisterType
    USE_QT5 = True

from UM.Extension import Extension
from UM.Logger import Logger
from UM.Resources import Resources
from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderManager import ExtruderManager
from cura.Settings.MaterialSettingsVisibilityHandler import MaterialSettingsVisibilityHandler

try:
    # Cura 3.6 and newer
    from cura.Settings.CuraFormulaFunctions import CuraFormulaFunctions
except ImportError:
    # Cura 3.5
    from cura.Settings.CustomSettingFunctions import CustomSettingFunctions as CuraFormulaFunctions  # type: ignore

from .MaterialSettingsPluginVisibilityHandler import MaterialSettingsPluginVisibilityHandler
from .MaterialSettingsProxy import MaterialSettingsProxy

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")


class MaterialSettingsPlugin(Extension):
    def __init__(self) -> None:
        super().__init__()

        default_material_settings = list(MaterialSettingsVisibilityHandler().getVisible())  # the default list
        default_material_settings.append("material_flow")

        CuraApplication.getInstance().getPreferences().addPreference(
            "material_settings/visible_settings",
            ";".join(default_material_settings)
        )

        CuraApplication.getInstance().engineCreatedSignal.connect(self._onEngineCreated)

        # Add item to settings list context menu
        if hasattr(CuraFormulaFunctions, "getValueFromContainerAtIndex"):
            api = CuraApplication.getInstance().getCuraAPI()
            api.interface.settings.addContextMenuItem({
               "name": catalog.i18nc("@item:inmenu", "Use value from material"),
               "icon_name": "",
               "actions": ["__call__"],
               "menu_item": self.useValueFromMaterialContainer
            })

        self._proxy = MaterialSettingsProxy()

    def _onEngineCreated(self) -> None:
        # Make MaterialSettingsProxy available without using qmlRegisterSingletonType
        try:
            qml_engine = CuraApplication.getInstance()._qml_engine
        except AttributeError:
            qml_engine = CuraApplication.getInstance()._engine

        qml_engine.rootContext().setContextProperty("MaterialSettingsPlugin", self._proxy)

        qml_folder = "qml" if not USE_QT5 else "qml_qt5"
        self._materials_page_path = QUrl.fromLocalFile(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            qml_folder,
            "MaterialsPage.qml"
        ))

        if USE_NEW_PREFERENCES_DIALOG:
            # Cura 5.11+: New PreferencesDialog without removePage/insertPage
            # We need to hook into dialog creation and modify the Materials page
            self._setupNewPreferencesDialogHook()
        else:
            # Cura 5.10 and earlier: Use the old method
            self._setupLegacyPreferencesDialog()

    def _setupNewPreferencesDialogHook(self) -> None:
        """Setup hook for Cura 5.11+ PreferencesDialog that uses hardcoded page list."""
        Logger.log("d", "Setting up MaterialSettingsPlugin for Cura 5.11+ PreferencesDialog")

        self._patched_dialogs = set()  # Track dialogs we've already patched

        main_window = CuraApplication.getInstance().getMainWindow()
        if not main_window:
            Logger.log("e", "Could not setup MaterialSettingsPlugin: no main window")
            return

        # Set context property with the path to the plugin's MaterialsPage
        # This allows QML to access the path
        try:
            qml_engine = CuraApplication.getInstance()._qml_engine
        except AttributeError:
            qml_engine = CuraApplication.getInstance()._engine

        qml_engine.rootContext().setContextProperty(
            "MaterialSettingsPluginMaterialsPagePath",
            self._materials_page_path.toString()
        )

        # Connect to focus window changes to detect new dialog windows
        # UM.Dialog creates a separate window, not a child of the main window
        QGuiApplication.instance().focusWindowChanged.connect(self._onFocusWindowChanged)
        Logger.log("d", "Connected to focusWindowChanged for preference dialog detection")

    def _onFocusWindowChanged(self, window) -> None:
        """Called when focus changes to a different window (e.g., new dialog opened)."""
        if window is None:
            return

        # Use a short timer to allow the QML to fully initialize
        QTimer.singleShot(50, lambda: self._checkWindowForPreferencesDialog(window))

    def _checkWindowForPreferencesDialog(self, window) -> None:
        """Check if the given window is a PreferencesDialog and patch it if so."""
        if window is None:
            return

        # Skip if we've already patched this window
        window_id = id(window)
        if window_id in self._patched_dialogs:
            return

        try:
            # Get the contentItem of the window (for QQuickWindow)
            content_item = window.contentItem() if hasattr(window, 'contentItem') else None
            if content_item is None:
                return

            # Check window title for "Preferences"
            title = window.title() if hasattr(window, 'title') else ""
            if "Preferences" not in str(title):
                return

            Logger.log("d", "Found Preferences window, attempting to patch...")

            # The PreferencesDialog structure: Window > contentItem > UM.Dialog content
            # We need to find the ListView with the page model
            if self._patchPreferencesDialog(content_item):
                self._patched_dialogs.add(window_id)

        except Exception as e:
            Logger.log("d", "Error checking window: %s" % str(e))

    def _findListViewWithModel(self, parent, depth=0):
        """Recursively find a ListView with a model property containing page entries."""
        if depth > 10:  # Prevent infinite recursion
            return None

        try:
            # For QQuickItem, use childItems() to get visual children
            # For QObject, use children() to get QObject children
            if hasattr(parent, 'childItems'):
                children = list(parent.childItems())
            elif hasattr(parent, 'children'):
                children = list(parent.children())
            else:
                children = []

            for child in children:
                # Check if this child has model and currentIndex (ListView characteristics)
                try:
                    model = child.property("model") if hasattr(child, 'property') else None

                    if model is not None:
                        # Verify it's the page list by checking model structure
                        try:
                            if hasattr(model, '__len__') and len(model) >= 4:
                                first_item = model[0]
                                if hasattr(first_item, '__contains__') and "name" in first_item and "item" in first_item:
                                    return child
                                elif hasattr(first_item, 'property'):
                                    # QML object, try property access
                                    name_prop = first_item.property("name")
                                    item_prop = first_item.property("item")
                                    if name_prop is not None and item_prop is not None:
                                        return child
                        except (TypeError, KeyError, IndexError):
                            pass
                except Exception:
                    pass

                # Recurse into children
                result = self._findListViewWithModel(child, depth + 1)
                if result is not None:
                    return result
        except Exception:
            pass

        return None

    def _patchPreferencesDialog(self, dialog) -> bool:
        """Patch a PreferencesDialog to use the plugin's MaterialsPage. Returns True if successful."""
        try:
            # Find the pagesList ListView in the dialog using recursive search
            list_view = self._findListViewWithModel(dialog)
            if list_view is None:
                Logger.log("w", "Could not find pagesList ListView in PreferencesDialog")
                return False

            current_model = list_view.property("model")
            if not current_model or len(current_model) < 4:
                Logger.log("w", "PreferencesDialog model is invalid or too short")
                return False

            # Create a new model with the plugin's MaterialsPage
            new_model = []
            for i, entry in enumerate(current_model):
                if i == 3:  # Materials page is at index 3
                    new_model.append({
                        "name": entry["name"],
                        "item": self._materials_page_path.toString()
                    })
                else:
                    new_model.append(entry)

            list_view.setProperty("model", new_model)
            Logger.log("d", "Successfully patched PreferencesDialog to use MaterialSettingsPlugin MaterialsPage")
            return True

        except Exception as e:
            Logger.log("w", "Failed to patch PreferencesDialog: %s" % str(e))
            return False

    def _setupLegacyPreferencesDialog(self) -> None:
        """Setup for Cura 5.10 and earlier using removePage/insertPage."""
        # Adding/removing pages from the preferences dialog is handled in QML
        # There is no way to access the preferences dialog directly, so we have to search for it
        preferencesDialog = None
        main_window = CuraApplication.getInstance().getMainWindow()
        if not main_window:
            Logger.log("e", "Could not replace Materials preferencepane with patched version because there is no main window")
            return
        for child in main_window.contentItem().children():
            try:
                test = child.setPage  # only PreferencesDialog has a setPage function
                preferencesDialog = child
                break
            except:
                pass

        if not preferencesDialog:
            Logger.log("e", "Could not replace Materials preferencepane with patched version")
            return

        Logger.log("d", "Replacing Materials preferencepane with patched version")

        materialPreferencesPage = self._materials_page_path
        if USE_QT5:
            materialPreferencesPage = materialPreferencesPage.toString()

        preferencesDialog.removePage(3)
        preferencesDialog.insertPage(3, catalog.i18nc("@title:tab", "Materials"), materialPreferencesPage)

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
