# Copyright (c) 2023 Aldo Hoeben / fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

from . import MaterialSettingsPlugin

try:
    from cura.ApplicationMetadata import CuraSDKVersion
except ImportError: # Cura <= 3.6
    CuraSDKVersion = "6.0.0"
if CuraSDKVersion >= "8.0.0":
    from PyQt6.QtQml import qmlRegisterType
else:
    from PyQt5.QtQml import qmlRegisterType


def getMetaData():
    return {}

def register(app):
    return {"extension": MaterialSettingsPlugin.MaterialSettingsPlugin()}
