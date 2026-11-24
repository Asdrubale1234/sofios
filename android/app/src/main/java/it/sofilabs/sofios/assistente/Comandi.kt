package it.sofilabs.sofios.assistente

import java.text.Normalizer
import java.util.Locale

/** Cosa ha capito Sofi: un'azione e un argomento. Le azioni sono le stesse del computer. */
data class Frase(val azione: String, val arg: Any? = null) {
    /** Testo stabile usato dai collaudi per confrontare con il programma del computer. */
    fun testo(): String = when (arg) {
        null -> ""
        is Pair<*, *> -> "${arg.first}:${arg.second.let { if (it is Boolean) (if (it) "True" else "False") else it.toString() }}"
        else -> arg.toString()
    }
}

/** Un programma che Sofi può aprire, chiudere o disinstallare. */
class Voce(val nome: String, val id: String)

/**
 * Comandi semplici di Sofi, portati da quelli del computer (mascotte_comandi.py): regole sul testo,
 * nessuna intelligenza artificiale e nessun invio all'esterno.
 */
object Comandi {

    fun norm(testo: String): String {
        val d = Normalizer.normalize(testo.lowercase(Locale.ROOT), Normalizer.Form.NFD)
        val senzaAccenti = d.filter { Character.getType(it) != Character.NON_SPACING_MARK.toInt() }
        return senzaAccenti.replace(Regex("[^a-z0-9 ]+"), " ").trim()
    }

    private val ARTICOLI = setOf(
        "il", "lo", "la", "i", "gli", "le", "un", "una", "uno", "l", "per", "favore", "piacere", "programma", "app",
        "applicazione", "mi", "ti", "che", "di", "del", "della", "dei", "delle", "al", "alla", "su", "in", "a", "da",
        "poi", "ora", "adesso", "puoi", "potresti", "vorrei", "voglio")

    private fun parole(t: String) = norm(t).split(Regex("\\s+")).filter { it.isNotEmpty() }
    fun paroleUtili(t: String) = parole(t).filter { it !in ARTICOLI }

    // nome detto dalle persone -> nomi che possono comparire tra i programmi del tablet
    private val SINONIMI = mapOf(
        "browser" to listOf("chrome", "firefox", "browser", "internet", "brave", "edge"),
        "internet" to listOf("chrome", "firefox", "browser", "internet"),
        "web" to listOf("chrome", "firefox", "browser"), "chrome" to listOf("chrome"), "firefox" to listOf("firefox"),
        "posta" to listOf("gmail", "mail", "posta", "outlook"), "email" to listOf("gmail", "mail", "posta"),
        "mail" to listOf("gmail", "mail", "posta"),
        "calcolatrice" to listOf("calcolatrice", "calculator"), "note" to listOf("note", "keep"),
        "file" to listOf("file", "files", "documenti"), "cartelle" to listOf("file", "files"),
        "documenti" to listOf("file", "files", "documenti"),
        "impostazioni" to listOf("impostazioni", "settings"), "settings" to listOf("impostazioni", "settings"),
        "foto" to listOf("foto", "photos", "galleria", "gallery"), "immagini" to listOf("foto", "photos", "galleria"),
        "musica" to listOf("musica", "music", "spotify"), "video" to listOf("video", "youtube"),
        "password" to listOf("cassaforte", "password"), "cassaforte" to listOf("cassaforte", "password"),
        "negozio" to listOf("play store", "store", "negozio"), "store" to listOf("play store", "store"),
        "fotocamera" to listOf("camera", "fotocamera"), "camera" to listOf("camera", "fotocamera"),
        "orologio" to listOf("orologio", "clock"), "sveglia" to listOf("orologio", "clock"),
        "calendario" to listOf("calendario", "calendar"), "mappe" to listOf("maps", "mappe"),
    )

    /** Programmi che corrispondono al nome detto, dal più al meno sicuro (come sul computer). */
    fun cercaProgrammi(frase: String, voci: List<Voce>): List<Voce> {
        val p = paroleUtili(frase)
        if (p.isEmpty()) return emptyList()
        val nomi = LinkedHashSet<String>(p)
        for (x in p) SINONIMI[x]?.let { nomi.addAll(it) }
        val unite = p.joinToString(" ")
        val punteggi = ArrayList<Pair<Int, Voce>>()
        for (v in voci) {
            val n = norm(v.nome)
            val idf = norm(v.id.replace('.', ' ').replace('_', ' '))
            val nParole = n.split(" "); val idParole = idf.split(" ")
            var punti = 0
            if (n == unite) punti = 100
            else if (p.all { it in nParole || it in idParole }) punti = 80
            else if (p.all { it in n || it in idf }) punti = 60
            else for (c in nomi) {
                if (c == n) punti = maxOf(punti, 70)
                else if (c in nParole || c in idParole) punti = maxOf(punti, 55)
                else if (c.length > 3 && (c in n || c in idf)) punti = maxOf(punti, 40)
            }
            if (punti > 0) punteggi.add(punti to v)
        }
        if (punteggi.isEmpty()) return emptyList()
        punteggi.sortWith(compareBy({ -it.first }, { it.second.nome.lowercase(Locale.ROOT) }))
        val migliore = punteggi[0].first
        return punteggi.filter { it.first >= migliore - 10 }.take(6).map { it.second }
    }

