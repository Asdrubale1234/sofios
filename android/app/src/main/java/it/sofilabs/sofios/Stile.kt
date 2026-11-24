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
    const val FONDO = 0xFF0B2740.toInt()
    const val PANNELLO = 0xFF12365A.toInt()
    const val TESTO = 0xFFE6F1FF.toInt()
    const val PICCOLO = 0xFF8FB3D4.toInt()
    const val SELEZ = 0xFF1E6FA8.toInt()
    const val SECONDARIO = 0xFF1E4F7C.toInt()
    const val ORO = 0xFFFFD479.toInt()
    const val BIANCO = 0xFFFFFFFF.toInt()

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
