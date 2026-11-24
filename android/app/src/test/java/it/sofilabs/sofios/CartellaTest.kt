package it.sofilabs.sofios

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.nio.file.Files

class CartellaTest {
    @Test fun copia_senza_cancellare_ne_sovrascrivere() {
        val base = Files.createTempDirectory("sofios").toFile()
        val da = base.resolve("vecchia").apply { mkdirs() }
        da.resolve("Note").mkdirs()
        da.resolve("Note/a.txt").writeText("dalla vecchia")
        da.resolve("Note/b.txt").writeText("seconda")
        da.resolve("Note/c.txt.tmp").writeText("temporaneo")
        val a = base.resolve("nuova").apply { mkdirs() }
        a.resolve("Note").mkdirs()
        a.resolve("Note/a.txt").writeText("gia presente")

        val n = Cartella.copiaSeMancano(da, a)

        assertEquals(1, n)                                                   // solo b.txt (a.txt c'era già, .tmp si salta)
        assertEquals("gia presente", a.resolve("Note/a.txt").readText())     // non sovrascritto
        assertEquals("seconda", a.resolve("Note/b.txt").readText())
        assertFalse(a.resolve("Note/c.txt.tmp").exists())
        assertTrue(da.resolve("Note/a.txt").exists())                        // l'originale resta
        assertEquals(0, Cartella.copiaSeMancano(da, a))                      // ripetere non cambia niente
    }
}
