import math
import random
import time
from utils import objective_function, get_neighbors

class SimulatedAnnealing:
    def __init__(self, initial_state, daftar_kendaraan, kapal,
                 initial_temperature=1000, cooling_rate=0.995, minimum_temperature=0.1):
        if not 0 < minimum_temperature < initial_temperature < math.inf:
            raise ValueError("Temperature harus bernilai positif dan minimum < initial")
        if not 0 < cooling_rate < 1:
            raise ValueError("Cooling rate harus berada di antara 0 dan 1")

        self.initial_state = initial_state
        self.daftar_kendaraan = daftar_kendaraan
        self.kapal = kapal
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.minimum_temperature = minimum_temperature
        self.iteration_count = 0
        self.duration = 0
        self.final_state = None
        self.final_value = None
        self.history = []
        self.stuck_count = 0 # Jumlah langkah lebih buruk yang ditolak

    def run(self):
        self.history = []
        self.iteration_count = 0
        self.stuck_count = 0
        waktu_mulai = time.time()

        current_state = self.initial_state[:]
        current_value = objective_function(current_state, self.daftar_kendaraan, self.kapal)
        temperature = self.initial_temperature
        self.history.append({
            "iterasi": self.iteration_count,
            "value": current_value,
            "probability": None
        })

        while temperature > self.minimum_temperature:
            neighbors = get_neighbors(current_state, self.daftar_kendaraan, self.kapal)
            if not neighbors:
                break

            neighbor = random.choice(neighbors)
            neighbor_value = objective_function(neighbor, self.daftar_kendaraan, self.kapal)
            delta_e = neighbor_value - current_value

            if delta_e >= 0:
                probability = 1.0
            else:
                probability = math.exp(delta_e / temperature)

            if delta_e >= 0 or random.random() < probability:
                current_state = neighbor
                current_value = neighbor_value
            else:
                self.stuck_count += 1

            self.iteration_count += 1
            self.history.append({
                "iterasi": self.iteration_count,
                "value": current_value,
                "probability": probability
            })
            temperature *= self.cooling_rate

        self.final_state = current_state
        self.final_value = current_value
        self.duration = time.time() - waktu_mulai