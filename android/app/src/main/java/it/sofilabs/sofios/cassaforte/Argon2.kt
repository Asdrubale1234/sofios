package it.sofilabs.sofios.cassaforte

import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Argon2d e Argon2id (RFC 9106, versione 0x13), usati da KeePass per trasformare la password.
 * Scritto qui perché Android non lo offre. Il collaudo automatico lo confronta con la libreria Python.
 */
object Argon2 {
    const val TIPO_D = 0
    const val TIPO_ID = 2

    fun calcola(
        password: ByteArray, sale: ByteArray, iterazioni: Int, memoriaKiB: Int, parallelismo: Int,
        lunghezza: Int, tipo: Int,
    ): ByteArray {
        require(tipo == TIPO_D || tipo == TIPO_ID)
        require(parallelismo >= 1 && iterazioni >= 1 && memoriaKiB >= 8 * parallelismo)
        val p = parallelismo
        val t = iterazioni
        val mBlocchi = 4 * p * (memoriaKiB / (4 * p))
        val q = mBlocchi / p                      // blocchi per corsia
        val seg = q / 4

        val h0 = Blake2b(64).apply {
            aggiorna(le32(p)); aggiorna(le32(lunghezza)); aggiorna(le32(memoriaKiB)); aggiorna(le32(t))
            aggiorna(le32(0x13)); aggiorna(le32(tipo))
            aggiorna(le32(password.size)); aggiorna(password)
            aggiorna(le32(sale.size)); aggiorna(sale)
            aggiorna(le32(0)); aggiorna(le32(0))     // niente segreto, niente dati associati
        }.fine()

        val m = LongArray(mBlocchi * 128)
        for (corsia in 0 until p) {
            for (k in 0 until 2) {
                val b = hashLungo(1024, h0, le32(k), le32(corsia))
                val buf = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN)
                val base = (corsia * q + k) * 128
                for (i in 0 until 128) m[base + i] = buf.getLong(i * 8)
            }
        }

        val zero = LongArray(128)
        val ingresso = LongArray(128)
        val indirizzi = LongArray(128)
        val tmp = LongArray(128)
        val r = LongArray(128)
        val z = LongArray(128)

        for (passo in 0 until t) {
            for (fetta in 0 until 4) {
                for (corsia in 0 until p) {
                    val indipendente = tipo == TIPO_ID && passo == 0 && fetta < 2
                    var inizio = 0
                    if (passo == 0 && fetta == 0) inizio = 2
                    if (indipendente) {
                        java.util.Arrays.fill(ingresso, 0L)
                        ingresso[0] = passo.toLong(); ingresso[1] = corsia.toLong(); ingresso[2] = fetta.toLong()
                        ingresso[3] = mBlocchi.toLong(); ingresso[4] = t.toLong(); ingresso[5] = tipo.toLong()
                        if (inizio == 2) prossimiIndirizzi(ingresso, zero, indirizzi, tmp, r, z)
                    }
                    for (idx in inizio until seg) {
                        val corrente = corsia * q + fetta * seg + idx
                        val prec = if (fetta * seg + idx == 0) corsia * q + q - 1 else corrente - 1
                        val casuale: Long = if (indipendente) {
                            if (idx % 128 == 0) prossimiIndirizzi(ingresso, zero, indirizzi, tmp, r, z)
                            indirizzi[idx % 128]
                        } else m[prec * 128]
                        val j1 = casuale and 0xFFFFFFFFL
                        val j2 = casuale ushr 32
                        val corsiaRif = if (passo == 0 && fetta == 0) corsia else (j2 % p).toInt()
                        val dimArea: Int = if (passo == 0) {
                            if (fetta == 0) idx - 1
                            else if (corsiaRif == corsia) fetta * seg + idx - 1
                            else fetta * seg + (if (idx == 0) -1 else 0)
                        } else {
                            if (corsiaRif == corsia) q - seg + idx - 1
                            else q - seg + (if (idx == 0) -1 else 0)
                        }
                        var rel = (j1 * j1) ushr 32
                        rel = dimArea.toLong() - 1 - ((dimArea.toLong() * rel) ushr 32)
                        val partenza = if (passo == 0) 0 else if (fetta == 3) 0 else (fetta + 1) * seg
                        val rifIdx = ((partenza + rel) % q).toInt()
                        val rif = corsiaRif * q + rifIdx
                        comprimi(m, prec * 128, rif * 128, corrente * 128, passo > 0, r, z)
                    }
                }
            }
        }

