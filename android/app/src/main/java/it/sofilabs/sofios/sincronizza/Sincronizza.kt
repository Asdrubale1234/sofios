package it.sofilabs.sofios.sincronizza

/** Una cartella da sincronizzare: l'identificatore è uguale su tutti i dispositivi (PC, tablet, telefono). */
data class CartellaSync(val id: String, val nome: String, val percorso: String)

data class Dispositivo(val id: String, val nome: String, val collegato: Boolean)

/**
 * Le impostazioni di SofiOS per la sincronizzazione (le stesse del computer, vedi docs/DISPOSITIVI.md del ramo del PC):
 * solo rete di casa, niente relay/scoperta globale/attraversamento del router/statistiche/aggiornamenti da soli,
 * cartelle sendreceive con cestino di 30 giorni. Gira solo quando l'utente apre la pagina «Dispositivi»:
 * dentro SofiOS non resta acceso niente.
 */
object Sincronizza {
    const val CESTINO_GIORNI = "30"

    val OPZIONI: Map<String, Any?> = linkedMapOf(
        "globalAnnounceEnabled" to false, "relaysEnabled" to false, "natEnabled" to false, "localAnnounceEnabled" to true,
        "urAccepted" to -1, "autoUpgradeIntervalH" to 0, "crashReportingEnabled" to false, "startBrowser" to false
    )

    @Suppress("UNCHECKED_CAST")
    private fun mappa(x: Any?) = x as Map<String, Any?>
    @Suppress("UNCHECKED_CAST")
    private fun elenco(x: Any?) = x as List<Any?>

    fun miaChiave(st: Syncthing): String = mappa(st.leggi("system/status"))["myID"] as String

    fun acceso(st: Syncthing): Boolean = try { st.leggi("system/ping"); true } catch (e: Exception) { false }

    /** Mette a posto le impostazioni, il nome del dispositivo e le cartelle. Si può ripetere senza danni. */
    fun prepara(st: Syncthing, nomeDispositivo: String, cartelle: List<CartellaSync>) {
        val io = miaChiave(st)
        st.modifica("config/options", OPZIONI)
        val me = mappa(st.leggi("config/devices/$io")).toMutableMap()
        if (me["name"] != nomeDispositivo) { me["name"] = nomeDispositivo; st.metti("config/devices/$io", me) }
        for (c in cartelle) {
            val esistente = try { mappa(st.leggi("config/folders/${c.id}")).toMutableMap() } catch (e: ErroreSincronizza) { if (e.codice == 404) null else throw e }
            val f = esistente ?: linkedMapOf<String, Any?>(
                "id" to c.id, "label" to c.nome, "path" to c.percorso, "type" to "sendreceive",
                "fsWatcherEnabled" to true, "fsWatcherDelayS" to 5,
                "devices" to listOf(mapOf("deviceID" to io))
            )
            if (esistente != null) f["type"] = "sendreceive"
            f["versioning"] = mapOf("type" to "trashcan", "params" to mapOf("cleanoutDays" to CESTINO_GIORNI))
            st.metti("config/folders/${c.id}", f)
        }
        condividiConTutti(st, cartelle)
    }

    /** Tutti i dispositivi di cui ci si fida ricevono tutte le cartelle SofiOS. */
    fun condividiConTutti(st: Syncthing, cartelle: List<CartellaSync>) {
        val io = miaChiave(st)
        val altri = elenco(st.leggi("config/devices")).map { mappa(it)["deviceID"] as String }.filter { it != io }
        for (c in cartelle) {
            val f = mappa(st.leggi("config/folders/${c.id}")).toMutableMap()
            val devs = elenco(f["devices"]).map { mappa(it) }.toMutableList()
            var cambiato = false
            for (d in altri) if (devs.none { it["deviceID"] == d }) { devs.add(mapOf("deviceID" to d, "introducedBy" to "", "encryptionPassword" to "")); cambiato = true }
            if (cambiato) { f["devices"] = devs; st.metti("config/folders/${c.id}", f) }
        }
    }

    fun dispositivi(st: Syncthing): List<Dispositivo> {
        val io = miaChiave(st)
        val conn = mappa(mappa(st.leggi("system/connections"))["connections"])
        return elenco(st.leggi("config/devices")).map { mappa(it) }.filter { it["deviceID"] != io }.map {
            val id = it["deviceID"] as String
            val nome = (it["name"] as? String)?.takeIf { n -> n.isNotBlank() } ?: id.take(7)
            Dispositivo(id, nome, (conn[id] as? Map<*, *>)?.get("connected") == true)
        }
    }

    /** Dispositivi che hanno chiesto di collegarsi e aspettano il consenso di questo. */
    fun inAttesa(st: Syncthing): List<Pair<String, String>> = try {
        mappa(st.leggi("cluster/pending/devices")).map { (id, v) ->
            id to ((v as? Map<*, *>)?.get("name") as? String)?.takeIf { it.isNotBlank() }.orEmpty().ifEmpty { id.take(7) }
        }
    } catch (e: ErroreSincronizza) { emptyList() }

    fun fidati(st: Syncthing, codice: String, nome: String, cartelle: List<CartellaSync>) {
        val c = codice.trim().uppercase()
        st.metti("config/devices/$c", mapOf("deviceID" to c, "name" to nome.ifBlank { c.take(7) }, "addresses" to listOf("dynamic"), "autoAcceptFolders" to false))
        condividiConTutti(st, cartelle)
    }

    fun rimuovi(st: Syncthing, codice: String, cartelle: List<CartellaSync>) {
        for (c in cartelle) {
            val f = mappa(st.leggi("config/folders/${c.id}")).toMutableMap()
            f["devices"] = elenco(f["devices"]).map { mappa(it) }.filter { it["deviceID"] != codice }
            st.metti("config/folders/${c.id}", f)
        }
        st.cancella("config/devices/$codice")
    }

    /** Percentuale media di completamento verso i dispositivi collegati, o null se non c'è nessun collegato. */
    fun completamento(st: Syncthing, cartelle: List<CartellaSync>): Double? {
        val v = ArrayList<Double>()
        for (d in dispositivi(st)) if (d.collegato) for (c in cartelle) {
            try { v.add((mappa(st.leggi("db/completion?device=${d.id}&folder=${c.id}"))["completion"] as? Double) ?: 100.0) } catch (e: ErroreSincronizza) { }
        }
        return if (v.isEmpty()) null else v.average()
    }

    fun codiceValido(codice: String) = Regex("([A-Z2-7]{7}-){7}[A-Z2-7]{7}").matches(codice.trim().uppercase())
}
