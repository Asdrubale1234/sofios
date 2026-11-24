package it.sofilabs.sofios.assistente

import android.app.ActivityManager
import android.app.AlertDialog
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.content.pm.ApplicationInfo
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.drawable.GradientDrawable
import android.media.AudioManager
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.text.Editable
import android.text.InputType
import android.text.TextWatcher
import android.view.Gravity
import android.view.KeyEvent
import android.view.View
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputMethodManager
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import it.sofilabs.sofios.CassaforteActivity
import it.sofilabs.sofios.Controlli
import it.sofilabs.sofios.FileActivity
import it.sofilabs.sofios.ImpostazioniActivity
import it.sofilabs.sofios.NoteActivity
import it.sofilabs.sofios.SchermataSofiOS
import it.sofilabs.sofios.SofiView
import it.sofilabs.sofios.Stile
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * La casella di Sofi: si scrive un comando e lo fa. Senza internet e senza intelligenza artificiale:
 * nulla esce dal tablet. Prima di cambiare o togliere qualcosa chiede sempre conferma.
 */
class CasellaSofi(private val att: SchermataSofiOS, private val sofi: SofiView) : FrameLayout(att) {

    private val scheda = LinearLayout(att).apply { orientation = LinearLayout.VERTICAL }
    private val campo = EditText(att)
    private val risposta = TextView(att)
    private val elenco = LinearLayout(att).apply { orientation = LinearLayout.VERTICAL }
    private val conferma = LinearLayout(att).apply { orientation = LinearLayout.HORIZONTAL }
    private var inAttesa: (() -> Unit)? = null
    private val ritardo = Handler(Looper.getMainLooper())
    private val tornaAscolta = Runnable { if (aperta()) sofi.posa("ascolta") }

