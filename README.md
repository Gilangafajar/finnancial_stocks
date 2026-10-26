# Radar Saham IDX (hampir realtime, otomatis)

Dashboard screening saham IDX: valuasi (PER/PBV/ROE), teknikal (MA50/MA200, RSI, momentum), lonjakan volume, arus asing (input manual), dan pencarian kode/nama saham.

**Bukan rekomendasi investasi.** Data dari Yahoo Finance (via `yfinance`), tertunda sekitar 10–20 menit. Ini bukan feed tick realtime.

## Cara kerja
- `update_prices.py` (GitHub Actions, tiap 15 menit pada jam bursa) menulis `data/market.json`.
- `update_fundamentals.py` (harian, 18.30 WIB) menulis `data/fundamentals.json`.
- `index.html` membaca kedua berkas itu dan memuat ulang sendiri tiap 60 detik.
- `data/asing.csv` diisi manual bila Anda ingin skor arus asing (format: `kode,net_miliar,tanggal`).

## Pasang di GitHub (repo baru, mis. `radar-saham`)
1. Buat repository **Public**, lalu upload `index.html`, `tickers.txt`, `requirements.txt`, `common.py`, `update_prices.py`, `update_fundamentals.py`, `README.md`, dan folder `data/`.
2. Berkas workflow harus berada di `.github/workflows/`. Karena folder berawalan titik sering tidak ikut ter-upload lewat drag-and-drop, buat lewat **Add file → Create new file**, ketik nama `.github/workflows/update-prices.yml`, lalu tempel isinya. Ulangi untuk `update-fundamentals.yml`.
3. **Settings → Actions → General → Workflow permissions**: pilih **Read and write permissions**, Save.
4. Tab **Actions**: jalankan **Update fundamental (harian)** dengan *Run workflow* (butuh ±5–15 menit), lalu **Update harga (jam bursa)**.
5. **Settings → Pages**: Source **Deploy from a branch**, branch `main`, folder `/ (root)`, Save.
6. Buka `https://USERNAME.github.io/NAMA-REPO/`.

## Menambah saham ke pencarian
Edit `tickers.txt` (satu kode per baris, tanpa `.JK`), lalu jalankan kedua workflow sekali. Semua ±950 kode IDX bisa dimasukkan, tapi workflow fundamental menjadi lebih lama.

## Batasan yang perlu diketahui
- Jadwal GitHub Actions bisa tertunda beberapa menit dan tidak menjamin tepat waktu. Hari libur bursa tetap menjalankan skrip (data tidak berubah).
- Yahoo Finance bukan sumber resmi dan bisa mengubah format atau memblokir permintaan; skrip mungkin perlu diperbaiki.
- Net buy/sell asing dan broker summary ("bandar") tidak punya sumber gratis yang stabil. Dashboard hanya menampilkan lonjakan volume sebagai petunjuk aktivitas besar, yang bukan bukti akumulasi pihak tertentu.
- Riwayat commit akan bertambah banyak karena data disimpan di repo. Itu aman; bisa dibersihkan bila perlu.
