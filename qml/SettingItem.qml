// Copyright (c) 2022 Aldo Hoeben / fieldOfView
// The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 2.1

import UM 1.5 as UM

UM.TooltipArea
{
    x: model.depth * UM.Theme.getSize("narrow_margin").width
    text: model.description

    width: childrenRect.width
    height: childrenRect.height

    UM.CheckBox
    {
        id: check
        text: definition.label
        checked: definition.visible;

        onClicked:
        {
            definitionsModel.visibilityHandler.setSettingVisibility(model.key, checked);
        }
    }
}
