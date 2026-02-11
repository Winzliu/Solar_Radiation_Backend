# 📘 Guide: Hourly Prediction System

Panduan lengkap untuk menggunakan sistem prediksi radiasi solar otomatis setiap jam.

## 📋 File-file yang Tersedia

1. **`predict_hourly.py`** - Script utama untuk prediksi
2. **`scheduler.py`** - Script untuk menjalankan prediksi otomatis setiap jam
3. **`config.py`** - File konfigurasi (API, model, output)
4. **`predictions_log.json`** - File hasil prediksi (auto-generated)

## 🚀 Quick Start

### 1. Setup API External

**PENTING:** Edit `predict_hourly.py` dan ganti fungsi `fetch_weather_data_from_api()`

Saat ini menggunakan dummy data. Anda perlu mengganti dengan API asli:

```python
def fetch_weather_data_from_api(hours=24):
    """
    Ambil data 24 jam terakhir dari API Anda
    """
    # Contoh untuk API custom
    response = requests.get(
        "https://your-api.com/weather/hourly",
        params={
            "hours": hours,
            "api_key": "YOUR_API_KEY"
        }
    )
    data = response.json()

    # Convert ke DataFrame
    df = pd.DataFrame({
        'Time': [item['timestamp'] for item in data],
        'Temp *C': [item['temperature'] for item in data],
        'Humidity %': [item['humidity'] for item in data],
        'Solar Radiation W/m2': [item.get('solar', 0) for item in data]
    })

    return df
```

### 2. Jalankan Prediksi Manual (Testing)

```bash
python predict_hourly.py
```

Output:

```
============================================================
🌤️  SOLAR RADIATION HOURLY PREDICTION
============================================================
📅 Waktu: 2026-01-29 23:40:33

📦 Loading LSTM model...
✅ Model loaded successfully

🌐 Fetching last 24 hours of weather data...
✅ Fetched 24 data points

⚙️  Preprocessing data...
✅ Data preprocessed

🔄 Converting to model input format...
✅ Input shape: (1, 24, 7)

🔮 Making prediction...
============================================================
📊 PREDICTION RESULTS
============================================================
🕐 Prediksi untuk: 2026-01-30 00:40:33

☀️  Solar Radiation: 125.45 W/m²

📈 Confidence Intervals:
   MAE Range : 100.05 - 150.85 W/m²
   RMSE Range: 73.35 - 177.55 W/m²

📊 Input Data Summary (Last 24 hours):
   Avg Temperature   : 26.45°C
   Avg Humidity      : 82.34%
   Avg Solar Radiation: 234.56 W/m²
============================================================
```

### 3. Jalankan Scheduler Otomatis

```bash
python scheduler.py
```

Scheduler akan:

- ✅ Menjalankan prediksi pertama saat startup
- ⏰ Menjalankan prediksi otomatis setiap jam tepat
- 💾 Menyimpan hasil ke `predictions_log.json`

Output:

```
======================================================================
🕐 SOLAR RADIATION PREDICTION SCHEDULER
======================================================================
📋 Configuration:
   - Prediction interval: Every hour
   - Using last 24 hours of data
   - Predictions logged to: predictions_log.json

🚀 Scheduler started!
   Press Ctrl+C to stop
======================================================================

🔄 Running initial prediction...
...
```

## 📊 Format Output

### JSON Log (`predictions_log.json`)

```json
[
	{
		"timestamp": "2026-01-29T23:40:33.123456",
		"prediction_for": "2026-01-30 00:40:33",
		"prediction": {
			"solar_radiation_w_m2": 125.45,
			"confidence_intervals": {
				"mae_lower": 100.05,
				"mae_upper": 150.85,
				"rmse_lower": 73.35,
				"rmse_upper": 177.55
			}
		},
		"input_data_summary": {
			"hours_used": 24,
			"time_range": {
				"start": "2026-01-29T00:40:33",
				"end": "2026-01-29T23:40:33"
			},
			"avg_temperature": 26.45,
			"avg_humidity": 82.34,
			"avg_solar_radiation": 234.56
		}
	}
]
```

## 🔧 Konfigurasi

### Mengubah Interval Prediksi

Edit `scheduler.py`:

```python
# Setiap jam (default)
schedule.every().hour.at(":00").do(run_prediction_job)

# Atau setiap 30 menit
schedule.every(30).minutes.do(run_prediction_job)

# Atau setiap 5 menit (untuk testing)
schedule.every(5).minutes.do(run_prediction_job)
```

### Mengubah Window Size

Edit `predict_hourly.py`:

```python
# Jika mau pakai 48 jam terakhir
results = predict_next_hour(hours=48)
```

**CATATAN:** Pastikan model Anda di-train dengan window size yang sama!

## 🌐 Integrasi dengan API External

### Option 1: OpenWeatherMap

```python
def fetch_weather_data_from_api(hours=24):
    API_KEY = "your_openweathermap_key"
    LAT = -6.2088  # Jakarta
    LON = 106.8456

    data_points = []
    for i in range(hours):
        dt = int((datetime.now() - timedelta(hours=i)).timestamp())
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/onecall/timemachine",
            params={
                "lat": LAT,
                "lon": LON,
                "dt": dt,
                "appid": API_KEY,
                "units": "metric"
            }
        )
        data = response.json()

        # Extract data
        current = data['current']
        data_points.append({
            'Time': datetime.fromtimestamp(current['dt']),
            'Temp *C': current['temp'],
            'Humidity %': current['humidity'],
            'Solar Radiation W/m2': current.get('uvi', 0) * 100  # Approx
        })

    return pd.DataFrame(data_points)
```

### Option 2: WeatherAPI.com

```python
def fetch_weather_data_from_api(hours=24):
    API_KEY = "your_weatherapi_key"

    response = requests.get(
        "http://api.weatherapi.com/v1/history.json",
        params={
            "key": API_KEY,
            "q": "Jakarta",
            "dt": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            "hour": list(range(24))
        }
    )
    data = response.json()

    hourly_data = data['forecast']['forecastday'][0]['hour']

    df = pd.DataFrame({
        'Time': [h['time'] for h in hourly_data],
        'Temp *C': [h['temp_c'] for h in hourly_data],
        'Humidity %': [h['humidity'] for h in hourly_data],
        'Solar Radiation W/m2': [h.get('uv', 0) * 100 for h in hourly_data]
    })

    return df
```

### Option 3: Custom Internal API

```python
def fetch_weather_data_from_api(hours=24):
    response = requests.get(
        "http://your-internal-api.com/api/weather/hourly",
        params={
            "limit": hours,
            "order": "desc"
        },
        headers={
            "Authorization": f"Bearer {API_TOKEN}"
        }
    )
    data = response.json()

    # Sesuaikan dengan struktur API Anda
    df = pd.DataFrame(data['results'])
    df.rename(columns={
        'timestamp': 'Time',
        'temp': 'Temp *C',
        'humidity': 'Humidity %',
        'radiation': 'Solar Radiation W/m2'
    }, inplace=True)

    return df
```

## 🐛 Troubleshooting

### Error: Model not found

```bash
FileNotFoundError: Model not found at ./LSTM.keras
```

**Solusi:** Pastikan file `LSTM.keras` ada di direktori yang sama dengan script.

### Error: Not enough data

```bash
ValueError: Need at least 24 rows, got 10
```

**Solusi:** API Anda tidak mengembalikan cukup data. Cek:

1. Parameter `hours` di API request
2. Apakah API punya data 24 jam terakhir?
3. Filtering atau pagination yang salah

### Warning: Using dummy data

```
⚠️  WARNING: Menggunakan dummy data untuk testing
```

**Solusi:** Ini normal untuk testing. Ganti fungsi `fetch_weather_data_from_api()` dengan API asli.

## 📝 Best Practices

1. **Testing:** Jalankan `predict_hourly.py` manual dulu sebelum pakai scheduler
2. **Logging:** Monitor `predictions_log.json` untuk melihat hasil
3. **Error Handling:** Add try-catch di API integration Anda
4. **Rate Limiting:** Perhatikan rate limit API eksternal
5. **Backup:** Simpan log predictions secara berkala

## 🔄 Menjalankan di Background (Production)

### Windows (Task Scheduler)

1. Buka Task Scheduler
2. Create Basic Task
3. Set trigger: At startup
4. Set action: Start program
    - Program: `python.exe`
    - Arguments: `scheduler.py`
    - Start in: `D:\AlwinLiufandy\College\Skripsi\Skripsi_Alwin\Hasil`

### Linux (systemd)

Create file `/etc/systemd/system/solar-prediction.service`:

```ini
[Unit]
Description=Solar Radiation Prediction Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/Hasil
ExecStart=/path/to/venv/bin/python scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable dan start:

```bash
sudo systemctl enable solar-prediction
sudo systemctl start solar-prediction
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "scheduler.py"]
```

## 📞 Support

Jika ada masalah:

1. Check log file
2. Verify API credentials
3. Test API endpoint manual dengan curl/Postman
4. Check model compatibility dengan TensorFlow version