    init {
        visibility = View.GONE
        addView(View(att).apply { setBackgroundColor(0x66000000); setOnClickListener { chiudi() } }, LayoutParams(-1, -1))
        val larghezza = minOf(att.resources.displayMetrics.widthPixels - dp(24), dp(520))
        scheda.apply {
            contentDescription = "Casella di Sofi"
            setPadding(dp(20), dp(16), dp(20), dp(18)); isClickable = true
            val r = dp(22).toFloat()
            background = GradientDrawable().apply { setColor(0xF50B2740.toInt()); cornerRadii = floatArrayOf(0f, 0f, 0f, 0f, r, r, r, r) }
        }
        scheda.addView(Stile.testo(att, "Cosa vuoi fare?", 20f, Stile.BIANCO, true))
        scheda.addView(Stile.testo(att, "Scrivi, per esempio: «apri note», «cerca fattura», «volume al 40». Scrivi «aiuto» per l'elenco.",
            13f, Stile.PICCOLO).apply { setPadding(0, dp(4), 0, dp(10)) })
        campo.apply {
            hint = "Scrivi qui e premi Invio…"; contentDescription = "Scrivi a Sofi"
            setHintTextColor(0xFF8FB0CC.toInt()); setTextColor(Stile.TESTO); textSize = 18f
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS
            imeOptions = EditorInfo.IME_ACTION_SEND
            setSingleLine()
            background = Stile.riquadro(att, Stile.PANNELLO, 12); setPadding(dp(14), dp(12), dp(14), dp(12))
            // da una tastiera fisica Android avvisa due volte (pressione e rilascio): si agisce solo alla pressione
            setOnEditorActionListener { _, _, e -> if (e == null || e.action == KeyEvent.ACTION_DOWN) invia(); true }
            addTextChangedListener(object : TextWatcher {
                override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
                override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
                override fun afterTextChanged(s: Editable?) { if (!s.isNullOrEmpty()) sofi.posa("ascolta") }
            })
        }
        scheda.addView(campo, LinearLayout.LayoutParams(-1, dp(52)))
        risposta.apply { textSize = 16f; setTextColor(Stile.TESTO); contentDescription = "Risposta di Sofi"; setPadding(0, dp(12), 0, 0) }
        scheda.addView(risposta)
        conferma.visibility = View.GONE
        conferma.addView(Stile.bottone(att, "Sì", Stile.ORO, Stile.FONDO) { risolvi(true) }, LinearLayout.LayoutParams(0, dp(52), 1f).apply { rightMargin = dp(6) })
        conferma.addView(Stile.bottone(att, "No", Stile.SELEZ, Stile.BIANCO) { risolvi(false) }, LinearLayout.LayoutParams(0, dp(52), 1f).apply { leftMargin = dp(6) })
        scheda.addView(conferma, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(12) })
        scheda.addView(ScrollView(att).apply { addView(elenco) }, LinearLayout.LayoutParams(-1, -2))
        addView(scheda, LayoutParams(larghezza, -2, Gravity.TOP or Gravity.CENTER_HORIZONTAL).apply { topMargin = dp(SchermataSofiOS.ALTEZZA_BARRA) })
    }

    private fun dp(v: Int) = Stile.dp(att, v)

    fun aperta() = visibility == View.VISIBLE

    fun apri() {
        pulisci(); risposta.text = ""; campo.setText("")
        visibility = View.VISIBLE
        sofi.posa("saluta"); ritardo.removeCallbacks(tornaAscolta); ritardo.postDelayed(tornaAscolta, 1400)
        campo.requestFocus()
        campo.postDelayed({
            (att.getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager).showSoftInput(campo, InputMethodManager.SHOW_IMPLICIT)
        }, 200)
    }

    fun chiudi() {
        ritardo.removeCallbacks(tornaAscolta)
        (att.getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager).hideSoftInputFromWindow(campo.windowToken, 0)
        visibility = View.GONE
        pulisci()
        sofi.posa("neutra")
    }

    // ---------- risposte e conferme ----------

    private fun pulisci() { elenco.removeAllViews(); conferma.visibility = View.GONE; inAttesa = null }

    private fun di(testo: String, posa: String = "parla") {
        risposta.text = testo
        sofi.posa(posa)
        ritardo.removeCallbacks(tornaAscolta); ritardo.postDelayed(tornaAscolta, 3000)
    }

    private fun chiedi(domanda: String, azione: () -> Unit) {
        pulisci(); di(domanda); inAttesa = azione; conferma.visibility = View.VISIBLE
    }

    private fun risolvi(si: Boolean) {
        val a = inAttesa; pulisci()
        if (si && a != null) a() else di("Va bene, non ho fatto niente.")
    }

    private fun voce(testo: String, azione: () -> Unit) = Stile.bottone(att, testo, Stile.SECONDARIO, Stile.BIANCO) {
        pulisci(); azione()
    }.also { elenco.addView(it, LinearLayout.LayoutParams(-1, dp(52)).apply { topMargin = dp(8) }) }

    // ---------- capire e fare ----------

    private fun invia() {
        val frase = campo.text.toString().trim()
        campo.setText(""); pulisci(); sofi.posa("pensa")
        val f = Comandi.interpreta(frase)
        when (f.azione) {
            "niente" -> di("Non ho capito. Scrivi «aiuto» per vedere cosa so fare.", "preoccupata")
            "aiuto" -> di(Comandi.AIUTO)
            "apri" -> faApri(f.arg as String)
            "chiudi" -> faChiudi(f.arg as String)
            "disinstalla" -> faDisinstalla(f.arg as String)
            "installa" -> faInstalla(f.arg as String)
            "cerca-file" -> faCercaFile(f.arg as String)
            "cerca-web" -> faCercaWeb(f.arg as String)
            "volume" -> faVolume(f.arg as Pair<*, *>)
            "luminosita" -> faLuminosita(f.arg as Pair<*, *>)
            "tema" -> di("Per ora SofiOS sul tablet ha solo il tema scuro: il tema chiaro non c'è ancora.", "preoccupata")
            "schermata" -> faSchermata()
        }
    }

    // elenco dei programmi che Sofi conosce: quelli del tablet, le app di SofiOS e gli assistenti scelti
    private fun programmi(): List<Voce> {
        val pm = att.packageManager
        val l = ArrayList<Voce>()
        for (r in pm.queryIntentActivities(Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER), 0)) {
            if (r.activityInfo.packageName == att.packageName) continue
            l.add(Voce(r.loadLabel(pm).toString(), r.activityInfo.packageName))
        }
        l.add(Voce("Note", "sofios:note")); l.add(Voce("File", "sofios:file"))
        l.add(Voce("Cassaforte Password", "sofios:cassaforte")); l.add(Voce("Impostazioni", "sofios:impostazioni"))
        for (a in Assistenti.scelti(att)) l.add(Voce(a.nome, "assistente:" + a.id))
        return l
    }

    private fun apriVoce(v: Voce) {
        try {
            when {
                v.id == "sofios:note" -> att.startActivity(Intent(att, NoteActivity::class.java))
                v.id == "sofios:file" -> att.startActivity(Intent(att, FileActivity::class.java))
                v.id == "sofios:cassaforte" -> att.startActivity(Intent(att, CassaforteActivity::class.java))
                v.id == "sofios:impostazioni" -> att.startActivity(Intent(att, ImpostazioniActivity::class.java))
                v.id.startsWith("assistente:") -> {
                    val a = Assistenti.tutti.first { it.id == v.id.removePrefix("assistente:") }
                    att.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(a.indirizzo)))
                }
                else -> att.packageManager.getLaunchIntentForPackage(v.id)?.let { att.startActivity(it) }
                    ?: run { di("Non riesco ad aprire «${v.nome}».", "preoccupata"); return }
            }
            chiudiDopo("Apro «${v.nome}».")
        } catch (e: ActivityNotFoundException) { di("Non riesco ad aprire «${v.nome}».", "preoccupata") }
    }

    private fun chiudiDopo(testo: String) { di(testo, "felice"); postDelayed({ if (aperta()) chiudi() }, 600) }

    private fun faApri(nome: String) {
        val t = Comandi.cercaProgrammi(nome, programmi())
        when {
            t.isEmpty() -> di("Non trovo «${Comandi.paroleUtili(nome).joinToString(" ")}» tra i programmi. Prova con un altro nome.", "preoccupata")
            t.size == 1 -> apriVoce(t[0])
            else -> { di("Quale vuoi aprire?"); for (v in t) voce(v.nome) { apriVoce(v) } }
        }
    }

    private fun esterne(t: List<Voce>) = t.filter { !it.id.startsWith("sofios:") && !it.id.startsWith("assistente:") }

    private fun faChiudi(nome: String) {
        val tutti = Comandi.cercaProgrammi(nome, programmi())
        if (tutti.isEmpty()) { di("Non trovo «${Comandi.paroleUtili(nome).joinToString(" ")}».", "preoccupata"); return }
        val t = esterne(tutti)
        if (t.isEmpty()) { di("Le app di SofiOS si chiudono con il tasto Indietro.", "parla"); return }
        if (t.size > 1) { di("Quale vuoi chiudere?"); for (v in t) voce(v.nome) { chiudiApp(v) }; return }
        chiudiApp(t[0])
    }

    private fun chiudiApp(v: Voce) {
        sofi.posa("concentrata")
        try {
            (att.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager).killBackgroundProcesses(v.id)
            di("Ho chiesto ad Android di chiudere «${v.nome}». Non posso controllare se l'ha fatto: lo decide Android, di solito solo per i programmi in secondo piano.", "parla")
        } catch (e: SecurityException) { di("Android non mi lascia chiudere «${v.nome}».", "preoccupata") }
    }

    private fun faDisinstalla(nome: String) {
        val tutti = Comandi.cercaProgrammi(nome, programmi())
        if (tutti.isEmpty()) { di("Non trovo «${Comandi.paroleUtili(nome).joinToString(" ")}».", "preoccupata"); return }
        val t = esterne(tutti)
        if (t.isEmpty()) { di("Le app di SofiOS non si disinstallano da qui.", "preoccupata"); return }
        if (t.size > 1) { di("Quale vuoi disinstallare?"); for (v in t) voce(v.nome) { chiediDisinstalla(v) }; return }
        chiediDisinstalla(t[0])
    }

    private fun chiediDisinstalla(v: Voce) {
        val info = try { att.packageManager.getApplicationInfo(v.id, 0) } catch (e: Exception) { null }
        if (info != null && (info.flags and ApplicationInfo.FLAG_SYSTEM) != 0) {
            di("«${v.nome}» è un programma del sistema: non si può disinstallare.", "preoccupata"); return
        }
        chiedi("Vuoi disinstallare «${v.nome}»? Poi Android ti chiederà l'ultima conferma.") {
            try { att.startActivity(Intent(Intent.ACTION_DELETE, Uri.parse("package:" + v.id))); di("Ti ho portato alla conferma di Android.", "felice") }
            catch (e: ActivityNotFoundException) { di("Non riesco a disinstallare «${v.nome}».", "preoccupata") }
        }
    }

    private fun faInstalla(nome: String) {
        val cerca = Comandi.paroleUtili(nome).joinToString(" ")
        val t = esterne(Comandi.cercaProgrammi(nome, programmi()))
        if (t.isNotEmpty() && Comandi.norm(t[0].nome) == cerca) { di("«${t[0].nome}» è già installato.", "felice"); return }
        chiedi("Vuoi cercare «$cerca» nello store? Android ti chiederà lui l'ultima conferma per installare.") {
            val q = Uri.encode(cerca)
            try { att.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("market://search?q=$q&c=apps"))) }
            catch (e: ActivityNotFoundException) {
                try { att.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/search?q=$q&c=apps"))) }
                catch (e2: ActivityNotFoundException) { di("Non trovo uno store o un browser.", "preoccupata"); return@chiedi }
            }
            di("Ti ho portato allo store.", "felice")
        }
    }

    private val tipi = mapOf(
        "foto" to listOf("jpg", "jpeg", "png", "gif", "webp", "heic", "bmp"), "immagini" to listOf("jpg", "jpeg", "png", "gif", "webp", "heic", "bmp", "svg"),
        "musica" to listOf("mp3", "flac", "ogg", "wav", "m4a", "opus"), "video" to listOf("mp4", "mkv", "avi", "mov", "webm"),
        "pdf" to listOf("pdf"), "documenti" to listOf("pdf", "doc", "docx", "odt", "txt", "rtf", "xls", "xlsx", "ods", "ppt", "pptx", "odp"))

    private fun faCercaFile(frase: String) {
        val inutili = setOf("file", "cartella", "documento", "cerca", "trova", "cercami", "trovami")
        var estensioni: List<String>? = null
        val nomi = ArrayList<String>()
        for (p in Comandi.paroleUtili(frase)) {
            if (p in tipi) estensioni = (estensioni ?: emptyList()) + tipi.getValue(p)
            else if (p !in inutili) nomi.add(p)
        }
        if (nomi.isEmpty() && estensioni == null) { di("Dimmi che file cerchi, per esempio «cerca fattura».", "preoccupata"); return }
        sofi.posa("concentrata"); risposta.text = "Cerco…"
        val radice = File(att.getExternalFilesDir(null) ?: att.filesDir, "SofiOS")
        Thread {
            val trovati = ArrayList<File>()
            val fine = System.currentTimeMillis() + 8000
            radice.walkTopDown().onEnter { System.currentTimeMillis() < fine && !it.name.startsWith(".") }.forEach { f ->
                if (f.isFile && !f.name.startsWith(".")) {
                    val n = Comandi.norm(f.name)
                    if (nomi.all { it in n } && (estensioni == null || f.extension.lowercase(Locale.ROOT) in estensioni)) trovati.add(f)
                }
            }
            trovati.sortByDescending { it.lastModified() }
            att.runOnUiThread {
                if (!aperta()) return@runOnUiThread
                if (trovati.isEmpty()) di("Non ho trovato niente nella Cartella SofiOS. Per ora è l'unica cartella che posso guardare.", "preoccupata")
                else {
                    di((if (trovati.size == 1) "Ho trovato 1 file" else "Ho trovato ${trovati.size} file") + " nella Cartella SofiOS. Tocca per aprirlo.", "felice")
                    for (f in trovati.take(12)) voce("📄  " + f.name) {
                        att.startActivity(Intent(att, FileActivity::class.java).putExtra(FileActivity.EXTRA_PERCORSO, f.path))
                    }
                }
            }
        }.start()
    }

    private fun faCercaWeb(testo: String) {
        try {
            att.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://duckduckgo.com/?q=" + Uri.encode(testo))))
            chiudiDopo("Apro il browser con la ricerca.")
        } catch (e: ActivityNotFoundException) { di("Non trovo un browser.", "preoccupata") }
    }

    private fun faVolume(a: Pair<*, *>) {
        val am = att.getSystemService(Context.AUDIO_SERVICE) as AudioManager
        val max = am.getStreamMaxVolume(AudioManager.STREAM_MUSIC)
        try {
            when (a.first) {
                "muto" -> am.adjustStreamVolume(AudioManager.STREAM_MUSIC,
                    if (a.second == true) AudioManager.ADJUST_MUTE else AudioManager.ADJUST_UNMUTE, 0)
                "livello" -> { am.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_UNMUTE, 0)
                    am.setStreamVolume(AudioManager.STREAM_MUSIC, Math.round(max * (a.second as Int).coerceIn(0, 100) / 100f), 0) }
                else -> { val d = a.second as Int
                    val nuovo = (am.getStreamVolume(AudioManager.STREAM_MUSIC) + Math.round(max * d / 100f)).coerceIn(0, max)
                    am.setStreamVolume(AudioManager.STREAM_MUSIC, nuovo, 0) }
            }
            di("Fatto.", "felice")
        } catch (e: SecurityException) { di("Su questo tablet non riesco a cambiare il volume.", "preoccupata") }
    }

    private fun faLuminosita(a: Pair<*, *>) {
        if (!Settings.System.canWrite(att)) {
            chiedi("Per cambiare la luminosità serve un permesso di Android, che dai tu una volta sola. Ti porto a darlo?") {
                Controlli.apri(att, Controlli.permessoScrittura(att))
            }; return
        }
        try {
            val ora = Settings.System.getInt(att.contentResolver, Settings.System.SCREEN_BRIGHTNESS, 128)
            val nuovo = when (a.first) {
                "livello" -> Math.round(255 * (a.second as Int).coerceIn(0, 100) / 100f)
                else -> ora + Math.round(255 * (a.second as Int) / 100f)
            }.coerceIn(5, 255)
            Settings.System.putInt(att.contentResolver, Settings.System.SCREEN_BRIGHTNESS_MODE, Settings.System.SCREEN_BRIGHTNESS_MODE_MANUAL)
            Settings.System.putInt(att.contentResolver, Settings.System.SCREEN_BRIGHTNESS, nuovo)
            di("Fatto.", "felice")
        } catch (e: SecurityException) { di("Questo schermo non si regola da qui.", "preoccupata") }
    }

    private fun faSchermata() {
        sofi.posa("concentrata")
        try {
            val cartella = File(File(att.getExternalFilesDir(null) ?: att.filesDir, "SofiOS"), "Schermate").apply { mkdirs() }
            val vista = att.window.decorView
            val prima = visibility
            visibility = View.INVISIBLE
            val bm = Bitmap.createBitmap(vista.width, vista.height, Bitmap.Config.ARGB_8888)
            vista.draw(Canvas(bm))
            visibility = prima
            val f = File(cartella, "schermata-" + SimpleDateFormat("yyyyMMdd-HHmmss", Locale.ROOT).format(Date()) + ".png")
            FileOutputStream(f).use { bm.compress(Bitmap.CompressFormat.PNG, 100, it) }
            di("Ho salvato la schermata di SofiOS nella Cartella SofiOS, dentro «Schermate».", "felice")
        } catch (e: IOException) { di("Non riesco a salvare la schermata. Controlla lo spazio.", "preoccupata") }
    }
}
