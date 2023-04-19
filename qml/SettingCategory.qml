// Copyright (c) 2023 Aldo Hoeben / fieldOfView
// The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 2.1

import Cura 1.5 as Cura
import UM 1.5 as UM
import ".."

Cura.CategoryButton
{
    id: base;

    categoryIcon: definition ? UM.Theme.getIcon(definition.icon) : ""
    labelText: definition ? definition.label : ""
    expanded: definition ? definition.expanded : false

    signal showTooltip(string text)
    signal hideTooltip()
    signal contextMenuRequested()

    onClicked: expanded ? settingDefinitionsModel.collapseRecursive(definition.key) : settingDefinitionsModel.expandRecursive(definition.key)
}