    private fun numero(t: String): Int? {
        Regex("(\\d{1,3})").find(t)?.let { return it.groupValues[1].toInt() }
        val parole = linkedMapOf("zero" to 0, "dieci" to 10, "venti" to 20, "trenta" to 30, "quaranta" to 40,
            "cinquanta" to 50, "sessanta" to 60, "settanta" to 70, "ottanta" to 80, "novanta" to 90, "cento" to 100,
            "massimo" to 100, "meta" to 50)
        for ((k, v) in parole) if (Regex("\\b$k\\b").containsMatchIn(t)) return v
        return null
    }

    private fun ha(t: String, schema: String) = Regex(schema).containsMatchIn(t)

    fun interpreta(frase: String): Frase {
        val t = norm(frase)
        if (t.isEmpty()) return Frase("niente")
        if (ha(t, "\\b(aiuto|cosa sai fare|cosa puoi fare|che cosa sai fare|comandi)\\b")) return Frase("aiuto")
        if (ha(t, "\\b(schermata|screenshot|cattura (lo )?schermo|foto (allo )?schermo)\\b")) return Frase("schermata")
        if (ha(t, "\\btema\\b|\\bmodalita (chiara|scura)\\b|\\bmetti (chiaro|scuro)\\b") ||
            (ha(t, "\\b(chiaro|scuro)\\b") && ha(t, "\\b(metti|passa|cambia|usa|attiva)\\b"))) {
            if (ha(t, "\\bchiar")) return Frase("tema", "chiaro")
            if (ha(t, "\\bscur")) return Frase("tema", "scuro")
        }
        if (ha(t, "\\bvolume\\b|\\baudio\\b|\\bsilenzio\\b|\\bmuto\\b|\\bmutal")) {
            if (ha(t, "\\b(togli|riattiva|riattivare) (il )?(muto|silenzio)\\b|\\bsmuta\\b|\\bnon muto\\b"))
                return Frase("volume", "muto" to false)
            if (ha(t, "\\b(muto|silenzio|zitto|muta|mutalo)\\b")) return Frase("volume", "muto" to true)
            val n = numero(t)
            val conPercento = frase.contains("%")
            if (ha(t, "\\b(alza|aumenta|piu forte|piu alto)\\b"))
                return Frase("volume", "delta" to (if (n != null && conPercento) n else 10))
            if (ha(t, "\\b(abbassa|diminuisci|riduci|piu basso|piano)\\b"))
                return Frase("volume", "delta" to -(if (n != null && conPercento) n else 10))
            if (n != null) return Frase("volume", "livello" to n)
        }
        if (ha(t, "\\bluminosit|\\bschermo (piu )?(chiaro|scuro|luminoso)|\\billuminazione\\b")) {
            val n = numero(t)
            val conPercento = frase.contains("%")
            if (ha(t, "\\b(alza|aumenta|piu luminos|piu chiaro)\\b"))
                return Frase("luminosita", "delta" to (if (n != null && conPercento) n else 10))
            if (ha(t, "\\b(abbassa|diminuisci|riduci|meno luminos|piu scuro)\\b"))
                return Frase("luminosita", "delta" to -(if (n != null && conPercento) n else 10))
            if (n != null) return Frase("luminosita", "livello" to n)
        }
        val prefisso = "(?:per favore |puoi |potresti |vorrei |voglio |mi )*"
        Regex("(?:per favore |puoi |potresti |vorrei |voglio )*(?:cerca|cercami|trova|trovami|dove (?:e|sono)|dov e|dove si trova)\\s+(?:su internet |in internet |sul web |online )(.+)")
            .matchEntire(t)?.let { return Frase("cerca-web", it.groupValues[1]) }
        Regex("$prefisso(?:cerca|cercami|trova|trovami|dove (?:e|sono)|dov e|dove si trova|cerca file|trova file)\\s+(.+)")
            .matchEntire(t)?.let { return Frase("cerca-file", it.groupValues[1]) }
        val verbi = listOf(
            "apri|aprimi|avvia|avviami|lancia|fai partire|mostrami|vai su|vai a" to "apri",
            "chiudi|chiudimi|termina|ferma|spegni|esci da" to "chiudi",
            "disinstalla|disinstallami|rimuovi|togli|elimina|cancella" to "disinstalla",
            "installa|installami|scarica|aggiungi" to "installa")
        for ((verbo, azione) in verbi) {
            Regex("(?:per favore |puoi |potresti |vorrei |voglio |mi |ti prego )*(?:$verbo)\\s+(.+)")
                .matchEntire(t)?.let { return Frase(azione, it.groupValues[1]) }
        }
        return Frase("niente")
    }

    const val AIUTO = "Posso fare queste cose:\n" +
        "• aprire un programma: «apri il browser», «apri note», «apri la cassaforte»\n" +
        "• chiudere un programma che è in secondo piano: «chiudi il browser»\n" +
        "• disinstallare (ti chiedo sempre conferma): «disinstalla Gmail»\n" +
        "• installare: «installa GIMP» ti porta allo store, dove Android chiede l'ultima conferma\n" +
        "• cercare i file della Cartella SofiOS: «cerca fattura», «cerca foto mare»\n" +
        "• volume: «volume al 40», «alza il volume», «muto»\n" +
        "• luminosità dello schermo: «luminosità 70», «abbassa la luminosità»\n" +
        "• «fai una schermata» salva la schermata di SofiOS; «cerca su internet…» apre il browser"
}
