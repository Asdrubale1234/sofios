package it.sofilabs.sofios

import org.junit.Assert.assertEquals
import org.junit.Test

class NovitaTest {
    @Test fun dalla_piu_nuova_e_solo_quelle_non_viste() {
        val esistono = setOf(2, 3, 5)
        assertEquals(listOf(5, 3, 2), Novita.arretrate(1, 5, esistono::contains))
        assertEquals(listOf(5), Novita.arretrate(3, 5, esistono::contains))
        assertEquals(emptyList<Int>(), Novita.arretrate(5, 5, esistono::contains))
        assertEquals(emptyList<Int>(), Novita.arretrate(1, 1, esistono::contains))
        assertEquals(listOf(3), Novita.arretrate(2, 4, esistono::contains))   // 4 non ha il file: si salta
    }
}
