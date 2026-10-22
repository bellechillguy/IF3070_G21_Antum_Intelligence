import csv
import json
import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # simpan gambar saja, tidak membuka jendela plot
import matplotlib.pyplot as plt

from algorithms.genetic import Genetic
from utils import load_data
from visualization import plot_state, plot_history

#### EKSPERIMEN CONFIG (CHANGE HERE) #####
SEEDS = [5, 6, 7]  # 3 run per konfigurasi, tiap run seed berbeda

# 1: Kontrol populasi
POP_KONTROL = 30
ITER_VARIASI = [50, 100, 200]

# 2: Kontrol iterasi
ITER_KONTROL = 100
POP_VARIASI = [20, 50, 100]

DATA_PATH = Path(__file__).parent / "data" / "data.json"
OUT_DIR = Path(__file__).parent.parent / "output" / "genetic"


def folder_run_baru():
    """Buat folder GA_RUN dengan nomor berikutnya tanpa menimpa hasil lama."""
    nomor_run = 1
    while (OUT_DIR / f"GA_RUN{nomor_run}").exists():
        nomor_run += 1
    folder = OUT_DIR / f"GA_RUN{nomor_run}"
    folder.mkdir(parents=True)
    return folder


def simpan_visualisasi(folder, ga, daftar_kendaraan, kapal):
    """Simpan initial state, end state, dan grafik riwayat GA sebagai PNG."""
    for nama, state, judul in (
        ("initial_state.png", ga.initial_state, "Initial state"),
        ("end_state.png", ga.final_state, "End state"),
    ):
        fig, ax = plt.subplots(figsize=(14, 8), layout="constrained")
        plot_state(ax, state, daftar_kendaraan, kapal, judul)
        fig.savefig(folder / nama, dpi=150)
        plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), layout="constrained")
    plot_history(axes, ga.history)
    fig.suptitle(f"Genetic Algorithm | {folder.parent.name} | {folder.name}")
    fig.savefig(folder / "plot.png", dpi=150)
    plt.close(fig)


def jalankan(kategori, nama_eksperimen, pop_size, iterations, seed,
             folder_run, daftar_kendaraan, kapal):
    """Menjalankan satu run GA dan menyimpan tiga visualisasinya."""
    random.seed(seed)
    ga = Genetic(daftar_kendaraan, kapal, pop_size, iterations)
    ga.run()

    folder_eksperimen = folder_run / kategori / nama_eksperimen
    folder_eksperimen.mkdir(parents=True, exist_ok=True)
    simpan_visualisasi(folder_eksperimen, ga, daftar_kendaraan, kapal)

    return {
        "grup": kategori,
        "eksperimen": nama_eksperimen,
        "pop_size": pop_size,
        "iterations": iterations,
        "seed": seed,
        "initial_value": ga.initial_value,
        "final_value": ga.final_value,
        "candidate_peak": ga.candidate_peak,
        "duration": round(ga.duration, 4),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    folder_run = folder_run_baru()
    kapal, daftar_kendaraan = load_data(DATA_PATH)

    konfigurasi = []
    for it in ITER_VARIASI:
        konfigurasi.append(("pop_kontrol", f"iter_{it}_pop_{POP_KONTROL}", POP_KONTROL, it))
    for pop in POP_VARIASI:
        konfigurasi.append(("iter_kontrol", f"pop_{pop}_iter_{ITER_KONTROL}", pop, ITER_KONTROL))

    hasil = []
    kolom_csv = ["grup", "eksperimen", "pop_size", "iterations", "seed",
                 "initial_value", "final_value", "candidate_peak", "duration"]
    with open(folder_run / "hasil.csv", "w", newline="", encoding="utf-8") as file_csv:
        writer = csv.DictWriter(file_csv, fieldnames=kolom_csv)
        writer.writeheader()
        for kategori, nama_eksperimen, pop, it in konfigurasi:
            for seed in SEEDS:
                nama_run = f"{nama_eksperimen}_seed_{seed}"
                print(f"[{kategori}/{nama_run}] ...", end=" ", flush=True)
                ringkasan = jalankan(kategori, nama_run, pop, it, seed, folder_run,
                                     daftar_kendaraan, kapal)
                hasil.append(ringkasan)
                writer.writerow(ringkasan)
                file_csv.flush()
                print(f"final={ringkasan['final_value']} durasi={ringkasan['duration']}s")

    with open(folder_run / "states.json", "w", encoding="utf-8") as file_json:
        json.dump(hasil, file_json, indent=2)
        file_json.write("\n")

    # Ringkasan per konfigurasi (rata-rata, min, max dari 3 run)
    print("\n=== Ringkasan per konfigurasi ===")
    print(f"{'grup':18} {'pop':>5} {'iter':>5} {'mean':>9} {'min':>9} {'max':>9} {'durasi':>8}")
    for kategori, _, pop, it in konfigurasi:
        run = [r for r in hasil
               if r["grup"] == kategori and r["pop_size"] == pop and r["iterations"] == it]
        nilai = [r["final_value"] for r in run]
        durasi = sum(r["duration"] for r in run) / len(run)
        print(f"{kategori:18} {pop:5} {it:5} {sum(nilai)/len(nilai):9.1f} "
              f"{min(nilai):9} {max(nilai):9} {durasi:7.2f}s")

    print(f"\nHasil disimpan di: {folder_run}")


if __name__ == "__main__":
    main()
