package it.sofilabs.sofios.assistente

import android.content.Context
import it.sofilabs.sofios.R

/** Un assistente online: si apre nel browser, con internet e il proprio account. Non si scarica niente. */
class Assistente(val id: String, val nome: String, val indirizzo: String, val icona: Int, val chiaro: Int, val scuro: Int)

object Assistenti {
    val tutti = listOf(
        Assistente("claude", "Claude", "https://claude.ai", R.drawable.ic_ass_claude, 0xFFFFD479.toInt(), 0xFFE8A33A.toInt()),
        Assistente("chatgpt", "ChatGPT", "https://chatgpt.com", R.drawable.ic_ass_chatgpt, 0xFF8BE37A.toInt(), 0xFF2E9E4F.toInt()),
        Assistente("gemini", "Gemini", "https://gemini.google.com", R.drawable.ic_ass_gemini, 0xFFC9A2FF.toInt(), 0xFF6B3FD1.toInt()),
        Assistente("copilot", "Copilot", "https://copilot.microsoft.com", R.drawable.ic_ass_copilot, 0xFF6FB3FF.toInt(), 0xFF2B6FD6.toInt()),
        Assistente("deepseek", "DeepSeek", "https://chat.deepseek.com", R.drawable.ic_ass_deepseek, 0xFF7CD4FF.toInt(), 0xFF2A8FD0.toInt()),
        Assistente("mistral", "Le Chat", "https://chat.mistral.ai", R.drawable.ic_ass_mistral, 0xFFFF8A80.toInt(), 0xFFD6453A.toInt()),
        Assistente("perplexity", "Perplexity", "https://www.perplexity.ai", R.drawable.ic_ass_perplexity, 0xFF3FC1C9.toInt(), 0xFF1D7F8C.toInt()),
    )

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
