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
import android.widget.PopupMenu
import android.widget.TextClock
import android.widget.TextView
import android.widget.Toast

/** Schermata iniziale di SofiOS: stile del computer, nessuna libreria, nessun servizio acceso. */
class MainActivity : Activity() {

    private val fully = "de.ozerov.fully"
    private lateinit var mascotte: FrameLayout
    private lateinit var tastoX: TextView
    private val nascondiX = Runnable { tastoX.visibility = View.GONE }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = FONDO
        window.navigationBarColor = FONDO

        val radice = FrameLayout(this)

        // Sfondo di SofiOS (lo stesso del computer): mare di notte e stelle.
        // Tenendo premuto sullo sfondo si può rimettere la mascotte (come «Aggiungi widget» sul computer).
        radice.addView(ImageView(this).apply {
            setImageResource(R.drawable.sfondo)
            scaleType = ImageView.ScaleType.CENTER_CROP
            setOnLongClickListener { menuSfondo(it); true }
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
        barra.addView(icona("Casa", R.drawable.ic_casa, ORO, ORO_SCURO) { apriFully() })
        barra.addView(icona("Impostazioni", R.drawable.ic_impostazioni, GRIGIO, GRIGIO_SCURO) {
            startActivity(Intent(Settings.ACTION_SETTINGS))
        })
        radice.addView(barra, FrameLayout.LayoutParams(-2, -2, Gravity.BOTTOM or Gravity.CENTER_HORIZONTAL).apply {
            bottomMargin = dp(16)
        })
        setContentView(radice)

        // Dopo ogni accensione, la prima volta che parte SofiOS apre da solo Casa (Fully).
        if (primaVoltaDopoAccensione()) apriFully(silenzioso = true)
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
        tastoX.postDelayed(nascondiX, 4000)
    }

    private fun menuSfondo(v: View) {
        val menu = PopupMenu(this, v, Gravity.CENTER)
        if (mascotteVisibile()) menu.menu.add("Nascondi la mascotte") else menu.menu.add("Mostra la mascotte")
        menu.setOnMenuItemClickListener { impostaMascotte(!mascotteVisibile()); true }
        menu.show()
    }

    /** Vero solo la prima volta dopo ogni accensione del dispositivo. */
    private fun primaVoltaDopoAccensione(): Boolean {
        val accensione = Settings.Global.getInt(contentResolver, Settings.Global.BOOT_COUNT, -1)
        if (memoria().getInt("accensione", -2) == accensione) return false
        memoria().edit().putInt("accensione", accensione).apply()
        return true
    }

    private fun apriFully(silenzioso: Boolean = false) {
        val i = packageManager.getLaunchIntentForPackage(fully)
        if (i != null) startActivity(i)
        else if (!silenzioso) Toast.makeText(this, "Fully Kiosk non è installato", Toast.LENGTH_LONG).show()
    }

    /** Icona nello stile del computer: riquadro colorato con simbolo bianco. */
    private fun icona(nome: String, immagine: Int, chiaro: Int, scuro: Int, azione: () -> Unit): View =
        ImageView(this).apply {
            setImageResource(immagine)
            contentDescription = nome
            scaleType = ImageView.ScaleType.CENTER_INSIDE
            setPadding(dp(14), dp(14), dp(14), dp(14))
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
        private const val GRIGIO = 0xFF7D8DA0.toInt()
        private const val GRIGIO_SCURO = 0xFF566577.toInt()
    }
}
