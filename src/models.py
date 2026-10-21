# Kelas untuk merepresentasikan Kapal
class Kapal:
    def __init__(self, dimensi_lebar, dimensi_panjang, kapasitas):
        self.dl = dimensi_lebar
        self.dp = dimensi_panjang
        self.kapasitas = kapasitas

# Kelas untuk merepresentasikan Kendaraan
class Kendaraan:
    def __init__(self, id, p, l, berat, fee, ETA):
        self.id = id
        self.p = p
        self.l = l
        self.berat = berat
        self.fee = fee
        self.ETA = ETA