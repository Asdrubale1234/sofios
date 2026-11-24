package it.sofilabs.sofios

import android.app.AlertDialog
import android.app.Dialog
import android.content.DialogInterface
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.os.Bundle
import android.text.InputType
import android.text.TextUtils
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import java.io.File
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * File di SofiOS: la «Cartella SofiOS» dell'app. Si vedono i file, si aprono (testo e immagini),
 * si creano cartelle, si rinomina e si elimina (con conferma). Nessun permesso speciale.
 */
class FileActivity : SchermataSofiOS() {

    private lateinit var radiceCartella: File
    private lateinit var corrente: File
    private var voci: List<File> = emptyList()
    private lateinit var percorso: TextView
    private lateinit var elenco: ListView
    private lateinit var vuoto: TextView
    private lateinit var su: TextView
    private val adattatore = Adattatore()
    private var daAprire: File? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        radiceCartella = Cartella.radice(this)
        corrente = radiceCartella
        intent.getStringExtra(EXTRA_PERCORSO)?.let { p ->
            val f = File(p)
            if (f.exists() && f.path.startsWith(radiceCartella.path)) {
                corrente = if (f.isDirectory) f else (f.parentFile ?: radiceCartella)
                if (f.isFile) daAprire = f
            }
        }

        val radice = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(20), dp(18), dp(20), dp(18))
        }
        radice.addView(Stile.testo(this, "File", 22f, Stile.BIANCO, true))
        percorso = Stile.testo(this, "", 13f, Stile.PICCOLO).apply { setPadding(0, dp(2), 0, dp(10)) }
        radice.addView(percorso)

        val corpo = FrameLayout(this).apply { background = Stile.riquadro(this@FileActivity, Stile.PANNELLO, 12) }
        elenco = ListView(this).apply {
            adapter = adattatore
            divider = null; dividerHeight = 0
            setPadding(dp(6), dp(6), dp(6), dp(6)); clipToPadding = false
            setOnItemClickListener { _, _, i, _ -> tocca(voci[i]) }
            setOnItemLongClickListener { _, _, i, _ -> opzioni(voci[i]); true }
        }
        corpo.addView(elenco, FrameLayout.LayoutParams(-1, -1))
        vuoto = Stile.testo(this, "Questa cartella è vuota.", 16f, Stile.PICCOLO).apply { gravity = Gravity.CENTER }
        corpo.addView(vuoto, FrameLayout.LayoutParams(-1, -1))
        radice.addView(corpo, LinearLayout.LayoutParams(-1, 0, 1f))

        val bottoni = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        su = Stile.bottone(this, "Cartella superiore", Stile.SECONDARIO, Stile.BIANCO) { vaiSu() }
        bottoni.addView(su, LinearLayout.LayoutParams(0, dp(48), 1f).apply { rightMargin = dp(8) })
        bottoni.addView(Stile.bottone(this, "Nuova cartella", Stile.ORO, Stile.FONDO) { nuovaCartella() },
            LinearLayout.LayoutParams(0, dp(48), 1f).apply { leftMargin = dp(8) })
        radice.addView(bottoni, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(12) })
        mostra(radice)
    }

    override fun onResume() {
        super.onResume()
        aggiorna()
        daAprire?.let { daAprire = null; tocca(it) }
    }

    private fun aggiorna() {
        voci = (corrente.listFiles { f -> !f.name.startsWith(".") && !f.name.endsWith(".tmp") }?.toList() ?: emptyList())
            .sortedWith(compareBy<File>({ !it.isDirectory }, { it.name.lowercase(Locale.ROOT) }))
        val rel = corrente.relativeTo(radiceCartella).path
        percorso.text = "Cartella SofiOS" + if (rel.isEmpty()) "" else " / " + rel.replace("/", " / ")
        su.alpha = if (corrente == radiceCartella) 0.4f else 1f
        vuoto.visibility = if (voci.isEmpty()) View.VISIBLE else View.GONE
        adattatore.notifyDataSetChanged()
    }

    private fun vaiSu() {
        if (corrente != radiceCartella) { corrente = corrente.parentFile ?: radiceCartella; aggiorna() }
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (chiudiPannelloSeAperto()) return
        if (corrente != radiceCartella) vaiSu() else super.onBackPressed()
    }

    private fun tocca(f: File) {
        if (f.isDirectory) { corrente = f; aggiorna(); return }
        when (f.extension.lowercase(Locale.ROOT)) {
            "txt", "md", "csv", "json", "log", "xml", "html" -> mostraTesto(f)
            "jpg", "jpeg", "png", "webp", "gif", "bmp" -> mostraImmagine(f)
            else -> Toast.makeText(this, "Questo tipo di file non si apre ancora.", Toast.LENGTH_LONG).show()
        }
    }

    // ---- elenco ----

    private inner class Adattatore : BaseAdapter() {
        override fun getCount() = voci.size
        override fun getItem(i: Int) = voci[i]
        override fun getItemId(i: Int) = i.toLong()
        override fun getView(i: Int, v: View?, p: ViewGroup?): View {
            val r = (v as? LinearLayout) ?: LinearLayout(this@FileActivity).apply {
                orientation = LinearLayout.VERTICAL
                setPadding(dp(12), dp(10), dp(12), dp(10))
                addView(Stile.testo(context, "", 16f, Stile.TESTO).apply { maxLines = 1; ellipsize = TextUtils.TruncateAt.END })
                addView(Stile.testo(context, "", 12f, Stile.PICCOLO))
            }
            val f = voci[i]
            (r.getChildAt(0) as TextView).text = (if (f.isDirectory) "📁  " else "📄  ") + f.name
            (r.getChildAt(1) as TextView).text = descrizione(f)
            return r
        }
    }

    private fun descrizione(f: File): String {
        val data = SimpleDateFormat("d/M/yyyy", Locale.ITALY).format(Date(f.lastModified()))
        return if (f.isDirectory) {
            val n = f.listFiles()?.size ?: 0
            (if (n == 1) "1 elemento" else "$n elementi") + " · $data"
        } else dimensione(f.length()) + " · $data"
    }

    private fun dimensione(b: Long): String = when {
        b < 1024 -> "$b byte"
        b < 1024 * 1024 -> String.format(Locale.ITALY, "%.0f KB", b / 1024.0)
        else -> String.format(Locale.ITALY, "%.1f MB", b / (1024.0 * 1024.0))
    }

    // ---- azioni ----

    private fun finestra(titolo: String): AlertDialog.Builder =
        AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert).setTitle(titolo)

    private fun senzaMaiuscole(d: AlertDialog) {
        d.getButton(DialogInterface.BUTTON_POSITIVE)?.isAllCaps = false
        d.getButton(DialogInterface.BUTTON_NEGATIVE)?.isAllCaps = false
    }

    private fun nomeValido(n: String) = n.isNotBlank() && !n.contains('/') && n != "." && n != ".." && !n.startsWith(".")

    private fun nuovaCartella() {
        val campo = EditText(this).apply { hint = "Nome della cartella"; inputType = InputType.TYPE_CLASS_TEXT; contentDescription = "Nome" }
        val d = finestra("Nuova cartella").setView(campo)
            .setPositiveButton("Crea") { _, _ ->
                val nome = campo.text.toString().trim()
                val f = File(corrente, nome)
                if (!nomeValido(nome)) Toast.makeText(this, "Nome non valido.", Toast.LENGTH_LONG).show()
                else if (f.exists()) Toast.makeText(this, "Esiste già.", Toast.LENGTH_LONG).show()
                else if (!f.mkdir()) Toast.makeText(this, "Non riesco a creare la cartella.", Toast.LENGTH_LONG).show()
                aggiorna()
            }
            .setNegativeButton("Annulla", null).show()
        senzaMaiuscole(d)
    }

    private fun opzioni(f: File) {
        val scelte = arrayOf("Rinomina", "Elimina")
        finestra(f.name).setItems(scelte) { _, k -> if (k == 0) rinomina(f) else elimina(f) }
            .setNegativeButton("Chiudi", null).show().getButton(DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
    }

    private fun rinomina(f: File) {
        val campo = EditText(this).apply { setText(f.name); inputType = InputType.TYPE_CLASS_TEXT; contentDescription = "Nome" }
        val d = finestra("Rinomina").setView(campo)
            .setPositiveButton("Salva") { _, _ ->
                val nome = campo.text.toString().trim()
                val nuovo = File(f.parentFile, nome)
                if (!nomeValido(nome)) Toast.makeText(this, "Nome non valido.", Toast.LENGTH_LONG).show()
                else if (nuovo.exists()) Toast.makeText(this, "Esiste già.", Toast.LENGTH_LONG).show()
                else if (!f.renameTo(nuovo)) Toast.makeText(this, "Non riesco a rinominare.", Toast.LENGTH_LONG).show()
                aggiorna()
            }
            .setNegativeButton("Annulla", null).show()
        senzaMaiuscole(d)
    }

    private fun elimina(f: File) {
        val d = finestra("Elimina")
            .setMessage(if (f.isDirectory) "Vuoi eliminare la cartella «${f.name}» e tutto ciò che contiene?"
                        else "Vuoi eliminare «${f.name}»?")
            .setPositiveButton("Sì") { _, _ ->
                if (!f.deleteRecursively()) Toast.makeText(this, "Non riesco a eliminare.", Toast.LENGTH_LONG).show()
                aggiorna()
            }
            .setNegativeButton("No", null).show()
        senzaMaiuscole(d)
    }

    // ---- visualizzatori ----

    private fun schermoIntero(titolo: String, corpo: View) {
        val d = Dialog(this, android.R.style.Theme_DeviceDefault_NoActionBar)
        val colonna = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; setBackgroundColor(Stile.FONDO)
            setPadding(dp(20), dp(18), dp(20), dp(18))
        }
        val testa = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        testa.addView(Stile.testo(this, titolo, 18f, Stile.BIANCO, true).apply {
            maxLines = 1; ellipsize = TextUtils.TruncateAt.END
        }, LinearLayout.LayoutParams(0, -2, 1f))
        testa.addView(Stile.bottone(this, "Chiudi", Stile.ORO, Stile.FONDO) { d.dismiss() }, LinearLayout.LayoutParams(-2, dp(48)))
        colonna.addView(testa)
        colonna.addView(corpo, LinearLayout.LayoutParams(-1, 0, 1f).apply { topMargin = dp(12) })
        d.setContentView(colonna)
        d.show()
    }

    private fun mostraTesto(f: File) {
        val t = try { f.inputStream().use { val b = ByteArray(200_000); val n = it.read(b); String(b, 0, maxOf(n, 0), Charsets.UTF_8) } } catch (e: IOException) { "Non riesco a leggere il file." }
        val vista = Stile.testo(this, t, 16f, Stile.TESTO).apply {
            setPadding(dp(14), dp(14), dp(14), dp(14)); setTextIsSelectable(true)
            contentDescription = "Contenuto del file"
        }
        val scroll = ScrollView(this).apply {
            background = Stile.riquadro(this@FileActivity, Stile.PANNELLO, 12); addView(vista)
        }
        schermoIntero(f.name, scroll)
    }

    private fun mostraImmagine(f: File) {
        val limiti = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeFile(f.path, limiti)
        var campione = 1
        while (limiti.outWidth / campione > 2048 || limiti.outHeight / campione > 2048) campione *= 2
        val bm: Bitmap? = BitmapFactory.decodeFile(f.path, BitmapFactory.Options().apply { inSampleSize = campione })
        if (bm == null) { Toast.makeText(this, "Non riesco ad aprire l'immagine.", Toast.LENGTH_LONG).show(); return }
        schermoIntero(f.name, ImageView(this).apply { setImageBitmap(bm); scaleType = ImageView.ScaleType.FIT_CENTER })
    }

    private fun dp(v: Int) = Stile.dp(this, v)

    companion object { const val EXTRA_PERCORSO = "percorso" }
}
