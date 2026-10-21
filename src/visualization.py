import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from utils import (objective_function, hitung_fee, cek_pelanggaran_kapasitas,
                   cek_pelanggaran_overlap, cek_pelanggaran_keluar_kapal)

def plot_state(ax, state, daftar_kendaraan, kapal, judul):
    warna = plt.get_cmap("tab20")
    tidak_diangkut = []
    x_min, x_max = 0, kapal.dp
    y_min, y_max = 0, kapal.dl

    ax.add_patch(Rectangle((0, 0), kapal.dp, kapal.dl,
                           facecolor="whitesmoke", edgecolor="black", linewidth=2))
    for i, posisi in enumerate(state):
        kendaraan = daftar_kendaraan[i]
        if posisi is None:
            tidak_diangkut.append(kendaraan.id)
            continue

        x, y, arah = posisi
        # Tukar panjang dan lebar untuk orientasi vertikal
        if arah == "H":
            ukuran_x, ukuran_y = kendaraan.p, kendaraan.l
        else:
            ukuran_x, ukuran_y = kendaraan.l, kendaraan.p

        ax.add_patch(Rectangle((x, y), ukuran_x, ukuran_y,
                               facecolor=warna(i % 20), edgecolor="black", alpha=0.6))
        ax.text(x + ukuran_x / 2, y + ukuran_y / 2, kendaraan.id,
                ha="center", va="center", fontsize=7)
        # Perluas batas plot jika posisi kendaraan melewati ukuran kapal
        x_min, x_max = min(x_min, x), max(x_max, x + ukuran_x)
        y_min, y_max = min(y_min, y), max(y_max, y + ukuran_y)

    ax.set_xlim(x_min - 0.5, x_max + 0.5)
    ax.set_ylim(y_max + 0.5, y_min - 0.5)
    ax.set_aspect("equal")
    ax.set_xticks(range(x_min, x_max + 1))
    ax.set_yticks(range(y_min, y_max + 1))
    ax.tick_params(labelsize=8)
    ax.grid(alpha=0.25)
    value = objective_function(state, daftar_kendaraan, kapal)
    ax.set_title(f"{judul} | Value: {value}")
    daftar_id = ", ".join(tidak_diangkut) if tidak_diangkut else "-"
    ax.set_xlabel("Tidak diangkut: " + daftar_id, fontsize=8)

def plot_hasil(initial_state, final_state, daftar_kendaraan, kapal,
               history, nama_algoritma, duration, stuck_count=None, pop_size = None):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), layout="constrained")
    plot_state(axes[0, 0], initial_state, daftar_kendaraan, kapal, "Initial state")
    plot_state(axes[0, 1], final_state, daftar_kendaraan, kapal, "Final state")

    plot_history(axes[1], history)

    ringkasan = f"Durasi: {duration:.2f} detik\nIterasi: {history[-1]['iterasi']}"
    if stuck_count is not None:
        ringkasan += f"\nLangkah lebih buruk ditolak: {stuck_count}"
    fig.suptitle(nama_algoritma + "\n" + ringkasan)

    return fig

def plot_history(axes, history):
    iterasi = [h["iterasi"] for h in history]
    value = [h["value"] for h in history]

    #GA : history memiliki "avg" : rata-rata populasi, "value" : max populasi
    ada_avg = any("avg" in h for h in history)
    if ada_avg:
        axes[0].plot(iterasi, value, marker=".", markersize=3, label="Maksimum populasi")
        axes[0].plot(iterasi, [h["avg"] for h in history], linewidth=1, label="Rata-rata populasi")
        axes[0].legend()
    else:
        axes[0].plot(iterasi, value, marker=".", markersize=3)
        axes[0].set_title("Perubahan nilai objective")
        axes[0].set_xlabel("Iterasi")
        axes[0].set_ylabel("Value")
        axes[0].grid(alpha=0.25)

    # Grafik probabilitas hanya tersedia untuk Simulated Annealing
    history_probability = [h for h in history if h.get("probability") is not None]
    if history_probability:
        axes[1].plot([h["iterasi"] for h in history_probability],
                        [h["probability"] for h in history_probability], linewidth=0.8)
        axes[1].set_title("Probabilitas penerimaan neighbor")
        axes[1].set_xlabel("Iterasi")
        axes[1].set_ylabel("Probabilitas")
        axes[1].set_ylim(-0.05, 1.05)
        axes[1].grid(alpha=0.25)
    else:
        axes[1].axis("off")

