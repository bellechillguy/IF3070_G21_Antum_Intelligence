import argparse
import random
from pathlib import Path
import matplotlib.pyplot as plt
from algorithms.hc_steepest_ascent import HC_steepest
from algorithms.simulated_annealing import SimulatedAnnealing
from algorithms.genetic import Genetic
from utils import load_data, random_initial_state
from visualization import plot_hasil

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("algoritma", choices=["hc", "sa", "gen"])
    parser.add_argument("--seed", type=int)
    parser.add_argument("--output")
    #param for genetic run
    parser.add_argument("--population", type=int, default=50)
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()

    # Gunakan seed agar hasil random bisa direproduksi
    random.seed(args.seed)
    # Data dibaca relatif terhadap lokasi file main.py
    data_path = Path(__file__).parent / "data" / "data.json"
    kapal, daftar_kendaraan = load_data(data_path)
    initial_state = random_initial_state(daftar_kendaraan, kapal)

    if args.algoritma == "hc":
        algoritma = HC_steepest(initial_state, daftar_kendaraan, kapal)
        nama = "Hill Climbing - Steepest Ascent"
    elif args.algoritma == "sa":
        algoritma = SimulatedAnnealing(initial_state, daftar_kendaraan, kapal)
        nama = "Simulated Annealing"
    else:
        algoritma = Genetic(daftar_kendaraan, kapal, args.population, args.iterations)
        nama = "Genetic Algorithm"

    print(f"Menjalankan {nama}...")
    algoritma.run()
    print(f"Nilai akhir: {algoritma.final_value} | Durasi: {algoritma.duration:.2f} detik")

    #GA membuat populasi sendiri, initial state = individu terbaik dari populasi asal
    if args.algoritma == "gen":
        initial_state = algoritma.initial_state
        pop_size = algoritma.pop_size
    else:
        pop_size = None
    
    # stuck_count hanya digunakan oleh Simulated Annealing
    stuck_count = algoritma.stuck_count if args.algoritma == "sa" else None
    fig = plot_hasil(initial_state, algoritma.final_state, daftar_kendaraan, kapal,
                     algoritma.history, nama, algoritma.duration, stuck_count)
    if args.output:
        fig.savefig(args.output, dpi=150)
        print(f"Gambar disimpan ke {args.output}")
    else:
        plt.show()
    plt.close(fig)

if __name__ == "__main__":
    main()
