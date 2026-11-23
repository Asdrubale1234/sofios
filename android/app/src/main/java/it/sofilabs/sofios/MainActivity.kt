package it.sofilabs.sofios

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast

/** Schermata iniziale di SofiOS: versione 0.1, solo due icone, nessuna libreria. */
class MainActivity : Activity() {

    private val fully = "de.ozerov.fully"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = BLU
        window.navigationBarColor = BLU

        val riga = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
        }
        riga.addView(icona("Casa", ORO) { apriFully() })
        riga.addView(icona("Impostazioni", Color.WHITE) {
            startActivity(Intent(Settings.ACTION_SETTINGS))
        })

        val radice = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setBackgroundColor(BLU)
        }
        radice.addView(TextView(this).apply {
            text = "SofiOS"
            textSize = 32f
            setTextColor(ORO)
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, dp(32))
        })
        radice.addView(riga)
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

    private fun icona(nome: String, colore: Int, azione: () -> Unit): View =
        TextView(this).apply {
            text = nome
            textSize = 18f
            setTextColor(BLU)
            gravity = Gravity.CENTER
            background = GradientDrawable().apply {
                setColor(colore)
                cornerRadius = dp(28).toFloat()
            }
            layoutParams = LinearLayout.LayoutParams(dp(160), dp(160)).apply {
                setMargins(dp(16), dp(16), dp(16), dp(16))
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
        private const val BLU = 0xFF0B2A4A.toInt()
        private const val ORO = 0xFFE8B84A.toInt()
    }
}
