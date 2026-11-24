package it.sofilabs.sofios.cassaforte

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import java.io.File

/** L'unione di due cassaforti deve dare lo stesso risultato del programma del computer (cassaforte_unione.py). */
class UnioneTest {
    private val dir = File(System.getProperty("user.dir"), "build/fixture")
    private val pw = "provaprova"
    private fun apri(n: String): Kdbx {
        assumeTrue("mancano i file di confronto dell'unione", File(dir, n).exists())
        return Kdbx.apri(File(dir, n).readBytes(), pw)
    }

    @Test fun due_dispositivi_come_il_computer() {
        val a = apri("unione-A.kdbx"); val r = a.unisci(apri("unione-B.kdbx"))
        assertEquals(apri("unione-pc-AB.kdbx").istantanea(), a.istantanea())
        assertTrue(r["vinte_dall_altra"]!! >= 1)
    }

    @Test fun nell_altra_direzione() {
        val b = apri("unione-B.kdbx"); b.unisci(apri("unione-A.kdbx"))
        assertEquals(apri("unione-pc-BA.kdbx").istantanea(), b.istantanea())
    }

    @Test fun una_voce_modificata_dopo_l_eliminazione_torna_in_vita() {
        val c = apri("unione-C.kdbx"); c.unisci(apri("unione-D.kdbx"))
        assertEquals(apri("unione-pc-CD.kdbx").istantanea(), c.istantanea())
        assertEquals("nuova", c.voci().first { it.titolo == "Comune" }.password)
    }

    @Test fun unire_di_nuovo_non_cambia_niente() {
        val a = apri("unione-A.kdbx"); a.unisci(apri("unione-B.kdbx")); val prima = a.istantanea()
        a.unisci(apri("unione-B.kdbx")); assertEquals(prima, a.istantanea())
    }

    /** Il tablet elimina e modifica; poi la prova Python (verifica-unione.py) controlla che il computer ne tenga conto. */
    @Test fun eliminazioni_e_modifiche_del_tablet_per_il_computer() {
        val k = apri("unione-base.kdbx")
        val posta = k.voci().first { it.titolo == "Posta" }
        posta.password = "p4-dal-tablet"; k.modifica(posta)
        k.elimina(k.voci().first { it.titolo == "Comune" }.id)
        k.aggiungi("SoloTablet", "t", "pt", "", "")
        File(dir, "unione-K.kdbx").writeBytes(k.salva())
        val ak = apri("unione-A.kdbx"); ak.unisci(apri("unione-K.kdbx"))
        File(dir, "unione-kotlin-AK.kdbx").writeBytes(ak.salva())
        val titoli = ak.voci().map { it.titolo }.toSet()
        assertTrue("Comune" !in titoli && "SoloTablet" in titoli && "SoloA" in titoli)
        assertEquals("p4-dal-tablet", ak.voci().first { it.titolo == "Posta" }.password)
    }
}
