package it.sofilabs.sofios

import android.content.Context
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.widget.TextView

/** Colori e piccoli pezzi comuni a tutte le app SofiOS (stessi colori del computer). */
object Stile {
    /** Tema scelto: false = scuro, true = chiaro. Colori nello stile «Apple» (stessi del computer). */
    var chiaro = false

    val FONDO get() = if (chiaro) 0xFFF2F2F7.toInt() else 0xFF1C1C1E.toInt()
    val PANNELLO get() = if (chiaro) 0xFFFFFFFF.toInt() else 0xFF2C2C2E.toInt()
    val BORDO get() = if (chiaro) 0xFFD1D1D6.toInt() else 0xFF3A3A3C.toInt()
    val TESTO get() = if (chiaro) 0xFF1C1C1E.toInt() else 0xFFF2F2F7.toInt()
    val PICCOLO get() = if (chiaro) 0xFF6E6E73.toInt() else 0xFF8E8E93.toInt()
    /** Blu di sistema: selezione piena (testo bianco), link, pulsanti secondari. */
    val BLU get() = if (chiaro) 0xFF007AFF.toInt() else 0xFF0A84FF.toInt()
    val SELEZ get() = BLU
    val SCELTA get() = BLU
    /** Riempimento neutro (righe, campi di testo). I pulsanti passati con questo colore diventano «secondari» (blu trasparente). */
    val SECONDARIO get() = if (chiaro) 0xFFE5E5EA.toInt() else 0xFF3A3A3C.toInt()
    /** Arancione: pulsante principale (testo scuro sopra). */
    val ORO get() = if (chiaro) 0xFFFF9500.toInt() else 0xFFFF9F0A.toInt()
    /** Arancione per i testi: nel tema chiaro è più scuro, per leggersi sul bianco. */
    val ORO_TESTO get() = if (chiaro) 0xFFC25E00.toInt() else 0xFFFF9F0A.toInt()
    /** Testo sopra l'arancione. */
    val SU_ORO get() = 0xFF1C1C1E.toInt()
    const val BIANCO = 0xFFFFFFFF.toInt()
    /** Per le cose che stanno sempre su fondo notte. */
    const val TESTO_NOTTE = 0xFFF2F2F7.toInt()

    private const val PREF = "sofios"
    fun carica(c: Context) {
        chiaro = try { c.getSharedPreferences(PREF, Context.MODE_PRIVATE).getBoolean("tema_chiaro", false) } catch (e: Exception) { false }
    }
    fun imposta(c: Context, vuoleChiaro: Boolean) {
        chiaro = vuoleChiaro
        try { c.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit().putBoolean("tema_chiaro", vuoleChiaro).apply() } catch (e: Exception) {}
    }

    /** Una posa di Luma come immagine (per le schermate vuote e simili); null se la posa non esiste. */
    fun luma(c: Context, nome: String, altezzaDp: Int): android.widget.ImageView? {
        val id = c.resources.getIdentifier("luma_" + nome.replace('-', '_'), "drawable", c.packageName)
        if (id == 0) return null
        return android.widget.ImageView(c).apply {
            setImageResource(id); scaleType = android.widget.ImageView.ScaleType.FIT_CENTER
            layoutParams = android.widget.LinearLayout.LayoutParams(-2, dp(c, altezzaDp)).apply { gravity = Gravity.CENTER_HORIZONTAL }
            adjustViewBounds = true
        }
    }

    fun dp(c: Context, v: Int) = (v * c.resources.displayMetrics.density).toInt()

    /** Angoli più morbidi, nello stile dei tablet Apple (il raggio richiesto è ingrandito del 40%). */
    fun riquadro(c: Context, colore: Int, raggioDp: Int) = GradientDrawable().apply {
        setColor(colore); cornerRadius = dp(c, raggioDp * 14 / 10).toFloat()
    }

    /** Un tocco leggero: il pulsante si rimpicciolisce appena sotto il dito e torna com'era. */
    fun premi(v: View) {
        v.setOnTouchListener { x, e ->
            when (e.actionMasked) {
                MotionEvent.ACTION_DOWN -> x.animate().scaleX(0.95f).scaleY(0.95f).setDuration(90).start()
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> x.animate().scaleX(1f).scaleY(1f).setDuration(120).start()
            }
            false
        }
    }

    fun bottone(c: Context, nome: String, sfondo: Int, colore: Int, azione: () -> Unit) = TextView(c).apply {
        text = nome; textSize = 16f; typeface = Typeface.DEFAULT_BOLD
        gravity = Gravity.CENTER
        minimumHeight = dp(c, 48)
        setPadding(dp(c, 16), 0, dp(c, 16), 0)
        if (sfondo == SECONDARIO) {
            // pulsante secondario: blu trasparente con bordo e testo blu
            setTextColor(BLU)
            background = GradientDrawable().apply {
                setColor(if (chiaro) 0x1A007AFF else 0x2E0A84FF)
                setStroke(dp(c, 1), if (chiaro) 0x73007AFF else 0xFF0A84FF.toInt())
                cornerRadius = dp(c, 10 * 14 / 10).toFloat()
            }
        } else {
            setTextColor(if (sfondo == ORO) SU_ORO else colore)
            background = riquadro(c, sfondo, 10)
        }
        setOnClickListener { azione() }
        premi(this)
    }

    fun testo(c: Context, t: String, dimensione: Float, colore: Int, grassetto: Boolean = false) = TextView(c).apply {
        text = t; textSize = dimensione; setTextColor(colore)
        if (grassetto) typeface = Typeface.DEFAULT_BOLD
    }
}
