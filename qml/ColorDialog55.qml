// Copyright (c) 2023 Aldo Hoeben / fieldOfView
// The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.15
import QtQuick.Dialogs

ColorDialog
{
    id: colorDialog
    title: catalog.i18nc("@title", "Material color picker")
    selectedColor: properties.color_code
    onAccepted: base.setMetaDataEntry("color_code", properties.color_code, selectedColor)
}
