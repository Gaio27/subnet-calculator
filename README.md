# Subnet Calculator dan VLSM

Alat baris perintah untuk menghitung subnet, membagi blok IP ke beberapa kebutuhan host (VLSM), dan memeriksa tumpang tindih alamat. Dibuat untuk latihan subnetting yang bisa diuji otomatis.

## Masalah

Menghitung subnet dengan tangan rawan salah, terutama saat ada banyak VLAN dengan kebutuhan host berbeda. Alat ini memberikan hasil yang bisa dicek ulang dengan metode blok ukuran.

## Pendekatan

- Python dengan library bawaan `ipaddress`, sehingga tidak perlu dependensi tambahan.
- `argparse` untuk antarmuka baris perintah.
- `pytest` untuk pengujian kasus normal dan kasus tepi (/30, /31, /32).

## Fitur

- Menampilkan alamat jaringan, broadcast, netmask, dan rentang host dari satu CIDR.
- Membagi satu blok induk ke beberapa subnet berdasarkan daftar kebutuhan host (VLSM), dari yang terbesar ke terkecil.
- Memeriksa apakah dua CIDR saling tumpang tindih.

## Arsitektur

```text
src/
  subnet_calc.py     # fungsi inti: hitung, bagi, periksa tumpang tindih
  cli.py             # antarmuka argparse
tests/
  test_subnet_calc.py
```

## Cara menjalankan
```
git clone https://github.com/Gaio27/subnet-calculator.git
cd subnet-calculator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
## Informasi satu subnet
```
python3 src/cli.py info 192.168.10.0/26
```
## VLSM: blok induk dan daftar kebutuhan host
```
python3 src/cli.py vlsm 10.10.0.0/16 --hosts 500 200 50 10
```
## Jalankan pengujian
```
pytest -v
```
## Contoh Keluaran
```
Blok induk: 10.10.0.0/16
Subnet 1: 10.10.0.0/23     (500 host dibutuhkan, 510 tersedia)
Subnet 2: 10.10.2.0/24     (200 host dibutuhkan, 254 tersedia)
Subnet 3: 10.10.3.0/26     (50 host dibutuhkan, 62 tersedia)
Subnet 4: 10.10.3.64/28    (10 host dibutuhkan, 14 tersedia)
```
Keluaran di atas telah diverifikasi melalui pengujian otomatis (test_vlsm_matches_readme_example).

## Hasil
- Jumlah kasus pengujian: 12 item (tests/test_subnet_calc.py)
- Hasil pytest: 12 passed in 0.02s (Python 3.12.3, pytest-9.2.0)

## Yang saya pelajari dan akan saya perbaiki
- Tantangan utama adalah mengurutkan kebutuhan host dari yang terbesar agar VLSM tidak menyisakan celah yang tidak efisien.
- Rencana berikutnya: mendukung input dari file CSV dan keluaran JSON untuk otomasi.

## Lisensi
MIT
