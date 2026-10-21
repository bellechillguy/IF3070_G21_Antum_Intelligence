import json
import random
from models import Kapal, Kendaraan

def load_data(path):
    with open(path, 'r') as file:
        data = json.load(file)
    kp  = data['kapal']
    kapal = Kapal(kp['dl'], kp['dp'], kp['kapasitas']) 

    d_kendaraan = []
    for kd in data["kendaraan"]:
        kendaraan = Kendaraan(kd['id'], kd['p'], kd['l'], kd['berat'], kd['fee'], kd['ETA'])
        d_kendaraan.append(kendaraan)

    return kapal, d_kendaraan

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
        
def random_initial_state(daftar_kendaraan, kapal):
    '''
    Membuat state awal secara acak
 
    Parameter:
    - daftar_kendaraan: list objek Kendaraan
    - kapal
 
    Return:
    - state: list posisi (None atau (x, y, arah)) untuk tiap kendaraan
    '''
    state = []
    for kendaraan in daftar_kendaraan:
        if random.random() < 0.5: # Tiap kendaraan punya peluang 50% tidak diangkut (None)
            state.append(None)
        else:
            x = random.randint(0, kapal.dp - 1)
            y = random.randint(0, kapal.dl - 1)
            arah = random.choice(["V", "H"])
            state.append((x, y, arah))
    return state

def get_neighbors(state, daftar_kendaraan, kapal):
    '''
    Menghasilkan semua Neighbor dari current state
    Neighbor didapatkan dengan cara berikut:
    1. Mengubah arah 1 Kendaraan (V to H, H to V)
        Tapi tidak berlaku untuk kendaraan dimensi 1:1 karena akan sama saja
    2. Memindahkan 1 Kendaraan ke koordinat lain
        Pemindahan koordinat yang ditangani:
        a. Pindahkan 1 Kendaraan di dalam kapal ke koordinat lain di dalam kapal juga
        b. Pindahlan 1 Kendaraan di luar kapal ke koordinat dalam kapal
        c. Pindahkan 1 Kendaraan di dalam kapal ke luar (None) 
    3. Menukar posisi 2 Kendaraan
        Penukaran yang ditangani:
        - Tukar 2 Kendaraan yang sama2 di dalam Kapal
        - Tukar 1 Kendaraan di dalam kapal dan 1 di luar 
        2 Kendaraan di luar kapal ga ditukar karena akan sama saja

    Parameter:
    - state (current)
    - daftar_kendaraan: list objek Kendaraan
    - kapal

    Return:
    - list of state: semua neighbor
    '''
    daftar_neighbor = []
    n = len(state)

    # Mengubah arah
    for i, posisi in enumerate(state):
        # Skip kendaraan yang gapunya posisi (gaaada arah)
        if posisi is None:
            continue
        # Skip Kendaraan 1:1 (karena akan sama saja)
        if daftar_kendaraan[i].p == daftar_kendaraan[i].l:
            continue

        x, y, arah = posisi
        if arah == "V":
            arah_baru = "H"
        else:
            arah_baru = "V"

        new_state = state[:]
        new_state[i] = (x, y, arah_baru)
        daftar_neighbor.append(new_state)

    # 2a. Pindahkan 1 Kendaraan di dalam kapal ke koordinat lain di dalam kapal juga
    for i, posisi in enumerate(state):
        if posisi is None:
            continue

        x, y, arah = posisi
        k = daftar_kendaraan[i]
        if arah == "H":
            ukuran_x, ukuran_y = k.p, k.l
        elif arah == "V":
            ukuran_x, ukuran_y = k.l, k.p

        # Hanya pindahkan ke titik yang membuat seluruh badannya tetap di dalam Kapal
        for x_baru in range(kapal.dp - ukuran_x+1):
            for y_baru in range(kapal.dl - ukuran_y+1):
                if (x_baru,y_baru) == (x,y):
                    continue
                new_state = state[:]
                new_state[i] = (x_baru, y_baru, arah)
                daftar_neighbor.append(new_state)

    # 2b. Pindahlan 1 Kendaraan di luar kapal ke koordinat dalam kapal
    for i, posisi in enumerate(state):
        if posisi is not None:
            continue

        k = daftar_kendaraan[i]
        ukuran_x, ukuran_y = k.p, k.l

        for x in range(kapal.dp - ukuran_x + 1):
            for y in range(kapal.dl - ukuran_y + 1):
                new_state = state[:]
                new_state[i] = (x, y, "H") #Default pas masuk Horizontal
                daftar_neighbor.append(new_state)

    # 2c. Memindahkan 1 Kendaraan di dalam ke luar (None)
    for i, posisi in enumerate(state):
        if posisi is None:
            continue

        new_state = state[:]
        new_state[i] = None
        daftar_neighbor.append(new_state)

    # Menukar posisi 2 Kendaraan 
    for i in range(n):
        for j in range(i+1, n):
            if state[i] is None and state[j] is None: #Skip kalau 2 2 nya di luar
                continue
            new_state = state[:]
            new_state[i], new_state[j] = new_state[j], new_state[i]
            daftar_neighbor.append(new_state)

    return daftar_neighbor

    