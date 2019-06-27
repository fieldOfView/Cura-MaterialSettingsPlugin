# Copyright (c) 2019 fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

from . import MaterialSettingsPlugin
from . import MaterialSettingDefinitionsModel

from PyQt5.QtQml import qmlRegisterType


def getMetaData():
    return {}

def register(app):
    qmlRegisterType(MaterialSettingDefinitionsModel.MaterialSettingDefinitionsModel, "MaterialSettingsPlugin", 1, 0, "MaterialSettingDefinitionsModel")

    return {"extension": MaterialSettingsPlugin.MaterialSettingsPlugin()}
