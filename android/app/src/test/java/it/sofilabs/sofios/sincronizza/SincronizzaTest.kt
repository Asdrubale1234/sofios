package it.sofilabs.sofios.sincronizza

import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test
import java.io.File

class SincronizzaTest {

    @Test fun jsonVaEVieneComeEra() {
        val t = """{"a":1,"b":[true,false,null,"x\"y\nè"],"c":{"d":-2.5e1,"e":""}}"""
        val v = Json.oggetto(t)
        assertEquals(1.0, v["a"])
        assertEquals(listOf(true, false, null, "x\"y\nè"), v["b"])
        assertEquals(-25.0, (v["c"] as Map<*, *>)["d"])
        assertEquals(v, Json.oggetto(Json.scrivi(v)))
        assertEquals("""{"n":3,"s":"a\"b"}""", Json.scrivi(linkedMapOf("n" to 3, "s" to "a\"b")))
        assertTrue(Json.lista("[]").isEmpty())
        assertTrue(Json.oggetto(" { } ").isEmpty())
    }

    @Test fun jsonRifiutaIlMalFatto() {
        for (t in listOf("{", "[1,", "{\"a\" 1}", "tru", "\"abc", "[1] x")) {
            try { Json.leggi(t); fail("doveva rifiutare: $t") } catch (e: IllegalArgumentException) { }
        }
    }

    @Test fun parlaSoloConIlTabletStesso() {
        assertTrue(Syncthing.indirizzoPermesso("http://127.0.0.1:8384/rest/system/status"))
        assertTrue(Syncthing.indirizzoPermesso("https://127.0.0.1:8384/rest/x"))
        for (x in listOf("http://example.com/rest", "https://192.168.1.5:8384/", "http://localhost:8384/", "http://127.0.0.1@evil.com/",
            "http://evil.com@127.0.0.1/", "ftp://127.0.0.1/", "http://127.0.0.2:8384/", "non un indirizzo", "http://[::1]:8384/", "http://127.0.0.1.evil.com/"))
            assertFalse("doveva rifiutare $x", Syncthing.indirizzoPermesso(x))
    }

    @Test fun codiciDeiDispositivi() {
        assertTrue(Sincronizza.codiceValido("MFZWI3D-BONSGYC-YLTMRWG-C43ENR5-QXGZDMM-FZWI3DP-BONSGYY-LTMRWAD"))
        assertTrue(Sincronizza.codiceValido(" mfzwi3d-bonsgyc-yltmrwg-c43enr5-qxgzdmm-fzwi3dp-bonsgyy-ltmrwad "))
        assertFalse(Sincronizza.codiceValido("MFZWI3D-BONSGYC"))
        assertFalse(Sincronizza.codiceValido("1111111-1111111-1111111-1111111-1111111-1111111-1111111-1111111"))
    }

    // ---- prova con un Syncthing vero (nel collaudo automatico): attiva solo se ci sono le variabili d'ambiente ----

    private fun vero(): Syncthing? {
        val porta = System.getenv("SOFIOS_SYNCTHING_PORTA")?.toIntOrNull()
        val chiave = System.getenv("SOFIOS_SYNCTHING_CHIAVE")
        assumeTrue("nessun Syncthing di prova (normale in locale)", porta != null && chiave != null)
        return Syncthing(porta!!, chiave!!)
    }

    @Test fun conUnSyncthingVero() {
        val st = vero()!!
        val base = File(System.getProperty("java.io.tmpdir"), "sofios-sync-prova-" + System.nanoTime()).also { it.mkdirs() }
        val cartelle = listOf("sofios-note" to "Note", "sofios-password" to "Password", "sofios-foto" to "Foto", "sofios-file" to "File")
            .map { (id, n) -> CartellaSync(id, n, File(base, n).also { it.mkdirs() }.path) }
        assertTrue(Sincronizza.acceso(st))
        val io = Sincronizza.miaChiave(st)
        assertTrue(Sincronizza.codiceValido(io))

        Sincronizza.prepara(st, "Tablet di prova", cartelle)
        Sincronizza.prepara(st, "Tablet di prova", cartelle) // ripetibile

        val o = Json.oggetto(Json.scrivi(st.leggi("config/options")))
        assertEquals(false, o["globalAnnounceEnabled"]); assertEquals(false, o["relaysEnabled"])
        assertEquals(false, o["natEnabled"]); assertEquals(true, o["localAnnounceEnabled"])
        assertEquals(-1.0, o["urAccepted"]); assertEquals(0.0, o["autoUpgradeIntervalH"])
        assertEquals("Tablet di prova", (st.leggi("config/devices/$io") as Map<*, *>)["name"])
        for (c in cartelle) {
            val f = st.leggi("config/folders/${c.id}") as Map<*, *>
            assertEquals("sendreceive", f["type"])
            val v = f["versioning"] as Map<*, *>
            assertEquals("trashcan", v["type"]); assertEquals("30", (v["params"] as Map<*, *>)["cleanoutDays"])
        }

        // un altro dispositivo (il PC): ci si fida e riceve tutte le cartelle; poi si toglie
        val pc = "MFZWI3D-BONSGYC-YLTMRWG-C43ENR5-QXGZDMM-FZWI3DP-BONSGYY-LTMRWAD"
        Sincronizza.fidati(st, pc, "PC di prova", cartelle)
        assertEquals(listOf("PC di prova"), Sincronizza.dispositivi(st).map { it.nome })
        assertFalse(Sincronizza.dispositivi(st)[0].collegato)
        for (c in cartelle) {
            val devs = ((st.leggi("config/folders/${c.id}") as Map<*, *>)["devices"] as List<*>).map { (it as Map<*, *>)["deviceID"] }
            assertTrue("${c.id} deve essere condivisa con il PC", pc in devs && io in devs)
        }
        Sincronizza.rimuovi(st, pc, cartelle)
        assertTrue(Sincronizza.dispositivi(st).isEmpty())
        assertNull(Sincronizza.completamento(st, cartelle))
        for (c in cartelle) {
            val devs = ((st.leggi("config/folders/${c.id}") as Map<*, *>)["devices"] as List<*>).map { (it as Map<*, *>)["deviceID"] }
            assertEquals(listOf(io), devs)
        }
    }
}
