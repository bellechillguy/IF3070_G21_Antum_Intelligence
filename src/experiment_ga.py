import csv
import json
import random
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # simpan gambar saja, tidak membuka jendela plot
import matplotlib.pyplot as plt
from algorithms.genetic import Genetic
from utils import load_data
from visualization import plot_hasil

#### EKSPERIMEN CONFIG (CHANGE HERE) #####
SEEDS = [1, 2, 3]                  # 3 run per konfigurasi, tiap run seed berbeda

#1: Kontrol : Populasi
POP_KONTROL = 30
ITER_VARIASI = [50, 100, 200]

#2: Kontrol : Iterasi
ITER_KONTROL = 100
POP_VARIASI = [20, 50, 100]

DATA_PATH = Path(__file__).parent / "data" / "data.json"
OUT_DIR = Path(__file__).parent.parent / "results" / "ga1"


def jalankan(grup, pop_size, iterations, seed, daftar_kendaraan, kapal):
    '''Menjalankan 1 run GA, menyimpan plot, dan mengembalikan ringkasan hasilnya.'''
    random.seed(seed)
    ga = Genetic(daftar_kendaraan, kapal, pop_size, iterations)
    ga.run()

    nama_file = f"{grup}_pop{pop_size}_iter{iterations}_seed{seed}"
    fig = plot_hasil(ga.initial_state, ga.final_state, daftar_kendaraan, kapal,
                     ga.history, "Genetic Algorithm", ga.duration, None, pop_size)
    fig.savefig(OUT_DIR / f"{nama_file}.png", dpi=150)
    plt.close(fig)

    return {
        "grup": grup,
        "pop_size": pop_size,
        "iterations": iterations,
        "seed": seed,
        "initial_value": ga.initial_value,
        "final_value": ga.final_value,
        "candidate_peak": ga.candidate_peak,
        "duration": round(ga.duration, 4),
        "initial_state": ga.initial_state,
        "final_state": ga.final_state,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    kapal, daftar_kendaraan = load_data(DATA_PATH)

    konfigurasi = []
    for it in ITER_VARIASI:
        konfigurasi.append(("kontrol_populasi", POP_KONTROL, it))
    for pop in POP_VARIASI:
        konfigurasi.append(("kontrol_iterasi", pop, ITER_KONTROL))

    # CSV ditulis per run, jadi hasil parsial tetap tersimpan kalau skrip berhenti di tengah
    kolom = ["grup", "pop_size", "iterations", "seed", "initial_value",
             "final_value", "candidate_peak", "duration"]
    hasil = []
    with open(OUT_DIR / "hasil.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=kolom, extrasaction="ignore")
        writer.writeheader()
        for grup, pop, it in konfigurasi:
            for seed in SEEDS:
                print(f"[{grup}] pop={pop} iter={it} seed={seed} ...", end=" ", flush=True)
                r = jalankan(grup, pop, it, seed, daftar_kendaraan, kapal)
                hasil.append(r)
                writer.writerow(r)
                f.flush()
                print(f"final={r['final_value']} durasi={r['duration']}s")

    # State awal dan akhir lengkap ke JSON
    with open(OUT_DIR / "states.json", "w") as f:
        json.dump(hasil, f, indent=2)

    # Ringkasan per konfigurasi (rata-rata, min, max dari 3 run)
    print("\n=== Ringkasan per konfigurasi ===")
    print(f"{'grup':18} {'pop':>5} {'iter':>5} {'mean':>9} {'min':>9} {'max':>9} {'durasi':>8}")
    for grup, pop, it in konfigurasi:
        run = [r for r in hasil
               if r["grup"] == grup and r["pop_size"] == pop and r["iterations"] == it]
        nilai = [r["final_value"] for r in run]
        durasi = sum(r["duration"] for r in run) / len(run)
        print(f"{grup:18} {pop:5} {it:5} {sum(nilai)/len(nilai):9.1f} "
              f"{min(nilai):9} {max(nilai):9} {durasi:7.2f}s")

    print(f"\nHasil disimpan di: {OUT_DIR}")


if __name__ == "__main__":
    main()