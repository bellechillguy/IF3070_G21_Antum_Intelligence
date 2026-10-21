BOBOT_PENALTI = 1000


def objective_function(state, daftar_kendaraan, kapal):
    """Hitung total fee kendaraan dikurangi penalti pelanggaran."""
    total_fee = hitung_fee(state, daftar_kendaraan)
    return total_fee - hitung_penalti(state, daftar_kendaraan, kapal)


def objective_function_jumlah(state, daftar_kendaraan, kapal):
    """Hitung jumlah kendaraan yang diangkut dikurangi penalti."""
    jumlah_kendaraan = sum(posisi is not None for posisi in state)
    return jumlah_kendaraan - hitung_penalti(state, daftar_kendaraan, kapal)


def hitung_penalti(state, daftar_kendaraan, kapal):
    pelanggaran_kapasitas = cek_pelanggaran_kapasitas(state, daftar_kendaraan, kapal)
    pelanggaran_overlap = cek_pelanggaran_overlap(state, daftar_kendaraan, kapal)
    pelanggaran_keluar = cek_pelanggaran_keluar_kapal(state, daftar_kendaraan, kapal)
    return BOBOT_PENALTI * (pelanggaran_kapasitas + pelanggaran_overlap + pelanggaran_keluar)


def hitung_fee(state, daftar_kendaraan):
    return sum(
        daftar_kendaraan[i].fee
        for i, posisi in enumerate(state)
        if posisi is not None
    )


def cek_pelanggaran_kapasitas(state, daftar_kendaraan, kapal):
    """Hitung kelebihan berat kendaraan dari kapasitas kapal."""
    total_berat = sum(
        daftar_kendaraan[i].berat
        for i, posisi in enumerate(state)
        if posisi is not None
    )
    return max(0, total_berat - kapal.kapasitas)


def cek_pelanggaran_overlap(state, daftar_kendaraan, kapal):
    """Hitung penempatan tambahan pada sel kapal yang sudah terisi."""
    jumlah_sel_overlap = 0
    sel_dipakai = set()

    for i, posisi in enumerate(state):
        if posisi is None:
            continue

        for x, y in sel_terisi(daftar_kendaraan[i], posisi):
            # Abaikan sel di luar kapal karena pelanggarannya dihitung terpisah
            if x < 0 or x >= kapal.dp or y < 0 or y >= kapal.dl:
                continue

            if (x, y) in sel_dipakai:
                jumlah_sel_overlap += 1
            else:
                sel_dipakai.add((x, y))

    return jumlah_sel_overlap


def cek_pelanggaran_keluar_kapal(state, daftar_kendaraan, kapal):
    """Hitung jumlah sel kendaraan yang berada di luar kapal."""
    jumlah_sel_keluar = 0

    for i, posisi in enumerate(state):
        if posisi is None:
            continue

        for x, y in sel_terisi(daftar_kendaraan[i], posisi):
            if x < 0 or x >= kapal.dp or y < 0 or y >= kapal.dl:
                jumlah_sel_keluar += 1

    return jumlah_sel_keluar


def sel_terisi(kendaraan, posisi):
    """Kembalikan sel kendaraan dengan posisi (x, y) sebagai pojok kiri atas."""
    x, y, arah = posisi

    if arah == "H":
        ukuran_x, ukuran_y = kendaraan.p, kendaraan.l
    elif arah == "V":
        ukuran_x, ukuran_y = kendaraan.l, kendaraan.p
    else:
        raise ValueError(f"Orientasi tidak valid: {arah}")

    sel = []
    for dx in range(ukuran_x):
        for dy in range(ukuran_y):
            sel.append((x + dx, y + dy))

    return sel
