package it.sofilabs.sofios.cassaforte

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Assume.assumeTrue
import org.junit.Test
import java.io.File

/** Collaudi della Cassaforte: confronto con la libreria Python del computer e prova di andata e ritorno. */
class CassaforteTest {
    private val dir = File(System.getProperty("user.dir"), "build/fixture")

    private fun hex(b: ByteArray) = b.joinToString("") { "%02x".format(it) }
    private fun unhex(s: String) = Kdbx.hex(s)
    private fun righe(): List<List<String>> {
        assumeTrue("mancano i file di confronto (vengono preparati dalla prova automatica)", File(dir, "fixture.tsv").exists())
        return File(dir, "fixture.tsv").readLines().filter { it.isNotBlank() }.map { it.split("\t") }
    }
    private fun unesc(s: String) = s.replace("\\n", "\n")

    @Test fun blake2b_abc() {
        val r = Blake2b.calcola(64, "abc".toByteArray())
        assertEquals("ba80a53f981c4d0d6a2797b69f12f6e94c212f14685ac4b74b12bb6fdbffa2d1" +
            "7d87c5392aab792dc252d5de4533cc9518d38aa8dbf1925ab92386edd4009923", hex(r))
    }

    @Test fun blake2b_lungo() {   // dati su più blocchi: confronto con la libreria di Java non c'è, quindi controllo coerenza
        val dati = ByteArray(1000) { it.toByte() }
        val a = Blake2b(64).aggiorna(dati).fine()
        val b = Blake2b(64).apply { aggiorna(dati, 0, 128); aggiorna(dati, 128, 1); aggiorna(dati, 129, 871) }.fine()
        assertArrayEquals(a, b)
    }

    @Test fun chacha20_rfc8439() {
        val chiave = ByteArray(32) { it.toByte() }
        val nonce = unhex("000000090000004a00000000")
        val flusso = ChaCha20(chiave, nonce, 1).applica(ByteArray(64))
        assertEquals("10f1e7e4d13b5915500fdd1fa32071c4", hex(flusso.copyOf(16)))
    }

    @Test fun argon2_come_python() {
        var n = 0
        for (r in righe()) {
            if (r[0] != "argon2") continue
            val atteso = r[7]
            val tipo = if (r[1] == "d") Argon2.TIPO_D else Argon2.TIPO_ID
            val h = Argon2.calcola(unhex(r[2]), unhex(r[3]), r[4].toInt(), r[5].toInt(), r[6].toInt(), 32, tipo)
            assertEquals("Argon2 ${r[1]} t=${r[4]} m=${r[5]} p=${r[6]}", atteso, hex(h)); n++
        }
        assertTrue("nessun confronto Argon2 eseguito", n > 0)
    }

    private fun voceCome(v: Voce) = listOf(v.titolo, v.utente, v.password, v.sito, v.note.replace("\n", "\\n"))

    @Test fun legge_le_cassaforti_del_pc() {
        val tutte = righe()
        var aperte = 0
        for (r in tutte.filter { it[0] == "kdbx" }) {
            val k = Kdbx.apri(File(dir, r[1]).readBytes(), r[2])
            val attese = tutte.filter { it[0] == "voce" && it[1] == r[1] }.map { it.subList(2, 7) }.toSet()
            val trovate = k.voci().map { voceCome(it) }.toSet()
            assertEquals("voci di ${r[1]}", attese, trovate)
            aperte++
        }
        assertTrue("nessuna cassaforte del PC provata", aperte > 0)
    }

    @Test fun password_sbagliata_e_file_rotto() {
        val r = righe().first { it[0] == "kdbx" }
        val dati = File(dir, r[1]).readBytes()
        try { Kdbx.apri(dati, "sbagliata"); fail("doveva rifiutare la password") } catch (e: PasswordSbagliata) { }
        val rotto = dati.copyOf(); rotto[rotto.size / 2] = (rotto[rotto.size / 2].toInt() xor 0x55).toByte()
        try { Kdbx.apri(rotto, r[2]); fail("doveva accorgersi del file rotto") } catch (e: FileDanneggiato) { }
        try { Kdbx.apri(dati.copyOf(40), r[2]); fail("doveva rifiutare il file troncato") } catch (e: FileDanneggiato) { }
    }

    private fun scrivi(nome: String, k: Kdbx, password: String) {
        dir.mkdirs()
        File(dir, nome).writeBytes(k.salva())
        File(dir, "$nome.attese.tsv").writeText(
            k.voci().joinToString("\n") { voceCome(it).joinToString("\t") } + "\n")
        File(dir, "$nome.password").writeText(password)
    }

    @Test fun modifica_una_cassaforte_del_pc_e_la_rilegge() {
        val r = righe().first { it[0] == "kdbx" && it[1] == "pc-predefinita.kdbx" }
        val k = Kdbx.apri(File(dir, r[1]).readBytes(), r[2])
        val prima = k.voci().sortedBy { it.titolo }
        val primo = prima.first()
        primo.password = "Nuova-password-1"; primo.note = "modificata da Android\nseconda riga"
        k.modifica(primo)
        k.elimina(prima.last().id)
        k.aggiungi("Aggiunta da Android", "sofi", "àèìòù-€-🌊", "https://sofilabs.it", "")
        scrivi("kotlin-da-pc.kdbx", k, r[2])
        val riletta = Kdbx.apri(File(dir, "kotlin-da-pc.kdbx").readBytes(), r[2])
        val titoli = riletta.voci().map { it.titolo }.toSet()
        assertTrue("Aggiunta da Android" in titoli)
        assertEquals(prima.size, riletta.voci().size)
        assertEquals("Nuova-password-1", riletta.voci().first { it.id == primo.id }.password)
    }

    @Test fun crea_una_cassaforte_nuova_e_la_rilegge() {
        val k = Kdbx.crea("prova-Android-1")
        k.aggiungi("Posta", "luca", "Segreta-1", "mail.sofilabs.it", "prima\nseconda")
        k.aggiungi("Banca è così", "luca", "p@ss wörd", "", "")
        scrivi("kotlin-nuovo.kdbx", k, "prova-Android-1")
        val riletta = Kdbx.apri(File(dir, "kotlin-nuovo.kdbx").readBytes(), "prova-Android-1")
        assertEquals(setOf("Posta", "Banca è così"), riletta.voci().map { it.titolo }.toSet())
        assertEquals("prima\nseconda", riletta.voci().first { it.titolo == "Posta" }.note)
        try { Kdbx.apri(File(dir, "kotlin-nuovo.kdbx").readBytes(), "altra"); fail() } catch (e: PasswordSbagliata) { }
    }
}
