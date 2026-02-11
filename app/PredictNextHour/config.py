"""
Configuration file untuk prediction script
Edit file ini untuk menyesuaikan dengan API Anda
"""

# ===== API CONFIGURATION =====

# Option 1: Custom API
WEATHER_API_CONFIG = {
    'type': 'custom',  # 'custom', 'openweathermap', 'weatherapi'
    'url': 'https://api.example.com/weather/hourly',
    'api_key': 'your_api_key_here',
    'params': {
        # Tambahkan parameter yang dibutuhkan API Anda
        # Contoh:
        # 'location': 'Jakarta',
        # 'units': 'metric',
    }
}

# Option 2: OpenWeatherMap
OPENWEATHERMAP_CONFIG = {
    'api_key': 'your_openweathermap_api_key',
    'lat': -6.2088,  # Jakarta latitude (ganti dengan lokasi Anda)
    'lon': 106.8456,  # Jakarta longitude (ganti dengan lokasi Anda)
}

# Option 3: WeatherAPI.com
WEATHERAPI_CONFIG = {
    'api_key': 'your_weatherapi_key',
    'location': 'Jakarta',  # Ganti dengan lokasi Anda
}

# ===== MODEL CONFIGURATION =====
MODEL_CONFIG = {
    'model_path': './LSTM.keras',
    'mae': 25.4,
    'rmse': 52.1,
    'window_size': 24,  # Jumlah jam yang digunakan untuk input (24 hours)
}

# ===== OUTPUT CONFIGURATION =====
OUTPUT_CONFIG = {
    'log_file': 'predictions_log.json',
    'max_logs': 100,  # Maksimal jumlah log yang disimpan
    'save_csv': True,  # Simpan juga dalam format CSV
    'csv_file': 'predictions.csv',
}

# ===== SCHEDULER CONFIGURATION =====
SCHEDULER_CONFIG = {
    'run_every_hour': True,  # True = setiap jam, False = custom interval
    'custom_interval_minutes': 30,  # Jika run_every_hour=False
    'run_on_startup': True,  # Jalankan prediksi saat startup
}

# ===== FIELD MAPPING =====
# Mapping nama field dari API response ke format yang dibutuhkan model
# Ganti sesuai dengan struktur response API Anda
API_FIELD_MAPPING = {
    'timestamp': 'timestamp',  # atau 'time', 'datetime', dll
    'temperature': 'temp',     # atau 'temperature', 'temp_c', dll
    'humidity': 'humidity',    # atau 'humidity_pct', 'rh', dll
    'solar_radiation': 'solar_radiation',  # atau 'radiation', 'irradiance', dll
}
