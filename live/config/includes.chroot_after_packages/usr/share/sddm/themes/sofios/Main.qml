import QtQuick

// Schermata di accesso di SofiOS. Solo QtQuick (nessun altro modulo), per funzionare su qualsiasi installazione.
Rectangle {
    id: radice
    width: 1280; height: 800
    color: "#0b2740"
    property string fam: "Inter"
    property bool errore: false
    property int utenteIdx: (typeof userModel !== "undefined" && userModel.lastIndex >= 0) ? userModel.lastIndex : 0
    property string nomeUtente: ""
    property string nomeVisibile: ""

    property var nomi: []
    property var reali: []
    function leggiUtente() {
        var n = nomi.length
        if (n === 0) { nomeUtente = ""; nomeVisibile = ""; return }
        var i = Math.max(0, Math.min(utenteIdx, n - 1))
        nomeUtente = nomi[i] || ""
        nomeVisibile = (reali[i] && reali[i].length > 0) ? reali[i] : nomeUtente
    }
    Repeater {
        model: (typeof userModel !== "undefined") ? userModel : 0
        delegate: Item { Component.onCompleted: { radice.nomi[index] = model.name; radice.reali[index] = model.realName; radice.leggiUtente() } }
    }
    function dataItaliana() {
        var g = ["Domenica", "Luned\u00ec", "Marted\u00ec", "Mercoled\u00ec", "Gioved\u00ec", "Venerd\u00ec", "Sabato"]
        var m = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
        var d = new Date()
        return g[d.getDay()] + " " + d.getDate() + " " + m[d.getMonth()]
    }
    function accedi() {
        if (campo.text.length === 0) return
        var sess = (typeof sessionModel !== "undefined") ? sessionModel.lastIndex : 0
        sddm.login(nomeUtente, campo.text, sess >= 0 ? sess : 0)
    }
    Component.onCompleted: { leggiUtente(); campo.forceActiveFocus() }

    Image { anchors.fill: parent; source: "sfondo.png"; fillMode: Image.PreserveAspectCrop }
    Rectangle { anchors.fill: parent; gradient: Gradient {
        GradientStop { position: 0.0; color: "#660b2740" }
        GradientStop { position: 0.55; color: "#aa0b2740" }
        GradientStop { position: 1.0; color: "#330b2740" } } }

    Connections {
        target: (typeof sddm !== "undefined") ? sddm : null
        ignoreUnknownSignals: true
        function onLoginFailed() { campo.text = ""; radice.errore = true; campo.forceActiveFocus() }
    }

    // orologio e data
    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height * 0.10
        spacing: 2
        Text { id: ora; anchors.horizontalCenter: parent.horizontalCenter; color: "#ffffff"; font.family: radice.fam; font.pixelSize: 84; font.weight: Font.DemiBold
            text: Qt.formatTime(new Date(), "hh:mm") }
        Text { id: data; anchors.horizontalCenter: parent.horizontalCenter; color: "#cfe3f7"; font.family: radice.fam; font.pixelSize: 20
            text: radice.dataItaliana() }
    }
    Timer { interval: 1000; running: true; repeat: true; onTriggered: { ora.text = Qt.formatTime(new Date(), "hh:mm"); data.text = radice.dataItaliana() } }

    // scheda di accesso
    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height * 0.42
        spacing: 14
        Image { anchors.horizontalCenter: parent.horizontalCenter; source: "logo.png"; width: 96; height: 96; smooth: true }
        Text { anchors.horizontalCenter: parent.horizontalCenter; color: "#ffffff"; font.family: radice.fam; font.pixelSize: 22; font.weight: Font.DemiBold; text: radice.nomeVisibile }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 8
            Rectangle {
                width: 300; height: 46; radius: 12
                color: "#cc12365a"; border.width: campo.activeFocus ? 2 : 1; border.color: campo.activeFocus ? "#ffd479" : "#1e4f7c"
                TextInput {
                    id: campo
                    anchors.fill: parent; anchors.leftMargin: 16; anchors.rightMargin: 16
                    verticalAlignment: TextInput.AlignVCenter
                    echoMode: TextInput.Password; passwordCharacter: "•"
                    color: "#ffffff"; font.family: radice.fam; font.pixelSize: 18; selectionColor: "#1e6fa8"; clip: true
                    onAccepted: radice.accedi()
                    onTextChanged: radice.errore = false
                    Text { visible: campo.text.length === 0; anchors.verticalCenter: parent.verticalCenter; text: "Password"; color: "#8fb3d4"; font.family: radice.fam; font.pixelSize: 18 }
                }
            }
            Rectangle {
                width: 46; height: 46; radius: 12; color: frecciaArea.pressed ? "#ffe19e" : "#ffd479"
                Text { anchors.centerIn: parent; text: "→"; color: "#0b2740"; font.pixelSize: 24; font.weight: Font.Bold; font.family: radice.fam }
                MouseArea { id: frecciaArea; anchors.fill: parent; onClicked: radice.accedi() }
            }
        }
        Text { anchors.horizontalCenter: parent.horizontalCenter; height: 20; color: "#ffd479"; font.family: radice.fam; font.pixelSize: 14
            text: radice.errore ? "Password sbagliata. Riprova." : "" }
    }

    // cambio utente (solo se ce ne sono piu' di uno)
    Row {
        visible: (typeof userModel !== "undefined") && userModel.count > 1
        anchors.horizontalCenter: parent.horizontalCenter; y: parent.height * 0.82; spacing: 10
        Rectangle { width: 40; height: 36; radius: 10; color: "#cc12365a"; Text { anchors.centerIn: parent; text: "‹"; color: "#ffffff"; font.pixelSize: 24 }
            MouseArea { anchors.fill: parent; onClicked: { radice.utenteIdx = (radice.utenteIdx + userModel.count - 1) % userModel.count; radice.leggiUtente(); campo.forceActiveFocus() } } }
        Rectangle { width: 40; height: 36; radius: 10; color: "#cc12365a"; Text { anchors.centerIn: parent; text: "›"; color: "#ffffff"; font.pixelSize: 24 }
            MouseArea { anchors.fill: parent; onClicked: { radice.utenteIdx = (radice.utenteIdx + 1) % userModel.count; radice.leggiUtente(); campo.forceActiveFocus() } } }
    }

    // spegni / riavvia / sospendi (in basso a sinistra, lontano dalla mascotte)
    Row {
        anchors.left: parent.left; anchors.bottom: parent.bottom; anchors.margins: 24; spacing: 10
        Repeater {
            model: [ { t: "Sospendi", a: 0 }, { t: "Riavvia", a: 1 }, { t: "Spegni", a: 2 } ]
            delegate: Rectangle {
                width: etichetta.implicitWidth + 28; height: 36; radius: 10
                color: area.containsMouse ? "#2a82c2" : "#cc12365a"
                Text { id: etichetta; anchors.centerIn: parent; text: modelData.t; color: "#ffffff"; font.family: radice.fam; font.pixelSize: 14; font.weight: Font.DemiBold }
                MouseArea { id: area; anchors.fill: parent; hoverEnabled: true
                    onClicked: { if (typeof sddm === "undefined") return; if (modelData.a === 0) sddm.suspend(); else if (modelData.a === 1) sddm.reboot(); else sddm.powerOff() } }
            }
        }
    }
    Keys.onEscapePressed: { campo.text = "" }
}