def simpan_state(state, daftar_kendaraan, kapal, judul, path):
    fig, ax = plt.subplots(figsize=(14, 8), layout="constrained")
    plot_state(ax, state, daftar_kendaraan, kapal, judul)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    total_berat = sum(k.berat for k, posisi in zip(daftar_kendaraan, state)
                      if posisi is not None)
    baris = [
        f"### {judul.upper()} ###",
        f"Objective: {objective_function(state, daftar_kendaraan, kapal)}",
        f"Total fee: {hitung_fee(state, daftar_kendaraan)}",
        f"Berat: {total_berat}/{kapal.kapasitas}",
        f"Kelebihan kapasitas: {cek_pelanggaran_kapasitas(state, daftar_kendaraan, kapal)}",
        f"Sel overlap: {cek_pelanggaran_overlap(state, daftar_kendaraan, kapal)}",
        f"Sel keluar kapal: {cek_pelanggaran_keluar_kapal(state, daftar_kendaraan, kapal)}",
        "",
        "ID | Posisi (x, y, arah) | Dimensi (p, l) | Berat | Fee"
    ]
    for k, posisi in zip(daftar_kendaraan, state):
        lokasi = str(posisi) if posisi is not None else "Tidak diangkut"
        baris.append(f"{k.id} | {lokasi} | ({k.p}, {k.l}) | {k.berat} | {k.fee}")
    return "\n".join(baris)

def simpan_hasil_sa(sa, daftar_kendaraan, kapal, folder, seed):
    folder.mkdir(parents=True, exist_ok=True)
    hasil = {
        "seed": seed,
        "parameters": {
            "initial_temperature": sa.initial_temperature,
            "cooling_rate": sa.cooling_rate,
            "minimum_temperature": sa.minimum_temperature
        },
        "kapal": vars(kapal),
        "kendaraan": [vars(k) for k in daftar_kendaraan],
        "initial_state": sa.initial_state,
        "final_state": sa.final_state,
        "initial_value": sa.history[0]["value"],
        "final_value": sa.final_value,
        "duration": sa.duration,
        "iteration_count": sa.iteration_count,
        "rejected_worse_moves": sa.stuck_count,
        "history": sa.history
    }
    with open(folder / "SA.json", "w", encoding="utf-8") as file:
        json.dump(hasil, file, indent=2)
        file.write("\n")

    awal = simpan_state(sa.initial_state, daftar_kendaraan, kapal,
                        "Initial state", folder / "initial.png")
    akhir = simpan_state(sa.final_state, daftar_kendaraan, kapal,
                         "Final state", folder / "final.png")
    ringkasan = (
        f"Simulated Annealing | {folder.name} | Seed {seed}\n"
        f"Initial temperature: {sa.initial_temperature}\n"
        f"Cooling rate: {sa.cooling_rate}\n"
        f"Minimum temperature: {sa.minimum_temperature}\n"
        f"Nilai akhir: {sa.final_value}\n"
        f"Durasi pencarian: {sa.duration:.4f} detik\n"
        f"Iterasi: {sa.iteration_count}\n"
        f"Langkah lebih buruk ditolak: {sa.stuck_count}\n\n"
    )
    (folder / "SA_info.txt").write_text(ringkasan + awal + "\n\n" + akhir + "\n",
                                       encoding="utf-8")

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), layout="constrained")
    plot_history(axes, sa.history)
    fig.suptitle(f"Simulated Annealing | {folder.name} | Seed {seed}")
    fig.savefig(folder / "plot.png", dpi=150)
    plt.close(fig)
