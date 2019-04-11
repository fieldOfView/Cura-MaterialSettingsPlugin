# Copyright (c) 2019 fieldOfView
# The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

from . import MaterialSettingsPlugin


def getMetaData():
    return {}

def register(app):
    return {"extension": MaterialSettingsPlugin.MaterialSettingsPlugin()}
