package it.sofilabs.sofios

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.Uri
import it.sofilabs.sofios.assistente.Assistenti
import android.os.BatteryManager
import android.os.Build
import android.provider.Settings
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.WindowInsets
import android.view.WindowInsetsController
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextClock
import android.widget.TextView
import android.media.AudioManager

class Scorciatoia(val nome: String, val azione: () -> Unit)

/**
 * Base di tutte le schermate SofiOS: nasconde la barra di Android e mostra la barra SofiOS
 * (rete, batteria, ora) con il pannello rapido che si apre toccandola o scorrendo giù da lì.
 * Vale solo dentro SofiOS e le sue app: nelle app di altri è Android a comandare.
 */
open class SchermataSofiOS : Activity() {

    private var barraInfo: TextView? = null
    private var pannello: PannelloRapido? = null
    private var batteria = -1
    private var inCarica = false
    private val ricevitore = object : BroadcastReceiver() {
        override fun onReceive(c: Context, i: Intent) { leggiBatteria(i); aggiornaBarra() }
    }

    private var temaMostrato = false

    override fun onCreate(savedInstanceState: android.os.Bundle?) {
        Stile.carica(this); temaMostrato = Stile.chiaro
        super.onCreate(savedInstanceState)
    }

    protected fun mostra(contenuto: View, sovrapposta: Boolean = false) {
        window.statusBarColor = Stile.FONDO
        window.navigationBarColor = Stile.FONDO
        val radice = FrameLayout(this).apply { setBackgroundColor(Stile.FONDO) }
        val barra = creaBarra(sovrapposta)
        val altezza = Stile.dp(this, ALTEZZA_BARRA)
        if (sovrapposta) {
            radice.addView(contenuto, FrameLayout.LayoutParams(-1, -1))
            radice.addView(barra, FrameLayout.LayoutParams(-1, altezza, Gravity.TOP))
        } else {
            val colonna = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
            colonna.addView(barra, LinearLayout.LayoutParams(-1, altezza))
            colonna.addView(contenuto, LinearLayout.LayoutParams(-1, 0, 1f))
            radice.addView(colonna, FrameLayout.LayoutParams(-1, -1))
        }
        val p = PannelloRapido(this)
        radice.addView(p, FrameLayout.LayoutParams(-1, -1))
        pannello = p
        setContentView(radice)
        nascondiBarraAndroid()
    }

    /** Scorciatoie mostrate nel pannello; le schermate possono cambiarle. */
    protected fun scorciatoieAssistenti(): List<Scorciatoia> = Assistenti.scelti(this).map { a ->
        Scorciatoia(a.nome) {
            try { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(a.indirizzo))) } catch (e: ActivityNotFoundException) { }
        }
    }

    open fun scorciatoie(): List<Scorciatoia> = listOf(
        Scorciatoia("Schermata iniziale") { startActivity(Intent(this, MainActivity::class.java)) },
        Scorciatoia("Note") { startActivity(Intent(this, NoteActivity::class.java)) },
        Scorciatoia("File") { startActivity(Intent(this, FileActivity::class.java)) },
        Scorciatoia("Cassaforte") { startActivity(Intent(this, CassaforteActivity::class.java)) },
        Scorciatoia("Impostazioni") { startActivity(Intent(this, ImpostazioniActivity::class.java)) },
    ) + scorciatoieAssistenti()

    /** Chiamato quando si apre il pannello: le schermate possono chiudere altro (es. la casella di Luma). */
    open fun alAprirePannello() {}

    protected fun chiudiPannelloSeAperto(): Boolean {
        val p = pannello ?: return false
        if (!p.aperto()) return false
        p.chiudi(); return true
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (!chiudiPannelloSeAperto()) super.onBackPressed()
    }

    // ---- barra SofiOS ----

    private fun creaBarra(sovrapposta: Boolean): View {
        val b = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setBackgroundColor(if (sovrapposta) (if (Stile.chiaro) 0x99F2F2F7.toInt() else 0x991C1C1E.toInt()) else Stile.FONDO)
            setPadding(Stile.dp(context, 16), 0, Stile.dp(context, 16), 0)
            contentDescription = "Barra SofiOS"
            isClickable = true
        }
        b.addView(TextView(this).apply {
            text = "SofiOS ▾"; textSize = 14f; setTextColor(Stile.ORO_TESTO); typeface = Typeface.DEFAULT_BOLD
        }, LinearLayout.LayoutParams(0, -2, 1f))
        val tb = Stile.TESTO
        barraInfo = TextView(this).apply { textSize = 14f; setTextColor(tb) }
        b.addView(barraInfo)
        b.addView(TextClock(this).apply {
            format24Hour = "HH:mm"; format12Hour = "HH:mm"
            textSize = 14f; setTextColor(tb)
            setPadding(Stile.dp(context, 12), 0, 0, 0)
        })
        // un tocco o uno scorrimento verso il basso aprono il pannello
        b.setOnTouchListener { _, e ->
            if (e.actionMasked == MotionEvent.ACTION_UP) pannello?.alterna()
            true
        }
        return b
    }

    private fun leggiBatteria(i: Intent) {
        val livello = i.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
        val scala = i.getIntExtra(BatteryManager.EXTRA_SCALE, 100)
        batteria = if (livello >= 0 && scala > 0) livello * 100 / scala else -1
        val stato = i.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
        inCarica = stato == BatteryManager.BATTERY_STATUS_CHARGING || stato == BatteryManager.BATTERY_STATUS_FULL
    }

    private fun rete(): String = try {
        val cm = getSystemService(ConnectivityManager::class.java)
        val c = cm.getNetworkCapabilities(cm.activeNetwork)
        when {
            c == null -> "Senza rete"
            c.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "Wi-Fi"
            c.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "Rete mobile"
            c.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> "Cavo"
            else -> "Rete"
        }
    } catch (e: SecurityException) { "" }

    private fun aggiornaBarra() {
        val bat = if (batteria >= 0) "$batteria%" + (if (inCarica) " ⚡" else "") else ""
        barraInfo?.text = listOf(rete(), bat).filter { it.isNotEmpty() }.joinToString("  ·  ")
    }

    override fun onResume() {
        super.onResume()
        Stile.carica(this)
        if (Stile.chiaro != temaMostrato) { recreate(); return }
        registerReceiver(ricevitore, IntentFilter(Intent.ACTION_BATTERY_CHANGED))?.let { leggiBatteria(it) }
        aggiornaBarra()
        nascondiBarraAndroid()
    }

    override fun onPause() {
        try { unregisterReceiver(ricevitore) } catch (e: IllegalArgumentException) { }
        pannello?.chiudi()
        super.onPause()
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) nascondiBarraAndroid()
    }

    private fun nascondiBarraAndroid() {
        if (Build.VERSION.SDK_INT >= 30) {
            window.insetsController?.let {
                it.hide(WindowInsets.Type.statusBars())
                it.systemBarsBehavior = WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            }
        } else {
            @Suppress("DEPRECATION")
            window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_FULLSCREEN or
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
        }
    }

    companion object { const val ALTEZZA_BARRA = 36 }
}

