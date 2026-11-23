package it.sofilabs.sofios

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.Toast

/** Schermata iniziale di SofiOS: versione 0.1, solo due icone, nessuna libreria. */
class MainActivity : Activity() {

    private val fully = "de.ozerov.fully"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = FONDO
        window.navigationBarColor = FONDO

        val radice = FrameLayout(this)
        // Sfondo di SofiOS (lo stesso del computer): mare di notte, stelle e il faro.
        radice.addView(ImageView(this).apply {
            setImageResource(R.drawable.sfondo)
            scaleType = ImageView.ScaleType.CENTER_CROP
        }, FrameLayout.LayoutParams(-1, -1))

        // Barra in basso, come sul computer: icone tonde colorate.
        val barra = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            setPadding(dp(14), dp(10), dp(14), dp(10))
            background = GradientDrawable().apply {
                setColor(BARRA)
                cornerRadius = dp(24).toFloat()
            }
        }
        barra.addView(icona("Casa", R.drawable.ic_casa, ORO) { apriFully() })
        barra.addView(icona("Impostazioni", R.drawable.ic_impostazioni, GRIGIO) {
            startActivity(Intent(Settings.ACTION_SETTINGS))
        })
        radice.addView(barra, FrameLayout.LayoutParams(-2, -2, Gravity.BOTTOM or Gravity.CENTER_HORIZONTAL).apply {
            bottomMargin = dp(16)
        })
        setContentView(radice)

        // Dopo ogni accensione, la prima volta che parte SofiOS apre da solo Casa (Fully).
        if (primaVoltaDopoAccensione()) apriFully(silenzioso = true)
    }

    /** Vero solo la prima volta dopo ogni accensione del dispositivo. Nessun servizio acceso. */
    private fun primaVoltaDopoAccensione(): Boolean {
        val accensione = Settings.Global.getInt(contentResolver, Settings.Global.BOOT_COUNT, -1)
        val memoria = getSharedPreferences("sofios", Context.MODE_PRIVATE)
        if (memoria.getInt("accensione", -2) == accensione) return false
        memoria.edit().putInt("accensione", accensione).apply()
        return true
    }

    private fun apriFully(silenzioso: Boolean = false) {
        val i = packageManager.getLaunchIntentForPackage(fully)
        if (i != null) startActivity(i)
        else if (!silenzioso) Toast.makeText(this, "Fully Kiosk non è installato", Toast.LENGTH_LONG).show()
    }

    private fun icona(nome: String, immagine: Int, colore: Int, azione: () -> Unit): View =
        ImageView(this).apply {
            setImageResource(immagine)
            contentDescription = nome
            scaleType = ImageView.ScaleType.CENTER_INSIDE
            setPadding(dp(14), dp(14), dp(14), dp(14))
            background = GradientDrawable().apply {
                setColor(colore)
                cornerRadius = dp(16).toFloat()
            }
            layoutParams = LinearLayout.LayoutParams(dp(72), dp(72)).apply {
                setMargins(dp(8), 0, dp(8), 0)
            }
            setOnClickListener { azione() }
        }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    // Tasto Home: resta qui, niente da fare.
    override fun onNewIntent(intent: Intent) { super.onNewIntent(intent) }

    // Indietro non deve mai chiudere la schermata iniziale.
    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {}

    companion object {
        private const val FONDO = 0xFF0B1F33.toInt()          // blu notte del computer
        private const val BARRA = 0xE60B1F33.toInt()          // barra in basso, un po' trasparente
        private const val ORO = 0xFFFFD479.toInt()
        private const val GRIGIO = 0xFF6B7A8C.toInt()
    }
}
