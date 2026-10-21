import math
import random
import time
from objective_function import objective_function
from utils import random_initial_state

def _ukuran(kendaraan, arah):
    """Ukuran (x, y) kendaraan sesuai arah."""
    if arah == "H":
        return kendaraan.p, kendaraan.l 
    return kendaraan.l, kendaraan.p

def _posisi_acak(kendaraan, kapal, arah):
    """Posisi (x, y) acak yang membuat seluruh badan kendaraan tetap di kapal"""
    ukuran_x, ukuran_y = _ukuran(kendaraan, arah)
    x = random.randint(0, max(0, kapal.dp-ukuran_x))
    y = random.randint(0, max(0, kapal.dp-ukuran_y))

    return x, y

class Genetic: 
    """Geneteic Algorithm (GA) untukk memaksimalkan objective_function.
    Pola pemakaian : ga = Genetic(daftar_kendaraan, kapal, pop_size, iterations)
    ga.run()
    Param yg bisa diubah : 
    - pop_size (jumlah individu (kendaraan))
    - iterations : banyak generasi

    Hyperparam tetap : crossover_rate, mutation_rate, tournament_k, elite
 
    Atribut hasil (setelah run()):
    - initial_state: individu terbaik di populasi awal
    - final_state: individu terbaik yang pernah ditemukan
    - final_value: objective final_state
    - candidate_peak: nilai maksimum populasi pada generasi terakhir
    - history: list of dict {"iterasi", "value" (max populasi), "avg" (rata-rata populasi)}
    - duration: lama pencarian (detik)
    """

    def __init__(self, daftar_Kendaraan, kapal, pop_size=50, iterations=100,
                crossover_rate = 0.9, mutation_rate=0.3, tournament_k=3, elite=2):
        self.daftar_kendaraan = daftar_Kendaraan
        self.kapal = kapal
        self.pop_size = pop_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_k = tournament_k
        self.elite = min(elite, pop_size)
 
        self.initial_state = None
        self.initial_value = None
        self.final_state = None
        self.final_value = None
        self.candidate_peak = None
        self.history = []
        self.duration = 0
        self.iterations = iterations

    def evaluate(self, population):
        return [objective_function(state, self.daftar_kendaraan, self.kapal)
                for state in population]

    def tournament(self, population, fitness):
        """Seleki tournament: ambik k individu acak dan kembalikan yg objectivenya tertinggi"""
        picked = random.sample(range(len(population)), min(self.tournament_k, len(population)))
        winner = max(picked, key=lambda i: fitness[i])
        return population[winner]

    def crossover(self, parent_a, parent_b):
        """Uniform crossover: tiap gen (1 kendaraan) diambil dari parent A atau B dengan peluang sama.
        Posisi ke-i selalu kendaraan ke-i. Return 2 anak (masing-masing berupa state).."""
        child_1, child_2 = [], []
        for gene_a, gene_b in zip(parent_a, parent_b): 
            if random.random() <0.5:
                child_1.append(gene_a)
                child_2.append(gene_b)
            else: 
                child_1.append(gene_b)
                child_2.append(gene_a)
        return child_1, child_2

    def mutate(self, state):
        """Mutasi: membuat 1 perubahaan acak pada 1 kendaraan. eg: 
        - No vehicle in ship : masukkan ke kapal dengan posisi acak
        - Vehicle avail in ship : ganti arah, pindah posisi, keluarkan
        return state : New state """
        new_state = state[:]
        i = random.randrange(len(new_state))
        kendaraan = self.daftar_kendaraan[i]
        posisi = new_state[i]

        if posisi is None:
            arah = random.choice(["H", "V"])
            x, y = _posisi_acak(kendaraan, self.kapal, arah)
            new_state[i] = (x, y, arah)
            return new_state

        x, y , arah = posisi
        move = random.choice(["rotate", "move", "remove"])

        #handling 1:1 vehicle

        if move == "rotate" and kendaraan.p == kendaraan.l :
            move = "move"

        if move == "rotate" : 
            new_state[i] = (x, y, "V" if arah == "H" else "H")
        elif move == "move" :
            x_baru, y_baru = _posisi_acak(kendaraan, self.kapal, arah)
            new_state[i] = (x_baru, y_baru, arah)
        else: 
            new_state[i] = None

        return new_state

    def run(self):
        start = time.perf_counter()

        #population initiation
        population = [
            random_initial_state(self.daftar_kendaraan, self.kapal)
            for _ in range(self.pop_size)
        ]           
        fitness = self.evaluate(population)

        best_idx = max(range(self.pop_size), key=lambda i: fitness[i])
        self.initial_state = population[best_idx]
        self.initial_value = fitness[best_idx]
        self.final_state = self.initial_state
        self.final_value = self.initial_value

        self.history = [{"iterasi" : 0,
                         "value" : max(fitness),
                         "avg" : sum(fitness)/self.pop_size}]

        #Genetic Loop

        for generasi in range(1, self.iterations + 1):
            #elitism : return is the best individual just as is
            order = sorted(range(self.pop_size), key=lambda i: fitness[i], reverse=True)
            next_pop = [population[i] for i in order [:self.elite]]

            while len(next_pop) < self.pop_size:
                parent_a = self.tournament(population, fitness)
                parent_b = self.tournament(population, fitness)

                if random.random() < self.crossover_rate:
                    child_1, child_2 = self.crossover(parent_a, parent_b)
                else:    
                    child_1, child_2 = parent_a[:], parent_b[:]

                for child in (child_1, child_2):
                    if random.random() < self.mutation_rate:
                        child = self.mutate(child)
                    if len(next_pop) < self.pop_size:
                        next_pop.append(child)

            population = next_pop
            fitness = self.evaluate(population)

            #reccord max and avrg
            gen_best = max(range(self.pop_size), key=lambda i: fitness[i])
            self.history.append({"iterasi": generasi,
                                 "value": fitness[gen_best],
                                 "avg": sum(fitness)/self.pop_size})

            if fitness[gen_best] > self.final_value:
                self.final_value = fitness[gen_best]
                self.final_state = population[gen_best]

        self.candidate_peak = self.history[-1]["value"]
        self.duration = time.perf_counter() - start