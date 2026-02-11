# 🌤️ Solar Radiation Hourly Prediction

Script untuk memprediksi radiasi solar 1 jam kedepan menggunakan data 24 jam terakhir dari OpenWeatherMap API.

## 📋 Setup

### 1. Install Dependencies

Pastikan Anda sudah install semua dependencies:

```bash
# Dari folder root Hasil
cd ..
pip install -r requirements.txt
```

### 2. Dapatkan OpenWeatherMap API Key

1. Daftar di [OpenWeatherMap](https://openweathermap.org/api)
2. Subscribe ke **"One Call API 3.0"** dengan paket yang support **Timemachine**
3. Copy API key Anda

### 3. Konfigurasi

Edit file `predict_hourly.py` dan update konfigurasi berikut:

```python
# Line 16-18
OPENWEATHERMAP_API_KEY = "your_api_key_here"  # Paste API key Anda
LATITUDE = -6.2088   # Ganti dengan latitude lokasi Anda
LONGITUDE = 106.8456  # Ganti dengan longitude lokasi Anda
```

**Cara mendapatkan koordinat lokasi Anda:**

- Buka [Google Maps](https://maps.google.com)
- Klik kanan pada lokasi yang diinginkan
- Copy koordinat (latitude, longitude)

### 4. Pastikan Model Ada

Pastikan file model `LSTM.keras` ada di folder `../model/`:

```
Hasil/
├── model/
│   └── LSTM.keras          ← Model harus ada di sini
└── PredictNextHour/
    ├── predict_hourly.py
    ├── scheduler.py
    └── config.py
```

## 🚀 Cara Menggunakan

### Manual Prediction (Sekali Jalan)

```bash
python predict_hourly.py
```

**Output:**

```
============================================================
🌤️  SOLAR RADIATION HOURLY PREDICTION
============================================================
📅 Waktu: 2026-01-29 23:54:15

📦 Loading LSTM model...
✅ Model loaded successfully

🌐 Fetching last 24 hours of weather data...
   Location: Lat -6.2088, Lon 106.8456
✅ Successfully fetched 24 hours of data

⚙️  Preprocessing data...
✅ Data preprocessed

🔄 Converting to model input format...
✅ Input shape: (1, 24, 7)

🔮 Making prediction...
============================================================
📊 PREDICTION RESULTS
============================================================
🕐 Prediksi untuk: 2026-01-30 00:54:15

☀️  Solar Radiation: 123.45 W/m²

📈 Confidence Intervals:
   MAE Range : 98.05 - 148.85 W/m²
   RMSE Range: 71.35 - 175.55 W/m²

📊 Input Data Summary (Last 24 hours):
   Avg Temperature   : 27.30°C
   Avg Humidity      : 78.50%
   Avg Solar Radiation: 215.30 W/m²
============================================================
💾 Results saved to predictions_log.json
```

### Automated Prediction (Setiap Jam)

```bash
python scheduler.py
```

Script akan menjalankan prediksi:

- ✅ Sekali saat startup
- ⏰ Otomatis setiap jam tepat (XX:00:00)
- 💾 Menyimpan hasil ke `predictions_log.json`

**Untuk stop scheduler:** Tekan `Ctrl+C`

## 📊 Output Files

### `predictions_log.json`

File ini berisi log semua prediksi (maksimal 100 terakhir):

```json
[
	{
		"timestamp": "2026-01-29T23:54:15.123456",
		"prediction_for": "2026-01-30 00:54:15",
		"prediction": {
			"solar_radiation_w_m2": 123.45,
			"confidence_intervals": {
				"mae_lower": 98.05,
				"mae_upper": 148.85,
				"rmse_lower": 71.35,
				"rmse_upper": 175.55
			}
		},
		"input_data_summary": {
			"hours_used": 24,
			"time_range": {
				"start": "2026-01-29T00:54:15",
				"end": "2026-01-29T23:54:15"
			},
			"avg_temperature": 27.3,
			"avg_humidity": 78.5,
			"avg_solar_radiation": 215.3
		}
	}
]
```

## 🔧 Konfigurasi Lanjutan

### Mengubah Lokasi

Edit `predict_hourly.py`:

```python
LATITUDE = -7.7956   # Contoh: Yogyakarta
LONGITUDE = 110.3695
```

### Mengubah Conversion UVI ke Solar Radiation

OpenWeatherMap API memberikan UV Index (UVI), bukan langsung Solar Radiation. Script melakukan konversi:

```python
# Line 70 di predict_hourly.py
solar_radiation = uvi * 100  # Anda bisa adjust multiplier ini
```

**Referensi konversi:**

- UVI 0-2 (Low) ≈ 0-200 W/m²
- UVI 3-5 (Moderate) ≈ 200-400 W/m²
- UVI 6-7 (High) ≈ 400-600 W/m²
- UVI 8-10 (Very High) ≈ 600-800 W/m²
- UVI 11+ (Extreme) ≈ 800+ W/m²

Sesuaikan multiplier berdasarkan data training Anda.

### Mengubah Interval Scheduler

Edit `scheduler.py`:

```python
# Setiap jam (default)
schedule.every().hour.at(":00").do(run_prediction_job)

# Atau setiap 30 menit
schedule.every(30).minutes.do(run_prediction_job)

# Atau jam tertentu setiap hari
schedule.every().day.at("10:00").do(run_prediction_job)
```

## ⚠️ Penting

### 1. API Rate Limits

OpenWeatherMap API memiliki rate limit:

- **Free tier**: 1,000 calls/day, 60 calls/minute
- Script ini membuat **24 API calls** setiap prediksi
- Jika pakai scheduler setiap jam = **24 × 24 = 576 calls/day** ✅

### 2. API Cost

OpenWeatherMap **One Call API 3.0 Timemachine** adalah **PAID API**:

- Free tier: **1,000 calls/day**
- Setelah itu: **$0.0015 per call**

**Perhitungan biaya (scheduler setiap jam):**

- 576 calls/day (masih dalam free tier) = **$0**
- Jika lebih: ~$0.86/day atau ~$26/month

### 3. Fallback ke Dummy Data

Jika API call gagal (no internet, invalid key, rate limit), script otomatis fallback ke dummy data untuk testing.

## 🐛 Troubleshooting

### Error: Invalid API Key

```
❌ Error fetching data from OpenWeatherMap API: 401 Client Error
```

**Solusi:**

1. Pastikan API key benar
2. Pastikan sudah subscribe ke "One Call API 3.0"
3. Tunggu beberapa menit setelah aktivasi API key

### Error: Model not found

```
FileNotFoundError: Model not found at ../model/LSTM.keras
```

**Solusi:**

- Pastikan struktur folder benar:
    ```
    Hasil/
    ├── model/
    │   └── LSTM.keras
    └── PredictNextHour/
        └── predict_hourly.py
    ```
- Atau update `MODEL_PATH` di script

### Error: Rate limit exceeded

```
❌ Error fetching data from OpenWeatherMap API: 429 Too Many Requests
```

**Solusi:**

- Tunggu beberapa menit
- Kurangi frekuensi scheduler
- Upgrade OpenWeatherMap plan

### Data UVI selalu 0 di malam hari

Ini normal! UV Index = 0 saat malam (tidak ada matahari). Script akan tetap jalan dan predict solar radiation untuk jam berikutnya berdasarkan pola waktu.

## 📝 Tips

1. **Testing:** Jalankan manual dulu dengan `python predict_hourly.py` sebelum pakai scheduler
2. **Monitoring:** Check `predictions_log.json` secara berkala
3. **Koordinat:** Gunakan koordinat yang sama dengan lokasi training data untuk hasil terbaik
4. **Backup:** Simpan `predictions_log.json` secara berkala

## 📞 Support

Untuk pertanyaan atau issues:

1. Check dokumentasi OpenWeatherMap: https://openweathermap.org/api/one-call-3
2. Verify API key dan subscription status
3. Check error messages di console

## 🔗 Links

- [OpenWeatherMap API Docs](https://openweathermap.org/api/one-call-3)
- [Get API Key](https://home.openweathermap.org/api_keys)
- [Pricing](https://openweathermap.org/price)
- [Find Coordinates](https://www.google.com/maps)
