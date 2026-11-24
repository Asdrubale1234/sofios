package it.sofilabs.sofios.sincronizza

/**
 * Un piccolo lettore/scrittore di JSON, per non usare librerie e per poterlo provare anche fuori da Android.
 * Valori: Map<String, Any?>, List<Any?>, String, Double, Boolean, null.
 */
object Json {
    fun leggi(testo: String): Any? {
        val p = Lettore(testo); p.spazi()
        val v = p.valore(); p.spazi()
        if (!p.fine()) throw IllegalArgumentException("JSON: resto dopo la fine, posizione ${p.i}")
        return v
    }

    @Suppress("UNCHECKED_CAST")
    fun oggetto(testo: String): Map<String, Any?> = leggi(testo) as? Map<String, Any?> ?: throw IllegalArgumentException("JSON: non è un oggetto")
    @Suppress("UNCHECKED_CAST")
    fun lista(testo: String): List<Any?> = leggi(testo) as? List<Any?> ?: throw IllegalArgumentException("JSON: non è una lista")

    fun scrivi(v: Any?): String = StringBuilder().also { scrivi(v, it) }.toString()

    private fun scrivi(v: Any?, o: StringBuilder) {
        when (v) {
            null -> o.append("null")
            is Boolean -> o.append(v.toString())
            is Int, is Long -> o.append(v.toString())
            is Number -> o.append(if (v.toDouble() == Math.floor(v.toDouble()) && Math.abs(v.toDouble()) < 1e15) v.toLong().toString() else v.toString())
            is String -> testo(v, o)
            is Map<*, *> -> {
                o.append('{'); var primo = true
                for ((k, x) in v) { if (!primo) o.append(','); primo = false; testo(k.toString(), o); o.append(':'); scrivi(x, o) }
                o.append('}')
            }
            is List<*> -> { o.append('['); v.forEachIndexed { n, x -> if (n > 0) o.append(','); scrivi(x, o) }; o.append(']') }
            else -> testo(v.toString(), o)
        }
    }

    private fun testo(s: String, o: StringBuilder) {
        o.append('"')
        for (c in s) when {
            c == '"' -> o.append("\\\"")
            c == '\\' -> o.append("\\\\")
            c == '\n' -> o.append("\\n")
            c == '\r' -> o.append("\\r")
            c == '\t' -> o.append("\\t")
            c < ' ' -> o.append(String.format("\\u%04x", c.code))
            else -> o.append(c)
        }
        o.append('"')
    }

    private class Lettore(val s: String) {
        var i = 0
        fun fine() = i >= s.length
        fun spazi() { while (i < s.length && s[i].isWhitespace()) i++ }
        fun errore(m: String): Nothing = throw IllegalArgumentException("JSON: $m, posizione $i")

        fun valore(): Any? {
            spazi()
            if (fine()) errore("fine inattesa")
            return when (val c = s[i]) {
                '{' -> oggetto()
                '[' -> lista()
                '"' -> stringa()
                't' -> parola("true", true)
                'f' -> parola("false", false)
                'n' -> parola("null", null)
                else -> if (c == '-' || c.isDigit()) numero() else errore("carattere inatteso «$c»")
            }
        }

        fun parola(p: String, v: Any?): Any? { if (!s.startsWith(p, i)) errore("atteso $p"); i += p.length; return v }

        fun numero(): Double {
            val inizio = i
            if (s[i] == '-') i++
            while (i < s.length && (s[i].isDigit() || s[i] in ".eE+-")) i++
            return s.substring(inizio, i).toDoubleOrNull() ?: errore("numero non valido")
        }

        fun stringa(): String {
            i++ // "
            val o = StringBuilder()
            while (true) {
                if (fine()) errore("stringa non chiusa")
                val c = s[i++]
                when (c) {
                    '"' -> return o.toString()
                    '\\' -> {
                        if (fine()) errore("escape incompleto")
                        when (val e = s[i++]) {
                            'n' -> o.append('\n'); 'r' -> o.append('\r'); 't' -> o.append('\t')
                            'b' -> o.append('\b'); 'f' -> o.append('\u000c')
                            '/', '\\', '"' -> o.append(e)
                            'u' -> {
                                if (i + 4 > s.length) errore("\\u incompleto")
                                o.append(s.substring(i, i + 4).toIntOrNull(16)?.toChar() ?: errore("\\u non valido")); i += 4
                            }
                            else -> errore("escape sconosciuto")
                        }
                    }
                    else -> o.append(c)
                }
            }
        }

        fun lista(): List<Any?> {
            i++; val l = ArrayList<Any?>(); spazi()
            if (i < s.length && s[i] == ']') { i++; return l }
            while (true) {
                l.add(valore()); spazi()
                if (fine()) errore("lista non chiusa")
                when (s[i++]) { ',' -> continue; ']' -> return l; else -> errore("atteso , o ]") }
            }
        }

        fun oggetto(): Map<String, Any?> {
            i++; val m = LinkedHashMap<String, Any?>(); spazi()
            if (i < s.length && s[i] == '}') { i++; return m }
            while (true) {
                spazi(); if (fine() || s[i] != '"') errore("attesa una chiave")
                val k = stringa(); spazi()
                if (fine() || s[i++] != ':') errore("atteso :")
                m[k] = valore(); spazi()
                if (fine()) errore("oggetto non chiuso")
                when (s[i++]) { ',' -> continue; '}' -> return m; else -> errore("atteso , o }") }
            }
        }
    }
}
