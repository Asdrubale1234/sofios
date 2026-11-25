package it.sofilabs.sofios

import android.app.Activity
import android.app.AlertDialog
import android.content.Context
import android.graphics.Typeface
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import it.sofilabs.sofios.sincronizza.Json

/**
 * «Novità dopo ogni aggiornamento»: al primo avvio dopo un aggiornamento compare una schermata con le novità, poi non riappare.
 * Ogni versione porta un file `assets/novita/<versionCode>.json` (titolo, sottotitolo, posa di Luma, voci con titolo e testo).
 * Chiuderla in qualunque modo vale come «vista». Nessuna schermata alla prima installazione (c'è già il benvenuto).
 */
object Novita {
    class Voce(val titolo: String, val testo: String)
    class Versione(val numero: Int, val titolo: String, val sottotitolo: String, val posa: String, val voci: List<Voce>)

    private const val VISTA = "novita_vista"

    /** Le versioni da mostrare: dalla più nuova, tra quella dopo l'ultima vista e quella attuale, per cui esiste il file. */
    fun arretrate(vista: Int, corrente: Int, esiste: (Int) -> Boolean): List<Int> =
        (corrente downTo vista + 1).filter(esiste)

    fun leggi(c: Context, numero: Int): Versione? = try {
        val t = c.assets.open("novita/$numero.json").use { it.readBytes().decodeToString() }
        val o = Json.oggetto(t)
        @Suppress("UNCHECKED_CAST")
        val voci = (o["voci"] as? List<Map<String, Any?>> ?: emptyList()).map { Voce(it["titolo"] as? String ?: "", it["testo"] as? String ?: "") }
        Versione(numero, o["titolo"] as? String ?: "Novità", o["sottotitolo"] as? String ?: "", o["posa"] as? String ?: "festa", voci)
    } catch (e: Exception) { null }

    private fun versioneAttuale(c: Context): Int = try {
        @Suppress("DEPRECATION")
        c.packageManager.getPackageInfo(c.packageName, 0).versionCode
    } catch (e: Exception) { 1 }

    private fun esiste(c: Context, n: Int) = try { c.assets.open("novita/$n.json").close(); true } catch (e: Exception) { false }

    private fun memoria(c: Context) = c.getSharedPreferences("sofios", Context.MODE_PRIVATE)

    /** Le novità ancora da vedere. Alla prima installazione ricorda la versione attuale e non mostra niente. */
    fun daVedere(c: Context): List<Versione> {
        val corrente = versioneAttuale(c)
        val m = memoria(c)
        if (!m.contains(VISTA)) {
            // prima installazione (c'è il benvenuto): si segna la versione e basta; chi aggiorna da una versione senza questa funzione vede le novità
            val aggiornamento = m.getBoolean("benvenuto_visto", false)
            m.edit().putInt(VISTA, if (aggiornamento) 1 else corrente).apply()
            if (!aggiornamento) return emptyList()
        }
        val vista = m.getInt(VISTA, corrente)
        return arretrate(vista, corrente) { esiste(c, it) }.mapNotNull { leggi(c, it) }
    }

    /** Tutte le novità disponibili, dalla più recente (per rivederle quando si vuole). */
    fun tutte(c: Context): List<Versione> =
        (versioneAttuale(c) downTo 1).filter { esiste(c, it) }.mapNotNull { leggi(c, it) }

    private fun segnaVista(c: Context) { memoria(c).edit().putInt(VISTA, versioneAttuale(c)).apply() }

    /** Mostra la schermata con le novità: Luma («festa») in alto se non è nascosta, le voci come schede, «Ho capito». */
    fun mostra(a: Activity, versioni: List<Versione>, dopo: () -> Unit) {
        if (versioni.isEmpty()) { dopo(); return }
        val colonna = LinearLayout(a).apply { orientation = LinearLayout.VERTICAL; setPadding(Stile.dp(a, 20), Stile.dp(a, 8), Stile.dp(a, 20), Stile.dp(a, 8)) }
        Stile.luma(a, versioni[0].posa)?.let { colonna.addView(it) }
        for ((k, v) in versioni.withIndex()) {
            colonna.addView(TextView(a).apply {
                text = v.titolo; textSize = 22f; typeface = Typeface.DEFAULT_BOLD; setTextColor(0xFFF2F2F7.toInt()); gravity = Gravity.CENTER
                setPadding(0, Stile.dp(a, if (k == 0) 12 else 24), 0, Stile.dp(a, 2))
            })
            if (v.sottotitolo.isNotEmpty()) colonna.addView(TextView(a).apply {
                text = v.sottotitolo; textSize = 14f; setTextColor(0xFF8E8E93.toInt()); gravity = Gravity.CENTER; setPadding(0, 0, 0, Stile.dp(a, 8))
            })
            for (voce in v.voci) {
                val scheda = LinearLayout(a).apply {
                    orientation = LinearLayout.VERTICAL; setPadding(Stile.dp(a, 16), Stile.dp(a, 12), Stile.dp(a, 16), Stile.dp(a, 12))
                    background = android.graphics.drawable.GradientDrawable().apply { setColor(0xFF3A3A3C.toInt()); cornerRadius = Stile.dp(a, 14).toFloat() }
                }
                scheda.addView(TextView(a).apply { text = voce.titolo; textSize = 16f; typeface = Typeface.DEFAULT_BOLD; setTextColor(0xFFF2F2F7.toInt()) })
                scheda.addView(TextView(a).apply { text = voce.testo; textSize = 14f; setTextColor(0xFFC7C7CC.toInt()); setPadding(0, Stile.dp(a, 4), 0, 0) })
                colonna.addView(scheda, LinearLayout.LayoutParams(-1, -2).apply { topMargin = Stile.dp(a, 8) })
            }
        }
        val d = AlertDialog.Builder(a, android.R.style.Theme_DeviceDefault_Dialog_Alert).setView(ScrollView(a).apply { addView(colonna) }).create()
        colonna.addView(Stile.bottone(a, "Ho capito", Stile.ORO, Stile.SU_ORO) { d.dismiss() },
            LinearLayout.LayoutParams(-1, Stile.dp(a, 48)).apply { topMargin = Stile.dp(a, 16) })
        d.setOnDismissListener { segnaVista(a); dopo() }   // pulsante, indietro o tocco fuori: è comunque «vista»
        d.show()
    }
}
