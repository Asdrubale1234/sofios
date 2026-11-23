package it.sofilabs.sofios

import android.app.AlertDialog
import android.content.Context
import android.content.DialogInterface
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.text.Editable
import android.text.InputType
import android.text.TextUtils
import android.text.TextWatcher
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Note di SofiOS, come sul computer: un file di testo per nota, salvataggio automatico,
 * elenco a sinistra e testo a destra (su schermi stretti: prima l'elenco, poi la nota).
 * Le note stanno nella cartella privata dell'app (più avanti diventerà la Cartella SofiOS).
 */
class NoteActivity : SchermataSofiOS() {

    private lateinit var cartella: File
    private var note: List<File> = emptyList()
    private var titoli: List<String> = emptyList()
    private var corrente: File? = null
    private var salvato: String? = null
    private var caricando = false
    private var stretto = false
    private var nelTesto = false

    private lateinit var elenco: ListView
    private lateinit var testo: EditText
    private lateinit var colonnaElenco: LinearLayout
    private lateinit var colonnaTesto: LinearLayout
    private val adattatore = Adattatore()
    private val ritardo = Handler(Looper.getMainLooper())
    private val salvaDopo = Runnable { salva() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = FONDO
        window.navigationBarColor = FONDO
        cartella = File(filesDir, "Note").apply { mkdirs() }
        stretto = resources.configuration.screenWidthDp < 600

        val radice = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setBackgroundColor(FONDO)
            setPadding(dp(20), dp(18), dp(20), dp(18))
        }

        // Colonna dell'elenco
        colonnaElenco = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        colonnaElenco.addView(TextView(this).apply {
            text = "Note"; textSize = 22f; setTextColor(0xFFFFFFFF.toInt()); typeface = Typeface.DEFAULT_BOLD
            setPadding(0, 0, 0, dp(10))
        })
        elenco = ListView(this).apply {
            adapter = adattatore
            divider = null; dividerHeight = 0
            background = riquadro(PANNELLO, 12)
            setPadding(dp(6), dp(6), dp(6), dp(6)); clipToPadding = false
            setOnItemClickListener { _, _, i, _ -> apri(note[i], vaiAlTesto = true) }
        }
        colonnaElenco.addView(elenco, LinearLayout.LayoutParams(-1, 0, 1f))
        colonnaElenco.addView(bottone("Nuova nota", ORO, FONDO) { nuova() }, voceBottone())
        colonnaElenco.addView(bottone("Elimina nota", SELEZ, 0xFFFFFFFF.toInt()) { elimina() }, voceBottone())

        // Colonna del testo
        colonnaTesto = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        if (stretto) {
            colonnaTesto.addView(TextView(this).apply {
                text = "‹ Note"; textSize = 20f; setTextColor(ORO); typeface = Typeface.DEFAULT_BOLD
                setPadding(0, 0, 0, dp(10))
                setOnClickListener { mostraElenco() }
            })
        }
        testo = EditText(this).apply {
            hint = "Scrivi qui la tua nota…"
            setHintTextColor(0xFF8FB0CC.toInt())
            setTextColor(TESTO)
            textSize = 17f
            gravity = Gravity.TOP or Gravity.START
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE or
                InputType.TYPE_TEXT_FLAG_CAP_SENTENCES
            background = riquadro(PANNELLO, 12)
            setPadding(dp(14), dp(14), dp(14), dp(14))
            addTextChangedListener(object : TextWatcher {
                override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
                override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
                override fun afterTextChanged(s: Editable?) {
                    if (caricando) return
                    ritardo.removeCallbacks(salvaDopo)
                    ritardo.postDelayed(salvaDopo, 600)   // salvataggio automatico
                }
            })
        }
        colonnaTesto.addView(testo, LinearLayout.LayoutParams(-1, 0, 1f))

        if (stretto) {
            radice.addView(colonnaElenco, LinearLayout.LayoutParams(-1, -1))
            radice.addView(colonnaTesto, LinearLayout.LayoutParams(-1, -1))
        } else {
            radice.addView(colonnaElenco, LinearLayout.LayoutParams(dp(250), -1))
            radice.addView(colonnaTesto, LinearLayout.LayoutParams(0, -1, 1f).apply { leftMargin = dp(16) })
        }
        mostra(radice)

        carica(null, vaiAlTesto = !stretto)
        if (note.isEmpty()) nuova() else if (stretto) mostraElenco()
    }

    // ---- elenco e file ----

    private fun carica(scegli: File?, vaiAlTesto: Boolean) {
        note = (cartella.listFiles { f -> f.name.endsWith(".txt") }?.toList() ?: emptyList())
            .sortedByDescending { it.lastModified() }
        titoli = note.map { titoloDi(leggi(it)) }
        adattatore.notifyDataSetChanged()
        if (note.isNotEmpty()) {
            val scelta = scegli?.takeIf { it in note } ?: corrente?.takeIf { it in note } ?: note[0]
            apri(scelta, vaiAlTesto)
        }
    }

    private fun apri(f: File, vaiAlTesto: Boolean) {
        if (corrente != null && corrente != f) salva()
        corrente = f
        salvato = leggi(f)
        caricando = true
        testo.setText(salvato)
        testo.setSelection(testo.text.length)
        caricando = false
        adattatore.notifyDataSetChanged()
        if (stretto) { if (vaiAlTesto) mostraTesto() else mostraElenco() }
    }

    private fun leggi(f: File): String = try { f.readText() } catch (e: IOException) { "" }

    private fun titoloDi(t: String): String {
        val riga = t.lineSequence().map { it.trim() }.firstOrNull { it.isNotEmpty() } ?: ""
        return if (riga.isEmpty()) "Nota vuota" else riga.take(48)
    }

    /**
     * Salva solo se il testo è cambiato, scrivendo prima in un file temporaneo e poi sostituendolo:
     * se il tablet si spegne a metà, la nota resta intera.
     */
    private fun salva() {
        ritardo.removeCallbacks(salvaDopo)
        val f = corrente ?: return
        val t = testo.text.toString()
        if (t == salvato) return
        val tmp = File(f.path + ".tmp")
        try {
            FileOutputStream(tmp).use { it.write(t.toByteArray(Charsets.UTF_8)); it.flush(); it.fd.sync() }
            if (!tmp.renameTo(f)) throw IOException("rename")
        } catch (e: IOException) {
            Toast.makeText(this, "Non riesco a salvare la nota. Controlla che la memoria non sia piena.",
                Toast.LENGTH_LONG).show()
            return
        }
        salvato = t
        val i = note.indexOf(f)
        if (i >= 0) { titoli = titoli.toMutableList().also { it[i] = titoloDi(t) }; adattatore.notifyDataSetChanged() }
    }

    private fun nuova() {
        salva()
        if (corrente != null && testo.text.isBlank()) {   // c'è già una nota vuota: si usa quella
            testo.requestFocus(); if (stretto) mostraTesto(); return
        }
        val base = "nota-" + SimpleDateFormat("yyyyMMdd-HHmmss", Locale.ROOT).format(Date())
        var n = 1
        var f: File
        while (true) {   // nome sempre nuovo: due note nello stesso secondo non si sovrascrivono
            f = File(cartella, base + (if (n == 1) "" else "-$n") + ".txt")
            try { if (f.createNewFile()) break else n++ } catch (e: IOException) {
                Toast.makeText(this, "Non riesco a creare la nota.", Toast.LENGTH_LONG).show(); return
            }
        }
        carica(f, vaiAlTesto = true)
        testo.requestFocus()
    }

    private fun elimina() {
        val f = corrente ?: return
        val d = AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle("Elimina nota")
            .setMessage("Vuoi eliminare questa nota?")
            .setPositiveButton("Sì") { _, _ ->
                ritardo.removeCallbacks(salvaDopo)
                f.delete()
                corrente = null; salvato = null
                carica(null, vaiAlTesto = false)
                if (note.isEmpty()) nuova()
            }
            .setNegativeButton("No", null)
            .show()
        d.getButton(DialogInterface.BUTTON_POSITIVE).isAllCaps = false
        d.getButton(DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
    }

    // ---- schermate (su schermi stretti) ----

    private fun mostraElenco() {
        if (!stretto) return
        salva(); nelTesto = false
        colonnaElenco.visibility = View.VISIBLE; colonnaTesto.visibility = View.GONE
    }

    private fun mostraTesto() {
        if (!stretto) return
        nelTesto = true
        colonnaElenco.visibility = View.GONE; colonnaTesto.visibility = View.VISIBLE
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (chiudiPannelloSeAperto()) return
        if (stretto && nelTesto) mostraElenco() else super.onBackPressed()
    }

    override fun onPause() {
        salva()
        super.onPause()
    }

    // ---- aspetto (stessi colori delle Note del computer) ----

    private inner class Adattatore : BaseAdapter() {
        override fun getCount() = note.size
        override fun getItem(i: Int) = note[i]
        override fun getItemId(i: Int) = i.toLong()
        override fun getView(i: Int, v: View?, p: ViewGroup?): View {
            val t = (v as? TextView) ?: TextView(this@NoteActivity).apply {
                textSize = 16f; setTextColor(TESTO); maxLines = 1; ellipsize = TextUtils.TruncateAt.END
                setPadding(dp(12), dp(14), dp(12), dp(14))
            }
            t.text = titoli.getOrElse(i) { "" }
            t.background = if (note[i] == corrente) riquadro(SELEZ, 8) else null
            return t
        }
    }

    private fun bottone(nome: String, sfondo: Int, colore: Int, azione: () -> Unit) =
        TextView(this).apply {
            text = nome; textSize = 16f; setTextColor(colore); typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            minimumHeight = dp(48)
            background = riquadro(sfondo, 10)
            setOnClickListener { azione() }
        }

    private fun voceBottone() = LinearLayout.LayoutParams(-1, dp(48)).apply { topMargin = dp(10) }

    private fun riquadro(colore: Int, raggio: Int) = GradientDrawable().apply {
        setColor(colore); cornerRadius = dp(raggio).toFloat()
    }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    companion object {
        private const val FONDO = 0xFF0B2740.toInt()
        private const val PANNELLO = 0xFF12365A.toInt()
        private const val TESTO = 0xFFE6F1FF.toInt()
        private const val SELEZ = 0xFF1E6FA8.toInt()
        private const val ORO = 0xFFFFD479.toInt()
    }
}
