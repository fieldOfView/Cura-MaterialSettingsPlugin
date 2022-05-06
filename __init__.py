# Copyright (c) 2022 Aldo Hoeben / fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

from . import MaterialSettingsPlugin
from . import MaterialSettingDefinitionsModel
from . import CustomStackProxy
from . import HelperProxy

try:
    from PyQt6.QtQml import qmlRegisterType
except ImportError:
    from PyQt5.QtQml import qmlRegisterType


def getMetaData():
    return {}

def register(app):
    qmlRegisterType(CustomStackProxy.CustomStackProxy, "MaterialSettingsPlugin", 1, 0, "CustomStack")
    qmlRegisterType(MaterialSettingDefinitionsModel.MaterialSettingDefinitionsModel, "MaterialSettingsPlugin", 1, 0, "MaterialSettingDefinitionsModel")
    qmlRegisterType(HelperProxy.HelperProxy, "MaterialSettingsPlugin", 1, 0, "Helper")

    return {"extension": MaterialSettingsPlugin.MaterialSettingsPlugin()}
