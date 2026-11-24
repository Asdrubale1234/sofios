package it.sofilabs.sofios

import android.app.AlertDialog
import android.content.ClipData
import android.content.ClipDescription
import android.content.ClipboardManager
import android.content.Context
import android.content.DialogInterface
import android.content.pm.ApplicationInfo
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.PersistableBundle
import android.text.InputType
import android.text.TextUtils
import android.text.method.PasswordTransformationMethod
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.BaseAdapter
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import it.sofilabs.sofios.cassaforte.FileDanneggiato
import it.sofilabs.sofios.cassaforte.FormatoNonSupportato
import it.sofilabs.sofios.cassaforte.Kdbx
import it.sofilabs.sofios.cassaforte.PasswordSbagliata
import it.sofilabs.sofios.cassaforte.Voce
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.security.SecureRandom
import java.util.Locale

/**
 * Cassaforte Password di SofiOS, come sul computer: stesso formato (KeePass .kdbx), password principale,
 * blocco automatico dopo 5 minuti, password copiata che sparisce dagli appunti dopo 20 secondi.
 * Su Android si blocca anche quando esci dall'app.
 */
class CassaforteActivity : SchermataSofiOS() {

    private val principale = Handler(Looper.getMainLooper())
    private val bloccaDopo = Runnable { blocca() }
    private val puliscDopo = Runnable { pulisciAppunti() }
    private var copiato: String? = null

    private var kdbx: Kdbx? = null
    private var voci: List<Voce> = emptyList()
    private var elencoVisibile: List<Voce> = emptyList()
    private var scelta: Voce? = null
    private var mostraPw = false
    private var stretto = false
    private var nelDettaglio = false
    private var avviata = false

