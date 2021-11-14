# TODO: bayad beshe az table khasi az data base backup begire v to folder haye moshakhas berize v bayad data archive ro tike tike konim
# TODO: jnjimjmmijmi
# import QtQuick
from PyQt5.QtWidgets import QListWidget

Item {
    width: 200; height: 250

    ListModel {
        id: myModel
        ListElement { type: "Dog"; age: 8 }
        ListElement { type: "Cat"; age: 5 }
    }

    Component {
        id: myDelegate
        Text { text: type + ", " + age }
    }

    ListView {
        anchors.fill: parent
        model: myModel
        delegate: myDelegate
    }
}