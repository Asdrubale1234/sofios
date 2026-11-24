// Mascotte SofiOS: il faro sulla scrivania. Passandoci sopra con il mouse compare una X che la toglie
// (si rimette da «Aggiungi widget»). Un clic sul faro apre la casella dei comandi.
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasma5support as P5Support

PlasmoidItem {
    id: root

    preferredRepresentation: fullRepresentation
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    // lancia la casella dei comandi (un secondo clic la richiude)
    P5Support.DataSource {
        id: lanciatore
        engine: "executable"
        connectedSources: []
        onNewData: (sorgente) => disconnectSource(sorgente)
    }

    // lo stato di Sofi: neutra, saluta, parla, ascolta, pensa, felice, concentrata, preoccupata
    property string stato: "neutra"
    P5Support.DataSource {
        id: lettore
        engine: "executable"
        interval: 400
        connectedSources: ["cat $HOME/.cache/sofios/sofi-stato 2>/dev/null"]
        onNewData: (sorgente, dati) => {
            var v = (dati["stdout"] || "").trim()
            if (["neutra", "saluta", "parla", "ascolta", "pensa", "felice", "concentrata", "preoccupata"].indexOf(v) < 0) v = "neutra"
            if (v !== root.stato) root.stato = v
        }
    }

    fullRepresentation: Item {
        id: scena
        implicitWidth: 180
        implicitHeight: 284
        Layout.minimumWidth: 90
        Layout.minimumHeight: 142

        HoverHandler { id: sopra }

        // Sofi: la posa cambia con lo stato (scritto da sofios-mascotte in ~/.cache/sofios/sofi-stato) e ondeggia piano
        Item {
            id: corpo
            anchors.fill: parent
            property bool davanti: true
            property string posa: root.stato
            onPosaChanged: {
                var src = Qt.resolvedUrl("../images/sofi-" + posa + ".png")
                if (davanti) { immB.source = src; immB.opacity = 1; immA.opacity = 0 }
                else { immA.source = src; immA.opacity = 1; immB.opacity = 0 }
                davanti = !davanti
            }
            // ondeggia piano: rotazione da -1,2° a +1,2° con perno ai piedi, 2,6 s per andata e ritorno
            property real ang: 0
            transform: Rotation { origin.x: corpo.width / 2; origin.y: corpo.height; angle: corpo.ang }
            SequentialAnimation on ang {
                loops: Animation.Infinite
                NumberAnimation { from: -1.2; to: 1.2; duration: 1300; easing.type: Easing.InOutSine }
                NumberAnimation { from: 1.2; to: -1.2; duration: 1300; easing.type: Easing.InOutSine }
            }
            Image {
                id: immA
                anchors.fill: parent
                source: Qt.resolvedUrl("../images/sofi-neutra.png")
                fillMode: Image.PreserveAspectFit
                smooth: true; mipmap: true
                Behavior on opacity { NumberAnimation { duration: 250 } }
            }
            Image {
                id: immB
                anchors.fill: parent
                opacity: 0
                fillMode: Image.PreserveAspectFit
                smooth: true; mipmap: true
                Behavior on opacity { NumberAnimation { duration: 250 } }
            }
        }

        // un clic sul faro apre la casella dove scrivere cosa fare
        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: lanciatore.connectSource("/usr/local/bin/sofios-mascotte")
            Accessible.role: Accessible.Button
            Accessible.name: "Apri l'assistente"
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