    private lateinit var file: File
    private lateinit var contenitore: FrameLayout
    // sblocco
    private lateinit var titoloSblocco: TextView
    private lateinit var testoSblocco: TextView
    private lateinit var campoPw: EditText
    private lateinit var campoPw2: EditText
    private lateinit var avvisoSblocco: TextView
    private lateinit var erroreSblocco: TextView
    private lateinit var bottoneSblocco: TextView
    private lateinit var paginaSblocco: View
    // principale
    private lateinit var paginaPrincipale: View
    private lateinit var colonnaElenco: LinearLayout
    private lateinit var colonnaDettaglio: FrameLayout
    private lateinit var cerca: EditText
    private lateinit var elenco: ListView
    private val adattatore = Adattatore()
    private lateinit var dTitolo: TextView
    private lateinit var dUtente: TextView
    private lateinit var dPassword: TextView
    private lateinit var dSito: TextView
    private lateinit var dNote: TextView
    private lateinit var dAvviso: TextView
    private lateinit var dMostra: TextView
    private lateinit var pilaScheda: FrameLayout
    private lateinit var schedaVuota: TextView
    private lateinit var scheda: View

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if ((applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE) == 0) {
            window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
        }
        stretto = resources.configuration.screenWidthDp < 600
        file = File(Cartella.password(this), "cassaforte.kdbx")
        contenitore = FrameLayout(this).apply { setBackgroundColor(Stile.FONDO) }
        paginaSblocco = creaSblocco()
        paginaPrincipale = creaPrincipale()
        contenitore.addView(paginaSblocco, FrameLayout.LayoutParams(-1, -1))
        contenitore.addView(paginaPrincipale, FrameLayout.LayoutParams(-1, -1))
        mostra(contenitore)
        mostraSblocco()
    }

    // ---------- sblocco ----------

    private fun campoTesto(descrizione: String, suggerimento: String) = EditText(this).apply {
        hint = suggerimento; contentDescription = descrizione
        setHintTextColor(Stile.PICCOLO); setTextColor(Stile.TESTO); textSize = 17f
        inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_PASSWORD
        background = Stile.riquadro(this@CassaforteActivity, Stile.PANNELLO, 10)
        setPadding(dp(14), dp(12), dp(14), dp(12))
        setSingleLine()
    }

    private fun creaSblocco(): View {
        val colonna = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER_HORIZONTAL
            setPadding(dp(24), dp(24), dp(24), dp(24))
        }
        val largo = LinearLayout.LayoutParams(dp(380), -2).apply { topMargin = dp(12) }
        titoloSblocco = Stile.testo(this, "", 26f, Stile.TESTO, true).apply { gravity = Gravity.CENTER }
        testoSblocco = Stile.testo(this, "", 14f, Stile.PICCOLO).apply { gravity = Gravity.CENTER }
        campoPw = campoTesto("Password principale", "Password principale")
        campoPw2 = campoTesto("Ripeti la password principale", "Ripeti la password principale")
        // Invio sulla tastiera: dalla prima password si passa alla seconda (se si crea), altrimenti si sblocca
        // da una tastiera fisica Android avvisa due volte (pressione e rilascio): si agisce solo alla pressione
        campoPw.setOnEditorActionListener { _, _, e ->
            if (e == null || e.action == android.view.KeyEvent.ACTION_DOWN) {
                if (campoPw2.visibility == View.VISIBLE) campoPw2.requestFocus() else sblocca()
            }
            true
        }
        campoPw2.setOnEditorActionListener { _, _, e ->
            if (e == null || e.action == android.view.KeyEvent.ACTION_DOWN) sblocca(); true
        }
        avvisoSblocco = Stile.testo(this, "Se la dimentichi, nessuno può recuperare le tue password: nemmeno noi.", 13f, Stile.ORO_TESTO)
        erroreSblocco = Stile.testo(this, "", 14f, Stile.ORO_TESTO).apply { gravity = Gravity.CENTER; contentDescription = "Errore" }
        bottoneSblocco = Stile.bottone(this, "", Stile.ORO, Stile.SU_ORO) { sblocca() }
        colonna.addView(titoloSblocco, largo); colonna.addView(testoSblocco, largo)
        colonna.addView(campoPw, largo); colonna.addView(campoPw2, largo)
        colonna.addView(avvisoSblocco, largo); colonna.addView(erroreSblocco, largo)
        colonna.addView(bottoneSblocco, LinearLayout.LayoutParams(dp(380), dp(48)).apply { topMargin = dp(16) })
        return ScrollView(this).apply {
            isFillViewport = true
            addView(FrameLayout(context).apply { addView(colonna, FrameLayout.LayoutParams(-1, -2, Gravity.CENTER)) },
                ViewGroup.LayoutParams(-1, -2))
        }
    }

    private fun mostraSblocco() {
        val nuovo = !file.exists()
        titoloSblocco.text = if (nuovo) "Crea la tua cassaforte" else "Cassaforte Password"
        testoSblocco.text = if (nuovo) "Scegli una password principale: sarà l'unica da ricordare."
                            else "Inserisci la password principale per aprire la cassaforte."
        campoPw2.visibility = if (nuovo) View.VISIBLE else View.GONE
        avvisoSblocco.visibility = if (nuovo) View.VISIBLE else View.GONE
        bottoneSblocco.text = if (nuovo) "Crea cassaforte" else "Sblocca"
        bottoneSblocco.isEnabled = true; bottoneSblocco.alpha = 1f
        campoPw.setText(""); campoPw2.setText(""); erroreSblocco.text = ""
        paginaSblocco.visibility = View.VISIBLE; paginaPrincipale.visibility = View.GONE
    }

    private fun sblocca() {
        val pw = campoPw.text.toString()
        val nuovo = !file.exists()
        if (nuovo) {
            if (pw.length < 8) { erroreSblocco.text = "Almeno 8 caratteri."; return }
            if (pw != campoPw2.text.toString()) { erroreSblocco.text = "Le due password non coincidono."; return }
        }
        bottoneSblocco.isEnabled = false; bottoneSblocco.alpha = 0.5f
        erroreSblocco.text = if (nuovo) "Sto creando la cassaforte…" else "Sblocco in corso…"
        Thread {
            var k: Kdbx? = null
            var errore = ""
            var messaggio = ""
            try {
                if (nuovo) {
                    k = Kdbx.crea(pw)
                    scrivi(k.salva())
                } else {
                    k = Kdbx.apri(file.readBytes(), pw)
                    messaggio = unisciConflitti(k, pw)
                }
            } catch (e: PasswordSbagliata) { errore = "Password sbagliata." }
            catch (e: FormatoNonSupportato) { errore = e.message ?: "Formato non supportato." }
            catch (e: FileDanneggiato) { errore = "Non riesco ad aprire la cassaforte: il file potrebbe essere danneggiato." }
            catch (e: IOException) { errore = "Non riesco a leggere o scrivere la cassaforte. Controlla lo spazio." }
            catch (e: OutOfMemoryError) { errore = "Questo tablet non ha abbastanza memoria per questa cassaforte." }
            principale.post {
                if (isDestroyed || !avviata) { k?.dimentica(); return@post }
                if (k == null) {
                    bottoneSblocco.isEnabled = true; bottoneSblocco.alpha = 1f
                    erroreSblocco.text = errore
                    campoPw.selectAll()
                } else {
                    kdbx = k
                    campoPw.setText(""); campoPw2.setText("")
                    paginaSblocco.visibility = View.GONE; paginaPrincipale.visibility = View.VISIBLE
                    nascondiTastiera()
                    carica(null)
                    if (messaggio.isNotEmpty()) Toast.makeText(this, messaggio, Toast.LENGTH_LONG).show()
                    riavviaBlocco()
                }
            }
        }.start()
    }

    /**
     * Se un altro dispositivo ha cambiato la cassaforte mentre questa era cambiata qui, la sincronizzazione lascia una
     * copia «cassaforte.sync-conflict-….kdbx». Qui si uniscono (stessa regola del computer) e la copia si mette da parte.
     */
    private fun unisciConflitti(k: Kdbx, password: String): String {
        val cartella = file.parentFile ?: return ""
        val copie = (cartella.listFiles { f -> f.name.startsWith("cassaforte.sync-conflict-") && f.name.endsWith(".kdbx") }
            ?.sortedBy { it.name }) ?: return ""
        var unite = 0; var altraPassword = 0
        for (f in copie) {
            try {
                k.unisci(Kdbx.apri(f.readBytes(), password))
                val da = File(cartella, ".conflitti").apply { mkdirs() }
                if (!f.renameTo(File(da, f.name))) f.delete()
                unite++
            } catch (e: PasswordSbagliata) { altraPassword++ }
            catch (e: FileDanneggiato) { /* si lascia dov'è: potrebbe essere ancora in arrivo */ }
            catch (e: FormatoNonSupportato) { }
        }
        if (unite > 0) { try { scrivi(k.salva()) } catch (e: IOException) { return "Non riesco a salvare la cassaforte unita." } }
        return when {
            unite > 0 && altraPassword > 0 -> "Ho unito $unite versioni. Un'altra ha una password diversa e l'ho lasciata da parte."
            unite > 0 -> if (unite == 1) "Ho unito una versione della cassaforte arrivata da un altro dispositivo."
                         else "Ho unito $unite versioni della cassaforte arrivate da altri dispositivi."
            altraPassword > 0 -> "Una versione della cassaforte arrivata da un altro dispositivo ha una password diversa: non l'ho unita."
            else -> ""
        }
    }

    private fun nascondiTastiera() {
        val imm = getSystemService(Context.INPUT_METHOD_SERVICE) as android.view.inputmethod.InputMethodManager
        currentFocus?.let { imm.hideSoftInputFromWindow(it.windowToken, 0); it.clearFocus() }
    }

    /** Scrive il file con una copia di sicurezza (.bak): se qualcosa va storto resta quello di prima. */
    private fun scrivi(dati: ByteArray) {
        val tmp = File(file.path + ".tmp")
        FileOutputStream(tmp).use { it.write(dati); it.flush(); it.fd.sync() }
        if (file.exists()) file.copyTo(File(file.path + ".bak"), overwrite = true)
        if (!tmp.renameTo(file)) throw IOException("rename")
    }

    private fun salvaFile(): Boolean = try {
        scrivi(kdbx!!.salva()); true
    } catch (e: IOException) {
        Toast.makeText(this, "Non riesco a salvare. Le modifiche non sono state scritte: controlla lo spazio.", Toast.LENGTH_LONG).show()
        false
    }

    private fun blocca() {
        principale.removeCallbacks(bloccaDopo)
        for (d in apertiDialoghi) d.dismiss()
        apertiDialoghi.clear()
        kdbx?.dimentica(); kdbx = null
        voci = emptyList(); elencoVisibile = emptyList(); scelta = null
        pulisciAppunti()
        adattatore.notifyDataSetChanged()
        cerca.setText("")
        mostraSblocco()
    }

    private fun riavviaBlocco() {
        principale.removeCallbacks(bloccaDopo)
        if (kdbx != null) principale.postDelayed(bloccaDopo, 5 * 60 * 1000L)
    }

    override fun onUserInteraction() { super.onUserInteraction(); riavviaBlocco() }

    override fun onStart() { super.onStart(); avviata = true }

    override fun onStop() {
        avviata = false
        if (kdbx != null) blocca()      // uscendo dall'app la cassaforte si richiude
        super.onStop()
    }

    // ---------- principale ----------

    private fun creaPrincipale(): View {
        val radice = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL; setPadding(dp(20), dp(18), dp(20), dp(18))
        }
        colonnaElenco = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        colonnaElenco.addView(Stile.testo(this, "Cassaforte Password", 20f, Stile.TESTO, true).apply { setPadding(0, 0, 0, dp(8)) })
        cerca = EditText(this).apply {
            hint = "Cerca…"; contentDescription = "Cerca"; setHintTextColor(Stile.PICCOLO); setTextColor(Stile.TESTO)
            textSize = 16f; setSingleLine(); inputType = InputType.TYPE_CLASS_TEXT
            background = Stile.riquadro(this@CassaforteActivity, Stile.PANNELLO, 10); setPadding(dp(12), dp(10), dp(12), dp(10))
            addTextChangedListener(object : android.text.TextWatcher {
                override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
                override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
                override fun afterTextChanged(s: android.text.Editable?) { if (kdbx != null) carica(scelta?.id) }
            })
        }
        colonnaElenco.addView(cerca, LinearLayout.LayoutParams(-1, -2).apply { bottomMargin = dp(8) })
        elenco = ListView(this).apply {
            adapter = adattatore; divider = null; dividerHeight = 0
            background = Stile.riquadro(this@CassaforteActivity, Stile.PANNELLO, 12)
            setPadding(dp(6), dp(6), dp(6), dp(6)); clipToPadding = false
            setOnItemClickListener { _, _, i, _ -> scegli(elencoVisibile[i], vaiAlDettaglio = true) }
        }
        colonnaElenco.addView(elenco, LinearLayout.LayoutParams(-1, 0, 1f))
        colonnaElenco.addView(Stile.bottone(this, "Nuova password", Stile.ORO, Stile.SU_ORO) { modificaVoce(null) },
            LinearLayout.LayoutParams(-1, dp(48)).apply { topMargin = dp(10) })
        colonnaElenco.addView(Stile.bottone(this, "Blocca", Stile.SECONDARIO, Stile.TESTO) { blocca() },
            LinearLayout.LayoutParams(-1, dp(48)).apply { topMargin = dp(10) })

        colonnaDettaglio = FrameLayout(this)
        pilaScheda = FrameLayout(this)
        scheda = creaScheda()
        schedaVuota = Stile.testo(this, "Scegli una password dall'elenco\noppure creane una nuova.", 16f, Stile.PICCOLO)
            .apply { gravity = Gravity.CENTER }
        pilaScheda.addView(schedaVuota, FrameLayout.LayoutParams(-1, -1))
        pilaScheda.addView(scheda, FrameLayout.LayoutParams(-1, -1))
        colonnaDettaglio.addView(pilaScheda, FrameLayout.LayoutParams(-1, -1))

        if (stretto) {
            radice.addView(colonnaElenco, LinearLayout.LayoutParams(-1, -1))
            radice.addView(colonnaDettaglio, LinearLayout.LayoutParams(-1, -1))
            colonnaDettaglio.visibility = View.GONE
        } else {
            radice.addView(colonnaElenco, LinearLayout.LayoutParams(dp(290), -1))
            radice.addView(colonnaDettaglio, LinearLayout.LayoutParams(0, -1, 1f).apply { leftMargin = dp(16) })
        }
        return radice
    }

    private fun creaScheda(): View {
        val colonna = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; setPadding(dp(26), dp(22), dp(26), dp(20))
            background = Stile.riquadro(this@CassaforteActivity, Stile.PANNELLO, 14)
        }
        if (stretto) colonna.addView(Stile.testo(this, "‹ Elenco", 16f, Stile.ORO_TESTO, true).apply {
            setPadding(0, 0, 0, dp(8)); setOnClickListener { mostraElenco() }
        })
        dTitolo = Stile.testo(this, "", 24f, Stile.TESTO, true).apply { contentDescription = "Titolo della voce" }
        colonna.addView(dTitolo)
        fun riga(nome: String, valore: TextView, vararg pulsanti: TextView) {
            colonna.addView(Stile.testo(this, nome, 12f, Stile.PICCOLO).apply { setPadding(0, dp(12), 0, 0) })
            val r = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
            r.addView(valore, LinearLayout.LayoutParams(0, -2, 1f))
            for (p in pulsanti) r.addView(p, LinearLayout.LayoutParams(-2, dp(40)).apply { leftMargin = dp(8) })
            colonna.addView(r)
        }
        fun piccolo(t: String, a: () -> Unit) = Stile.bottone(this, t, Stile.SECONDARIO, Stile.TESTO, a).apply { textSize = 13f; minimumHeight = dp(40) }
        dUtente = Stile.testo(this, "", 16f, Stile.TESTO).apply { contentDescription = "Valore utente" }
        dPassword = Stile.testo(this, "", 16f, Stile.TESTO).apply { contentDescription = "Valore password" }
        dSito = Stile.testo(this, "", 16f, Stile.TESTO).apply { contentDescription = "Valore sito" }
        dNote = Stile.testo(this, "", 16f, Stile.TESTO).apply { contentDescription = "Valore note" }
        dMostra = piccolo("Mostra") { alternaPassword() }
        riga("Utente", dUtente, piccolo("Copia utente") { copia(scelta?.utente, false) })
        riga("Password", dPassword, dMostra, piccolo("Copia password") { copia(scelta?.password, true) })
        riga("Sito", dSito)
        riga("Note", dNote)
        dAvviso = Stile.testo(this, "", 13f, Stile.ORO_TESTO).apply { setPadding(0, dp(10), 0, 0) }
        colonna.addView(dAvviso)
        colonna.addView(View(this), LinearLayout.LayoutParams(-1, 0, 1f))
        val b = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        b.addView(Stile.bottone(this, "Modifica", Stile.ORO, Stile.SU_ORO) { modificaVoce(scelta) },
            LinearLayout.LayoutParams(0, dp(48), 1f).apply { rightMargin = dp(8) })
        b.addView(Stile.bottone(this, "Elimina", Stile.SECONDARIO, Stile.TESTO) { eliminaVoce() },
            LinearLayout.LayoutParams(0, dp(48), 1f).apply { leftMargin = dp(8) })
        colonna.addView(b)
        return colonna
    }

    private fun carica(vuoiScegliere: String?) {
        val k = kdbx ?: return
        voci = k.voci()
        val q = cerca.text.toString().trim().lowercase(Locale.ROOT)
        elencoVisibile = voci.filter { q.isEmpty() || it.titolo.lowercase(Locale.ROOT).contains(q) ||
            it.utente.lowercase(Locale.ROOT).contains(q) || it.sito.lowercase(Locale.ROOT).contains(q) }
            .sortedBy { it.titolo.lowercase(Locale.ROOT) }
        adattatore.notifyDataSetChanged()
        val s = elencoVisibile.firstOrNull { it.id == vuoiScegliere } ?: elencoVisibile.firstOrNull()
        if (s != null) scegli(s, vaiAlDettaglio = vuoiScegliere != null && stretto)
        else { scelta = null; schedaVuota.visibility = View.VISIBLE; scheda.visibility = View.GONE; if (stretto) mostraElenco() }
    }

    private fun scegli(v: Voce, vaiAlDettaglio: Boolean) {
        scelta = v; mostraPw = false
        dTitolo.text = v.titolo.ifEmpty { "(senza nome)" }
        dUtente.text = v.utente.ifEmpty { "—" }; dSito.text = v.sito.ifEmpty { "—" }; dNote.text = v.note.ifEmpty { "—" }
        dPassword.text = PUNTINI; dMostra.text = "Mostra"; dAvviso.text = ""
        schedaVuota.visibility = View.GONE; scheda.visibility = View.VISIBLE
        adattatore.notifyDataSetChanged()
        if (stretto && vaiAlDettaglio) mostraDettaglio()
    }

    private fun alternaPassword() {
        val v = scelta ?: return
        mostraPw = !mostraPw
        dPassword.text = if (mostraPw) v.password else PUNTINI
        dMostra.text = if (mostraPw) "Nascondi" else "Mostra"
    }

    private fun mostraElenco() { if (!stretto) return; nelDettaglio = false; colonnaElenco.visibility = View.VISIBLE; colonnaDettaglio.visibility = View.GONE }
    private fun mostraDettaglio() { if (!stretto) return; nelDettaglio = true; colonnaElenco.visibility = View.GONE; colonnaDettaglio.visibility = View.VISIBLE }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (chiudiPannelloSeAperto()) return
        if (kdbx != null && stretto && nelDettaglio) mostraElenco() else super.onBackPressed()
    }

    private inner class Adattatore : BaseAdapter() {
        override fun getCount() = elencoVisibile.size
        override fun getItem(i: Int) = elencoVisibile[i]
        override fun getItemId(i: Int) = i.toLong()
        override fun getView(i: Int, v: View?, p: ViewGroup?): View {
            val r = (v as? LinearLayout) ?: LinearLayout(this@CassaforteActivity).apply {
                orientation = LinearLayout.VERTICAL; setPadding(dp(12), dp(10), dp(12), dp(10))
                addView(Stile.testo(context, "", 16f, Stile.TESTO).apply { maxLines = 1; ellipsize = TextUtils.TruncateAt.END })
                addView(Stile.testo(context, "", 12f, Stile.PICCOLO).apply { maxLines = 1; ellipsize = TextUtils.TruncateAt.END })
            }
            val x = elencoVisibile[i]
            (r.getChildAt(0) as TextView).text = x.titolo.ifEmpty { "(senza nome)" }
            (r.getChildAt(1) as TextView).text = x.utente
            r.getChildAt(1).visibility = if (x.utente.isEmpty()) View.GONE else View.VISIBLE
            val sel = x.id == scelta?.id && !stretto
            r.background = if (sel) Stile.riquadro(this@CassaforteActivity, Stile.SCELTA, 8) else null
            (r.getChildAt(0) as TextView).setTextColor(if (sel) Stile.BIANCO else Stile.TESTO)
            (r.getChildAt(1) as TextView).setTextColor(if (sel) 0xCCFFFFFF.toInt() else Stile.PICCOLO)
            return r
        }
    }

    // ---------- copia negli appunti ----------

    private fun copia(testo: String?, segreto: Boolean) {
        val t = testo ?: return
        val cm = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = ClipData.newPlainText("SofiOS", t)
        if (segreto && Build.VERSION.SDK_INT >= 33) {
            clip.description.extras = PersistableBundle().apply { putBoolean(ClipDescription.EXTRA_IS_SENSITIVE, true) }
        }
        cm.setPrimaryClip(clip)
        copiato = t
        principale.removeCallbacks(puliscDopo)
        if (segreto) {
            principale.postDelayed(puliscDopo, 20_000L)
            dAvviso.text = "Password copiata: sparirà dagli appunti tra 20 secondi."
        } else dAvviso.text = "Utente copiato."
    }

    private fun pulisciAppunti() {
        principale.removeCallbacks(puliscDopo)
        val c = copiato ?: return
        copiato = null
        try {
            val cm = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val ora = cm.primaryClip?.getItemAt(0)?.text?.toString()
            if (ora == null || ora == c) { if (Build.VERSION.SDK_INT >= 28) cm.clearPrimaryClip() else cm.setPrimaryClip(ClipData.newPlainText("", "")) }
        } catch (e: SecurityException) { }
    }

    // ---------- modifica, elimina ----------

    private val apertiDialoghi = ArrayList<AlertDialog>()

    private fun genera(): String {
        val r = SecureRandom()
        val alfabeto = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.!?#"
        while (true) {
            val p = (1..20).map { alfabeto[r.nextInt(alfabeto.length)] }.joinToString("")
            if (p.any { it.isLowerCase() } && p.any { it.isUpperCase() } && p.any { it.isDigit() }) return p
        }
    }

    private fun modificaVoce(v: Voce?) {
        val k = kdbx ?: return
        fun campo(nome: String, valore: String, multi: Boolean = false) = EditText(this).apply {
            contentDescription = nome; hint = nome; setText(valore); setTextColor(Stile.TESTO); setHintTextColor(Stile.PICCOLO)
            textSize = 16f
            inputType = if (multi) InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE
                        else InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS
            if (multi) { minLines = 2; gravity = Gravity.TOP } else setSingleLine()
        }
        val titolo = campo("Nome", v?.titolo ?: "")
        titolo.hint = "Nome (per esempio: Posta, Banca…)"
        val utente = campo("Utente", v?.utente ?: "")
        val pw = campo("Password", v?.password ?: genera())
        pw.transformationMethod = PasswordTransformationMethod.getInstance()
        val sito = campo("Sito", v?.sito ?: "")
        val note = campo("Note", v?.note ?: "", multi = true)
        val colonna = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(20), dp(8), dp(20), 0) }
        colonna.addView(titolo); colonna.addView(utente)
        val rigaPw = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        rigaPw.addView(pw, LinearLayout.LayoutParams(0, -2, 1f))
        var visibile = false
        val mostra = Stile.bottone(this, "Mostra", Stile.SECONDARIO, Stile.TESTO) {}.apply { textSize = 13f; minimumHeight = dp(40) }
        mostra.setOnClickListener {
            visibile = !visibile
            pw.transformationMethod = if (visibile) null else PasswordTransformationMethod.getInstance()
            mostra.text = if (visibile) "Nascondi" else "Mostra"
        }
        val gen = Stile.bottone(this, "Genera", Stile.SECONDARIO, Stile.TESTO) {
            pw.setText(genera()); visibile = true; pw.transformationMethod = null; mostra.text = "Nascondi"
        }.apply { textSize = 13f; minimumHeight = dp(40) }
        rigaPw.addView(mostra, LinearLayout.LayoutParams(-2, dp(40)).apply { leftMargin = dp(6) })
        rigaPw.addView(gen, LinearLayout.LayoutParams(-2, dp(40)).apply { leftMargin = dp(6) })
        colonna.addView(rigaPw); colonna.addView(sito); colonna.addView(note)
        val d = AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle(if (v == null) "Nuova password" else "Modifica")
            .setView(ScrollView(this).apply { addView(colonna) })
            .setPositiveButton("Salva", null)
            .setNegativeButton("Annulla", null)
            .create()
        d.window?.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
        d.setOnDismissListener { apertiDialoghi.remove(d) }
        d.show()
        apertiDialoghi.add(d)
        d.getButton(DialogInterface.BUTTON_POSITIVE).isAllCaps = false
        d.getButton(DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
        d.getButton(DialogInterface.BUTTON_POSITIVE).setOnClickListener {
            val t = titolo.text.toString().trim()
            if (t.isEmpty()) { Toast.makeText(this, "Scrivi un nome.", Toast.LENGTH_SHORT).show(); return@setOnClickListener }
            val id: String
            if (v == null) {
                id = k.aggiungi(t, utente.text.toString().trim(), pw.text.toString(), sito.text.toString().trim(), note.text.toString())
            } else {
                v.titolo = t; v.utente = utente.text.toString().trim(); v.password = pw.text.toString()
                v.sito = sito.text.toString().trim(); v.note = note.text.toString()
                k.modifica(v); id = v.id
            }
            salvaFile()
            d.dismiss()
            carica(id)
        }
    }

    private fun eliminaVoce() {
        val v = scelta ?: return
        val d = AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle("Elimina").setMessage("Vuoi eliminare «${v.titolo}»?")
            .setPositiveButton("Sì") { _, _ ->
                kdbx?.elimina(v.id); salvaFile(); scelta = null; carica(null)
            }
            .setNegativeButton("No", null).show()
        d.getButton(DialogInterface.BUTTON_POSITIVE).isAllCaps = false
        d.getButton(DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
    }

    override fun scorciatoie(): List<Scorciatoia> = listOf(
        Scorciatoia("Schermata iniziale") { startActivity(android.content.Intent(this, MainActivity::class.java)) },
    )

    private fun dp(v: Int) = Stile.dp(this, v)

    companion object { private const val PUNTINI = "••••••••••••" }
}
