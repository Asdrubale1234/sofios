package it.sofilabs.sofios.cassaforte

/** ChaCha20 (RFC 8439): chiave da 32 byte, nonce da 12 byte, contatore iniziale a scelta. */
class ChaCha20(chiave: ByteArray, nonce: ByteArray, contatore: Int = 0) {
    private val stato = IntArray(16)
    private val flusso = ByteArray(64)
    private var usati = 64

    init {
        require(chiave.size == 32 && nonce.size == 12)
        stato[0] = 0x61707865; stato[1] = 0x3320646e; stato[2] = 0x79622d32; stato[3] = 0x6b206574
        for (i in 0 until 8) stato[4 + i] = leggi(chiave, i * 4)
        stato[12] = contatore
        for (i in 0 until 3) stato[13 + i] = leggi(nonce, i * 4)
    }

    private fun leggi(b: ByteArray, o: Int) =
        (b[o].toInt() and 0xff) or ((b[o + 1].toInt() and 0xff) shl 8) or
            ((b[o + 2].toInt() and 0xff) shl 16) or ((b[o + 3].toInt() and 0xff) shl 24)

    private fun quarto(x: IntArray, a: Int, b: Int, c: Int, d: Int) {
        x[a] += x[b]; x[d] = Integer.rotateLeft(x[d] xor x[a], 16)
        x[c] += x[d]; x[b] = Integer.rotateLeft(x[b] xor x[c], 12)
        x[a] += x[b]; x[d] = Integer.rotateLeft(x[d] xor x[a], 8)
        x[c] += x[d]; x[b] = Integer.rotateLeft(x[b] xor x[c], 7)
    }

    private fun nuovoBlocco() {
        val x = stato.copyOf()
        for (r in 0 until 10) {
            quarto(x, 0, 4, 8, 12); quarto(x, 1, 5, 9, 13); quarto(x, 2, 6, 10, 14); quarto(x, 3, 7, 11, 15)
            quarto(x, 0, 5, 10, 15); quarto(x, 1, 6, 11, 12); quarto(x, 2, 7, 8, 13); quarto(x, 3, 4, 9, 14)
        }
        for (i in 0 until 16) {
            val v = x[i] + stato[i]
            flusso[i * 4] = v.toByte(); flusso[i * 4 + 1] = (v ushr 8).toByte()
            flusso[i * 4 + 2] = (v ushr 16).toByte(); flusso[i * 4 + 3] = (v ushr 24).toByte()
        }
        stato[12]++
        usati = 0
    }

    /** Applica (con XOR) il flusso ai dati: vale sia per cifrare sia per decifrare. */
    fun applica(dati: ByteArray): ByteArray {
        val fuori = ByteArray(dati.size)
        for (i in dati.indices) {
            if (usati == 64) nuovoBlocco()
            fuori[i] = (dati[i].toInt() xor flusso[usati++].toInt()).toByte()
        }
        return fuori
    }
}
