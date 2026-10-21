## Menjalankan algoritma

Jalankan dari folder utama project. Jika belum punya environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Jalankan dari folder utama project:

```bash
python src/main.py sa --seed 21 --output-dir output/simulated_annealing/SA_run1
python src/main.py sa --seed 42 --output-dir output/simulated_annealing/SA_run2
python src/main.py sa --seed 63 --output-dir output/simulated_annealing/SA_run3
```