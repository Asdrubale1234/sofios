package it.sofilabs.sofios

import android.content.Context
import android.graphics.Canvas
import android.graphics.ColorFilter
import android.graphics.LinearGradient
import android.graphics.Paint
import android.graphics.Path
import android.graphics.PixelFormat
import android.graphics.RectF
import android.graphics.Shader
import android.graphics.drawable.Drawable

/**
 * Icona nello stile Apple, uguale a quella del computer: quadrato morbido (angoli 22,5%) con sfumatura verticale
 * (colore chiaro in alto, scuro in basso), un filo di luce bianca sul bordo, un riflesso bianco sulla metà alta e
 * un simbolo bianco a linea (56% del lato) con ombra nera al 22% spostata in basso.
 * Con `foto` al posto del simbolo a linea si mette un'immagine (la faccia di Luma), senza ombra.
 */
class IconaApple(c: Context, simbolo: Int, private val alto: Int, private val basso: Int, private val foto: Boolean = false) : Drawable() {
    private val sim = c.getDrawable(simbolo)!!.mutate()
    private val ombra = c.getDrawable(simbolo)!!.mutate().apply { if (!foto) setTint(0xFF000000.toInt()) }
    private val sfondo = Paint(Paint.ANTI_ALIAS_FLAG)
    private val filo = Paint(Paint.ANTI_ALIAS_FLAG).apply { style = Paint.Style.STROKE }
    private val riflesso = Paint(Paint.ANTI_ALIAS_FLAG)

    init { if (!foto) sim.setTint(0xFFFFFFFF.toInt()) }

    override fun draw(canvas: Canvas) {
        val s = minOf(bounds.width(), bounds.height()).toFloat()
        val x0 = bounds.left.toFloat(); val y0 = bounds.top.toFloat()
        val r = s * 0.225f
        val forma = RectF(x0, y0, x0 + s, y0 + s)
        sfondo.shader = LinearGradient(0f, y0, 0f, y0 + s, alto, basso, Shader.TileMode.CLAMP)
        canvas.drawRoundRect(forma, r, r, sfondo)

        // riflesso sulla metà alta (si ferma dentro l'angolo arrotondato)
        canvas.save()
        val p = Path().apply { addRoundRect(forma, r, r, Path.Direction.CW) }
        canvas.clipPath(p)
        riflesso.shader = LinearGradient(0f, y0, 0f, y0 + s / 2, 0x47FFFFFF, 0x0FFFFFFF, Shader.TileMode.CLAMP)
        canvas.drawRect(x0, y0, x0 + s, y0 + s / 2, riflesso)
        canvas.restore()

        // filo di luce sul bordo: 55% in alto, sfuma a metà
        val w = maxOf(1f, s * 0.014f)
        filo.strokeWidth = w
        filo.shader = LinearGradient(0f, y0, 0f, y0 + s / 2, 0x8CFFFFFF.toInt(), 0x00FFFFFF, Shader.TileMode.CLAMP)
        val dentro = RectF(x0 + w / 2, y0 + w / 2, x0 + s - w / 2, y0 + s - w / 2)
        canvas.drawRoundRect(dentro, r - w / 2, r - w / 2, filo)

        // simbolo
        val lato = if (foto) s * 0.88f else s * 0.56f
        val sx = (x0 + (s - lato) / 2).toInt(); val sy = (y0 + (s - lato) / 2).toInt()
        if (!foto) {
            val dy = maxOf(1, (s * 0.03f).toInt())   // ombra morbida, spostata appena in basso
            ombra.setBounds(sx, sy + dy, sx + lato.toInt(), sy + dy + lato.toInt())
            ombra.alpha = 56   // 22%
            ombra.draw(canvas)
        }
        sim.setBounds(sx, sy, sx + lato.toInt(), sy + lato.toInt())
        sim.draw(canvas)
    }

    override fun setAlpha(alpha: Int) {}
    override fun setColorFilter(colorFilter: ColorFilter?) {}
    @Deprecated("Deprecated in Java")
    override fun getOpacity() = PixelFormat.TRANSLUCENT
}
