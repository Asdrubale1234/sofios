package it.sofilabs.sofios

import android.app.Activity
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
import android.widget.TextClock
import android.widget.TextView

/** Schermata iniziale di SofiOS: stile del computer, nessuna libreria, nessun servizio acceso. */
class MainActivity : Activity() {

    private val fully = "de.ozerov.fully"
    private var fullyTrovato: String? = null
    private lateinit var mascotte: FrameLayout
    private lateinit var tastoX: TextView
    private lateinit var casa: FrameLayout
    private lateinit var puntino: View
    private val nascondiX = Runnable { tastoX.visibility = View.GONE }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = FONDO
        window.navigationBarColor = FONDO

        val radice = FrameLayout(this)

        // Sfondo di SofiOS (lo stesso del computer): mare di notte e stelle.
        radice.addView(ImageView(this).apply {
            setImageResource(R.drawable.sfondo)
            scaleType = ImageView.ScaleType.CENTER_CROP
        }, FrameLayout.LayoutParams(-1, -1))

        // Orologio e data, in alto a sinistra.
        val orologio = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(32), dp(24), dp(32), 0)
        }
        orologio.addView(TextClock(this).apply {
            format24Hour = "HH:mm"; format12Hour = "HH:mm"
            textSize = 56f
            setTextColor(TESTO)
            typeface = Typeface.create("sans-serif-light", Typeface.NORMAL)
        })
        orologio.addView(TextClock(this).apply {
            format24Hour = "EEEE d MMMM"; format12Hour = "EEEE d MMMM"
            textSize = 20f
            setTextColor(ORO)
        })
        radice.addView(orologio, FrameLayout.LayoutParams(-2, -2, Gravity.TOP or Gravity.START))

        // La mascotte: sta sul fondo a destra. Un tocco mostra la X che la toglie.
        mascotte = FrameLayout(this)
        mascotte.addView(ImageView(this).apply {
            setImageResource(R.drawable.mascotte)
            scaleType = ImageView.ScaleType.FIT_CENTER
            contentDescription = "Mascotte SofiOS"
            setOnClickListener { mostraX() }
        }, FrameLayout.LayoutParams(-1, -1))
        tastoX = TextView(this).apply {
            text = "✕"
            textSize = 14f
            setTextColor(0xFFFFFFFF.toInt())
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            contentDescription = "Nascondi la mascotte"
            background = GradientDrawable().apply { setColor(0xCC0B2740.toInt()); setShape(GradientDrawable.OVAL); setStroke(dp(1), 0x66FFFFFF) }
            visibility = View.GONE
            setOnClickListener { impostaMascotte(false) }
        }
        mascotte.addView(tastoX, FrameLayout.LayoutParams(dp(36), dp(36), Gravity.TOP or Gravity.END).apply {
            topMargin = dp(6); rightMargin = dp(6)
        })
        radice.addView(mascotte, FrameLayout.LayoutParams(dp(180), dp(284), Gravity.BOTTOM or Gravity.END).apply {
            bottomMargin = dp(112); rightMargin = dp(56)
        })
        mascotte.visibility = if (mascotteVisibile()) View.VISIBLE else View.GONE

        // Barra in basso, come sul computer: icone tonde colorate.
        val barra = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            setPadding(dp(14), dp(10), dp(14), dp(10))
            background = GradientDrawable().apply { setColor(BARRA); cornerRadius = dp(24).toFloat() }
        }
        // Casa (Fully): si vede solo se Fully è installato. Dopo il primo tocco, parte sempre da solo
        // all'accensione. Tenendo premuto si spegne e si riaccende (puntino verde = parte da solo).
        val tastoCasa = icona("Casa", R.drawable.ic_casa, ORO, ORO_SCURO) {
            memoria().edit().putBoolean("casa_auto", true).apply()
            aggiornaCasa()
            apriFully()
        }
        tastoCasa.setOnLongClickListener {
            memoria().edit().putBoolean("casa_auto", !casaAuto()).apply()
            aggiornaCasa()
            true
        }
        puntino = View(this).apply {
            background = GradientDrawable().apply { setColor(VERDE); setShape(GradientDrawable.OVAL); setStroke(dp(2), FONDO) }
        }
        casa = FrameLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(dp(88), dp(72))
            addView(tastoCasa)
            addView(puntino, FrameLayout.LayoutParams(dp(16), dp(16), Gravity.TOP or Gravity.END).apply {
                topMargin = dp(4); rightMargin = dp(10)
            })
        }
        barra.addView(casa)
        barra.addView(icona("Impostazioni", R.drawable.ic_impostazioni, GRIGIO, GRIGIO_SCURO) {
            startActivity(Intent(Settings.ACTION_SETTINGS))
        })
        // Note: stesse note e stesso aspetto del computer
        barra.addView(icona("Note", R.drawable.ic_note, ROSA, ROSA_SCURO, piena = true) {
            startActivity(Intent(this, NoteActivity::class.java))
        })
        // Icona della mascotte: la toglie o la rimette (sul computer è «Aggiungi widget»).
        barra.addView(icona("Mostra o nascondi la mascotte", R.drawable.mascotte, MARE, MARE_SCURO, piena = true) {
            impostaMascotte(!mascotteVisibile())
        })
        radice.addView(barra, FrameLayout.LayoutParams(-2, -2, Gravity.BOTTOM or Gravity.CENTER_HORIZONTAL).apply {
            bottomMargin = dp(16)
        })

        setContentView(radice)

        aggiornaCasa()
        // Dopo ogni accensione, se Casa è attiva, SofiOS apre da solo Fully (una volta sola per accensione).
        if (primaVoltaDopoAccensione() && casaAuto() && fullyInstallato()) apriFully()
    }

    override fun onResume() {
        super.onResume()
        aggiornaCasa()
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
        mascotte.visibility = if (visibile) View.VISIBLE else View.GONE
        tastoX.visibility = View.GONE
    }

    /** Un tocco sulla mascotte mostra la X per qualche secondo (sul computer compare passandoci sopra). */
    private fun mostraX() {
        tastoX.visibility = View.VISIBLE
        tastoX.removeCallbacks(nascondiX)
        tastoX.postDelayed(nascondiX, 6000)
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

    /** Icona nello stile del computer: riquadro colorato con simbolo bianco. */
    private fun icona(nome: String, immagine: Int, chiaro: Int, scuro: Int, piena: Boolean = false, azione: () -> Unit): View =
        ImageView(this).apply {
            setImageResource(immagine)
            contentDescription = nome
            scaleType = ImageView.ScaleType.CENTER_INSIDE
            val m = if (piena) dp(6) else dp(14)
            setPadding(m, m, m, m)
            background = GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM, intArrayOf(chiaro, scuro)).apply {
                cornerRadius = dp(16).toFloat()
            }
            layoutParams = LinearLayout.LayoutParams(dp(72), dp(72)).apply { setMargins(dp(8), 0, dp(8), 0) }
            setOnClickListener { azione() }
        }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    // Tasto Home: resta qui, niente da fare.
    override fun onNewIntent(intent: Intent) { super.onNewIntent(intent) }

    // Indietro non deve mai chiudere la schermata iniziale.
    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {}

    companion object {
        private const val FONDO = 0xFF0B1F33.toInt()       // blu notte del computer
        private const val BARRA = 0xE60B1F33.toInt()
        private const val TESTO = 0xFFE8F1F8.toInt()
        private const val ORO = 0xFFFFD479.toInt()
        private const val ORO_SCURO = 0xFFE0A93C.toInt()
        private const val VERDE = 0xFF6FE0B0.toInt()
        private const val GRIGIO = 0xFF7D8DA0.toInt()
        private const val GRIGIO_SCURO = 0xFF566577.toInt()
        private const val ROSA = 0xFFFF8FB8.toInt()
        private const val ROSA_SCURO = 0xFFD6457F.toInt()
        private const val MARE = 0xFF3A86B8.toInt()
        private const val MARE_SCURO = 0xFF1B4F7A.toInt()
    }
}
