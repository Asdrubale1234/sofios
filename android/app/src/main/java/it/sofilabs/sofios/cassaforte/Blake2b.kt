package it.sofilabs.sofios.cassaforte

import java.nio.ByteBuffer
import java.nio.ByteOrder

/** BLAKE2b senza chiave (RFC 7693). Serve ad Argon2, che Android non ha già pronto. */
class Blake2b(private val lunghezza: Int) {
    private val h = LongArray(8)
    private val blocco = ByteArray(128)
    private var inBlocco = 0
    private var contatore = 0L

    init {
        require(lunghezza in 1..64)
        for (i in 0 until 8) h[i] = IV[i]
        h[0] = h[0] xor (0x01010000L or lunghezza.toLong())
    }

    fun aggiorna(dati: ByteArray, da: Int = 0, n: Int = dati.size): Blake2b {
        var pos = da
        var resto = n
        while (resto > 0) {
            if (inBlocco == 128) {          // il blocco pieno si elabora solo se ne arriva altro
                contatore += 128
                comprimi(false)
                inBlocco = 0
            }
            val k = minOf(128 - inBlocco, resto)
            System.arraycopy(dati, pos, blocco, inBlocco, k)
            inBlocco += k; pos += k; resto -= k
        }
        return this
    }

    fun fine(): ByteArray {
        contatore += inBlocco
        for (i in inBlocco until 128) blocco[i] = 0
        comprimi(true)
        val fuori = ByteBuffer.allocate(64).order(ByteOrder.LITTLE_ENDIAN)
        for (i in 0 until 8) fuori.putLong(h[i])
        return fuori.array().copyOf(lunghezza)
    }

    private fun comprimi(ultimo: Boolean) {
        val m = LongArray(16)
        val b = ByteBuffer.wrap(blocco).order(ByteOrder.LITTLE_ENDIAN)
        for (i in 0 until 16) m[i] = b.getLong(i * 8)
        val v = LongArray(16)
        for (i in 0 until 8) { v[i] = h[i]; v[i + 8] = IV[i] }
        v[12] = v[12] xor contatore
        if (ultimo) v[14] = v[14].inv()
        for (r in 0 until 12) {
            val s = SIGMA[r % 10]
            g(v, 0, 4, 8, 12, m[s[0]], m[s[1]])
            g(v, 1, 5, 9, 13, m[s[2]], m[s[3]])
            g(v, 2, 6, 10, 14, m[s[4]], m[s[5]])
            g(v, 3, 7, 11, 15, m[s[6]], m[s[7]])
            g(v, 0, 5, 10, 15, m[s[8]], m[s[9]])
            g(v, 1, 6, 11, 12, m[s[10]], m[s[11]])
            g(v, 2, 7, 8, 13, m[s[12]], m[s[13]])
            g(v, 3, 4, 9, 14, m[s[14]], m[s[15]])
        }
        for (i in 0 until 8) h[i] = h[i] xor v[i] xor v[i + 8]
    }

    private fun g(v: LongArray, a: Int, b: Int, c: Int, d: Int, x: Long, y: Long) {
        v[a] = v[a] + v[b] + x
        v[d] = java.lang.Long.rotateRight(v[d] xor v[a], 32)
        v[c] = v[c] + v[d]
        v[b] = java.lang.Long.rotateRight(v[b] xor v[c], 24)
        v[a] = v[a] + v[b] + y
        v[d] = java.lang.Long.rotateRight(v[d] xor v[a], 16)
        v[c] = v[c] + v[d]
        v[b] = java.lang.Long.rotateRight(v[b] xor v[c], 63)
    }

    companion object {
        private val IV = longArrayOf(
            0x6a09e667f3bcc908UL.toLong(), 0xbb67ae8584caa73bUL.toLong(),
            0x3c6ef372fe94f82bUL.toLong(), 0xa54ff53a5f1d36f1UL.toLong(),
            0x510e527fade682d1UL.toLong(), 0x9b05688c2b3e6c1fUL.toLong(),
            0x1f83d9abfb41bd6bUL.toLong(), 0x5be0cd19137e2179UL.toLong())
        private val SIGMA = arrayOf(
            intArrayOf(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15),
            intArrayOf(14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3),
            intArrayOf(11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4),
            intArrayOf(7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8),
            intArrayOf(9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13),
            intArrayOf(2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9),
            intArrayOf(12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11),
            intArrayOf(13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10),
            intArrayOf(6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5),
            intArrayOf(10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0))

        fun calcola(lunghezza: Int, vararg parti: ByteArray): ByteArray {
            val b = Blake2b(lunghezza)
            for (p in parti) b.aggiorna(p)
            return b.fine()
        }
    }
}
