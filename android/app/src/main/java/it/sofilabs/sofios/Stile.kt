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
    /** Tema scelto: false = scuro (blu notte), true = chiaro (come SofiOSChiaro del computer). */
    var chiaro = false

    val FONDO get() = if (chiaro) 0xFFF2F2F7.toInt() else 0xFF0B2740.toInt()
    val PANNELLO get() = if (chiaro) 0xFFFFFFFF.toInt() else 0xFF12365A.toInt()
    val TESTO get() = if (chiaro) 0xFF1C1C1E.toInt() else 0xFFE6F1FF.toInt()
    val PICCOLO get() = if (chiaro) 0xFF6E6E76.toInt() else 0xFF8FB3D4.toInt()
    val SELEZ get() = if (chiaro) 0xFF0A6EDC.toInt() else 0xFF1E6FA8.toInt()
    val SECONDARIO get() = if (chiaro) 0xFFE2E2EA.toInt() else 0xFF1E4F7C.toInt()
    /** Riga scelta in un elenco (testo normale sopra). */
    val SCELTA get() = if (chiaro) 0xFFD2E4FA.toInt() else 0xFF1E6FA8.toInt()
    /** Oro: nel tema chiaro è più scuro, per potersi leggere su sfondo bianco. */
    val ORO get() = if (chiaro) 0xFFA66A00.toInt() else 0xFFFFD479.toInt()
    /** Testo sopra l'oro e sopra il blu: sempre leggibile. */
    val SU_ORO get() = if (chiaro) 0xFFFFFFFF.toInt() else 0xFF0B2740.toInt()
    const val BIANCO = 0xFFFFFFFF.toInt()
    /** Per le cose che stanno sempre su fondo notte (barra sopra lo sfondo, dock). */
    const val TESTO_NOTTE = 0xFFE6F1FF.toInt()

    private const val PREF = "sofios"
    fun carica(c: Context) {
        chiaro = try { c.getSharedPreferences(PREF, Context.MODE_PRIVATE).getBoolean("tema_chiaro", false) } catch (e: Exception) { false }
    }
    fun imposta(c: Context, vuoleChiaro: Boolean) {
        chiaro = vuoleChiaro
        try { c.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit().putBoolean("tema_chiaro", vuoleChiaro).apply() } catch (e: Exception) {}
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
        text = nome; textSize = 16f; setTextColor(colore); typeface = Typeface.DEFAULT_BOLD
        gravity = Gravity.CENTER
        minimumHeight = dp(c, 48)
        setPadding(dp(c, 16), 0, dp(c, 16), 0)
        background = riquadro(c, sfondo, 10)
        setOnClickListener { azione() }
        premi(this)
    }

    fun testo(c: Context, t: String, dimensione: Float, colore: Int, grassetto: Boolean = false) = TextView(c).apply {
        text = t; textSize = dimensione; setTextColor(colore)
        if (grassetto) typeface = Typeface.DEFAULT_BOLD
    }
}
