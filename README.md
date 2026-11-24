# SIPP Karhutla — Sistem Informasi Pencegahan Kebakaran Hutan dan Lahan

Prototipe dashboard pemantauan risiko kebakaran, prediksi tiga kelas berbasis XGBoost, dan rekomendasi prioritas patroli. Aplikasi ini adalah alat bantu petugas, bukan pengganti verifikasi lapangan atau otoritas penanganan kebakaran.

## Latar belakang dan tujuan

Pemantauan titik panas, cuaca, kekeringan vegetasi, riwayat kejadian, dan cakupan patroli dapat membantu petugas menentukan lokasi yang perlu diperiksa lebih dahulu. SIPP Karhutla menyatukan visualisasi peta, prediksi risiko (Low/Medium/High), data patroli demonstrasi, dan penjelasan faktor pemicu dalam antarmuka lokal.

## Fitur

- Dashboard ringkasan hotspot, sebaran kelas risiko, dan aktivitas patroli.
- Peta Leaflet dengan tile OpenStreetMap serta marker berwarna menurut label data demonstrasi.
- Prediksi XGBoost dan probabilitas kelas; preprocessing imputer dan scaler disimpan bersama model.
- Form input patroli dan rekomendasi berprioritas berdasarkan prediksi.
- Status **Perlu Verifikasi Petugas** untuk data tidak lengkap/kedaluwarsa atau confidence < 0,60.
- Ekspor ringkasan CSV.
- Skema PostgreSQL/PostGIS disediakan; demo saat ini memakai CSV dan memori proses untuk patroli.

## Teknologi

Python 3.10+, Flask, Flask-CORS, pandas, scikit-learn, XGBoost, joblib, PostgreSQL/PostGIS (opsional), HTML/CSS/JavaScript, Leaflet, OpenStreetMap.

## Struktur repositori

```text
sipp-karhutla/
├── frontend/ (index.html, css/style.css, js/script.js)
├── backend/ (main.py, routes/, services/)
├── model/ (train_model.py, predict.py, saved_model/)
├── dataset/dummy_data.csv
├── database/schema.sql
├── requirements.txt
├── .env.example
└── README.md
```

## Arsitektur

```text
Browser (HTML/CSS/JS + Leaflet)
          │ HTTP/JSON
          ▼
Flask API: dashboard, hotspot, prediction, patrol, recommendation, health
      ├── services: data / XGBoost inference / recommendation
      ├── dataset/dummy_data.csv
      └── model/saved_model/risk_model.joblib (dibuat saat training)
          │ (rancangan untuk integrasi berikutnya)
          ▼
PostgreSQL + PostGIS — database/schema.sql
```

## Menjalankan secara lokal

Prasyarat: Python 3.10 atau lebih baru dan pip. Tile peta/Google Fonts memerlukan koneksi internet. Dari root repository:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env   # Windows: copy .env.example .env
python model/train_model.py
python backend/main.py
```

API berjalan di `http://127.0.0.1:5000`. Buka `frontend/index.html` langsung di browser, atau layani direktori frontend dengan server statis (terminal kedua):

```bash
python -m http.server 8080 --directory frontend
```

Lalu buka `http://127.0.0.1:8080`. Frontend mengakses API di `http://127.0.0.1:5000/api`; ubah `API_BASE` dalam `frontend/js/script.js` jika host/port backend berbeda. Flask-CORS diaktifkan untuk demonstrasi lokal.

### Pelatihan dan inferensi model

```bash
python model/train_model.py
python model/predict.py
```

Pelatihan mencetak accuracy, macro precision/recall/F1, confusion matrix, dan classification report. **Metrik hanya hasil pemisahan data sintetis; tidak menunjukkan performa lapangan.** File model tidak disimpan di Git (diabaikan oleh `.gitignore`); jalankan training setelah instalasi.

## Konfigurasi PostgreSQL/PostGIS

Demo belum membaca/menulis PostgreSQL. `DATABASE_URL` pada `.env.example` disiapkan untuk pengembangan integrasi selanjutnya; saat ini penyimpanan patroli hanya berada di memori dan kembali ke data contoh saat proses dimulai ulang. Untuk menyiapkan rancangan skema (PostGIS harus sudah terpasang dan database telah dibuat):

```bash
createdb sipp_karhutla
psql -d sipp_karhutla -f database/schema.sql
```

Atur `DATABASE_URL` melalui environment atau `.env` (jangan commit nilai rahasia). `schema.sql` mendefinisikan users, hotspots, patrols, predictions, recommendations, relasi, timestamp, geometri EPSG:4326, dan indeks spasial.

## API

Semua respons API berbentuk JSON.

| Method | Path | Keterangan |
|---|---|---|
| GET | `/api/health` | Pemeriksaan layanan |
| GET | `/api/dashboard` | Total hotspot, hitungan risiko, patroli |
| GET | `/api/hotspots` | Titik pemetaan demonstrasi |
| POST | `/api/predict` | Prediksi satu wilayah |
| GET | `/api/patrol` | Data patroli |
| POST | `/api/patrol` | Tambah patroli (memori proses) |
| GET | `/api/recommendations` | Rekomendasi diperingkat |

Contoh prediksi:

```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -H 'Content-Type: application/json' \
  -d '{"location_name":"Sebangau","Hotspot_Density_7D":0.7,"Consecutive_Dry_Days":30,"Historical_Fire_Frequency":0.6,"Patrol_Coverage_Gap":0.6,"NDVI_Dryness_Index":0.7,"Mean_Temp_Humidity_Ratio":0.7,"Wind_Speed_Mean_3D":12}'
```

Tambahkan `observed_at` ISO-8601 pada body, misalnya `"observed_at":"2026-11-24T00:00:00Z"`; data berumur lebih dari 7 hari akan diberi status verifikasi. Field fitur wajib divalidasi dan input tidak valid menghasilkan HTTP 400. Model yang belum dilatih menghasilkan HTTP 503.

Contoh patroli:

```bash
curl -X POST http://127.0.0.1:5000/api/patrol \
  -H 'Content-Type: application/json' \
  -d '{"officer_name":"Siti","location":"Sebangau","patrol_date":"2026-11-24","latitude":-2.32,"longitude":113.90,"status":"Selesai"}'
```

## Dataset dan batasan

`dataset/dummy_data.csv` berisi data **sintetis/dummy**, bukan catatan hotspot, kebakaran, cuaca, atau patroli sebenarnya. Label dibuat untuk demonstrasi alur model dan tidak boleh dipakai untuk keputusan operasional. Label peta yang ada di dataset adalah label dummy. Ambang rekomendasi adalah aturan sederhana, bukan asesmen risiko resmi. Sistem tidak memberi keputusan otomatis pemadaman; rekomendasi harus diverifikasi petugas. Contoh patroli dan penyimpanan patroli bersifat sementara.

## Pengembangan selanjutnya

Ganti dataset dengan sumber resmi dan berlisensi, dokumentasikan kualitas/missing data, validasi temporal dan geografis, kalibrasi probabilitas, evaluasi independen di lapangan, serta persetujuan pakar. Tambahkan autentikasi/otorisasi, audit log, persistensi PostgreSQL/PostGIS, pembaruan data berkala, konfigurasi CORS ketat, logging/monitoring, dan pengujian otomatis sebelum deployment.
