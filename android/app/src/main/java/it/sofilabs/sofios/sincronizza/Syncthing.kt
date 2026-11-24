package it.sofilabs.sofios.sincronizza

import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.security.cert.X509Certificate
import javax.net.ssl.HostnameVerifier
import javax.net.ssl.HttpsURLConnection
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

class ErroreSincronizza(val codice: Int, messaggio: String) : IOException(messaggio)

/**
 * Parla con l'app di sincronizzazione (Syncthing-Fork) che gira sullo STESSO tablet.
 *
 * LIMITE (scritto qui e in docs/ECOSISTEMA.md): questo programma si collega SOLTANTO a 127.0.0.1, cioè al tablet stesso.
 * Qualsiasi altro indirizzo viene rifiutato prima di aprire la connessione. Niente telemetria, niente altri server.
 * Il permesso «internet» di Android serve solo per questo dialogo interno.
 *
 * Il certificato dell'app di sincronizzazione è autofirmato: viene accettato solo perché l'indirizzo è sempre 127.0.0.1.
 */
class Syncthing(private val porta: Int, private val chiave: String, private val provaHttps: Boolean = true) {

    companion object {
        const val HOST = "127.0.0.1"

        /** Vero solo per indirizzi che puntano al tablet stesso (http o https, host 127.0.0.1). */
        fun indirizzoPermesso(indirizzo: String): Boolean = try {
            val u = URL(indirizzo)
            (u.protocol == "http" || u.protocol == "https") && u.host == HOST && u.userInfo == null
        } catch (e: Exception) { false }

        private val fidaDiTutti = arrayOf<TrustManager>(object : X509TrustManager {
            override fun checkClientTrusted(c: Array<X509Certificate>?, t: String?) {}
            override fun checkServerTrusted(c: Array<X509Certificate>?, t: String?) {}
            override fun getAcceptedIssuers(): Array<X509Certificate> = emptyArray()
        })
    }

    private var schema: String? = null

    private fun indirizzo(schema: String, percorso: String) = "$schema://$HOST:$porta/rest/$percorso"

    private fun apri(schema: String, percorso: String): HttpURLConnection {
        val url = indirizzo(schema, percorso)
        check(indirizzoPermesso(url)) { "Indirizzo non permesso: solo 127.0.0.1" }
        val c = URL(url).openConnection() as HttpURLConnection
        if (c is HttpsURLConnection) {
            val ctx = SSLContext.getInstance("TLS"); ctx.init(null, fidaDiTutti, null)
            c.sslSocketFactory = ctx.socketFactory
            c.hostnameVerifier = HostnameVerifier { host, _ -> host == HOST }
        }
        c.connectTimeout = 4000; c.readTimeout = 8000
        c.setRequestProperty("X-API-Key", chiave)
        return c
    }

    /** Una richiesta alle API. Ritorna il JSON letto (Map, List, ecc.) oppure null se la risposta è vuota. */
    fun chiama(metodo: String, percorso: String, corpo: Any? = null): Any? {
        val ordine = schema?.let { listOf(it) } ?: if (provaHttps) listOf("https", "http") else listOf("http")
        var ultimo: IOException? = null
        for (s in ordine) {
            try {
                val c = apri(s, percorso)
                c.requestMethod = metodo
                if (corpo != null) {
                    c.doOutput = true; c.setRequestProperty("Content-Type", "application/json")
                    c.outputStream.use { it.write(Json.scrivi(corpo).toByteArray()) }
                }
                val codice = c.responseCode
                if (codice >= 400) {
                    val m = try { (c.errorStream ?: c.inputStream).readBytes().decodeToString() } catch (e: IOException) { "" }
                    throw ErroreSincronizza(codice, "HTTP $codice: ${m.take(200)}")
                }
                val t = c.inputStream.use { it.readBytes().decodeToString() }
                schema = s
                return if (t.isBlank()) null else Json.leggi(t)
            } catch (e: ErroreSincronizza) { schema = s; throw e
            } catch (e: IOException) { ultimo = e }
        }
        throw ultimo ?: IOException("nessuna risposta")
    }

    fun leggi(percorso: String) = chiama("GET", percorso)
    fun metti(percorso: String, corpo: Any?) = chiama("PUT", percorso, corpo)
    fun cancella(percorso: String) = chiama("DELETE", percorso)
}
