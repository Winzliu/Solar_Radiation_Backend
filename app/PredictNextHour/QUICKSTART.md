# ⚙️ Quick Setup Guide

Panduan cepat untuk menjalankan prediksi solar radiation dengan OpenWeatherMap API.

## 🚀 3 Langkah Setup

### 1️⃣ Edit Konfigurasi

Buka `predict_hourly.py` dan edit baris 16-18:

```python
OPENWEATHERMAP_API_KEY = "paste_your_api_key_here"
LATITUDE = -6.2088   # Ganti dengan koordinat Anda
LONGITUDE = 106.8456  # Ganti dengan koordinat Anda
```

### 2️⃣ Dapatkan API Key

1. Buka https://openweathermap.org/api
2. Daftar/Login
3. Subscribe ke **"One Call API 3.0"**
4. Copy API key dari https://home.openweathermap.org/api_keys

⚠️ **PENTING:** Free tier = 1,000 calls/day (cukup untuk 41 prediksi/hari dengan 24 API calls per prediksi)

### 3️⃣ Jalankan

```bash
python predict_hourly.py
```

## 📍 Cara Dapat Koordinat

1. Buka https://www.google.com/maps
2. Klik kanan pada lokasi Anda
3. Copy angka pertama (latitude) dan kedua (longitude)
4. Contoh: `-6.2088, 106.8456`

## ✅ Output yang Diharapkan

```
============================================================
🌤️  SOLAR RADIATION HOURLY PREDICTION
============================================================
📦 Loading LSTM model...
✅ Model loaded successfully

🌐 Fetching last 24 hours of weather data...
   Location: Lat -6.2088, Lon 106.8456
✅ Successfully fetched 24 hours of data

🔮 Making prediction...
☀️  Solar Radiation: 123.45 W/m²
============================================================
```

## ❌ Troubleshooting

**Error: 401 Unauthorized**

- ✅ API key salah atau belum aktif
- ✅ Tunggu 5-10 menit setelah aktivasi

**Error: 404 Not Found**

- ✅ Belum subscribe ke "One Call API 3.0"
- ✅ Check subscription di dashboard

**Error: Model not found**

- ✅ Pastikan `LSTM.keras` ada di folder `../model/`

**Fallback to dummy data**

- ✅ Tidak fatal, tapi artinya API gagal
- ✅ Check koneksi internet dan API key

## 📁 Struktur Folder

```
Hasil/
├── model/
│   └── LSTM.keras          ← Pastikan ada!
├── PredictNextHour/
│   ├── predict_hourly.py   ← Edit API key di sini
│   ├── scheduler.py
│   └── README.md
└── requirements.txt
```

## 🔗 Links Penting

- Get API Key: https://home.openweathermap.org/api_keys
- API Docs: https://openweathermap.org/api/one-call-3
- Find Coordinates: https://www.google.com/maps
- Full README: [README.md](README.md)
