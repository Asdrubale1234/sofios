package it.sofilabs.sofios

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.res.ColorStateList
import android.content.Intent
import android.media.AudioManager
import android.net.Uri
import android.provider.Settings
import android.view.View
import android.widget.LinearLayout
import android.widget.SeekBar
import android.widget.TextView

/** Controlli veri (luminosità, volume, rotazione) usati dal pannello e dalle Impostazioni. */
object Controlli {

    fun permessoScrittura(a: Activity) =
        Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS, Uri.parse("package:" + a.packageName))

    fun apri(a: Activity, i: Intent) {
        try { a.startActivity(i) } catch (e: ActivityNotFoundException) { /* pagina non presente su questo tablet */ }
    }

    private fun cursore(a: Activity, nome: String, massimo: Int, valore: Int, ascolta: (Int) -> Unit) = SeekBar(a).apply {
        max = massimo; progress = valore.coerceIn(0, massimo)
        contentDescription = nome
        progressTintList = ColorStateList.valueOf(Stile.ORO)
        thumbTintList = ColorStateList.valueOf(Stile.ORO)
        progressBackgroundTintList = ColorStateList.valueOf(Stile.SECONDARIO)
        minimumHeight = Stile.dp(a, 40)
        setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(s: SeekBar, p: Int, daUtente: Boolean) { if (daUtente) ascolta(p) }
            override fun onStartTrackingTouch(s: SeekBar) {}
            override fun onStopTrackingTouch(s: SeekBar) {}
        })
    }

    private fun riga(a: Activity, etichetta: String, corpo: View): View = LinearLayout(a).apply {
        orientation = LinearLayout.VERTICAL
        setPadding(0, Stile.dp(a, 6), 0, Stile.dp(a, 6))
        addView(Stile.testo(a, etichetta, 13f, Stile.PICCOLO))
        addView(corpo, LinearLayout.LayoutParams(-1, -2))
    }

    fun luminosita(a: Activity): View {
        val corpo: View = if (Settings.System.canWrite(a)) {
            val ora = Settings.System.getInt(a.contentResolver, Settings.System.SCREEN_BRIGHTNESS, 128)
            cursore(a, "Luminosità", 255, ora) { p ->
                try {
                    Settings.System.putInt(a.contentResolver, Settings.System.SCREEN_BRIGHTNESS_MODE,
                        Settings.System.SCREEN_BRIGHTNESS_MODE_MANUAL)
                    Settings.System.putInt(a.contentResolver, Settings.System.SCREEN_BRIGHTNESS, p.coerceAtLeast(5))
                } catch (e: SecurityException) { }
            }
        } else {
            Stile.bottone(a, "Consenti di cambiare la luminosità", Stile.ORO, Stile.FONDO) {
                apri(a, permessoScrittura(a))
            }.apply { contentDescription = "Consenti luminosità" }
        }
        return riga(a, "Luminosità", corpo)
    }

    fun volume(a: Activity, flusso: Int, nome: String): View {
        val am = a.getSystemService(Context.AUDIO_SERVICE) as AudioManager
        val corpo = cursore(a, nome, am.getStreamMaxVolume(flusso), am.getStreamVolume(flusso)) { p ->
            try { am.setStreamVolume(flusso, p, 0) } catch (e: SecurityException) { }
        }
        return riga(a, nome, corpo)
    }

    /** Pulsante che attiva o spegne la rotazione automatica dello schermo. */
    fun rotazione(a: Activity): View {
        val ok = Settings.System.canWrite(a)
        fun testo(): String {
            val v = Settings.System.getInt(a.contentResolver, Settings.System.ACCELEROMETER_ROTATION, 1)
            return "Rotazione automatica: " + if (v == 1) "sì" else "no"
        }
        val b = Stile.bottone(a, if (ok) testo() else "Consenti la rotazione", Stile.SECONDARIO, Stile.BIANCO) {}
        b.setOnClickListener {
            if (!Settings.System.canWrite(a)) { apri(a, permessoScrittura(a)); return@setOnClickListener }
            val v = Settings.System.getInt(a.contentResolver, Settings.System.ACCELEROMETER_ROTATION, 1)
            try { Settings.System.putInt(a.contentResolver, Settings.System.ACCELEROMETER_ROTATION, 1 - v) } catch (e: SecurityException) { }
            (it as TextView).text = testo()
        }
        return b
    }
}
