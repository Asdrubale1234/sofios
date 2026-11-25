package it.sofilabs.sofios.assistente

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import java.io.File

class ComandiTest {
    private fun f(t: String) = Comandi.interpreta(t)

    @Test fun luma_nelle_pagine() {
        assertEquals(Frase("luma-programmi", "no"), f("nascondi Luma"))
        assertEquals(Frase("luma-programmi", "no"), f("togli Luma dalle pagine"))
        assertEquals(Frase("luma-programmi", "si"), f("mostra Luma"))
        assertEquals(Frase("luma-programmi", "si"), f("rimetti Luma"))
    }

    @Test fun frasi_di_base() {
        assertEquals(Frase("apri", "il browser"), f("apri il browser"))   // come sul computer: gli articoli si tolgono dopo
        assertEquals(Frase("volume", "livello" to 40), f("volume al 40"))
        assertEquals(Frase("volume", "delta" to 10), f("alza il volume"))
        assertEquals(Frase("volume", "muto" to true), f("muto"))
        assertEquals(Frase("luminosita", "livello" to 70), f("luminosità 70"))
        assertEquals(Frase("tema", "scuro"), f("metti il tema scuro"))
        assertEquals(Frase("cerca-file", "fattura"), f("cerca fattura"))
        assertEquals(Frase("cerca-web", "gatti"), f("cerca su internet gatti"))
        assertEquals(Frase("installa", "gimp"), f("installa GIMP"))
        assertEquals(Frase("aiuto"), f("aiuto"))
        assertEquals(Frase("niente"), f("ciao"))
    }

    @Test fun trova_i_programmi_per_nome() {
        val v = listOf(Voce("Chrome", "com.android.chrome"), Voce("Gmail", "com.google.android.gm"),
            Voce("Note", "sofios:note"), Voce("Fully (FINTO, solo prova)", "de.ozerov.fully"), Voce("Calculator", "com.android.calculator2"))
        assertEquals("Chrome", Comandi.cercaProgrammi("browser", v).first().nome)
        assertEquals("Gmail", Comandi.cercaProgrammi("posta", v).first().nome)
        assertEquals("Note", Comandi.cercaProgrammi("note", v).first().nome)
        assertEquals("Fully (FINTO, solo prova)", Comandi.cercaProgrammi("fully", v).first().nome)
        assertEquals("Calculator", Comandi.cercaProgrammi("calcolatrice", v).first().nome)
        assertTrue(Comandi.cercaProgrammi("astronave", v).isEmpty())
    }

    @Test fun stesse_risposte_del_computer() {
        val file = File(System.getProperty("user.dir"), "build/fixture/comandi.tsv")
        assumeTrue("mancano le risposte del computer (le prepara la prova automatica)", file.exists())
        var n = 0
        for (riga in file.readLines()) {
            if (riga.isBlank()) continue
            val c = riga.split("\t")
            val frase = c[0]; val azione = c[1]; val arg = c.getOrElse(2) { "" }
            val k = Comandi.interpreta(frase)
            assertEquals("azione per «$frase»", azione, k.azione)
            assertEquals("argomento per «$frase»", arg, k.testo())
            n++
        }
        assertTrue(n > 40)
    }
}
