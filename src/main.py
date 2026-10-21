import argparse
import random
from pathlib import Path
import matplotlib.pyplot as plt
from algorithms.hc_steepest_ascent import HC_steepest
from algorithms.simulated_annealing import SimulatedAnnealing
from algorithms.genetic import Genetic
from utils import load_data, random_initial_state
from visualization import plot_hasil, simpan_hasil_sa

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("algoritma", choices=["hc", "sa", "gen"])
    parser.add_argument("--seed", type=int)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--output", type=Path)
    output.add_argument("--output-dir", type=Path)
    # Parameter khusus Genetic Algorithm
    parser.add_argument("--population", type=int, default=50)
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()
    if args.output_dir is not None and args.algoritma != "sa":
        parser.error("--output-dir hanya untuk SA")

    random.seed(args.seed)
    data_path = Path(__file__).parent / "data" / "data.json"
    kapal, daftar_kendaraan = load_data(data_path)
    if args.algoritma in ("hc", "sa"):
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

    if args.output_dir is not None:
        simpan_hasil_sa(algoritma, daftar_kendaraan, kapal, args.output_dir, args.seed)
        print(f"Output disimpan ke {args.output_dir}")
        return

    # GA menggunakan individu terbaik dari populasi awal untuk visualisasi
    if args.algoritma == "gen":
        initial_state = algoritma.initial_state

    rejected_moves = algoritma.rejected_moves if args.algoritma == "sa" else None
    fig = plot_hasil(initial_state, algoritma.final_state, daftar_kendaraan, kapal,
                     algoritma.history, nama, algoritma.duration, rejected_moves)
    if args.output:
        fig.savefig(args.output, dpi=150)
        print(f"Gambar disimpan ke {args.output}")
    else:
        plt.show()
    plt.close(fig)

if __name__ == "__main__":
    main()
