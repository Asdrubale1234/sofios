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
import android.os.StatFs
import android.provider.Settings
import android.text.TextUtils
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.ScrollView
import android.widget.TextView
import java.util.Locale

/**
 * Impostazioni di SofiOS: le cose che un'app può fare da sola sono qui, con i nostri colori.
 * Per le altre (Wi-Fi con password, Bluetooth, data, lingua…) il pulsante porta alla pagina di Android.
 */
class ImpostazioniActivity : SchermataSofiOS() {

    private val voci = listOf("Schermo", "Suono", "Batteria", "Spazio", "App", "Altre impostazioni", "Informazioni")
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
        colonnaElenco.addView(Stile.testo(this, "Impostazioni", 22f, Stile.BIANCO, true).apply {
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
                t.background = if (i == scelta && !stretto) Stile.riquadro(this@ImpostazioniActivity, Stile.SELEZ, 8) else null
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

    override fun onResume() {
        super.onResume()
        if (!stretto || nelContenuto) apri(scelta)   // aggiorna dopo un permesso concesso
    }

    private fun apri(i: Int) {
        scelta = i
        adattatore.notifyDataSetChanged()
        colonnaContenuto.removeAllViews()
        val corpo = when (voci[i]) {
            "Schermo" -> pagina("Schermo", Controlli.luminosita(this), Controlli.rotazione(this))
            "Suono" -> pagina("Suono",
                Controlli.volume(this, AudioManager.STREAM_MUSIC, "Volume multimediale"),
                Controlli.volume(this, AudioManager.STREAM_ALARM, "Volume della sveglia"))
            "Batteria" -> pagina("Batteria", *batteria())
            "Spazio" -> pagina("Spazio", *spazio())
            "App" -> paginaApp()
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

    private fun pagina(titolo: String, vararg corpo: View): View {
        val colonna = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(24), dp(20), dp(24), dp(20))
        }
        colonna.addView(Stile.testo(this, titolo, 22f, Stile.BIANCO, true).apply { setPadding(0, 0, 0, dp(12)) })
        for (v in corpo) colonna.addView(v, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(8) })
        return ScrollView(this).apply { addView(colonna) }
    }

    private fun riga(nome: String, valore: String): View = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL
        addView(Stile.testo(context, nome, 13f, Stile.PICCOLO))
        addView(Stile.testo(context, valore, 18f, Stile.BIANCO))
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
            Stile.bottone(this, "Componenti e licenze", Stile.SECONDARIO, Stile.BIANCO) { licenze() },
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

    private fun altre(): Array<View> {
        fun voce(nome: String, i: Intent) = Stile.bottone(this, nome, Stile.SECONDARIO, Stile.BIANCO) { Controlli.apri(this, i) }
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
        colonna.addView(Stile.testo(this, "App", 22f, Stile.BIANCO, true).apply { setPadding(0, 0, 0, dp(6)) })
        colonna.addView(Stile.testo(this, "${app.size} app. Tocca un'app per aprirla o disinstallarla.", 13f, Stile.PICCOLO))
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
        val scelte = if (diSistema) arrayOf("Apri", "Informazioni dell'app") else arrayOf("Apri", "Disinstalla", "Informazioni dell'app")
        AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle(nome)
            .setItems(scelte) { _, k ->
                when (scelte[k]) {
                    "Apri" -> packageManager.getLaunchIntentForPackage(pacchetto)?.let { startActivity(it) }
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
