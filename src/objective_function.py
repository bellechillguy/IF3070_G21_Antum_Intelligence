def objective_function(state, daftar_kendaraan, kapal):
    '''
    Menghitung nilai objektif dari State
    Nilai objektif = total fee - penalti atas pelanggaran

    Total fee: Jumlah seluruh fee dari kendaraan yang diangkut Kapal

    Jenis pelanggaran:
    1. Pelanggaran total berat Kendaraan diangkut > Kapasitas Kapal
    2. Pelanggaran Kendaraan menempati sel yang sama dengan Kendaraan lain
    3. Pelanggaran body Kendaraan keluar dari Kapal
    Nantinya pelanggaran ini akan diberi bobot besar

    Parameter:
    - State
    - daftar_kendaraan: list of objek Kendaraan
    - kapal

    Return:
    - int: nilai objektif

    '''
    bobot_penalti = 1000
    total_fee = hitung_fee(state, daftar_kendaraan)

    pelanggaran_kapasitas = cek_pelanggaran_kapasitas(state, daftar_kendaraan, kapal)
    pelanggaran_overlap = cek_pelanggaran_overlap(state, daftar_kendaraan, kapal)
    pelanggaran_keluar = cek_pelanggaran_keluar_kapal(state, daftar_kendaraan, kapal)
    penalti = bobot_penalti * (pelanggaran_kapasitas + pelanggaran_overlap + pelanggaran_keluar)

    nilai_objektif = total_fee - penalti
    return nilai_objektif

def objective_function_jumlah(state, daftar_kendaraan, kapal):
    # Utamakan jumlah kendaraan yang diangkut, dengan penalti yang sama
    jumlah_kendaraan = sum(posisi is not None for posisi in state)
    bobot_penalti = 1000

    pelanggaran_kapasitas = cek_pelanggaran_kapasitas(state, daftar_kendaraan, kapal)
    pelanggaran_overlap = cek_pelanggaran_overlap(state, daftar_kendaraan, kapal)
    pelanggaran_keluar = cek_pelanggaran_keluar_kapal(state, daftar_kendaraan, kapal)
    penalti = bobot_penalti * (pelanggaran_kapasitas + pelanggaran_overlap + pelanggaran_keluar)

    return jumlah_kendaraan - penalti

def hitung_fee(state, daftar_kendaraan):
    '''
    Menghitung total fee yang didapatkan Kapal
    Total fee dihitung dengan menjumlahkan seluruh fee Kendaraan yang diangkut

    Parameter:
    - State
    - dafar_kendaraan: list objek Kendaraan

    Return:
    - int: total fee
    '''

    total_fee = 0
    for i, posisi in enumerate(state):
        if posisi is None:
            continue

        total_fee += daftar_kendaraan[i].fee

    return total_fee

def cek_pelanggaran_kapasitas(state, daftar_kendaraan, kapal):
    '''
    Cek apakah total berat Kendaraan yang diangkut melebihi kapasitas Kapal

    Parameter:
    - state
    - daftar_kendaraan: list objek Kendaraan
    - kapal

    Return:
    - int: kelebihan berat, kalau ga melanggar 0
    '''
    total_berat = 0
    for i, posisi in enumerate(state):
        if posisi is None:
            continue

        total_berat += daftar_kendaraan[i].berat
    
    kelebihan_berat = max(0, total_berat - kapal.kapasitas)
    return kelebihan_berat

def cek_pelanggaran_overlap(state, daftar_kendaraan, kapal):
    '''
    Cek apakah ada pelanggaran di mana ada beberapa Kendaraan yang menempati sel yang sama

    Parameter:
    - State
    - Daftar Kendaraan (list of objek)
    - Kapal

    Return:
    - int: jumlah sel overlap

    '''
    jumlah_sel_overlap = 0
    sel_dipakai = set()

    for i, posisi in enumerate(state):
        if posisi is None:
            continue

        for (x,y) in sel_terisi(daftar_kendaraan[i], posisi):
            # Skip jika sel berada di luar kapal karena akan dihitung di violation luar kapal
            if x < 0 or x >= kapal.dp or y < 0 or y >= kapal.dl:
                continue

            if (x,y) in sel_dipakai: 
                jumlah_sel_overlap += 1
            else:
                sel_dipakai.add((x,y))

    return jumlah_sel_overlap

def cek_pelanggaran_keluar_kapal(state, daftar_kendaraan, kapal):
    '''
    Cek apakah ada bagian Kendaraan (sel-sel) yang keluar dari batas Kapal
    Koordinat valid yang ada dalam kapal berada pada rentang:
    - 0 <= x < dimensi panjang Kapal 
    - 0 <= y < dimensi lebar Kapal

    Parameter: 
    - State
    - Daftar Kendaraan (list of objek)
    - Kapal

    Return:
    - int: jumlah sel keluar
    '''

    jumlah_sel_keluar = 0

    for i, posisi in enumerate(state):
        if posisi is None:
            continue

        for (x, y) in sel_terisi(daftar_kendaraan[i], posisi):
            if x<0 or x>=kapal.dp or y<0 or y>=kapal.dl:
                jumlah_sel_keluar+=1

    return jumlah_sel_keluar


def sel_terisi(kendaraan, posisi):
    '''
    Cek sel mana saja yang terisi ketika 1 Kendaraan menempati posisi tertentu 

    Cara hitungnya:
    - Posisi kendaraan (x,y) ini merupakan pojok kiri atas kendaraan
    - Arah "H": kendaraan melebar ke kanan sepanjang p.kendaraan dan ke bawah sepanjang l.kendaraan
    - Arah "V": kendaraan melebar ke kanan sepanjang l dan ke bawah sepanjang p

    Parameter:
    - 1 objek kendaraan
    - posisi (x, y, arah) dari State

    Return:
    - list of (x,y): semua sel yang ditempati kendaraan
    '''
    x, y, arah = posisi

    if arah == "H":
        ukuran_x, ukuran_y = kendaraan.p, kendaraan.l
    elif arah == "V":
        ukuran_x, ukuran_y = kendaraan.l, kendaraan.p

    sel = []
    for i in range(ukuran_x):
        for j in range(ukuran_y):
            sel.append((x+i, y+j))
    
    return sel
