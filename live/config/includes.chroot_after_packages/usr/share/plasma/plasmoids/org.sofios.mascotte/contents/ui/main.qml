// Mascotte SofiOS: il faro sulla scrivania. Passandoci sopra con il mouse compare una X che la toglie
// (si rimette da «Aggiungi widget»). Un giorno un clic aprirà l'assistente.
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: root

    preferredRepresentation: fullRepresentation
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    fullRepresentation: Item {
        id: scena
        implicitWidth: 180
        implicitHeight: 284
        Layout.minimumWidth: 90
        Layout.minimumHeight: 142

        HoverHandler { id: sopra }

        Image {
            anchors.fill: parent
            source: Qt.resolvedUrl("../images/mascotte.png")
            fillMode: Image.PreserveAspectFit
            smooth: true
            mipmap: true
        }

        // la X: compare solo con il mouse sopra
        Rectangle {
            id: chiudi
            width: 28; height: 28; radius: 14
            anchors.top: parent.top; anchors.right: parent.right
            anchors.topMargin: 6; anchors.rightMargin: 6
            color: xArea.containsMouse ? "#d6453a" : "#cc0b2740"
            border.color: "#66ffffff"; border.width: 1
            opacity: (sopra.hovered || xArea.containsMouse) ? 1 : 0
            visible: opacity > 0
            Behavior on opacity { NumberAnimation { duration: 140 } }

            Text {
                anchors.centerIn: parent
                text: "✕"
                color: "white"
                font.pixelSize: 13
                font.bold: true
            }
            MouseArea {
                id: xArea
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: Plasmoid.internalAction("remove").trigger()
            }
            Accessible.role: Accessible.Button
            Accessible.name: "Nascondi la mascotte"
        }
    }
}
