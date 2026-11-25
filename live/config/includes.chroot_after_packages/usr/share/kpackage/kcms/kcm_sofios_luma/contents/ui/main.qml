// Impostazioni → Luma: dove si vede la mascotte (sul desktop e nelle pagine dei programmi)
import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.kcmutils as KCM
import org.kde.plasma.plasma5support as P5Support

KCM.SimpleKCM {
    id: pagina

    property bool sulDesktop: true
    property bool nelleProgrammi: true
    property bool caricato: false

    // piccola utilita' per lanciare un comando e leggerne la risposta
    P5Support.DataSource {
        id: sh
        engine: "executable"
        connectedSources: []
        property var attese: ({})
        onNewData: (sorgente, dati) => {
            var cb = attese[sorgente]; delete attese[sorgente]
            disconnectSource(sorgente)
            if (cb) cb((dati["stdout"] || "").trim())
        }
        function esegui(cmd, cb) { attese[cmd] = cb; connectSource(cmd) }
    }

    function leggi() {
        sh.esegui("/usr/local/bin/sofios-mascotte --pagine-stato", function (r) { pagina.nelleProgrammi = (r !== "no"); pagina.caricato = true })
        sh.esegui("/usr/local/bin/sofios-mascotte --desktop-stato", function (r) { pagina.sulDesktop = (r === "si") })
    }
    Component.onCompleted: leggi()

    ColumnLayout {
        spacing: Kirigami.Units.largeSpacing

        RowLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.largeSpacing
            Image {
                source: "file:///usr/share/plasma/plasmoids/org.sofios.mascotte/contents/images/sofi-saluta.png"
                Layout.preferredHeight: Kirigami.Units.gridUnit * 9
                Layout.preferredWidth: Layout.preferredHeight * 0.79
                fillMode: Image.PreserveAspectFit
                smooth: true; mipmap: true
            }
            ColumnLayout {
                Layout.fillWidth: true
                Kirigami.Heading { text: "Luma"; level: 1 }
                QQC2.Label {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    text: "Luma è la mascotte di SofiOS: ti aiuta a fare le cose scrivendole in una casella. Qui scegli dove vuoi vederla. Puoi cambiare idea quando vuoi."
                }
            }
        }

        Kirigami.Separator { Layout.fillWidth: true }

        QQC2.Switch {
            text: "Luma sul desktop"
            checked: pagina.sulDesktop
            enabled: pagina.caricato
            onToggled: sh.esegui("/usr/local/bin/sofios-mascotte " + (checked ? "--desktop-metti" : "--desktop-togli"), function (r) { pagina.sulDesktop = (r === "si") })
        }
        QQC2.Label {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.gridUnit * 2
            wrapMode: Text.WordWrap
            opacity: 0.7
            text: "Il faro con la faccia in basso a destra. Cliccandoci si apre la casella dei comandi."
        }

        QQC2.Switch {
            text: "Luma nelle pagine dei programmi"
            checked: pagina.nelleProgrammi
            enabled: pagina.caricato
            onToggled: sh.esegui("/usr/local/bin/sofios-mascotte " + (checked ? "--mostra-pagine" : "--nascondi-pagine"), function (r) { pagina.nelleProgrammi = checked })
        }
        QQC2.Label {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.gridUnit * 2
            wrapMode: Text.WordWrap
            opacity: 0.7
            text: "In Note, Cassaforte, Dispositivi e SoStore. Se la togli, i programmi restano uguali ma senza Luma."
        }

        QQC2.Label {
            Layout.fillWidth: true
            Layout.topMargin: Kirigami.Units.largeSpacing
            wrapMode: Text.WordWrap
            opacity: 0.7
            text: "Suggerimento: tasto destro su Luma dentro una pagina per nasconderla subito."
        }
    }
}
