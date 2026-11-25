import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation {
    id: presentation
    function nextSlide() { presentation.goToNextSlide() }
    Timer { interval: 7000; running: true; repeat: true; onTriggered: presentation.goToNextSlide() }
    Slide {
        Rectangle { anchors.fill: parent; color: "#1c1c1e" }
        Image { anchors.fill: parent; source: "slide-benvenuto.jpg"; fillMode: Image.PreserveAspectCrop; smooth: true }
        Rectangle { anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom; height: 120; color: "#cc1c1c1e" }
        Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.bottom: parent.bottom; anchors.bottomMargin: 62; text: "Benvenuto in SofiOS"; color: "#f5f5f7"; font.pixelSize: 30; font.weight: Font.DemiBold }
        Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.bottom: parent.bottom; anchors.bottomMargin: 26; text: "Il sistema italiano, semplice e rispettoso della tua privacy."; color: "#aeaeb2"; font.pixelSize: 18 }
    }
    Slide {
        Rectangle { anchors.fill: parent; color: "#1c1c1e" }
        Image { anchors.fill: parent; source: "slide-aspetto.jpg"; fillMode: Image.PreserveAspectCrop; smooth: true }
        Rectangle { anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom; height: 120; color: "#cc1c1c1e" }
        Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.bottom: parent.bottom; anchors.bottomMargin: 62; text: "Chiaro o scuro, come vuoi tu"; color: "#f5f5f7"; font.pixelSize: 30; font.weight: Font.DemiBold }
        Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.bottom: parent.bottom; anchors.bottomMargin: 26; text: "Puoi cambiare aspetto quando vuoi, in un attimo."; color: "#aeaeb2"; font.pixelSize: 18 }
    }
    Slide {
        Rectangle { anchors.fill: parent; color: "#1c1c1e" }
        Image { anchors.fill: parent; source: "slide-assistenti.jpg"; fillMode: Image.PreserveAspectCrop; smooth: true }
        Rectangle { anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom; height: 120; color: "#cc1c1c1e" }
        Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.bottom: parent.bottom; anchors.bottomMargin: 62; text: "I tuoi assistenti online"; color: "#f5f5f7"; font.pixelSize: 30; font.weight: Font.DemiBold }
        Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.bottom: parent.bottom; anchors.bottomMargin: 26; text: "ChatGPT, Claude, Gemini e altri: li scegli tu e stanno nel Dock."; color: "#aeaeb2"; font.pixelSize: 18 }
    }
    Slide {
        Rectangle { anchors.fill: parent; color: "#1c1c1e" }
        Image { anchors.fill: parent; source: "slide-sicurezza.jpg"; fillMode: Image.PreserveAspectCrop; smooth: true }
        Rectangle { anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom; height: 120; color: "#cc1c1c1e" }
        Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.bottom: parent.bottom; anchors.bottomMargin: 62; text: "Sicuro fin dall'inizio"; color: "#f5f5f7"; font.pixelSize: 30; font.weight: Font.DemiBold }
        Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.bottom: parent.bottom; anchors.bottomMargin: 26; text: "Cassaforte password e protezione già pronte, senza fare niente."; color: "#aeaeb2"; font.pixelSize: 18 }
    }
    Slide {
        Rectangle { anchors.fill: parent; color: "#1c1c1e" }
        Image { anchors.fill: parent; source: "slide-dispositivi.jpg"; fillMode: Image.PreserveAspectCrop; smooth: true }
        Rectangle { anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom; height: 120; color: "#cc1c1c1e" }
        Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.bottom: parent.bottom; anchors.bottomMargin: 62; text: "PC, tablet e telefono insieme"; color: "#f5f5f7"; font.pixelSize: 30; font.weight: Font.DemiBold }
        Text { anchors.left: parent.left; anchors.leftMargin: 32; anchors.bottom: parent.bottom; anchors.bottomMargin: 26; text: "Foto e file in sincronia, solo nella tua rete di casa."; color: "#aeaeb2"; font.pixelSize: 18 }
    }
}
