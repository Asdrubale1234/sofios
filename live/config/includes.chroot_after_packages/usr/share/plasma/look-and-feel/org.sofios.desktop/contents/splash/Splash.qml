import QtQuick

// Schermata di caricamento SofiOS: mare scuro, logo, barra sottile che avanza
Rectangle {
    id: root
    color: "#0b2740"
    property int stage: 0

    Image {
        id: logo
        source: "images/logo.png"
        width: 200
        height: 200
        smooth: true
        anchors.centerIn: parent
        opacity: 0
        NumberAnimation on opacity { from: 0; to: 1; duration: 700; running: true }
    }

    Rectangle {
        id: traccia
        width: 220
        height: 4
        radius: 2
        color: "#1b3b5a"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: logo.bottom
        anchors.topMargin: 36
        Rectangle {
            height: parent.height
            radius: 2
            color: "#ffd479"
            width: parent.width * Math.min(root.stage, 6) / 6
            Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
        }
    }
}
