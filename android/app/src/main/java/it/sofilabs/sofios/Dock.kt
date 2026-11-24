package it.sofilabs.sofios

import android.app.Activity
import android.app.AlertDialog
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager

/**
 * Le app che l'utente mette nel Dock (la barra in basso della schermata iniziale), oltre alle sei di SofiOS.
 * Stessi testi del computer: «Metti nel Dock», «Togli dal Dock», «Vuoi metterla nel Dock?».
 * Il Dock ha un numero massimo di icone (dipende dalla larghezza dello schermo): se è pieno, l'utente sceglie quale togliere.
 */
object Dock {
    private const val FISSE = 6      // Casa, Impostazioni, Note, File, Cassaforte, Luma
    private const val LARGHEZZA_DP = 92
    private const val CHIAVE = "dock_app"
    private const val VISTE = "app_viste"

    private fun m(c: Context) = c.getSharedPreferences("sofios", Context.MODE_PRIVATE)

    fun fissate(c: Context): List<String> =
        (m(c).getString(CHIAVE, "") ?: "").split("\n").filter { it.isNotBlank() }

    private fun salva(c: Context, l: List<String>) { m(c).edit().putString(CHIAVE, l.joinToString("\n")).apply() }

    fun inDock(c: Context, pacchetto: String) = pacchetto in fissate(c)

    /** Quante app si possono aggiungere alle sei di SofiOS, in base alla larghezza dello schermo. */
    fun capienza(c: Context): Int {
        val dm = c.resources.displayMetrics
        val larghezzaDp = dm.widthPixels / dm.density
        return maxOf(0, ((larghezzaDp - 48) / LARGHEZZA_DP).toInt() - FISSE)
    }

    fun togli(c: Context, pacchetto: String) = salva(c, fissate(c) - pacchetto)

    /** Aggiunge l'app; ritorna falso se il Dock è pieno. */
    fun fissa(c: Context, pacchetto: String): Boolean {
        val l = fissate(c)
        if (pacchetto in l) return true
        if (l.size >= capienza(c)) return false
        salva(c, l + pacchetto); return true
    }

    private fun nome(c: Context, pacchetto: String): String = try {
        val pm = c.packageManager; pm.getApplicationInfo(pacchetto, 0).loadLabel(pm).toString()
    } catch (e: PackageManager.NameNotFoundException) { pacchetto }

    /** Le app fissate che sono ancora installate (le altre si ignorano). */
    fun daMostrare(c: Context): List<String> =
        fissate(c).filter { c.packageManager.getLaunchIntentForPackage(it) != null }.take(capienza(c))

    /**
     * Mette l'app nel Dock. Se è pieno chiede quale togliere al suo posto. `dopo` viene chiamato quando il Dock è cambiato.
     */
    fun fissaConScelta(a: Activity, pacchetto: String, dopo: () -> Unit) {
        if (capienza(a) == 0) {
            AlertDialog.Builder(a, android.R.style.Theme_DeviceDefault_Dialog_Alert)
                .setTitle("Dock").setMessage("Su questo schermo non c'è spazio per altre app nel Dock.")
                .setPositiveButton("Ok", null).show().getButton(android.content.DialogInterface.BUTTON_POSITIVE).isAllCaps = false
            return
        }
        if (fissa(a, pacchetto)) { dopo(); return }
        val attuali = fissate(a)
        val nomi = attuali.map { nome(a, it) }.toTypedArray()
        AlertDialog.Builder(a, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle("Il Dock è pieno. Quale vuoi togliere?")
            .setItems(nomi) { _, k ->
                togli(a, attuali[k]); fissa(a, pacchetto); dopo()
            }
            .setNegativeButton("Annulla", null)
            .show().getButton(android.content.DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
    }

    // ---- app nuove: «Vuoi metterla nel Dock?» ----

    private fun installate(c: Context): Set<String> {
        val pm = c.packageManager
        return pm.queryIntentActivities(Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER), 0)
            .map { it.activityInfo.packageName }.filter { it != c.packageName }.toSet()
    }

    /**
     * Confronta le app di adesso con quelle già viste: per ogni app nuova chiede una volta «Vuoi metterla nel Dock?».
     * La prima volta in assoluto si limita a ricordare quelle che ci sono già.
     */
    fun chiediPerLeNuove(a: Activity, dopo: () -> Unit) {
        val ora = installate(a)
        val viste = m(a).getStringSet(VISTE, null)
        if (viste == null) { m(a).edit().putStringSet(VISTE, ora).apply(); return }
        m(a).edit().putStringSet(VISTE, ora).apply()   // chi è stato disinstallato sparisce: se torna, si richiede
        val nuove = (ora - viste).sorted()
        if (nuove.isEmpty() || capienza(a) == 0) return
        val p = nuove.first()
        val d = AlertDialog.Builder(a, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle(nome(a, p)).setMessage("Vuoi metterla nel Dock?")
            .setPositiveButton("Sì") { _, _ -> fissaConScelta(a, p, dopo) }
            .setNegativeButton("No", null)
            .show()
        d.getButton(android.content.DialogInterface.BUTTON_POSITIVE).isAllCaps = false
        d.getButton(android.content.DialogInterface.BUTTON_NEGATIVE).isAllCaps = false
    }
}
