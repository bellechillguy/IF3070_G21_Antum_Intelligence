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

    