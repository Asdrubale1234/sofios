package it.sofilabs.sofios

import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextClock
import android.widget.TextView
import it.sofilabs.sofios.assistente.Assistenti
import it.sofilabs.sofios.assistente.CasellaSofi

/** Schermata iniziale di SofiOS: stile del computer, nessuna libreria, nessun servizio acceso. */
class MainActivity : SchermataSofiOS() {

    private val fully = "de.ozerov.fully"
    private var fullyTrovato: String? = null
    private lateinit var sofi: SofiView
    private lateinit var casella: CasellaSofi
    private lateinit var casa: FrameLayout
    private lateinit var puntino: View

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val radice = FrameLayout(this)

        // Sfondo di SofiOS (lo stesso del computer): mare di notte e stelle.
        radice.addView(ImageView(this).apply {
            setImageResource(if (Stile.chiaro) R.drawable.sfondo_chiaro else R.drawable.sfondo)
            scaleType = ImageView.ScaleType.CENTER_CROP
        }, FrameLayout.LayoutParams(-1, -1))

        // Orologio e data, in alto a sinistra.
        val orologio = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(32), dp(48), dp(32), 0)
        }
        orologio.addView(TextClock(this).apply {
            format24Hour = "HH:mm"; format12Hour = "HH:mm"
            textSize = 56f
            setTextColor(Stile.TESTO)
            typeface = Typeface.create("sans-serif-light", Typeface.NORMAL)
        })
        orologio.addView(TextClock(this).apply {
            format24Hour = "EEEE d MMMM"; format12Hour = "EEEE d MMMM"
            textSize = 20f
            setTextColor(Stile.ORO_TESTO)
        })
        radice.addView(orologio, FrameLayout.LayoutParams(-2, -2, Gravity.TOP or Gravity.START))

        // Luma, la mascotte: sta sul fondo a destra. Un tocco fa comparire la X e apre la casella dove si scrive un comando.
        sofi = SofiView(this).apply {
            alToccare = { chiudiPannelloSeAperto(); mostraX(0); casella.apri() }
            alNascondere = { impostaMascotte(false) }
        }
        sofi.visibility = if (mascotteVisibile()) View.VISIBLE else View.GONE
        casella = CasellaSofi(this, sofi)
        radice.addView(casella, FrameLayout.LayoutParams(-1, -1))
        // Luma sta SOPRA la casella: resta luminosa e la sua X si può toccare
        val altezzaLuma = (resources.displayMetrics.heightPixels * 0.26f).toInt()   // come sul computer: circa un quarto dello schermo
        radice.addView(sofi, FrameLayout.LayoutParams(altezzaLuma * 440 / 560, altezzaLuma, Gravity.BOTTOM or Gravity.END).apply {
            bottomMargin = dp(140); rightMargin = dp(56)
        })

        // Barra in basso, come sul computer: icone tonde colorate.
        val barra = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            setPadding(dp(14), dp(12), dp(14), dp(10))
            // barra «di vetro»: trasparente, con un filo chiaro sul bordo (senza sfocatura, per non pesare sui tablet modesti)
            background = GradientDrawable().apply { setColor(if (Stile.chiaro) 0xB3FFFFFF.toInt() else BARRA); cornerRadius = dp(32).toFloat(); setStroke(dp(1), if (Stile.chiaro) 0x22000000 else 0x33FFFFFF) }
        }
        // Casa (Fully): si vede solo se Fully è installato. Dopo il primo tocco, parte sempre da solo
        // all'accensione. Tenendo premuto si spegne e si riaccende (puntino verde = parte da solo).
        val tastoCasa = icona("Casa", R.drawable.ic_s_casa, BLU_A, BLU_B) { tocchiCasa() }
        tastoCasa.setOnLongClickListener {
            memoria().edit().putBoolean("casa_auto", !casaAuto()).apply()
            aggiornaCasa()
            true
        }
        puntino = View(this).apply {
            background = GradientDrawable().apply { setColor(VERDE); setShape(GradientDrawable.OVAL); setStroke(dp(2), FONDO) }
        }
        casa = FrameLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(dp(92), -2).apply { setMargins(dp(4), 0, dp(4), 0) }
            tastoCasa.layoutParams = FrameLayout.LayoutParams(-1, -2)
            addView(tastoCasa)
            addView(puntino, FrameLayout.LayoutParams(dp(16), dp(16), Gravity.TOP or Gravity.END).apply {
                topMargin = dp(2); rightMargin = dp(6)
            })
        }
        barra.addView(casa)
        barra.addView(icona("Impostazioni", R.drawable.ic_s_impostazioni, GRIGIO_A, GRIGIO_B) {
            startActivity(Intent(this, ImpostazioniActivity::class.java))
        })
        // Note: stesse note e stesso aspetto del computer
        barra.addView(icona("Note", R.drawable.ic_s_note, ARANCIO_A, ARANCIO_B) {
            startActivity(Intent(this, NoteActivity::class.java))
        })
        barra.addView(icona("File", R.drawable.ic_s_file, ARANCIO_A, ARANCIO_B) {
            startActivity(Intent(this, FileActivity::class.java))
        })
        barra.addView(icona("Cassaforte", R.drawable.ic_s_cassaforte, VERDE_A, VERDE_B) {
            startActivity(Intent(this, CassaforteActivity::class.java))
        })
        // Icona di Luma: la toglie o la rimette (sul computer è «Aggiungi widget»).
        barra.addView(icona("Mostra o nascondi Luma", R.drawable.sofi_volto, ARANCIO_A, ARANCIO_B, foto = true, etichetta = "Luma") {
            impostaMascotte(!mascotteVisibile())
        })
        zonaApp = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        barra.addView(zonaApp)
        riempiApp()
        radice.addView(barra, FrameLayout.LayoutParams(-2, -2, Gravity.BOTTOM or Gravity.CENTER_HORIZONTAL).apply {
            bottomMargin = dp(16)
        })

        mostra(radice, sovrapposta = true)

        aggiornaCasa()
        // Dopo ogni accensione, se Casa è attiva, SofiOS apre da solo Fully (una volta sola per accensione).
        if (primaVoltaDopoAccensione() && casaAuto() && fullyInstallato()) apriFully()
    }

    private lateinit var zonaApp: LinearLayout

    /** Luma si vede com'è il tablet: batteria quasi scarica e non in carica, oppure senza internet; altrimenti neutra. */
    private fun posaDiRiposo(): String {
        val i = registerReceiver(null, android.content.IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val livello = i?.getIntExtra(android.os.BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scala = i?.getIntExtra(android.os.BatteryManager.EXTRA_SCALE, 100) ?: 100
        val stato = i?.getIntExtra(android.os.BatteryManager.EXTRA_STATUS, -1) ?: -1
        val inCarica = stato == android.os.BatteryManager.BATTERY_STATUS_CHARGING || stato == android.os.BatteryManager.BATTERY_STATUS_FULL
        if (livello >= 0 && scala > 0 && livello * 100 / scala <= 15 && !inCarica) return "batteria_scarica"
        val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as android.net.ConnectivityManager
        val rete = try { cm.activeNetwork?.let { cm.getNetworkCapabilities(it) } } catch (e: SecurityException) { null }
        if (rete == null || !rete.hasCapability(android.net.NetworkCapabilities.NET_CAPABILITY_INTERNET)) return "senza_internet"
        return "neutra"
    }

    /** Le domande del primo avvio, una alla volta: aspetto (scuro/chiaro), assistenti online, poi le app nuove per il Dock. */
    private var passoAperto: AlertDialog? = null

    private fun primiPassi() {
        if (passoAperto?.isShowing == true) return    // una domanda alla volta, anche se la schermata si riattiva più volte
        if (!memoria().getBoolean("benvenuto_visto", false)) Novita.primaInstallazione(this)   // prima volta: niente schermata delle novità
        when {
            !memoria().getBoolean("benvenuto_visto", false) -> benvenuto()
            !memoria().getBoolean("tema_scelto", false) -> sceltaTema()
            !memoria().getBoolean("assistenti_chiesti", false) -> sceltaAssistenti()
            else -> {
                val novita = if (novitaMostrate) emptyList() else Novita.daVedere(this)
                novitaMostrate = true
                if (novita.isNotEmpty()) Novita.mostra(this, novita) { Dock.chiediPerLeNuove(this) { riempiApp() } }
                else Dock.chiediPerLeNuove(this) { riempiApp() }
            }
        }
    }

    private var novitaMostrate = false

    /** Tre pagine di benvenuto, la prima volta: cos'è SofiOS, la sincronizzazione, la sicurezza. */
    private fun benvenuto() {
        val pagine = listOf(
            Triple("benvenuto", "Benvenuto in SofiOS", "Il tuo tablet, semplice e tuo. Note, password, file e Luma, la tua assistente, sono già qui."),
            Triple("sincronizza", "Tutto uguale su ogni dispositivo", "Note, password, foto e file si sincronizzano con il tuo computer, solo dentro casa tua. Non passa da nessun server."),
            Triple("sicurezza", "Al sicuro", "Le tue password sono cifrate e le sai solo tu. Niente pubblicità e nessuna raccolta di dati."))
        var n = 0
        val altezza = (resources.displayMetrics.heightPixels * 0.5f).toInt()
        val colonna = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER_HORIZONTAL; setPadding(dp(20), dp(8), dp(20), dp(8)) }
        val immagine = ImageView(this).apply {
            scaleType = ImageView.ScaleType.CENTER_CROP
            outlineProvider = object : android.view.ViewOutlineProvider() {
                override fun getOutline(v: View, o: android.graphics.Outline) { o.setRoundRect(0, 0, v.width, v.height, dp(18).toFloat()) }
            }
            clipToOutline = true
        }
        val titolo = TextView(this).apply { textSize = 22f; typeface = Typeface.DEFAULT_BOLD; setTextColor(0xFFF2F2F7.toInt()); gravity = Gravity.CENTER; setPadding(0, dp(14), 0, dp(4)) }
        val testo = TextView(this).apply { textSize = 15f; setTextColor(0xFF8E8E93.toInt()); gravity = Gravity.CENTER; setPadding(dp(8), 0, dp(8), dp(12)) }
        var dialogo: AlertDialog? = null
        val avanti = Stile.bottone(this, "Avanti", Stile.ORO, Stile.SU_ORO) {
            if (n < pagine.size - 1) { n++; mostraPagina(n, immagine, titolo, testo, pagine) }
            else { memoria().edit().putBoolean("benvenuto_visto", true).apply(); dialogo?.dismiss(); primiPassi() }
        }
        fun aggiorna() { mostraPagina(n, immagine, titolo, testo, pagine); avanti.text = if (n == pagine.size - 1) "Inizia" else "Avanti" }
        avanti.setOnClickListener {
            if (n < pagine.size - 1) { n++; aggiorna() }
            else { memoria().edit().putBoolean("benvenuto_visto", true).apply(); dialogo?.dismiss(); primiPassi() }
        }
        aggiorna()
        colonna.addView(immagine, LinearLayout.LayoutParams(altezza * 9 / 16, altezza))
        colonna.addView(titolo, LinearLayout.LayoutParams(-1, -2)); colonna.addView(testo, LinearLayout.LayoutParams(-1, -2))
        colonna.addView(avanti, LinearLayout.LayoutParams(dp(220), dp(48)))
        dialogo = AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setView(ScrollView(this).apply { addView(colonna) }).setCancelable(false).show()
        passoAperto = dialogo
    }

    private fun mostraPagina(n: Int, immagine: ImageView, titolo: TextView, testo: TextView, pagine: List<Triple<String, String, String>>) {
        val (img, t, d) = pagine[n]
        val id = resources.getIdentifier("benvenuto_$img", "drawable", packageName)
        if (id != 0) immagine.setImageResource(id)
        titolo.text = t; testo.text = d
    }

    private val descrizioniAssistenti = mapOf(
        "claude" to "Scrive, riassume e spiega; aiuta con documenti e programmi. Si entra con un account: c'è una parte gratuita.",
        "chatgpt" to "Risponde alle domande, scrive testi e traduce. Si entra con un account: c'è una parte gratuita.",
        "gemini" to "L'assistente di Google, anche per immagini. Si entra con l'account Google.",
        "copilot" to "L'assistente di Microsoft. Gratuito, si può provare anche senza account.",
        "deepseek" to "Gratuito, con un account. Attenzione: è un servizio con sede in Cina, quello che scrivi viene trattato lì.",
        "mistral" to "Assistente europeo (Francia). Ha una parte gratuita, con un account.",
        "perplexity" to "Cerca sul web e risponde indicando le fonti. Ha una parte gratuita, anche senza account.")

    /** Facoltativo, scelta multipla, niente da scaricare: gli assistenti si aprono nel browser (stessi testi dell'installazione del computer). */
    private fun sceltaAssistenti() {
        val scelti = HashSet<String>(Assistenti.scelti(this).map { it.id })
        val colonna = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(16), dp(4), dp(16), dp(4)) }
        colonna.addView(TextView(this).apply {
            text = "Facoltativo. Si aprono nel browser, con internet e il tuo account: non si scarica niente."
            textSize = 13f; setTextColor(0xFF8E8E93.toInt()); setPadding(dp(4), 0, dp(4), dp(8))
        })
        for (a in Assistenti.tutti) {
            val riga = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL; isClickable = true
                contentDescription = a.nome; setPadding(dp(10), dp(8), dp(10), dp(8))
            }
            fun colora() { riga.background = GradientDrawable().apply {
                setColor(if (a.id in scelti) 0x440A84FF else 0x00000000); cornerRadius = dp(14).toFloat()
                if (a.id in scelti) setStroke(dp(1), 0xFF0A84FF.toInt()) } }
            colora()
            riga.addView(ImageView(this).apply {
                val o = Assistenti.iconaOriginale(this@MainActivity, a)
                if (o != null) setImageDrawable(o) else setImageResource(a.icona)
                scaleType = ImageView.ScaleType.FIT_CENTER
                outlineProvider = object : android.view.ViewOutlineProvider() {
                    override fun getOutline(v: View, ou: android.graphics.Outline) { ou.setRoundRect(0, 0, v.width, v.height, dp(10).toFloat()) }
                }
                clipToOutline = true
            }, LinearLayout.LayoutParams(dp(44), dp(44)))
            val testi = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(12), 0, 0, 0) }
            testi.addView(TextView(this).apply { text = a.nome; textSize = 16f; typeface = Typeface.DEFAULT_BOLD; setTextColor(0xFFF2F2F7.toInt()) })
            testi.addView(TextView(this).apply { text = descrizioniAssistenti[a.id] ?: ""; textSize = 12.5f; setTextColor(0xFF8E8E93.toInt()) })
            riga.addView(testi, LinearLayout.LayoutParams(0, -2, 1f))
            val spunta = TextView(this).apply { textSize = 18f; setTextColor(0xFF0A84FF.toInt()); text = if (a.id in scelti) "✓" else "" }
            riga.addView(spunta)
            riga.setOnClickListener {
                if (!scelti.add(a.id)) scelti.remove(a.id)
                spunta.text = if (a.id in scelti) "✓" else ""; colora()
            }
            colonna.addView(riga, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(4) })
        }
        fine@ run {
            val d = AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
                .setTitle("Assistenti online").setView(ScrollView(this).apply { addView(colonna) })
                .setPositiveButton("Continua") { _, _ ->
                    for (a in Assistenti.tutti) Assistenti.imposta(this, a.id, a.id in scelti)
                    memoria().edit().putBoolean("assistenti_chiesti", true).apply(); primiPassi()
                }
                .setNegativeButton("Non ora") { _, _ -> memoria().edit().putBoolean("assistenti_chiesti", true).apply(); primiPassi() }
                .setCancelable(false).show()
            d.getButton(android.content.DialogInterface.BUTTON_POSITIVE).isAllCaps = false
            d.getButton(android.content.DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
            passoAperto = d
        }
    }

    /** Primo avvio: scuro o chiaro, con l'anteprima dello sfondo (come nell'installazione del computer). */
    private fun sceltaTema() {
        var d: AlertDialog? = null
        fun carta(nome: String, sfondo: Int, chiaro: Boolean): View = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER_HORIZONTAL
            contentDescription = nome; isClickable = true
            setPadding(dp(8), dp(8), dp(8), dp(8))
            addView(ImageView(this@MainActivity).apply {
                setImageResource(sfondo); scaleType = ImageView.ScaleType.CENTER_CROP
                outlineProvider = object : android.view.ViewOutlineProvider() {
                    override fun getOutline(v: View, o: android.graphics.Outline) { o.setRoundRect(0, 0, v.width, v.height, dp(14).toFloat()) }
                }
                clipToOutline = true
            }, LinearLayout.LayoutParams(dp(190), dp(110)))
            addView(TextView(this@MainActivity).apply {
                text = nome; textSize = 16f; setTextColor(0xFFF2F2F7.toInt()); gravity = Gravity.CENTER
                typeface = Typeface.DEFAULT_BOLD; setPadding(0, dp(8), 0, 0)
            })
            setOnClickListener {
                memoria().edit().putBoolean("tema_scelto", true).apply()
                d?.dismiss()
                if (Stile.chiaro != chiaro) { Stile.imposta(this@MainActivity, chiaro); recreate() }
                else primiPassi()
            }
        }
        val riga = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER; setPadding(dp(8), dp(8), dp(8), dp(8)) }
        riga.addView(carta("Scuro", R.drawable.sfondo, false)); riga.addView(carta("Chiaro", R.drawable.sfondo_chiaro, true))
        d = AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle("Che aspetto preferisci?").setView(riga).setCancelable(false).show()
        passoAperto = d
    }

    /** Le app che l'utente ha messo nel Dock (si toglie con una pressione lunga). */
    private fun riempiApp() {
        zonaApp.removeAllViews()
        val pm = packageManager
        for (p in Dock.daMostrare(this)) {
            val nome = try { pm.getApplicationInfo(p, 0).loadLabel(pm).toString() } catch (e: Exception) { continue }
            val icona = try { pm.getApplicationIcon(p) } catch (e: Exception) { continue }
            val tessera = ImageView(this).apply {
                setImageDrawable(icona); scaleType = ImageView.ScaleType.FIT_CENTER
                outlineProvider = object : android.view.ViewOutlineProvider() {
                    override fun getOutline(v: View, o: android.graphics.Outline) { o.setRoundRect(0, 0, v.width, v.height, dp(18).toFloat()) }
                }
                clipToOutline = true; elevation = dp(3).toFloat()
            }
            val etichetta = TextView(this).apply {
                text = nome; textSize = 11.5f; setTextColor(Stile.TESTO); gravity = Gravity.CENTER
                typeface = Typeface.create("sans-serif-medium", Typeface.NORMAL); maxLines = 1
                ellipsize = android.text.TextUtils.TruncateAt.END; setPadding(0, dp(6), 0, 0)
            }
            zonaApp.addView(LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER_HORIZONTAL
                contentDescription = nome; isClickable = true
                addView(tessera, LinearLayout.LayoutParams(dp(76), dp(76)))
                addView(etichetta, LinearLayout.LayoutParams(dp(88), -2))
                layoutParams = LinearLayout.LayoutParams(dp(92), -2).apply { setMargins(dp(4), 0, dp(4), 0) }
                setOnClickListener { pm.getLaunchIntentForPackage(p)?.let { startActivity(it) } }
                setOnLongClickListener {
                    AlertDialog.Builder(this@MainActivity, android.R.style.Theme_DeviceDefault_Dialog_Alert)
                        .setTitle(nome).setItems(arrayOf("Togli dal Dock")) { _, _ -> Dock.togli(this@MainActivity, p); riempiApp() }
                        .setNegativeButton("Chiudi", null).show().getButton(android.content.DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
                    true
                }
                Stile.premi(this)
            })
        }
    }

    override fun onResume() {
        super.onResume()
        riempiApp()
        primiPassi()
        sofi.ondeggia(mascotteVisibile())
        sofi.posaRiposo = posaDiRiposo(); if (!casella.aperta()) sofi.riposo()
        aggiornaCasa()
        if (!Cartella.permesso(this) && !memoria().getBoolean("cartella_chiesta", false)) avvisoCartella()
    }

    /** Una sola volta: spiega perché serve l'accesso ai file (Cartella SofiOS comune ai dispositivi). */
    private fun avvisoCartella() {
        memoria().edit().putBoolean("cartella_chiesta", true).apply()
        val d = android.app.AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle("Cartella SofiOS")
            .setMessage("Per tenere note, password e foto uguali sugli altri tuoi dispositivi, SofiOS ha bisogno dell'accesso ai file. " +
                "Ti porto alla pagina di Android dove si concede. Puoi farlo anche più tardi da Impostazioni, «Cartella SofiOS».")
            .setPositiveButton("Consenti") { _, _ -> Controlli.apri(this, Cartella.richiestaPermesso(this)) }
            .setNegativeButton("Più tardi", null)
            .show()
        d.getButton(android.content.DialogInterface.BUTTON_POSITIVE).isAllCaps = false
        d.getButton(android.content.DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
    }

    /** Cerca Fully tra i programmi che si possono aprire: per nome del pacchetto, oppure per nome «Fully». */
    private fun cercaFully(): String? {
        val elenco = packageManager.queryIntentActivities(
            Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER), 0)
        elenco.firstOrNull { it.activityInfo.packageName == fully }?.let { return fully }
        return elenco.firstOrNull { it.loadLabel(packageManager).toString().contains("fully", ignoreCase = true) }
            ?.activityInfo?.packageName
    }

    private fun fullyInstallato(): Boolean {
        fullyTrovato = cercaFully()
        return fullyTrovato != null
    }

    private fun casaAuto() = memoria().getBoolean("casa_auto", false)

    /** Casa si vede solo se Fully è installato; il puntino verde dice se parte da solo. */
    private fun aggiornaCasa() {
        casa.visibility = if (fullyInstallato()) View.VISIBLE else View.GONE
        puntino.visibility = if (casaAuto()) View.VISIBLE else View.GONE
    }

    private fun memoria() = getSharedPreferences("sofios", Context.MODE_PRIVATE)

    private fun mascotteVisibile() = memoria().getBoolean("mascotte", true)

    private fun impostaMascotte(visibile: Boolean) {
        memoria().edit().putBoolean("mascotte", visibile).apply()
        sofi.visibility = if (visibile) View.VISIBLE else View.GONE
        if (visibile) sofi.ondeggia(true) else { sofi.nascondiX(); sofi.ondeggia(false); casella.chiudi() }
    }

    /** Vero solo la prima volta dopo ogni accensione del dispositivo. */
    private fun primaVoltaDopoAccensione(): Boolean {
        val accensione = Settings.Global.getInt(contentResolver, Settings.Global.BOOT_COUNT, -1)
        if (memoria().getInt("accensione", -2) == accensione) return false
        memoria().edit().putInt("accensione", accensione).apply()
        return true
    }

    private fun apriFully() {
        val nome = fullyTrovato ?: cercaFully() ?: return
        packageManager.getLaunchIntentForPackage(nome)?.let { startActivity(it) }
    }

    /** Icona del Dock nello stile Apple (uguale al computer), con il nome sotto. */
    private fun icona(nome: String, simbolo: Int, alto: Int, basso: Int, foto: Boolean = false,
                      etichetta: String = nome, azione: () -> Unit): LinearLayout {
        val tessera = ImageView(this).apply {
            setImageDrawable(IconaApple(this@MainActivity, simbolo, alto, basso, foto))
            scaleType = ImageView.ScaleType.FIT_XY
            elevation = dp(3).toFloat()
        }
        val nomeSotto = TextView(this).apply {
            text = etichetta; textSize = 11.5f; setTextColor(Stile.TESTO); gravity = Gravity.CENTER
            typeface = Typeface.create("sans-serif-medium", Typeface.NORMAL); maxLines = 1
            setPadding(0, dp(6), 0, 0)
        }
        return LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER_HORIZONTAL
            contentDescription = nome; isClickable = true
            addView(tessera, LinearLayout.LayoutParams(dp(76), dp(76)))
            addView(nomeSotto, LinearLayout.LayoutParams(dp(88), -2))
            layoutParams = LinearLayout.LayoutParams(dp(92), -2).apply { setMargins(dp(4), 0, dp(4), 0) }
            setOnClickListener { azione() }
            Stile.premi(this)
        }
    }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    // Tasto Home: resta qui, niente da fare.
    override fun onNewIntent(intent: Intent) { super.onNewIntent(intent) }

    // Indietro non deve mai chiudere la schermata iniziale (chiude solo il pannello, se aperto).
    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (casella.aperta()) { casella.chiudi(); return }
        chiudiPannelloSeAperto()
    }

    override fun onPause() {
        if (::sofi.isInitialized) sofi.ondeggia(false)
        if (::casella.isInitialized && casella.aperta()) casella.chiudi()
        super.onPause()
    }

    override fun alAprirePannello() {
        if (::casella.isInitialized && casella.aperta()) casella.chiudi()
    }

    // Scorciatoie del pannello SofiOS, quando si è nella schermata iniziale.
    override fun scorciatoie(): List<Scorciatoia> {
        val l = mutableListOf<Scorciatoia>()
        if (fullyInstallato()) l.add(Scorciatoia("Casa") { tocchiCasa() })
        l.add(Scorciatoia("Luma") { if (!mascotteVisibile()) impostaMascotte(true); casella.apri() })
        l.add(Scorciatoia("Note") { startActivity(Intent(this, NoteActivity::class.java)) })
        l.add(Scorciatoia("File") { startActivity(Intent(this, FileActivity::class.java)) })
        l.add(Scorciatoia("Cassaforte") { startActivity(Intent(this, CassaforteActivity::class.java)) })
        l.add(Scorciatoia("Impostazioni") { startActivity(Intent(this, ImpostazioniActivity::class.java)) })
        l.addAll(scorciatoieAssistenti())
        return l
    }

    private fun tocchiCasa() {
        memoria().edit().putBoolean("casa_auto", true).apply()
        aggiornaCasa()
        apriFully()
    }

    companion object {
        // palette delle icone (alto → basso), uguale al computer
        private val BLU_A = 0xFF4DA3FF.toInt(); private val BLU_B = 0xFF0A6CDF.toInt()
        private val ARANCIO_A = 0xFFFFC040.toInt(); private val ARANCIO_B = 0xFFFF8A00.toInt()
        private val VERDE_A = 0xFF4BE06A.toInt(); private val VERDE_B = 0xFF1F9D40.toInt()
        private val GRIGIO_A = 0xFFA2A2A8.toInt(); private val GRIGIO_B = 0xFF636366.toInt()
        private const val FONDO = 0xFF1C1C1E.toInt()
        private const val BARRA = 0xB32C2C2E.toInt()
        private const val TESTO = 0xFFE8F1F8.toInt()
        private const val ORO = 0xFFFFD479.toInt()
        private const val ORO_SCURO = 0xFFE0A93C.toInt()
        private const val VERDE = 0xFF6FE0B0.toInt()
        private const val GRIGIO = 0xFF7D8DA0.toInt()
        private const val GRIGIO_SCURO = 0xFF566577.toInt()
        private const val ORO_FILE = 0xFFF2C26B.toInt()
        private const val ORO_FILE_SCURO = 0xFFC98A2B.toInt()
        private const val TURCHESE = 0xFF3FC1C9.toInt()
        private const val TURCHESE_SCURO = 0xFF1D7F8C.toInt()
        private const val ROSA = 0xFFFF8FB8.toInt()
        private const val ROSA_SCURO = 0xFFD6457F.toInt()
        private const val MARE = 0xFF3A86B8.toInt()
        private const val MARE_SCURO = 0xFF1B4F7A.toInt()
    }
}
