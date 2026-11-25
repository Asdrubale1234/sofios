package it.sofilabs.sofios

import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.content.pm.ResolveInfo
import android.graphics.Typeface
import android.media.AudioManager
import android.net.Uri
import android.os.BatteryManager
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.os.StatFs
import android.provider.Settings
import android.text.TextUtils
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.ScrollView
import android.widget.TextView
import it.sofilabs.sofios.assistente.Assistenti
import it.sofilabs.sofios.sincronizza.CartellaSync
import it.sofilabs.sofios.sincronizza.Sincronizza
import it.sofilabs.sofios.sincronizza.Syncthing
import java.util.Locale

/**
 * Impostazioni di SofiOS: le cose che un'app può fare da sola sono qui, con i nostri colori.
 * Per le altre (Wi-Fi con password, Bluetooth, data, lingua…) il pulsante porta alla pagina di Android.
 */
class ImpostazioniActivity : SchermataSofiOS() {

    private val voci = listOf("Schermo", "Suono", "Batteria", "Spazio", "Cartella SofiOS", "Dispositivi", "App", "Assistenti online", "Altre impostazioni", "Informazioni")
    private var stretto = false
    private var nelContenuto = false
    private var scelta = 0
    private lateinit var colonnaElenco: LinearLayout
    private lateinit var colonnaContenuto: FrameLayout
    private lateinit var adattatore: BaseAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        stretto = resources.configuration.screenWidthDp < 600
        val radice = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(dp(20), dp(18), dp(20), dp(18))
        }
        colonnaElenco = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        colonnaElenco.addView(Stile.testo(this, "Impostazioni", 22f, Stile.TESTO, true).apply {
            setPadding(0, 0, 0, dp(10))
        })
        adattatore = object : BaseAdapter() {
            override fun getCount() = voci.size
            override fun getItem(i: Int) = voci[i]
            override fun getItemId(i: Int) = i.toLong()
            override fun getView(i: Int, v: View?, p: ViewGroup?): View {
                val t = (v as? TextView) ?: TextView(this@ImpostazioniActivity).apply {
                    textSize = 17f; setTextColor(Stile.TESTO); setPadding(dp(14), dp(16), dp(14), dp(16))
                }
                t.text = voci[i]
                val sel = i == scelta && !stretto
                t.background = if (sel) Stile.riquadro(this@ImpostazioniActivity, Stile.SCELTA, 8) else null
                t.setTextColor(if (sel) Stile.BIANCO else Stile.TESTO)
                return t
            }
        }
        colonnaElenco.addView(ListView(this).apply {
            adapter = adattatore
            divider = null; dividerHeight = 0
            background = Stile.riquadro(this@ImpostazioniActivity, Stile.PANNELLO, 12)
            setPadding(dp(6), dp(6), dp(6), dp(6)); clipToPadding = false
            setOnItemClickListener { _, _, i, _ -> apri(i) }
        }, LinearLayout.LayoutParams(-1, 0, 1f))

        colonnaContenuto = FrameLayout(this).apply {
            background = Stile.riquadro(this@ImpostazioniActivity, Stile.PANNELLO, 12)
        }
        if (stretto) {
            radice.addView(colonnaElenco, LinearLayout.LayoutParams(-1, -1))
            radice.addView(colonnaContenuto, LinearLayout.LayoutParams(-1, -1))
            colonnaContenuto.visibility = View.GONE
        } else {
            radice.addView(colonnaElenco, LinearLayout.LayoutParams(dp(250), -1))
            radice.addView(colonnaContenuto, LinearLayout.LayoutParams(0, -1, 1f).apply { leftMargin = dp(16) })
            apri(0)
        }
        mostra(radice)
    }

    override fun onPause() { rinfresca.removeCallbacksAndMessages(null); super.onPause() }

    override fun onResume() {
        super.onResume()
        if (!stretto || nelContenuto) apri(scelta)   // aggiorna dopo un permesso concesso
    }

    private fun apri(i: Int) {
        scelta = i
        adattatore.notifyDataSetChanged()
        colonnaContenuto.removeAllViews()
        val corpo = when (voci[i]) {
            "Schermo" -> pagina("Schermo", temaScelta(), lumaInterruttore(), Controlli.luminosita(this), Controlli.rotazione(this))
            "Suono" -> pagina("Suono",
                Controlli.volume(this, AudioManager.STREAM_MUSIC, "Volume multimediale"),
                Controlli.volume(this, AudioManager.STREAM_ALARM, "Volume della sveglia"))
            "Batteria" -> pagina("Batteria", *batteria())
            "Spazio" -> pagina("Spazio", *spazio())
            "Cartella SofiOS" -> pagina("Cartella SofiOS", *cartellaSofios())
            "Dispositivi" -> paginaDispositivi()
            "App" -> paginaApp()
            "Assistenti online" -> pagina("Assistenti online", *assistenti())
            "Altre impostazioni" -> pagina("Altre impostazioni di Android", *altre())
            else -> pagina("Informazioni", *informazioni())
        }
        colonnaContenuto.addView(corpo, FrameLayout.LayoutParams(-1, -1))
        if (stretto) {
            nelContenuto = true
            colonnaElenco.visibility = View.GONE; colonnaContenuto.visibility = View.VISIBLE
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (chiudiPannelloSeAperto()) return
        if (stretto && nelContenuto) {
            nelContenuto = false
            colonnaElenco.visibility = View.VISIBLE; colonnaContenuto.visibility = View.GONE
        } else super.onBackPressed()
    }

    // ---- pagine ----

    /** Tema scuro o chiaro (come sul computer). */
    private fun temaScelta(): View {
        val riga = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; contentDescription = "Tema" }
        fun tasto(nome: String, chiaro: Boolean, ultimo: Boolean): View {
            val attivo = Stile.chiaro == chiaro
            return Stile.bottone(this, nome, if (attivo) Stile.SELEZ else Stile.SECONDARIO, if (attivo) Stile.BIANCO else Stile.TESTO) {
                if (Stile.chiaro != chiaro) { Stile.imposta(this, chiaro); recreate() }
            }.apply { contentDescription = nome + if (attivo) " (attivo)" else "" }
        }
        riga.addView(tasto("Tema scuro", false, false), LinearLayout.LayoutParams(0, -2, 1f).apply { rightMargin = dp(6) })
        riga.addView(tasto("Tema chiaro", true, true), LinearLayout.LayoutParams(0, -2, 1f).apply { leftMargin = dp(6) })
        return riga
    }

    /** «Mostra Luma nelle pagine dei programmi»: acceso di serie (non tocca la Luma della schermata iniziale). */
    private fun lumaInterruttore(): View {
        fun testo() = "Mostra Luma nelle pagine dei programmi: " + if (Stile.lumaNelleSchermate(this)) "sì" else "no"
        val b = Stile.bottone(this, testo(), Stile.SECONDARIO, Stile.TESTO) {}
        b.setOnClickListener { Stile.impostaLumaNelleSchermate(this, !Stile.lumaNelleSchermate(this)); b.text = testo() }
        b.contentDescription = "Mostra Luma nelle pagine dei programmi"
        return b
    }

    private fun pagina(titolo: String, vararg corpo: View): View {
        val colonna = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(24), dp(20), dp(24), dp(20))
        }
        colonna.addView(Stile.testo(this, titolo, 28f, Stile.TESTO, true).apply { setPadding(0, 0, 0, dp(12)) })
        for (v in corpo) colonna.addView(v, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(8) })
        return ScrollView(this).apply { addView(colonna) }
    }

    private fun riga(nome: String, valore: String): View = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL
        addView(Stile.testo(context, nome, 13f, Stile.PICCOLO))
        addView(Stile.testo(context, valore, 18f, Stile.TESTO))
    }

    private fun batteria(): Array<View> {
        val i = registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val livello = i?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scala = i?.getIntExtra(BatteryManager.EXTRA_SCALE, 100) ?: 100
        val stato = i?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) ?: -1
        val temp = i?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1) ?: -1
        val pct = if (livello >= 0 && scala > 0) "${livello * 100 / scala}%" else "non disponibile"
        val s = when (stato) {
            BatteryManager.BATTERY_STATUS_CHARGING -> "In carica"
            BatteryManager.BATTERY_STATUS_FULL -> "Carica completa"
            BatteryManager.BATTERY_STATUS_DISCHARGING, BatteryManager.BATTERY_STATUS_NOT_CHARGING -> "Non in carica"
            else -> "Non disponibile"
        }
        val t = if (temp > 0) String.format(Locale.ITALY, "%.1f °C", temp / 10.0) else "non disponibile"
        return arrayOf(riga("Livello", pct), riga("Stato", s), riga("Temperatura", t))
    }

    private fun cartellaSofios(): Array<View> {
        val ok = Cartella.permesso(this)
        val l = ArrayList<View>()
        l.add(Stile.testo(this, "Una sola cartella con Note, Password, Foto e File, uguale su tutti i tuoi dispositivi SofiOS.", 13f, Stile.PICCOLO))
        l.add(riga("Posizione", if (ok) "Memoria del tablet, cartella «SofiOS»" else "Privata, dentro l'app"))
        l.add(riga("Accesso ai file", if (ok) "Concesso" else "Non concesso"))
        if (!ok) {
            l.add(Stile.testo(this, "Senza l'accesso ai file la cartella resta privata e gli altri dispositivi non possono sincronizzarla.", 13f, Stile.PICCOLO))
            l.add(Stile.bottone(this, "Consenti accesso ai file", Stile.ORO, Stile.SU_ORO) { Controlli.apri(this, Cartella.richiestaPermesso(this)) })
        }
        l.add(Stile.testo(this, "La sincronizzazione con gli altri dispositivi si attiva dalla pagina «Dispositivi».", 13f, Stile.PICCOLO))
        return l.toTypedArray()
    }

    // ---- Dispositivi: sincronizzazione con PC e altri tablet (tramite l'app Syncthing-Fork, che resta un'app a parte) ----

    private val rinfresca = Handler(Looper.getMainLooper())
    private val APP_SYNC = "com.github.catfriend1.syncthingandroid"
    private fun memoriaSync() = getSharedPreferences("sofios", Context.MODE_PRIVATE)

    private fun cartelleSync(): List<CartellaSync> {
        @Suppress("DEPRECATION")
        val foto = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM)
        return listOf(
            CartellaSync("sofios-note", "Note", Cartella.note(this).path),
            CartellaSync("sofios-password", "Password", Cartella.password(this).path),
            CartellaSync("sofios-foto", "Foto", foto.path),
            CartellaSync("sofios-file", "File", java.io.File(Cartella.radice(this), "File").path)
        )
    }

    private fun appSyncInstallata() = try { packageManager.getPackageInfo(APP_SYNC, 0); true } catch (e: PackageManager.NameNotFoundException) { false }

    private fun apriAppSync() {
        val i = packageManager.getLaunchIntentForPackage(APP_SYNC)
        if (i != null) startActivity(i)
    }

    private fun installaAppSync() {
        try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=$APP_SYNC"))) }
        catch (e: Exception) {
            try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://f-droid.org/packages/$APP_SYNC/"))) } catch (x: Exception) { }
        }
    }

    private fun paginaDispositivi(): View {
        val contenitore = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; contentDescription = "Dispositivi" }
        riempiDispositivi(contenitore)
        return pagina("Dispositivi", contenitore)
    }

    private fun lumaDi(c: LinearLayout, nome: String) {
        Stile.luma(this, nome)?.let { c.addView(it, LinearLayout.LayoutParams(-2, dp(Stile.ALTEZZA_LUMA_DP)).apply { topMargin = dp(10); gravity = Gravity.END }) }
    }

    private fun testoSync(t: String) = Stile.testo(this, t, 14f, Stile.PICCOLO)
    private fun aggiungi(c: LinearLayout, v: View) = c.addView(v, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(10) })

    private fun riempiDispositivi(c: LinearLayout) {
        c.removeAllViews()
        aggiungi(c, testoSync("Per avere le stesse note, password, foto e file sul computer e sugli altri tablet, SofiOS usa un'app a parte che sincronizza soltanto dentro casa. Non passa da nessun server."))
        if (!appSyncInstallata()) {
            lumaDi(c, "senza_internet")   // sincronizzazione spenta
            aggiungi(c, riga("Stato", "L'app di sincronizzazione non è installata"))
            aggiungi(c, Stile.bottone(this, "Installa l'app di sincronizzazione", Stile.ORO, Stile.SU_ORO) { installaAppSync() }.apply {
                setCompoundDrawablesWithIntrinsicBounds(R.drawable.ic_download, 0, 0, 0); compoundDrawablePadding = dp(10)
            })
            aggiungi(c, Stile.bottone(this, "Ricontrolla", Stile.SECONDARIO, Stile.TESTO) { riempiDispositivi(c) })
            return
        }
        val chiave = memoriaSync().getString("sync_chiave", "") ?: ""
        if (chiave.isEmpty()) { schermataChiave(c); return }
        if (!Cartella.permesso(this)) {
            aggiungi(c, riga("Stato", "Serve l'accesso ai file"))
            aggiungi(c, testoSync("Senza l'accesso ai file, Note, Password e Foto non si possono sincronizzare."))
            aggiungi(c, Stile.bottone(this, "Consenti accesso ai file", Stile.ORO, Stile.SU_ORO) { Controlli.apri(this, Cartella.richiestaPermesso(this)) })
            return
        }
        aggiungi(c, riga("Stato", "Controllo…"))
        val st = Syncthing(memoriaSync().getInt("sync_porta", 8384), chiave)
        val nome = memoriaSync().getString("sync_nome", "Tablet di Luca") ?: "Tablet di Luca"
        val cartelle = cartelleSync()
        Thread {
            val esito: Result<Triple<List<it.sofilabs.sofios.sincronizza.Dispositivo>, List<Pair<String, String>>, Double?>> = try {
                Sincronizza.prepara(st, nome, cartelle)
                Result.success(Triple(Sincronizza.dispositivi(st), Sincronizza.inAttesa(st), Sincronizza.completamento(st, cartelle)))
            } catch (e: Exception) { Result.failure(e) }
            runOnUiThread {
                if (isFinishing || voci.getOrNull(scelta) != "Dispositivi") return@runOnUiThread
                c.removeAllViews()
                esito.onSuccess { (dispositivi, attesa, perc) -> mostraDispositivi(c, st, cartelle, dispositivi, attesa, perc) }
                esito.onFailure { e -> nonRisponde(c, e) }
            }
        }.start()
    }

    private fun schermataChiave(c: LinearLayout) {
        lumaDi(c, "senza_internet")   // sincronizzazione spenta
        aggiungi(c, riga("Stato", "Manca il collegamento con l'app di sincronizzazione"))
        aggiungi(c, testoSync("1. Apri l'app di sincronizzazione.\n2. Dal menu apri «Interfaccia web» → Azioni → Impostazioni.\n3. Copia la «Chiave API» e incollala qui sotto."))
        aggiungi(c, Stile.bottone(this, "Apri l'app di sincronizzazione", Stile.SECONDARIO, Stile.TESTO) { apriAppSync() })
        val campo = EditText(this).apply {
            hint = "Incolla qui la chiave"; contentDescription = "Chiave dell'app di sincronizzazione"
            setHintTextColor(Stile.PICCOLO); setTextColor(Stile.TESTO); textSize = 16f; setSingleLine()
            background = Stile.riquadro(this@ImpostazioniActivity, Stile.SECONDARIO, 12); setPadding(dp(14), dp(12), dp(14), dp(12))
        }
        aggiungi(c, campo)
        aggiungi(c, Stile.bottone(this, "Collega", Stile.ORO, Stile.SU_ORO) {
            val k = campo.text.toString().trim()
            if (k.length >= 8) { memoriaSync().edit().putString("sync_chiave", k).apply(); riempiDispositivi(c) }
        })
    }

    private fun nonRisponde(c: LinearLayout, e: Throwable) {
        lumaDi(c, "senza_internet")
        aggiungi(c, riga("Stato", "L'app di sincronizzazione non risponde"))
        aggiungi(c, testoSync("Aprila una volta e lascia che si avvii, poi tocca «Riprova». Se la chiave è cambiata, scrivila di nuovo."))
        aggiungi(c, Stile.bottone(this, "Apri l'app di sincronizzazione", Stile.SECONDARIO, Stile.TESTO) { apriAppSync() })
        aggiungi(c, Stile.bottone(this, "Riprova", Stile.ORO, Stile.SU_ORO) { riempiDispositivi(c) })
        aggiungi(c, Stile.bottone(this, "Scrivi di nuovo la chiave", Stile.SECONDARIO, Stile.TESTO) { memoriaSync().edit().remove("sync_chiave").apply(); riempiDispositivi(c) })
        aggiungi(c, testoSync("Dettaglio: " + (e.message ?: e.javaClass.simpleName).take(120)))
    }

    private fun mostraDispositivi(c: LinearLayout, st: Syncthing, cartelle: List<CartellaSync>,
                                  dispositivi: List<it.sofilabs.sofios.sincronizza.Dispositivo>, attesa: List<Pair<String, String>>, perc: Double?) {
        val stato = when {
            dispositivi.none { it.collegato } -> if (dispositivi.isEmpty()) "Pronto: nessun dispositivo collegato" else "Nessun dispositivo in casa adesso"
            perc != null && perc < 99.5 -> "Sincronizzo… ${perc.toInt()}%"
            else -> "Tutto aggiornato"
        }
        // come sul computer: nessuno collegato = sincronizza, collegati = wifi connesso
        lumaDi(c, if (dispositivi.any { it.collegato }) "wifi_connesso" else "sincronizza")
        aggiungi(c, riga("Stato", stato))
        for ((codice, nome) in attesa) {
            aggiungi(c, Stile.testo(this, "«$nome» vuole collegarsi. Vuoi fidarti?", 16f, Stile.TESTO, true))
            aggiungi(c, Stile.bottone(this, "Mi fido di $nome", Stile.ORO, Stile.SU_ORO) {
                Thread { try { Sincronizza.fidati(st, codice, nome, cartelle) } catch (e: Exception) { }; runOnUiThread { riempiDispositivi(c) } }.start()
            })
        }
        if (dispositivi.isEmpty() && attesa.isEmpty()) {
            aggiungi(c, testoSync("Per collegare il computer: sul computer apri «Dispositivi» e scegli «Collega un nuovo dispositivo»; poi, nell'app di sincronizzazione, tocca «+» e leggi il codice QR che compare sul computer. Torna qui e tocca «Mi fido» quando te lo chiede."))
        }
        for (d in dispositivi) {
            val riga = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
                setPadding(dp(12), dp(10), dp(12), dp(10)); contentDescription = d.nome
                background = Stile.riquadro(this@ImpostazioniActivity, Stile.SECONDARIO, 12)
            }
            riga.addView(Stile.testo(this, d.nome, 17f, Stile.TESTO, true), LinearLayout.LayoutParams(0, -2, 1f))
            riga.addView(Stile.testo(this, if (d.collegato) "Collegato" else "Non in casa", 14f, if (d.collegato) Stile.ORO_TESTO else Stile.PICCOLO))
            aggiungi(c, riga)
            aggiungi(c, Stile.bottone(this, "Rimuovi ${d.nome}", Stile.SECONDARIO, Stile.TESTO) {
                AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
                    .setTitle("Rimuovere ${d.nome}?").setMessage("I file restano dove sono: smettono solo di sincronizzarsi.")
                    .setPositiveButton("Rimuovi") { _, _ -> Thread { try { Sincronizza.rimuovi(st, d.id, cartelle) } catch (e: Exception) { }; runOnUiThread { riempiDispositivi(c) } }.start() }
                    .setNegativeButton("Annulla", null).show()
            }.apply { textSize = 13f; minimumHeight = dp(40) })
        }
        aggiungi(c, testoSync("Le foto del tablet (cartella Fotocamera) e quelle del computer si sincronizzano nei due sensi. Se elimini una foto su un dispositivo, sparisce da tutti; per 30 giorni resta una copia nel cestino della sincronizzazione."))
        aggiungi(c, Stile.bottone(this, "Aggiorna", Stile.SECONDARIO, Stile.TESTO) { riempiDispositivi(c) })
        // finché la pagina è aperta, ogni 8 secondi si aggiorna l'elenco (niente resta acceso a pagina chiusa)
        rinfresca.removeCallbacksAndMessages(null)
        rinfresca.postDelayed({ if (!isFinishing && voci.getOrNull(scelta) == "Dispositivi") riempiDispositivi(c) }, 8000)
    }

    private fun gb(b: Long) = String.format(Locale.ITALY, "%.1f GB", b / 1_000_000_000.0)

    private fun spazio(): Array<View> {
        val s = StatFs(Environment.getDataDirectory().path)
        val totale = s.totalBytes; val libero = s.availableBytes
        return arrayOf(riga("Totale", gb(totale)), riga("Libero", gb(libero)), riga("Usato", gb(totale - libero)))
    }

    private fun informazioni(): Array<View> {
        val versione = try { packageManager.getPackageInfo(packageName, 0).versionName } catch (e: PackageManager.NameNotFoundException) { "" }
        return arrayOf(
            riga("SofiOS", "versione $versione"),
            riga("Android", Build.VERSION.RELEASE),
            riga("Sviluppato da", "Sofi Labs · © 2026 · Tutti i diritti riservati"),
            Stile.bottone(this, "Componenti e licenze", Stile.SECONDARIO, Stile.TESTO) { licenze() },
        )
    }

    private fun licenze() {
        AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle("Componenti e licenze")
            .setMessage("SofiOS per Android non usa librerie esterne.\n\n" +
                "Usa i componenti di Android (Android Open Source Project), con licenza Apache 2.0.\n\n" +
                "Le icone, i colori e la mascotte sono di Sofi Labs.")
            .setPositiveButton("Chiudi", null)
            .show().getButton(android.content.DialogInterface.BUTTON_POSITIVE).isAllCaps = false
    }

    /** Scelta degli assistenti online: quelli attivi compaiono nel pannello e si aprono nel browser. */
    private fun assistenti(): Array<View> {
        val scelti = Assistenti.scelti(this).map { it.id }.toSet()
        val l = ArrayList<View>()
        l.add(Stile.testo(this, "Si aprono nel browser, con internet e il tuo account (o con la loro app, se la installi). SofiOS non vede cosa scrivi.",
            13f, Stile.PICCOLO))
        for (a in Assistenti.tutti) {
            val acceso = a.id in scelti
            val riga = LinearLayout(this).apply {
                orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
                setPadding(dp(12), dp(10), dp(12), dp(10)); isClickable = true
                contentDescription = a.nome
                background = Stile.riquadro(this@ImpostazioniActivity, if (acceso) Stile.SCELTA else Stile.SECONDARIO, 12)
                setOnClickListener { Assistenti.imposta(this@ImpostazioniActivity, a.id, !acceso); apri(scelta) }
            }
            val originale = Assistenti.iconaOriginale(this, a)
            riga.addView(ImageView(this).apply {
                if (originale != null) {
                    // icona originale dell'assistente (se il file è stato messo nell'app)
                    setImageDrawable(originale); scaleType = ImageView.ScaleType.FIT_CENTER
                    outlineProvider = object : android.view.ViewOutlineProvider() {
                        override fun getOutline(v: View, o: android.graphics.Outline) { o.setRoundRect(0, 0, v.width, v.height, dp(12).toFloat()) }
                    }
                    clipToOutline = true
                } else {
                    setImageResource(a.icona); setPadding(dp(8), dp(8), dp(8), dp(8))
                    background = android.graphics.drawable.GradientDrawable(
                        android.graphics.drawable.GradientDrawable.Orientation.TOP_BOTTOM, intArrayOf(a.chiaro, a.scuro)).apply { cornerRadius = dp(12).toFloat() }
                }
            }, LinearLayout.LayoutParams(dp(48), dp(48)))
            riga.addView(Stile.testo(this, a.nome, 18f, if (acceso) Stile.BIANCO else Stile.TESTO, true).apply { setPadding(dp(14), 0, 0, 0) },
                LinearLayout.LayoutParams(0, -2, 1f))
            riga.addView(Stile.testo(this, if (acceso) "Attivo ✓" else "Spento", 15f, if (acceso) Stile.BIANCO else Stile.PICCOLO))
            // facoltativo: tastino a destra per l'app ufficiale (Play Store, con la conferma di Android); se c'è, SofiOS apre quella
            if (Assistenti.appInstallata(this, a)) {
                riga.addView(Stile.testo(this, "App installata", 13f, if (acceso) Stile.BIANCO else Stile.PICCOLO).apply { setPadding(dp(14), 0, 0, 0) })
            } else {
                // sulla riga blu (assistente attivo) il tastino è bianco trasparente, altrimenti il blu non si vedrebbe
                val tastino = if (acceso) Stile.bottone(this, "Installa l'app", 0x33FFFFFF, Stile.BIANCO) { Assistenti.installa(this, a) }
                    else Stile.bottone(this, "Installa l'app", Stile.SECONDARIO, Stile.TESTO) { Assistenti.installa(this, a) }
                riga.addView(tastino.apply { textSize = 13f; minimumHeight = dp(36); setPadding(dp(14), 0, dp(14), 0) },
                    LinearLayout.LayoutParams(-2, dp(36)).apply { leftMargin = dp(14) })
            }
            l.add(riga)
        }
        l.add(Stile.testo(this, "Le app sono facoltative: il browser va sempre bene. Le app chiedono più permessi (microfono, foto) e si aggiornano da sole.", 13f, Stile.PICCOLO))
        return l.toTypedArray()
    }

    private fun altre(): Array<View> {
        fun voce(nome: String, i: Intent) = Stile.bottone(this, nome, Stile.SECONDARIO, Stile.TESTO) { Controlli.apri(this, i) }
        return arrayOf(
            Stile.testo(this, "Queste pagine sono di Android: qui sono solo le scorciatoie.", 13f, Stile.PICCOLO),
            voce("Wi-Fi", Intent(Settings.ACTION_WIFI_SETTINGS)),
            voce("Bluetooth", Intent(Settings.ACTION_BLUETOOTH_SETTINGS)),
            voce("Data e ora", Intent(Settings.ACTION_DATE_SETTINGS)),
            voce("Lingua", Intent(Settings.ACTION_LOCALE_SETTINGS)),
            voce("Accessibilità", Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)),
            voce("App predefinite", Intent(Settings.ACTION_MANAGE_DEFAULT_APPS_SETTINGS)),
            voce("Tutte le impostazioni di Android", Intent(Settings.ACTION_SETTINGS)),
        )
    }

    // ---- elenco delle app ----

    private fun paginaApp(): View {
        val app: List<ResolveInfo> = packageManager.queryIntentActivities(
            Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER), 0)
            .filter { it.activityInfo.packageName != packageName }
            .sortedBy { it.loadLabel(packageManager).toString().lowercase(Locale.ROOT) }
        val colonna = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(24), dp(20), dp(24), dp(12))
        }
        colonna.addView(Stile.testo(this, "App", 22f, Stile.TESTO, true).apply { setPadding(0, 0, 0, dp(6)) })
        colonna.addView(Stile.testo(this, "${app.size} app. Tocca un'app per aprirla, metterla nel Dock o disinstallarla.", 13f, Stile.PICCOLO))
        colonna.addView(ListView(this).apply {
            divider = null; dividerHeight = 0
            adapter = object : BaseAdapter() {
                override fun getCount() = app.size
                override fun getItem(i: Int) = app[i]
                override fun getItemId(i: Int) = i.toLong()
                override fun getView(i: Int, v: View?, p: ViewGroup?): View {
                    val r = (v as? LinearLayout) ?: LinearLayout(this@ImpostazioniActivity).apply {
                        orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
                        setPadding(0, dp(8), 0, dp(8))
                        addView(ImageView(context), LinearLayout.LayoutParams(dp(40), dp(40)))
                        addView(Stile.testo(context, "", 16f, Stile.TESTO).apply {
                            maxLines = 1; ellipsize = TextUtils.TruncateAt.END; setPadding(dp(14), 0, 0, 0)
                        })
                    }
                    (r.getChildAt(0) as ImageView).setImageDrawable(app[i].loadIcon(packageManager))
                    (r.getChildAt(1) as TextView).text = app[i].loadLabel(packageManager)
                    return r
                }
            }
            setOnItemClickListener { _, _, i, _ -> opzioniApp(app[i]) }
        }, LinearLayout.LayoutParams(-1, 0, 1f).apply { topMargin = dp(8) })
        return colonna
    }

    private fun opzioniApp(r: ResolveInfo) {
        val pacchetto = r.activityInfo.packageName
        val nome = r.loadLabel(packageManager).toString()
        val diSistema = (r.activityInfo.applicationInfo.flags and ApplicationInfo.FLAG_SYSTEM) != 0
        val inDock = Dock.inDock(this, pacchetto)
        val dock = if (inDock) "Togli dal Dock" else "Metti nel Dock"
        val scelte = if (diSistema) arrayOf("Apri", dock, "Informazioni dell'app") else arrayOf("Apri", dock, "Disinstalla", "Informazioni dell'app")
        AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle(nome)
            .setItems(scelte) { _, k ->
                when (scelte[k]) {
                    "Apri" -> packageManager.getLaunchIntentForPackage(pacchetto)?.let { startActivity(it) }
                    "Metti nel Dock" -> Dock.fissaConScelta(this, pacchetto) { }
                    "Togli dal Dock" -> Dock.togli(this, pacchetto)
                    "Disinstalla" -> disinstalla(pacchetto, nome)
                    else -> Controlli.apri(this, Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:$pacchetto")))
                }
            }
            .setNegativeButton("Chiudi", null)
            .show().getButton(android.content.DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
    }

    private fun disinstalla(pacchetto: String, nome: String) {
        val d = AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle("Disinstalla")
            .setMessage("Vuoi disinstallare «$nome»? Poi Android ti chiederà l'ultima conferma.")
            .setPositiveButton("Sì") { _, _ ->
                Controlli.apri(this, Intent(Intent.ACTION_DELETE, Uri.parse("package:$pacchetto")))
            }
            .setNegativeButton("No", null)
            .show()
        d.getButton(android.content.DialogInterface.BUTTON_POSITIVE).isAllCaps = false
        d.getButton(android.content.DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
    }

    private fun dp(v: Int) = Stile.dp(this, v)
}
