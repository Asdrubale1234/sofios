package it.sofilabs.sofios.cassaforte

import org.w3c.dom.Document
import org.w3c.dom.Element
import org.w3c.dom.Node
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.StringWriter
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest
import java.security.SecureRandom
import java.util.Base64
import java.util.zip.GZIPInputStream
import java.util.zip.GZIPOutputStream
import javax.crypto.Cipher
import javax.crypto.Mac
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec
import javax.xml.parsers.DocumentBuilderFactory
import javax.xml.transform.OutputKeys
import javax.xml.transform.TransformerFactory
import javax.xml.transform.dom.DOMSource
import javax.xml.transform.stream.StreamResult

class PasswordSbagliata : Exception("Password sbagliata")
class FileDanneggiato(motivo: String) : Exception(motivo)
class FormatoNonSupportato(motivo: String) : Exception(motivo)

/** Una voce della cassaforte. */
class Voce(
    val id: String, var titolo: String, var utente: String, var password: String,
    var sito: String, var note: String,
)

/**
 * Cassaforte nel formato KeePass 4 (.kdbx), lo stesso della Cassaforte Password del computer.
 * La cifratura usa solo i componenti standard di Android (AES, SHA, HMAC) più Argon2 e ChaCha20 qui accanto.
 */
class Kdbx private constructor(
    private val doc: Document,
    private val cifrario: ByteArray,
    private val compressione: Int,
    private val campiKdf: LinkedHashMap<String, Pair<Int, ByteArray>>,
    private val altriCampi: List<Pair<Int, ByteArray>>,
    private val binari: List<ByteArray>,
    private val versione: ByteArray,
    private var chiaveTrasformata: ByteArray,
) {
    private val casuale = SecureRandom()

    // ---------- voci ----------

    private fun radice(): Element =
        (doc.documentElement.getElementsByTagName("Root").item(0) as Element)
            .let { r -> figli(r, "Group").first() }

    private fun figli(e: Element, nome: String): List<Element> {
        val l = ArrayList<Element>()
        var n: Node? = e.firstChild
        while (n != null) { if (n is Element && n.tagName == nome) l.add(n); n = n.nextSibling }
        return l
    }

    private fun testoFiglio(e: Element, nome: String): String = figli(e, nome).firstOrNull()?.textContent ?: ""

    private fun idCestino(): String {
        val m = doc.documentElement.getElementsByTagName("RecycleBinUUID").item(0) as? Element
        return m?.textContent ?: ""
    }

    private fun tutteLeEntry(): List<Element> {
        val cestino = idCestino()
        val risultato = ArrayList<Element>()
        fun gruppo(g: Element) {
            if (cestino.isNotEmpty() && cestino != ZERO_UUID && testoFiglio(g, "UUID") == cestino) return
            for (e in figli(g, "Entry")) risultato.add(e)
            for (s in figli(g, "Group")) gruppo(s)
        }
        gruppo(radice())
        return risultato
    }

    private fun campo(entry: Element, chiave: String): String {
        for (s in figli(entry, "String")) {
            if (testoFiglio(s, "Key") == chiave) return figli(s, "Value").firstOrNull()?.textContent ?: ""
        }
        return ""
    }

    private fun impostaCampo(entry: Element, chiave: String, valore: String, protetto: Boolean = false) {
        var stringa = figli(entry, "String").firstOrNull { testoFiglio(it, "Key") == chiave }
        if (stringa == null) {
            stringa = doc.createElement("String")
            val k = doc.createElement("Key"); k.textContent = chiave; stringa.appendChild(k)
            stringa.appendChild(doc.createElement("Value"))
            // le stringhe vanno prima di AutoType/History
            val dopo = figli(entry, "AutoType").firstOrNull() ?: figli(entry, "History").firstOrNull()
            if (dopo != null) entry.insertBefore(stringa, dopo) else entry.appendChild(stringa)
        }
        val v = figli(stringa, "Value").first()
        v.textContent = valore
        if (protetto) v.setAttribute("Protected", "True")
    }

    fun voci(): List<Voce> = tutteLeEntry().map { e ->
        Voce(testoFiglio(e, "UUID"), campo(e, "Title"), campo(e, "UserName"), campo(e, "Password"),
            campo(e, "URL"), campo(e, "Notes"))
    }

    fun aggiungi(titolo: String, utente: String, password: String, sito: String, note: String): String {
        val e = doc.createElement("Entry")
        val id = nuovoUuid()
        val u = doc.createElement("UUID"); u.textContent = id; e.appendChild(u)
        val ic = doc.createElement("IconID"); ic.textContent = "0"; e.appendChild(ic)
        e.appendChild(tempi())
        e.appendChild(doc.createElement("History"))
        for ((k, v) in listOf("Title" to titolo, "UserName" to utente, "Password" to password, "URL" to sito, "Notes" to note)) {
            impostaCampo(e, k, v, protetto = k == "Password")
        }
        val at = doc.createElement("AutoType")
        val en = doc.createElement("Enabled"); en.textContent = "True"; at.appendChild(en)
        val ob = doc.createElement("DataTransferObfuscation"); ob.textContent = "0"; at.appendChild(ob)
        e.insertBefore(at, figli(e, "History").first())
        radice().appendChild(e)
        return id
    }

    private fun trova(id: String): Element? = tutteLeEntry().firstOrNull { testoFiglio(it, "UUID") == id }

    fun modifica(v: Voce) {
        val e = trova(v.id) ?: return
        // copia di sicurezza della versione precedente nella cronologia (come sul computer)
        val vecchia = e.cloneNode(true) as Element
        figli(vecchia, "History").forEach { vecchia.removeChild(it) }
        val storia = figli(e, "History").firstOrNull() ?: doc.createElement("History").also { e.appendChild(it) }
        storia.appendChild(vecchia)
        impostaCampo(e, "Title", v.titolo); impostaCampo(e, "UserName", v.utente)
        impostaCampo(e, "Password", v.password, protetto = true)
        impostaCampo(e, "URL", v.sito); impostaCampo(e, "Notes", v.note)
        figli(e, "Times").firstOrNull()?.let { t ->
            figli(t, "LastModificationTime").firstOrNull()?.textContent = ora()
        }
    }

    fun elimina(id: String) {
        val e = trova(id) ?: return
        e.parentNode.removeChild(e)
    }

    private fun nuovoUuid(): String {
        val b = ByteArray(16); casuale.nextBytes(b); return Base64.getEncoder().encodeToString(b)
    }

    private fun ora(): String {
        val secondi = System.currentTimeMillis() / 1000 + 62135596800L   // dal 1/1/0001
        return Base64.getEncoder().encodeToString(
            ByteBuffer.allocate(8).order(ByteOrder.LITTLE_ENDIAN).putLong(secondi).array())
    }

    private fun tempi(): Element {
        val t = doc.createElement("Times")
        for (n in listOf("CreationTime", "LastModificationTime", "LastAccessTime", "ExpiryTime")) {
            val x = doc.createElement(n); x.textContent = ora(); t.appendChild(x)
        }
        val s = doc.createElement("Expires"); s.textContent = "False"; t.appendChild(s)
        val u = doc.createElement("UsageCount"); u.textContent = "0"; t.appendChild(u)
        val l = doc.createElement("LocationChanged"); l.textContent = ora(); t.appendChild(l)
        return t
    }

    /** Cancella dalla memoria la chiave (da fare quando la cassaforte si blocca). */
    fun dimentica() { java.util.Arrays.fill(chiaveTrasformata, 0) }

    // ---------- salvataggio ----------

    fun salva(): ByteArray {
        val semeMaestro = ByteArray(32).also { casuale.nextBytes(it) }
        val iv = ByteArray(if (cifrario.contentEquals(CIFRARIO_CHACHA)) 12 else 16).also { casuale.nextBytes(it) }
        val chiaveInterna = ByteArray(64).also { casuale.nextBytes(it) }

        // 1) il testo XML, con le password protette dal flusso interno
        val copia = doc.cloneNode(true) as Document
        val flusso = flussoInterno(chiaveInterna)
        val valori = copia.getElementsByTagName("Value")
        for (i in 0 until valori.length) {
            val v = valori.item(i) as Element
            if (v.getAttribute("Protected").equals("True", ignoreCase = true)) {
                val chiaro = v.textContent.toByteArray(Charsets.UTF_8)
                v.textContent = Base64.getEncoder().encodeToString(flusso.applica(chiaro))
            }
        }
        val xml = serializza(copia)

        // 2) intestazione interna + XML, compressi e cifrati
        val interno = ByteArrayOutputStream()
        interno.write(campoInterno(1, le32(STREAM_CHACHA20)))
        interno.write(campoInterno(2, chiaveInterna))
        for (b in binari) interno.write(campoInterno(3, b))
        interno.write(campoInterno(0, ByteArray(0)))
        interno.write(xml)
        var dati = interno.toByteArray()
        if (compressione == 1) {
            val o = ByteArrayOutputStream()
            GZIPOutputStream(o).use { it.write(dati) }
            dati = o.toByteArray()
        }
        val chiaveCifrario = sha256(semeMaestro, chiaveTrasformata)
        val cifrato = if (cifrario.contentEquals(CIFRARIO_CHACHA)) ChaCha20(chiaveCifrario, iv).applica(dati)
                      else aes(Cipher.ENCRYPT_MODE, chiaveCifrario, iv, dati)

        // 3) intestazione esterna
        val h = ByteArrayOutputStream()
        h.write(SIG1); h.write(SIG2); h.write(versione)
        h.write(campoEsterno(2, cifrario))
        h.write(campoEsterno(3, le32(compressione)))
        h.write(campoEsterno(4, semeMaestro))
        h.write(campoEsterno(7, iv))
        h.write(campoEsterno(11, scriviVariante(campiKdf)))
        for ((id, b) in altriCampi) h.write(campoEsterno(id, b))
        h.write(campoEsterno(0, byteArrayOf(13, 10, 13, 10)))
        val intestazione = h.toByteArray()
        val baseHmac = sha512(semeMaestro, chiaveTrasformata, byteArrayOf(1))

        val fuori = ByteArrayOutputStream()
        fuori.write(intestazione)
        fuori.write(sha256(intestazione))
        fuori.write(hmac(chiaveBlocco(baseHmac, -1L), intestazione))
        var indice = 0L
        var pos = 0
        while (true) {
            val n = minOf(BLOCCO, cifrato.size - pos)
            val blocco = cifrato.copyOfRange(pos, pos + n)
            fuori.write(hmac(chiaveBlocco(baseHmac, indice),
                le64(indice), le32(n), blocco))
            fuori.write(le32(n)); fuori.write(blocco)
            pos += n; indice++
            if (n == 0) break
        }
        return fuori.toByteArray()
    }

    companion object {
        private val SIG1 = byteArrayOf(0x03, 0xD9.toByte(), 0xA2.toByte(), 0x9A.toByte())
        private val SIG2 = byteArrayOf(0x67, 0xFB.toByte(), 0x4B, 0xB5.toByte())
        private const val STREAM_CHACHA20 = 3
        private const val BLOCCO = 1024 * 1024
        private const val ZERO_UUID = "AAAAAAAAAAAAAAAAAAAAAA=="
        private val CIFRARIO_AES = hex("31C1F2E6BF714350BE5805216AFC5AFF")
        private val CIFRARIO_CHACHA = hex("D6038A2B8B6F4CB5A524339A31DBB59A")
        private val KDF_ARGON2D = hex("EF636DDF8C29444B91F7A9A403E30A0C")
        private val KDF_ARGON2ID = hex("9E298B1956DB4773B23DFC3EC6F0A1E6")
        private val KDF_AES = hex("C9D9F39A628A4460BF740D08C18A4FEA")

        // Impostazioni delle nuove cassaforti (più alte = più sicure ma più lente sui tablet modesti).
        const val ARGON_MEMORIA_KIB = 19 * 1024
        const val ARGON_ITERAZIONI = 2
        const val ARGON_PARALLELISMO = 2

        fun hex(s: String) = ByteArray(s.length / 2) { s.substring(it * 2, it * 2 + 2).toInt(16).toByte() }

        private fun le32(v: Int) = ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(v).array()
        private fun le64(v: Long) = ByteBuffer.allocate(8).order(ByteOrder.LITTLE_ENDIAN).putLong(v).array()
        private fun sha256(vararg p: ByteArray) = MessageDigest.getInstance("SHA-256").also { for (x in p) it.update(x) }.digest()
        private fun sha512(vararg p: ByteArray) = MessageDigest.getInstance("SHA-512").also { for (x in p) it.update(x) }.digest()
        private fun hmac(chiave: ByteArray, vararg p: ByteArray): ByteArray {
            val m = Mac.getInstance("HmacSHA256"); m.init(SecretKeySpec(chiave, "HmacSHA256"))
            for (x in p) m.update(x); return m.doFinal()
        }
        private fun chiaveBlocco(baseHmac: ByteArray, indice: Long) = sha512(le64(indice), baseHmac)

        private fun aes(modo: Int, chiave: ByteArray, iv: ByteArray, dati: ByteArray): ByteArray {
            val c = Cipher.getInstance("AES/CBC/PKCS5Padding")
            c.init(modo, SecretKeySpec(chiave, "AES"), IvParameterSpec(iv)); return c.doFinal(dati)
        }

        private fun flussoInterno(chiave: ByteArray): ChaCha20 {
            val h = sha512(chiave)
            return ChaCha20(h.copyOfRange(0, 32), h.copyOfRange(32, 44), 0)
        }

        private fun campoEsterno(id: Int, d: ByteArray) = byteArrayOf(id.toByte()) + le32(d.size) + d
        private fun campoInterno(id: Int, d: ByteArray) = byteArrayOf(id.toByte()) + le32(d.size) + d

        private fun serializza(d: Document): ByteArray {
            val t = TransformerFactory.newInstance().newTransformer()
            t.setOutputProperty(OutputKeys.ENCODING, "utf-8")
            t.setOutputProperty(OutputKeys.INDENT, "no")
            t.setOutputProperty(OutputKeys.STANDALONE, "yes")
            val o = ByteArrayOutputStream()
            t.transform(DOMSource(d), StreamResult(o))
            return o.toByteArray()
        }

        // ---- VariantDictionary (parametri del KDF) ----

        private fun leggiVariante(b: ByteArray): LinkedHashMap<String, Pair<Int, ByteArray>> {
            val buf = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN)
            buf.short                                   // versione
            val m = LinkedHashMap<String, Pair<Int, ByteArray>>()
            while (true) {
                val tipo = buf.get().toInt() and 0xff
                if (tipo == 0) break
                val nome = ByteArray(buf.int).also { buf.get(it) }.toString(Charsets.UTF_8)
                val valore = ByteArray(buf.int).also { buf.get(it) }
                m[nome] = tipo to valore
            }
            return m
        }

        private fun scriviVariante(m: Map<String, Pair<Int, ByteArray>>): ByteArray {
            val o = ByteArrayOutputStream()
            o.write(byteArrayOf(0x00, 0x01))
            for ((nome, tv) in m) {
                o.write(tv.first); val n = nome.toByteArray(Charsets.UTF_8)
                o.write(le32(n.size)); o.write(n); o.write(le32(tv.second.size)); o.write(tv.second)
            }
            o.write(0)
            return o.toByteArray()
        }

        private fun u64(m: Map<String, Pair<Int, ByteArray>>, k: String) =
            ByteBuffer.wrap(m[k]?.second ?: throw FileDanneggiato("parametro mancante")).order(ByteOrder.LITTLE_ENDIAN).long
        private fun u32(m: Map<String, Pair<Int, ByteArray>>, k: String) =
            ByteBuffer.wrap(m[k]?.second ?: throw FileDanneggiato("parametro mancante")).order(ByteOrder.LITTLE_ENDIAN).int

        private fun trasforma(chiaveComposta: ByteArray, kdf: Map<String, Pair<Int, ByteArray>>): ByteArray {
            val id = kdf["\$UUID"]?.second ?: throw FileDanneggiato("KDF mancante")
            val sale = kdf["S"]?.second ?: throw FileDanneggiato("sale mancante")
            return when {
                id.contentEquals(KDF_ARGON2D) || id.contentEquals(KDF_ARGON2ID) -> {
                    if (kdf["V"] != null && u32(kdf, "V") != 0x13) throw FormatoNonSupportato("Versione di Argon2 non supportata")
                    val memoria = u64(kdf, "M") / 1024
                    if (memoria > 256 * 1024) throw FormatoNonSupportato("Memoria troppo grande per questo tablet")
                    Argon2.calcola(chiaveComposta, sale, u64(kdf, "I").toInt(), memoria.toInt(), u32(kdf, "P"), 32,
                        if (id.contentEquals(KDF_ARGON2D)) Argon2.TIPO_D else Argon2.TIPO_ID)
                }
                id.contentEquals(KDF_AES) -> {
                    var k = chiaveComposta.copyOf()
                    val c = Cipher.getInstance("AES/ECB/NoPadding")
                    c.init(Cipher.ENCRYPT_MODE, SecretKeySpec(sale, "AES"))
                    var i = 0L; val giri = u64(kdf, "R")
                    while (i < giri) { k = c.update(k); i++ }
                    sha256(k)
                }
                else -> throw FormatoNonSupportato("Tipo di protezione non supportato")
            }
        }

        private fun chiaveComposta(password: String) = sha256(sha256(password.toByteArray(Charsets.UTF_8)))

        // ---- apertura ----

        fun apri(dati: ByteArray, password: String): Kdbx {
            val b = ByteBuffer.wrap(dati).order(ByteOrder.LITTLE_ENDIAN)
            try {
                if (dati.size < 64 || !dati.copyOfRange(0, 4).contentEquals(SIG1) || !dati.copyOfRange(4, 8).contentEquals(SIG2))
                    throw FileDanneggiato("Non è un file di cassaforte")
                val versione = dati.copyOfRange(8, 12)
                val maggiore = ((versione[3].toInt() and 0xff) shl 8) or (versione[2].toInt() and 0xff)
                if (maggiore != 4) throw FormatoNonSupportato("Versione del file non supportata")
                b.position(12)
                var cifrario = ByteArray(0); var compressione = 0; var seme = ByteArray(0); var iv = ByteArray(0)
                var kdf = LinkedHashMap<String, Pair<Int, ByteArray>>()
                val altri = ArrayList<Pair<Int, ByteArray>>()
                while (true) {
                    val id = b.get().toInt() and 0xff
                    val n = b.int
                    if (n < 0 || n > b.remaining()) throw FileDanneggiato("Intestazione danneggiata")
                    val d = ByteArray(n).also { b.get(it) }
                    when (id) {
                        0 -> break
                        2 -> cifrario = d
                        3 -> compressione = ByteBuffer.wrap(d).order(ByteOrder.LITTLE_ENDIAN).int
                        4 -> seme = d
                        7 -> iv = d
                        11 -> kdf = leggiVariante(d)
                        else -> altri.add(id to d)
                    }
                }
                val finIntestazione = b.position()
                val hashLetto = ByteArray(32).also { b.get(it) }
                val hmacLetto = ByteArray(32).also { b.get(it) }
                if (!sha256(dati.copyOfRange(0, finIntestazione)).contentEquals(hashLetto))
                    throw FileDanneggiato("Intestazione danneggiata")

                val trasformata = trasforma(chiaveComposta(password), kdf)
                val baseHmac = sha512(seme, trasformata, byteArrayOf(1))
                val atteso = hmac(chiaveBlocco(baseHmac, -1L), dati.copyOfRange(0, finIntestazione))
                if (!MessageDigest.isEqual(atteso, hmacLetto)) throw PasswordSbagliata()

                // blocchi
                val cifrato = ByteArrayOutputStream()
                var indice = 0L
                while (true) {
                    val h = ByteArray(32).also { b.get(it) }
                    val n = b.int
                    if (n < 0 || n > b.remaining()) throw FileDanneggiato("Dati danneggiati")
                    val blocco = ByteArray(n).also { b.get(it) }
                    val ok = hmac(chiaveBlocco(baseHmac, indice), le64(indice), le32(n), blocco)
                    if (!MessageDigest.isEqual(ok, h)) throw FileDanneggiato("Dati danneggiati")
                    if (n == 0) break
                    cifrato.write(blocco); indice++
                }
                val chiaveCifrario = sha256(seme, trasformata)
                var chiaro = if (cifrario.contentEquals(CIFRARIO_CHACHA)) ChaCha20(chiaveCifrario, iv).applica(cifrato.toByteArray())
                             else if (cifrario.contentEquals(CIFRARIO_AES)) aes(Cipher.DECRYPT_MODE, chiaveCifrario, iv, cifrato.toByteArray())
                             else throw FormatoNonSupportato("Cifratura non supportata")
                if (compressione == 1) chiaro = GZIPInputStream(ByteArrayInputStream(chiaro)).use { it.readBytes() }

                // intestazione interna
                val ib = ByteBuffer.wrap(chiaro).order(ByteOrder.LITTLE_ENDIAN)
                var tipoFlusso = 0; var chiaveFlusso = ByteArray(0); val binari = ArrayList<ByteArray>()
                while (true) {
                    val id = ib.get().toInt() and 0xff
                    val n = ib.int
                    if (n < 0 || n > ib.remaining()) throw FileDanneggiato("Dati danneggiati")
                    val d = ByteArray(n).also { ib.get(it) }
                    when (id) { 0 -> break; 1 -> tipoFlusso = ByteBuffer.wrap(d).order(ByteOrder.LITTLE_ENDIAN).int
                        2 -> chiaveFlusso = d; 3 -> binari.add(d) }
                }
                if (tipoFlusso != STREAM_CHACHA20) throw FormatoNonSupportato("Protezione interna non supportata")
                val xml = chiaro.copyOfRange(ib.position(), chiaro.size)
                val f = DocumentBuilderFactory.newInstance()
                try { f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true) } catch (e: Exception) { }
                val doc = f.newDocumentBuilder().parse(ByteArrayInputStream(xml))

                val flusso = flussoInterno(chiaveFlusso)
                val valori = doc.getElementsByTagName("Value")
                for (i in 0 until valori.length) {
                    val v = valori.item(i) as Element
                    if (v.getAttribute("Protected").equals("True", ignoreCase = true)) {
                        val cifrata = Base64.getDecoder().decode(v.textContent.trim())
                        v.textContent = String(flusso.applica(cifrata), Charsets.UTF_8)
                    }
                }
                return Kdbx(doc, cifrario, compressione, kdf, altri, binari, versione, trasformata)
            } catch (e: java.nio.BufferUnderflowException) {
                throw FileDanneggiato("File troppo corto")
            } catch (e: java.util.zip.ZipException) {
                throw FileDanneggiato("Dati danneggiati")
            } catch (e: org.xml.sax.SAXException) {
                throw FileDanneggiato("Dati danneggiati")
            } catch (e: java.security.GeneralSecurityException) {
                throw FileDanneggiato("Dati danneggiati")
            }
        }

        // ---- creazione ----

        fun crea(password: String): Kdbx {
            val r = SecureRandom()
            fun casuali(n: Int) = ByteArray(n).also { r.nextBytes(it) }
            val sale = casuali(32)
            val kdf = LinkedHashMap<String, Pair<Int, ByteArray>>()
            kdf["\$UUID"] = 0x42 to KDF_ARGON2D
            kdf["S"] = 0x42 to sale
            kdf["P"] = 0x04 to le32(ARGON_PARALLELISMO)
            kdf["M"] = 0x05 to le64(ARGON_MEMORIA_KIB.toLong() * 1024)
            kdf["I"] = 0x05 to le64(ARGON_ITERAZIONI.toLong())
            kdf["V"] = 0x04 to le32(0x13)
            val trasformata = trasforma(chiaveComposta(password), kdf)

            val doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument()
            val ora = {
                Base64.getEncoder().encodeToString(ByteBuffer.allocate(8).order(ByteOrder.LITTLE_ENDIAN)
                    .putLong(System.currentTimeMillis() / 1000 + 62135596800L).array())
            }
            fun el(genitore: Node, nome: String, testo: String? = null): Element {
                val e = doc.createElement(nome); if (testo != null) e.textContent = testo; genitore.appendChild(e); return e
            }
            val kp = doc.createElement("KeePassFile"); doc.appendChild(kp)
            val meta = el(kp, "Meta")
            el(meta, "Generator", "SofiOS")
            el(meta, "DatabaseName", "Cassaforte"); el(meta, "DatabaseNameChanged", ora())
            el(meta, "DatabaseDescription", ""); el(meta, "DatabaseDescriptionChanged", ora())
            el(meta, "DefaultUserName", ""); el(meta, "DefaultUserNameChanged", ora())
            el(meta, "MaintenanceHistoryDays", "365")
            el(meta, "MasterKeyChanged", ora()); el(meta, "MasterKeyChangeRec", "-1"); el(meta, "MasterKeyChangeForce", "-1")
            val mp = el(meta, "MemoryProtection")
            el(mp, "ProtectTitle", "False"); el(mp, "ProtectUserName", "False"); el(mp, "ProtectPassword", "True")
            el(mp, "ProtectURL", "False"); el(mp, "ProtectNotes", "False")
            el(meta, "RecycleBinEnabled", "False"); el(meta, "RecycleBinUUID", ZERO_UUID); el(meta, "RecycleBinChanged", ora())
            el(meta, "EntryTemplatesGroup", ZERO_UUID); el(meta, "EntryTemplatesGroupChanged", ora())
            el(meta, "LastSelectedGroup", ZERO_UUID); el(meta, "LastTopVisibleGroup", ZERO_UUID)
            el(meta, "HistoryMaxItems", "10"); el(meta, "HistoryMaxSize", "6291456")
            el(meta, "SettingsChanged", ora())
            el(meta, "CustomData")
            val root = el(kp, "Root")
            val g = el(root, "Group")
            el(g, "UUID", Base64.getEncoder().encodeToString(casuali(16)))
            el(g, "Name", "Root"); el(g, "Notes", ""); el(g, "IconID", "48")
            val t = el(g, "Times")
            for (n in listOf("CreationTime", "LastModificationTime", "LastAccessTime", "ExpiryTime")) el(t, n, ora())
            el(t, "Expires", "False"); el(t, "UsageCount", "0"); el(t, "LocationChanged", ora())
            el(g, "IsExpanded", "True"); el(g, "DefaultAutoTypeSequence", "")
            el(g, "EnableAutoType", "null"); el(g, "EnableSearching", "null"); el(g, "LastTopVisibleEntry", ZERO_UUID)
            return Kdbx(doc, CIFRARIO_AES, 1, kdf, emptyList(), emptyList(), byteArrayOf(0, 0, 4, 0), trasformata)
        }
    }
}
