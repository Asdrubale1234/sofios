package it.sofilabs.sofios

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.Settings
import java.io.File

/**
 * La Cartella SofiOS: un'unica cartella con `Note`, `Password`, `Foto` e `File`, uguale su tutti i dispositivi
 * (sul computer sarà la stessa). Con il permesso «accesso ai file» sta nella memoria del tablet, dove la raggiungono
 * anche gli altri programmi (per la sincronizzazione). Senza permesso resta privata dentro l'app.
 */
object Cartella {

    fun permesso(c: Context): Boolean =
        if (Build.VERSION.SDK_INT >= 30) Environment.isExternalStorageManager()
        else c.checkSelfPermission("android.permission.WRITE_EXTERNAL_STORAGE") == PackageManager.PERMISSION_GRANTED

    /** Pagina di Android dove si concede l'accesso ai file. */
    fun richiestaPermesso(c: Context): Intent =
        if (Build.VERSION.SDK_INT >= 30)
            Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, Uri.parse("package:" + c.packageName))
        else Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + c.packageName))

    private fun privata(c: Context) = File(c.getExternalFilesDir(null) ?: c.filesDir, "SofiOS")

    @Suppress("DEPRECATION")
    private fun condivisa() = File(Environment.getExternalStorageDirectory(), "SofiOS")

    /** La cartella di lavoro di adesso (condivisa se c'è il permesso, privata altrimenti); le copie dei file vecchi si fanno una volta. */
    fun radice(c: Context): File {
        val r = if (permesso(c)) condivisa() else privata(c)
        r.mkdirs()
        migra(c, r)
        for (n in listOf("Note", "Password", "Foto", "File")) File(r, n).mkdirs()
        return r
    }

    fun note(c: Context) = File(radice(c), "Note")
    fun password(c: Context) = File(radice(c), "Password")

    /** Copia (senza mai cancellare né sovrascrivere) i file delle versioni precedenti nella cartella di lavoro. */
    private fun migra(c: Context, destinazione: File) {
        val memoria = c.getSharedPreferences("sofios", Context.MODE_PRIVATE)
        val chiave = "migrato:" + destinazione.path
        if (memoria.getBoolean(chiave, false)) return
        try {
            // versione 0.1: note e cassaforte nella cartella privata dell'app
            copiaSeMancano(File(c.filesDir, "Note"), File(destinazione, "Note"))
            copiaSeMancano(File(c.filesDir, "Password"), File(destinazione, "Password"))
            // cartella privata «SofiOS» (File e schermate di prima)
            val p = privata(c)
            if (p.path != destinazione.path) copiaSeMancano(p, destinazione)
            memoria.edit().putBoolean(chiave, true).apply()
        } catch (e: java.io.IOException) { /* si riprova la prossima volta */ }
    }

    /** Copia ricorsivamente `da` in `a`, saltando i file che esistono già. Ritorna quanti file ha copiato. */
    fun copiaSeMancano(da: File, a: File): Int {
        if (!da.exists()) return 0
        var n = 0
        if (da.isDirectory) {
            a.mkdirs()
            for (f in da.listFiles() ?: emptyArray()) n += copiaSeMancano(f, File(a, f.name))
        } else if (!a.exists() && !da.name.endsWith(".tmp")) {
            a.parentFile?.mkdirs()
            da.copyTo(a)
            n++
        }
        return n
    }
}
