package it.sofilabs.sofios.assistente

import android.content.Context
import it.sofilabs.sofios.R

/** Un assistente online: si apre nel browser, con internet e il proprio account; l'app ufficiale è facoltativa (Play Store). */
class Assistente(val id: String, val nome: String, val indirizzo: String, val icona: Int, val chiaro: Int, val scuro: Int,
                 /** Nome dell'app ufficiale su Android (da controllare sul Play Store prima della pubblicazione). */
                 val pacchetto: String)

object Assistenti {
    val tutti = listOf(
        Assistente("claude", "Claude", "https://claude.ai", R.drawable.ic_ass_claude, 0xFFFFD479.toInt(), 0xFFE8A33A.toInt(), "com.anthropic.claude"),
        Assistente("chatgpt", "ChatGPT", "https://chatgpt.com", R.drawable.ic_ass_chatgpt, 0xFF8BE37A.toInt(), 0xFF2E9E4F.toInt(), "com.openai.chatgpt"),
        Assistente("gemini", "Gemini", "https://gemini.google.com", R.drawable.ic_ass_gemini, 0xFFC9A2FF.toInt(), 0xFF6B3FD1.toInt(), "com.google.android.apps.bard"),
        Assistente("copilot", "Copilot", "https://copilot.microsoft.com", R.drawable.ic_ass_copilot, 0xFF6FB3FF.toInt(), 0xFF2B6FD6.toInt(), "com.microsoft.copilot"),
        Assistente("deepseek", "DeepSeek", "https://chat.deepseek.com", R.drawable.ic_ass_deepseek, 0xFF7CD4FF.toInt(), 0xFF2A8FD0.toInt(), "com.deepseek.chat"),
        Assistente("mistral", "Le Chat", "https://chat.mistral.ai", R.drawable.ic_ass_mistral, 0xFFFF8A80.toInt(), 0xFFD6453A.toInt(), "ai.mistral.chat"),
        Assistente("perplexity", "Perplexity", "https://www.perplexity.ai", R.drawable.ic_ass_perplexity, 0xFF3FC1C9.toInt(), 0xFF1D7F8C.toInt(), "ai.perplexity.app.android"),
    )

    /**
     * Icona originale dell'assistente, se il file `ass_<id>.png` (o .webp) è nella cartella delle immagini dell'app.
     * Se non c'è, si usa l'icona nostra (la stessa del computer).
     */
    fun iconaOriginale(c: Context, a: Assistente): android.graphics.drawable.Drawable? {
        val id = c.resources.getIdentifier("ass_" + a.id, "drawable", c.packageName)
        return if (id != 0) c.resources.getDrawable(id, c.theme) else null
    }

    fun appInstallata(c: Context, a: Assistente) = c.packageManager.getLaunchIntentForPackage(a.pacchetto) != null

    /** Apre l'app ufficiale se è installata, altrimenti il sito nel browser. */
    fun apri(c: Context, a: Assistente) {
        val app = c.packageManager.getLaunchIntentForPackage(a.pacchetto)
        try {
            if (app != null) c.startActivity(app)
            else c.startActivity(android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse(a.indirizzo)).addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK))
        } catch (e: android.content.ActivityNotFoundException) { }
    }

    /** Porta alla pagina dell'app sul Play Store (o, senza Play Store, a quella di F-Droid/web); Android chiede lui la conferma. */
    fun installa(c: Context, a: Assistente) {
        try { c.startActivity(android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse("market://details?id=" + a.pacchetto)).addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)) }
        catch (e: android.content.ActivityNotFoundException) {
            try { c.startActivity(android.content.Intent(android.content.Intent.ACTION_VIEW, android.net.Uri.parse("https://play.google.com/store/apps/details?id=" + a.pacchetto)).addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)) }
            catch (e2: android.content.ActivityNotFoundException) { }
        }
    }

    private fun memoria(c: Context) = c.getSharedPreferences("sofios", Context.MODE_PRIVATE)

    fun scelti(c: Context): List<Assistente> {
        val ids = memoria(c).getStringSet("assistenti", emptySet()) ?: emptySet()
        return tutti.filter { it.id in ids }
    }

    fun imposta(c: Context, id: String, acceso: Boolean) {
        val m = memoria(c)
        val ids = HashSet(m.getStringSet("assistenti", emptySet()) ?: emptySet())
        if (acceso) ids.add(id) else ids.remove(id)
        m.edit().putStringSet("assistenti", ids).apply()
    }
}
