import time
from utils import objective_function, get_neighbors

class HC_steepest:
    '''
    Hill Climbing Steepest Ascent
    1x iterasi: 
    - Periksa semua neighbor, lalu pilih neighbor dengan value tertinggi
    - Jika value neighbor terpilih > value state sekarang, pindah.
    - Jika value neighbor terpilih <= value state sekarang, terminate dan kembalikan solusi.
    '''
    def __init__(self, initial_state, daftar_kendaraan, kapal):
        self.initial_state = initial_state
        self.daftar_kendaraan = daftar_kendaraan
        self.kapal = kapal
        self.iteration_count = 0
        self.duration = 0
        self.final_state = None 
        self.final_value = None 
        self.history = []

    def run(self):
        # Inisialisasi
        self.history = []
        self.iteration_count = 0
        waktu_mulai = time.time()

        # Memulai dengan initial state
        current_state = self.initial_state[:]
        current_value = objective_function(current_state, self.daftar_kendaraan, self.kapal)
        self.history.append({
            "iterasi": self.iteration_count,
            "value": current_value
        })

        while True:
            # Cari semua suksesor/neighbor
            neighbors = get_neighbors(current_state, self.daftar_kendaraan, self.kapal)
            if not neighbors:
                break

            # Cari neighbor yang punya value terbaik
            highest_value = float("-inf")
            best_neighbor = None 
            for n in neighbors:
                neighbor_value = objective_function(n, self.daftar_kendaraan, self.kapal)
                if neighbor_value > highest_value:
                    highest_value = neighbor_value
                    best_neighbor = n

            # Tidak menerima jika value neighbor terpilih <= current value, terminate
            if highest_value <= current_value:
                break

            # Pindah ke best neighbor, perbarui current value
            current_state = best_neighbor
            current_value = highest_value
            self.iteration_count += 1
            self.history.append({
                "iterasi": self.iteration_count,
                "value": current_value
            })

        self.final_state = current_state
        self.final_value = current_value
        self.duration = time.time() - waktu_mulai