/** Il pannello rapido SofiOS: luminosità, volume, rete e scorciatoie, con i colori del computer. */
class PannelloRapido(private val att: SchermataSofiOS) : FrameLayout(att) {

    private val contenuto = LinearLayout(att).apply { orientation = LinearLayout.VERTICAL }
    private val scheda = ScrollView(att)

    init {
        visibility = View.GONE
        addView(View(att).apply {
            setBackgroundColor(0x66000000)
            setOnClickListener { chiudi() }
        }, LayoutParams(-1, -1))
        val larghezza = minOf(att.resources.displayMetrics.widthPixels, Stile.dp(att, 460))
        contenuto.apply {
            setPadding(Stile.dp(att, 20), Stile.dp(att, 16), Stile.dp(att, 20), Stile.dp(att, 18))
            contentDescription = "Pannello SofiOS"
        }
        scheda.apply {
            addView(contenuto)
            isClickable = true; overScrollMode = View.OVER_SCROLL_NEVER
            val r = Stile.dp(att, 30).toFloat()
            background = GradientDrawable().apply {
                setColor(if (Stile.chiaro) 0xEEF2F2F7.toInt() else 0xEE2C2C2E.toInt()); setStroke(Stile.dp(att, 1), if (Stile.chiaro) 0x22000000 else 0x33FFFFFF)
                cornerRadii = floatArrayOf(0f, 0f, 0f, 0f, r, r, r, r)
            }
        }
        addView(scheda, LayoutParams(larghezza, -2, Gravity.TOP or Gravity.CENTER_HORIZONTAL).apply {
            topMargin = Stile.dp(att, SchermataSofiOS.ALTEZZA_BARRA)
        })
    }

    fun aperto() = visibility == View.VISIBLE
    fun chiudi() { visibility = View.GONE }
    fun alterna() { if (aperto()) chiudi() else apri() }

    private fun apri() {
        att.alAprirePannello()
        contenuto.removeAllViews()
        contenuto.addView(Stile.testo(att, "Pannello SofiOS", 18f, Stile.TESTO, true))
        contenuto.addView(Controlli.luminosita(att))
        contenuto.addView(Controlli.volume(att, AudioManager.STREAM_MUSIC, "Volume"))
        contenuto.addView(Controlli.rotazione(att), voce())
        val reti = LinearLayout(att).apply { orientation = LinearLayout.HORIZONTAL }
        reti.addView(tessera("Wi-Fi") {
            val i = if (Build.VERSION.SDK_INT >= 29) Intent(Settings.Panel.ACTION_INTERNET_CONNECTIVITY)
                    else Intent(Settings.ACTION_WIFI_SETTINGS)
            Controlli.apri(att, i)
        }, peso())
        reti.addView(tessera("Bluetooth") { Controlli.apri(att, Intent(Settings.ACTION_BLUETOOTH_SETTINGS)) }, peso())
        contenuto.addView(reti, voce())
        val s = att.scorciatoie()
        var i = 0
        while (i < s.size) {
            val r = LinearLayout(att).apply { orientation = LinearLayout.HORIZONTAL }
            for (k in i until minOf(i + 3, s.size)) {
                r.addView(tessera(s[k].nome) { chiudi(); s[k].azione() }, peso())
            }
            contenuto.addView(r, voce())
            i += 3
        }
        visibility = View.VISIBLE
        scheda.alpha = 0f; scheda.translationY = -Stile.dp(att, 14).toFloat()
        scheda.animate().alpha(1f).translationY(0f).setDuration(190).start()
    }

    private fun voce() = LinearLayout.LayoutParams(-1, -2).apply { topMargin = Stile.dp(att, 10) }
    private fun peso() = LinearLayout.LayoutParams(0, Stile.dp(att, 52), 1f).apply {
        leftMargin = Stile.dp(att, 4); rightMargin = Stile.dp(att, 4)
    }

    private fun tessera(nome: String, azione: () -> Unit) =
        Stile.bottone(att, nome, Stile.SECONDARIO, Stile.TESTO, azione).apply { textSize = 14f }
}