        val finale = LongArray(128)
        for (corsia in 0 until p) {
            val base = (corsia * q + q - 1) * 128
            for (i in 0 until 128) finale[i] = finale[i] xor m[base + i]
        }
        val bytes = ByteBuffer.allocate(1024).order(ByteOrder.LITTLE_ENDIAN)
        for (i in 0 until 128) bytes.putLong(finale[i])
        java.util.Arrays.fill(m, 0L)
        return hashLungo(lunghezza, bytes.array())
    }

    private fun le32(v: Int) = ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(v).array()

    /** H' di RFC 9106: hash di lunghezza qualsiasi costruito con BLAKE2b. */
    private fun hashLungo(lunghezza: Int, vararg dati: ByteArray): ByteArray {
        val b0 = Blake2b(if (lunghezza <= 64) lunghezza else 64).apply {
            aggiorna(le32(lunghezza)); for (d in dati) aggiorna(d)
        }.fine()
        if (lunghezza <= 64) return b0
        val fuori = ByteArray(lunghezza)
        var v = b0
        System.arraycopy(v, 0, fuori, 0, 32)
        var scritti = 32
        val r = (lunghezza + 31) / 32 - 2
        for (i in 1 until r) {
            v = Blake2b.calcola(64, v)
            System.arraycopy(v, 0, fuori, scritti, 32); scritti += 32
        }
        v = Blake2b.calcola(lunghezza - 32 * r, v)
        System.arraycopy(v, 0, fuori, scritti, lunghezza - scritti)
        return fuori
    }

    private fun prossimiIndirizzi(
        ingresso: LongArray, zero: LongArray, indirizzi: LongArray, tmp: LongArray, r: LongArray, z: LongArray,
    ) {
        ingresso[6]++
        comprimiBlocchi(zero, ingresso, tmp, r, z)
        comprimiBlocchi(zero, tmp, indirizzi, r, z)
    }

    /** fuori = G(x, y) con x e y blocchi interi. */
    private fun comprimiBlocchi(x: LongArray, y: LongArray, fuori: LongArray, r: LongArray, z: LongArray) {
        for (i in 0 until 128) { r[i] = x[i] xor y[i]; z[i] = r[i] }
        permuta(z)
        for (i in 0 until 128) fuori[i] = z[i] xor r[i]
    }

    /** m[dest] = G(m[prec], m[rif]) (e nei passi successivi al primo si fa XOR con il vecchio valore). */
    private fun comprimi(m: LongArray, prec: Int, rif: Int, dest: Int, xorVecchio: Boolean, r: LongArray, z: LongArray) {
        for (i in 0 until 128) { r[i] = m[prec + i] xor m[rif + i]; z[i] = r[i] }
        permuta(z)
        if (xorVecchio) for (i in 0 until 128) m[dest + i] = m[dest + i] xor z[i] xor r[i]
        else for (i in 0 until 128) m[dest + i] = z[i] xor r[i]
    }

    private fun permuta(z: LongArray) {
        for (i in 0 until 8) {            // righe
            val b = i * 16
            runda(z, b, b + 1, b + 2, b + 3, b + 4, b + 5, b + 6, b + 7, b + 8, b + 9, b + 10, b + 11, b + 12, b + 13, b + 14, b + 15)
        }
        for (i in 0 until 8) {            // colonne
            val b = i * 2
            runda(z, b, b + 1, b + 16, b + 17, b + 32, b + 33, b + 48, b + 49,
                b + 64, b + 65, b + 80, b + 81, b + 96, b + 97, b + 112, b + 113)
        }
    }

    private fun runda(
        v: LongArray, i0: Int, i1: Int, i2: Int, i3: Int, i4: Int, i5: Int, i6: Int, i7: Int,
        i8: Int, i9: Int, i10: Int, i11: Int, i12: Int, i13: Int, i14: Int, i15: Int,
    ) {
        gb(v, i0, i4, i8, i12); gb(v, i1, i5, i9, i13); gb(v, i2, i6, i10, i14); gb(v, i3, i7, i11, i15)
        gb(v, i0, i5, i10, i15); gb(v, i1, i6, i11, i12); gb(v, i2, i7, i8, i13); gb(v, i3, i4, i9, i14)
    }

    private fun gb(v: LongArray, a: Int, b: Int, c: Int, d: Int) {
        var va = v[a]; var vb = v[b]; var vc = v[c]; var vd = v[d]
        va = va + vb + 2 * (va and 0xFFFFFFFFL) * (vb and 0xFFFFFFFFL)
        vd = java.lang.Long.rotateRight(vd xor va, 32)
        vc = vc + vd + 2 * (vc and 0xFFFFFFFFL) * (vd and 0xFFFFFFFFL)
        vb = java.lang.Long.rotateRight(vb xor vc, 24)
        va = va + vb + 2 * (va and 0xFFFFFFFFL) * (vb and 0xFFFFFFFFL)
        vd = java.lang.Long.rotateRight(vd xor va, 16)
        vc = vc + vd + 2 * (vc and 0xFFFFFFFFL) * (vd and 0xFFFFFFFFL)
        vb = java.lang.Long.rotateRight(vb xor vc, 63)
        v[a] = va; v[b] = vb; v[c] = vc; v[d] = vd
    }
}
