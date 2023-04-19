// Copyright (c) 2023 Aldo Hoeben / fieldOfView
// The MaterialSettingsPlugin is released under the terms of the AGPLv3 or higher.

import QtQuick 2.15
import QtQuick.Controls 2.4

import UM 1.5 as UM
import Cura 1.0 as Cura
import MaterialSettingsPlugin 1.0 as MaterialSettingsPlugin

UM.Dialog {
    id: settingsDialog

    title: catalog.i18nc("@title:window", "Select available Material Settings")
    width: screenScaleFactor * 360

    backgroundColor: UM.Theme.getColor("background_1")
    onVisibilityChanged:
    {
        if(visible)
        {
            updateFilter()
        }
    }

    function updateFilter()
    {
        var new_filter = {};

        if(filterInput.text != "")
        {
            new_filter["i18n_label"] = "*" + filterInput.text;
        }

        listview.model.filter = new_filter;
    }

    Cura.TextField {
        id: filterInput

        anchors {
            top: parent.top
            left: parent.left
            right: toggleShowAll.left
            rightMargin: UM.Theme.getSize("default_margin").width
        }

        placeholderText: catalog.i18nc("@label:textbox", "Filter...");

        onTextChanged: settingsDialog.updateFilter()
    }

    UM.CheckBox
    {
        id: toggleShowAll

        anchors {
            top: parent.top
            right: parent.right
        }

        text: catalog.i18nc("@label:checkbox", "Show all")
        checked: listview.model.showAll
        onClicked:
        {
            listview.model.showAll = checked;
        }
    }

    ListView
    {
        id:listview

        anchors
        {
            top: filterInput.bottom;
            left: parent.left;
            right: parent.right;
            bottom: parent.bottom;
        }

        ScrollBar.vertical: UM.ScrollBar { id: scrollBar }
        clip: true

        model: MaterialSettingsPlugin.MaterialSettingDefinitionsModel
        {
            id: definitionsModel;
            containerId: Cura.MachineManager.activeMachine.definition.id
            visibilityHandler: Cura.MaterialSettingsVisibilityHandler {}
            showAll: true
            showAncestors: true
            expanded: [ "*" ]
            exclude: [ "machine_settings", "command_line_settings" ]
        }
        delegate:Loader
        {
            id: loader

            width: parent ? parent.width : undefined
            height: model.type != undefined ? UM.Theme.getSize("section").height : 0;

            property var definition: model
            property var settingDefinitionsModel: definitionsModel

            asynchronous: true
            source:
            {
                switch(model.type)
                {
                    case "category":
                        return "SettingCategory.qml"
                    default:
                        return "SettingItem.qml"
                }
            }
        }
        Component.onCompleted: settingsDialog.updateFilter()
    }

    rightButtons: [
        Cura.TertiaryButton {
            text: catalog.i18nc("@action:button", "Close");
            onClicked: {
                settingsDialog.visible = false;
            }
        }
    ]

    Item
    {
        UM.I18nCatalog { id: catalog; name: "cura"; }
    }
}
