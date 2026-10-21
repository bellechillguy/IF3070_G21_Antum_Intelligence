import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from utils import objective_function

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

    iterasi = [h["iterasi"] for h in history]
    value = [h["value"] for h in history]

    #GA : history memiliki "avg" : rata-rata populasi, "value" : max populasi
    ada_avg = any("avg" in h for h in history)
    if ada_avg:
        axes[1, 0].plot(iterasi, value, marker=".", markersize=3, label="Maksimum populasi")
        axes[1, 0].plot(iterasi, [h["avg"] for h in history], linewidth=1, label="Rata-rata populasi")
        axes[1, 0].legend()
    else:
        axes[1, 0].plot(iterasi, value, marker=".", markersize=3)
        axes[1, 0].set_title("Perubahan nilai objective")
        axes[1, 0].set_xlabel("Iterasi")
        axes[1, 0].set_ylabel("Value")
        axes[1, 0].grid(alpha=0.25)

    ringkasan = f"Durasi: {duration:.2f} detik\nIterasi: {iterasi[-1]}"
    if stuck_count is not None:
        ringkasan += f"\nStuck: {stuck_count} iterasi"
    fig.suptitle(nama_algoritma + "\n" + ringkasan)

    # Grafik probabilitas hanya tersedia untuk Simulated Annealing
    history_probability = [h for h in history if h.get("probability") is not None]
    if history_probability:
        axes[1, 1].plot([h["iterasi"] for h in history_probability],
                        [h["probability"] for h in history_probability], linewidth=0.8)
        axes[1, 1].set_title("Probabilitas penerimaan neighbor")
        axes[1, 1].set_xlabel("Iterasi")
        axes[1, 1].set_ylabel("Probabilitas")
        axes[1, 1].set_ylim(-0.05, 1.05)
        axes[1, 1].grid(alpha=0.25)
    else:
        axes[1, 1].axis("off")

    return fig
