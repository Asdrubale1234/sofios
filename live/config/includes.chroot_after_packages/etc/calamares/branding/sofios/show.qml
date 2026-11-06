import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation {
    id: presentation
    Slide {
        Rectangle { anchors.fill: parent; color: "#0b2740" }
        Text {
            anchors.centerIn: parent
            text: "Sto installando SofiOS…\nCi vorrà qualche minuto."
            color: "#e6f1ff"
            font.pixelSize: 28
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
