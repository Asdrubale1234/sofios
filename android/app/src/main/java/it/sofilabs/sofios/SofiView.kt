package it.sofilabs.sofios

import android.animation.ObjectAnimator
import android.animation.ValueAnimator
import android.content.Context
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.view.animation.AccelerateDecelerateInterpolator
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.TextView
import android.graphics.drawable.GradientDrawable

/**
 * Luma, la mascotte di SofiOS: un faro di pietra con la faccia. Ha otto pose che cambiano con una
 * dissolvenza di un quarto di secondo, ondeggia piano da ferma e ha una piccola X per nasconderla.
 */
class SofiView(context: Context) : FrameLayout(context) {

    private val a = ImageView(context)
    private val b = ImageView(context)
    private var davanti = a
    var posaCorrente = "neutra"
        private set
    private var ondeggio: ObjectAnimator? = null
    private lateinit var tastoX: TextView
    private val nascondiX = Runnable { tastoX.visibility = View.GONE }
    var alToccare: () -> Unit = {}
    var alNascondere: () -> Unit = {}

    private val pose = mapOf(
        "neutra" to R.drawable.sofi_neutra, "parla" to R.drawable.sofi_parla, "ascolta" to R.drawable.sofi_ascolta,
        "pensa" to R.drawable.sofi_pensa, "felice" to R.drawable.sofi_felice, "concentrata" to R.drawable.sofi_concentrata,
        "preoccupata" to R.drawable.sofi_preoccupata, "saluta" to R.drawable.sofi_saluta)

    init {
        for (v in listOf(a, b)) {
            v.scaleType = ImageView.ScaleType.FIT_CENTER
            addView(v, LayoutParams(-1, -1))
        }
        a.setImageResource(R.drawable.sofi_neutra)
        b.alpha = 0f
        contentDescription = "Luma"
        isClickable = true
        setOnClickListener { alToccare() }

        // la piccola X per nasconderla (sempre visibile: sul tablet non c'è il passaggio del mouse)
        val d = Stile.dp(context, 1)
        tastoX = TextView(context).apply {
            text = "✕"; textSize = 13f; setTextColor(0xFFFFFFFF.toInt()); gravity = Gravity.CENTER
            typeface = android.graphics.Typeface.DEFAULT_BOLD
            contentDescription = "Nascondi Luma"
            background = GradientDrawable().apply { setColor(0xAA0B2740.toInt()); shape = GradientDrawable.OVAL; setStroke(d, 0x66FFFFFF) }
            setOnClickListener { alNascondere() }
            visibility = View.GONE
        }
        addView(tastoX, LayoutParams(Stile.dp(context, 32), Stile.dp(context, 32), Gravity.TOP or Gravity.END).apply {
            topMargin = Stile.dp(context, 4); rightMargin = Stile.dp(context, 4)
        })
    }

    /**
     * La X compare quando si tocca Luma (sul computer compare passandoci sopra con il mouse).
     * `per` = per quanti millisecondi resta; 0 = resta finché non la si nasconde.
     */
    fun mostraX(per: Long = 6000) {
        tastoX.visibility = View.VISIBLE
        removeCallbacks(nascondiX)
        if (per > 0) postDelayed(nascondiX, per)
    }

    fun nascondiX() { removeCallbacks(nascondiX); tastoX.visibility = View.GONE }

    /** Cambia posa con una dissolvenza di circa un quarto di secondo. */
    fun posa(nome: String) {
        val risorsa = pose[nome] ?: return
        if (nome == posaCorrente) return
        posaCorrente = nome
        val dietro = if (davanti === a) b else a
        dietro.setImageResource(risorsa)
        dietro.animate().cancel(); davanti.animate().cancel()
        dietro.alpha = 0f
        dietro.animate().alpha(1f).setDuration(250).start()
        davanti.animate().alpha(0f).setDuration(250).start()
        davanti = dietro
    }

    override fun onSizeChanged(w: Int, h: Int, ow: Int, oh: Int) {
        super.onSizeChanged(w, h, ow, oh)
        pivotX = w / 2f; pivotY = h.toFloat()
    }

    /** Ondeggia piano da ferma. Si ferma quando lo schermo non è in primo piano o le animazioni sono spente. */
    fun ondeggia(acceso: Boolean) {
        ondeggio?.cancel(); ondeggio = null
        rotation = 0f
        if (!acceso) return
        if (Settings.Global.getFloat(context.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f) return
        ondeggio = ObjectAnimator.ofFloat(this, View.ROTATION, -1.2f, 1.2f).apply {
            duration = 2600; repeatCount = ValueAnimator.INFINITE; repeatMode = ValueAnimator.REVERSE
            interpolator = AccelerateDecelerateInterpolator(); start()
        }
    }
}
