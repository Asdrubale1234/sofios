package it.sofilabs.sofios

import android.content.Context
import android.content.Intent
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextClock
import android.widget.TextView
import it.sofilabs.sofios.assistente.CasellaSofi

/** Schermata iniziale di SofiOS: stile del computer, nessuna libreria, nessun servizio acceso. */
class MainActivity : SchermataSofiOS() {

    private val fully = "de.ozerov.fully"
    private var fullyTrovato: String? = null
    private lateinit var sofi: SofiView
    private lateinit var casella: CasellaSofi
    private lateinit var casa: FrameLayout
    private lateinit var puntino: View

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val radice = FrameLayout(this)

        // Sfondo di SofiOS (lo stesso del computer): mare di notte e stelle.
        radice.addView(ImageView(this).apply {
            setImageResource(R.drawable.sfondo)
            scaleType = ImageView.ScaleType.CENTER_CROP
        }, FrameLayout.LayoutParams(-1, -1))

        // Orologio e data, in alto a sinistra.
        val orologio = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(32), dp(48), dp(32), 0)
        }
        orologio.addView(TextClock(this).apply {
            format24Hour = "HH:mm"; format12Hour = "HH:mm"
            textSize = 56f
            setTextColor(TESTO)
            typeface = Typeface.create("sans-serif-light", Typeface.NORMAL)
        })
        orologio.addView(TextClock(this).apply {
            format24Hour = "EEEE d MMMM"; format12Hour = "EEEE d MMMM"
            textSize = 20f
            setTextColor(ORO)
        })
        radice.addView(orologio, FrameLayout.LayoutParams(-2, -2, Gravity.TOP or Gravity.START))

        // Sofi, la mascotte: sta sul fondo a destra. Un tocco fa comparire la X e apre la casella dove si scrive un comando.
        sofi = SofiView(this).apply {
            alToccare = { chiudiPannelloSeAperto(); mostraX(0); casella.apri() }
            alNascondere = { impostaMascotte(false) }
        }
        sofi.visibility = if (mascotteVisibile()) View.VISIBLE else View.GONE
        casella = CasellaSofi(this, sofi)
        radice.addView(casella, FrameLayout.LayoutParams(-1, -1))
        // Sofi sta SOPRA la casella: resta luminosa e la sua X si può toccare
        radice.addView(sofi, FrameLayout.LayoutParams(dp(200), dp(255), Gravity.BOTTOM or Gravity.END).apply {
            bottomMargin = dp(140); rightMargin = dp(56)
        })

        // Barra in basso, come sul computer: icone tonde colorate.
        val barra = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER
            setPadding(dp(14), dp(12), dp(14), dp(10))
            // barra «di vetro»: trasparente, con un filo chiaro sul bordo (senza sfocatura, per non pesare sui tablet modesti)
            background = GradientDrawable().apply { setColor(BARRA); cornerRadius = dp(32).toFloat(); setStroke(dp(1), 0x33FFFFFF) }
        }
        // Casa (Fully): si vede solo se Fully è installato. Dopo il primo tocco, parte sempre da solo
        // all'accensione. Tenendo premuto si spegne e si riaccende (puntino verde = parte da solo).
        val tastoCasa = icona("Casa", R.drawable.ic_casa, ORO, ORO_SCURO) { tocchiCasa() }
        tastoCasa.setOnLongClickListener {
            memoria().edit().putBoolean("casa_auto", !casaAuto()).apply()
            aggiornaCasa()
            true
        }
        puntino = View(this).apply {
            background = GradientDrawable().apply { setColor(VERDE); setShape(GradientDrawable.OVAL); setStroke(dp(2), FONDO) }
        }
        casa = FrameLayout(this).apply {
            layoutParams = LinearLayout.LayoutParams(dp(92), -2).apply { setMargins(dp(4), 0, dp(4), 0) }
            tastoCasa.layoutParams = FrameLayout.LayoutParams(-1, -2)
            addView(tastoCasa)
            addView(puntino, FrameLayout.LayoutParams(dp(16), dp(16), Gravity.TOP or Gravity.END).apply {
                topMargin = dp(2); rightMargin = dp(6)
            })
        }
        barra.addView(casa)
        barra.addView(icona("Impostazioni", R.drawable.ic_impostazioni, GRIGIO, GRIGIO_SCURO) {
            startActivity(Intent(this, ImpostazioniActivity::class.java))
        })
        // Note: stesse note e stesso aspetto del computer
        barra.addView(icona("Note", R.drawable.ic_note, ROSA, ROSA_SCURO, piena = true) {
            startActivity(Intent(this, NoteActivity::class.java))
        })
        barra.addView(icona("File", R.drawable.ic_file, ORO_FILE, ORO_FILE_SCURO, piena = true) {
            startActivity(Intent(this, FileActivity::class.java))
        })
        barra.addView(icona("Cassaforte", R.drawable.ic_password, TURCHESE, TURCHESE_SCURO, piena = true) {
            startActivity(Intent(this, CassaforteActivity::class.java))
        })
        // Icona di Sofi: la toglie o la rimette (sul computer è «Aggiungi widget»).
        barra.addView(icona("Mostra o nascondi Sofi", R.drawable.sofi_volto, MARE, MARE_SCURO, piena = true, etichetta = "Sofi") {
            impostaMascotte(!mascotteVisibile())
        })
        radice.addView(barra, FrameLayout.LayoutParams(-2, -2, Gravity.BOTTOM or Gravity.CENTER_HORIZONTAL).apply {
            bottomMargin = dp(16)
        })

        mostra(radice, sovrapposta = true)

        aggiornaCasa()
        // Dopo ogni accensione, se Casa è attiva, SofiOS apre da solo Fully (una volta sola per accensione).
        if (primaVoltaDopoAccensione() && casaAuto() && fullyInstallato()) apriFully()
    }

    override fun onResume() {
        super.onResume()
        sofi.ondeggia(mascotteVisibile())
        aggiornaCasa()
        if (!Cartella.permesso(this) && !memoria().getBoolean("cartella_chiesta", false)) avvisoCartella()
    }

    /** Una sola volta: spiega perché serve l'accesso ai file (Cartella SofiOS comune ai dispositivi). */
    private fun avvisoCartella() {
        memoria().edit().putBoolean("cartella_chiesta", true).apply()
        val d = android.app.AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle("Cartella SofiOS")
            .setMessage("Per tenere note, password e foto uguali sugli altri tuoi dispositivi, SofiOS ha bisogno dell'accesso ai file. " +
                "Ti porto alla pagina di Android dove si concede. Puoi farlo anche più tardi da Impostazioni, «Cartella SofiOS».")
            .setPositiveButton("Consenti") { _, _ -> Controlli.apri(this, Cartella.richiestaPermesso(this)) }
            .setNegativeButton("Più tardi", null)
            .show()
        d.getButton(android.content.DialogInterface.BUTTON_POSITIVE).isAllCaps = false
        d.getButton(android.content.DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
    }

    /** Cerca Fully tra i programmi che si possono aprire: per nome del pacchetto, oppure per nome «Fully». */
    private fun cercaFully(): String? {
        val elenco = packageManager.queryIntentActivities(
            Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER), 0)
        elenco.firstOrNull { it.activityInfo.packageName == fully }?.let { return fully }
        return elenco.firstOrNull { it.loadLabel(packageManager).toString().contains("fully", ignoreCase = true) }
            ?.activityInfo?.packageName
    }

    private fun fullyInstallato(): Boolean {
        fullyTrovato = cercaFully()
        return fullyTrovato != null
    }

    private fun casaAuto() = memoria().getBoolean("casa_auto", false)

    /** Casa si vede solo se Fully è installato; il puntino verde dice se parte da solo. */
    private fun aggiornaCasa() {
        casa.visibility = if (fullyInstallato()) View.VISIBLE else View.GONE
        puntino.visibility = if (casaAuto()) View.VISIBLE else View.GONE
    }

    private fun memoria() = getSharedPreferences("sofios", Context.MODE_PRIVATE)

    private fun mascotteVisibile() = memoria().getBoolean("mascotte", true)

    private fun impostaMascotte(visibile: Boolean) {
        memoria().edit().putBoolean("mascotte", visibile).apply()
        sofi.visibility = if (visibile) View.VISIBLE else View.GONE
        if (visibile) sofi.ondeggia(true) else { sofi.nascondiX(); sofi.ondeggia(false); casella.chiudi() }
    }

    /** Vero solo la prima volta dopo ogni accensione del dispositivo. */
    private fun primaVoltaDopoAccensione(): Boolean {
        val accensione = Settings.Global.getInt(contentResolver, Settings.Global.BOOT_COUNT, -1)
        if (memoria().getInt("accensione", -2) == accensione) return false
        memoria().edit().putInt("accensione", accensione).apply()
        return true
    }

    private fun apriFully() {
        val nome = fullyTrovato ?: cercaFully() ?: return
        packageManager.getLaunchIntentForPackage(nome)?.let { startActivity(it) }
    }

    /** Icona nello stile del computer: riquadro colorato con simbolo bianco. */
    /** Icona del dock: riquadro colorato con simbolo bianco e il nome sotto, come sui tablet Apple. */
    private fun icona(nome: String, immagine: Int, chiaro: Int, scuro: Int, piena: Boolean = false,
                      etichetta: String = nome, azione: () -> Unit): LinearLayout {
        val tessera = ImageView(this).apply {
            setImageResource(immagine)
            scaleType = ImageView.ScaleType.CENTER_INSIDE
            val m = if (piena) dp(7) else dp(15)
            setPadding(m, m, m, m)
            background = GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM, intArrayOf(chiaro, scuro)).apply {
                cornerRadius = dp(18).toFloat()
            }
            elevation = dp(3).toFloat()
        }
        val nomeSotto = TextView(this).apply {
            text = etichetta; textSize = 11.5f; setTextColor(TESTO); gravity = Gravity.CENTER
            typeface = Typeface.create("sans-serif-medium", Typeface.NORMAL); maxLines = 1
            setPadding(0, dp(6), 0, 0)
        }
        return LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER_HORIZONTAL
            contentDescription = nome; isClickable = true
            addView(tessera, LinearLayout.LayoutParams(dp(76), dp(76)))
            addView(nomeSotto, LinearLayout.LayoutParams(dp(88), -2))
            layoutParams = LinearLayout.LayoutParams(dp(92), -2).apply { setMargins(dp(4), 0, dp(4), 0) }
            setOnClickListener { azione() }
            Stile.premi(this)
        }
    }

    private fun dp(v: Int) = (v * resources.displayMetrics.density).toInt()

    // Tasto Home: resta qui, niente da fare.
    override fun onNewIntent(intent: Intent) { super.onNewIntent(intent) }

    // Indietro non deve mai chiudere la schermata iniziale (chiude solo il pannello, se aperto).
    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (casella.aperta()) { casella.chiudi(); return }
        chiudiPannelloSeAperto()
    }

    override fun onPause() {
        if (::sofi.isInitialized) sofi.ondeggia(false)
        if (::casella.isInitialized && casella.aperta()) casella.chiudi()
        super.onPause()
    }

    override fun alAprirePannello() {
        if (::casella.isInitialized && casella.aperta()) casella.chiudi()
    }

    // Scorciatoie del pannello SofiOS, quando si è nella schermata iniziale.
    override fun scorciatoie(): List<Scorciatoia> {
        val l = mutableListOf<Scorciatoia>()
        if (fullyInstallato()) l.add(Scorciatoia("Casa") { tocchiCasa() })
        l.add(Scorciatoia("Sofi") { if (!mascotteVisibile()) impostaMascotte(true); casella.apri() })
        l.add(Scorciatoia("Note") { startActivity(Intent(this, NoteActivity::class.java)) })
        l.add(Scorciatoia("File") { startActivity(Intent(this, FileActivity::class.java)) })
        l.add(Scorciatoia("Cassaforte") { startActivity(Intent(this, CassaforteActivity::class.java)) })
        l.add(Scorciatoia("Impostazioni") { startActivity(Intent(this, ImpostazioniActivity::class.java)) })
        l.addAll(scorciatoieAssistenti())
        return l
    }

    private fun tocchiCasa() {
        memoria().edit().putBoolean("casa_auto", true).apply()
        aggiornaCasa()
        apriFully()
    }

    companion object {
        private const val FONDO = 0xFF0B1F33.toInt()       // blu notte del computer
        private const val BARRA = 0xB30B1F33.toInt()
        private const val TESTO = 0xFFE8F1F8.toInt()
        private const val ORO = 0xFFFFD479.toInt()
        private const val ORO_SCURO = 0xFFE0A93C.toInt()
        private const val VERDE = 0xFF6FE0B0.toInt()
        private const val GRIGIO = 0xFF7D8DA0.toInt()
        private const val GRIGIO_SCURO = 0xFF566577.toInt()
        private const val ORO_FILE = 0xFFF2C26B.toInt()
        private const val ORO_FILE_SCURO = 0xFFC98A2B.toInt()
        private const val TURCHESE = 0xFF3FC1C9.toInt()
        private const val TURCHESE_SCURO = 0xFF1D7F8C.toInt()
        private const val ROSA = 0xFFFF8FB8.toInt()
        private const val ROSA_SCURO = 0xFFD6457F.toInt()
        private const val MARE = 0xFF3A86B8.toInt()
        private const val MARE_SCURO = 0xFF1B4F7A.toInt()
    }
}
