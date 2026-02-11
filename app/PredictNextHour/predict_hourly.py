"""
Script untuk mengambil data 24 jam terakhir dari API eksternal
dan memprediksi radiasi solar untuk jam ke-25
"""
import requests
import pandas as pd
import numpy as np
import tensorflow as tf
from datetime import datetime, timedelta
import json
import os

# ===== KONFIGURASI =====
# OpenWeatherMap API Configuration
OPENWEATHERMAP_API_KEY = "8884dcf224248ab0222cff8ed6e736fc"  # GANTI INI dengan API key Anda
LATITUDE = 3.58333  # Jakarta latitude (GANTI dengan lokasi Anda)
LONGITUDE = 98.66667  # Jakarta longitude (GANTI dengan lokasi Anda)

# Model configuration
MODEL_PATH = "./model/LSTM.keras"
MAE_VALUE = 25.4
RMSE_VALUE = 52.1

# Output file
OUTPUT_FILE = "./PredictNextHour/predictions_log.json"


def fetch_weather_data_from_api(hours=24):
    """
    Ambil data cuaca 24 jam terakhir dari OpenWeatherMap Timemachine API
    
    API: https://api.openweathermap.org/data/3.0/onecall/timemachine
    Response format:
    {
      "data": [
        {
          "dt": unix_timestamp,
          "temp": temperature_in_kelvin,
          "humidity": percentage,
          "uvi": uv_index,
          ...
        }
      ]
    }
    
    Returns:
        DataFrame dengan kolom: Time, Temp *C, Humidity %, Solar Radiation W/m2
    """
    try:
        print(f"🌐 Fetching data from OpenWeatherMap API...")
        print(f"   Location: Lat {LATITUDE}, Lon {LONGITUDE}")
        
        # Collect data for each hour
        data_points = []
        now = datetime.now()
        
        for i in range(hours, 0, -1):
            # Calculate timestamp for each hour
            target_time = now - timedelta(hours=i)
            unix_timestamp = int(target_time.timestamp())
            
            # Make API call
            url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"
            params = {
                "lat": LATITUDE,
                "lon": LONGITUDE,
                "dt": unix_timestamp,
                "appid": OPENWEATHERMAP_API_KEY,
                "units": "metric"  # Use Celsius
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            api_data = response.json()
            
            # Extract relevant data from the first item in data array
            if "data" in api_data and len(api_data["data"]) > 0:
                hourly_data = api_data["data"][0]
                
                # Convert UVI to approximate solar radiation (W/m²)
                # Formula: Solar Radiation ≈ UVI × 25 (rough approximation)
                # For more accuracy, you might need a different conversion
                uvi = hourly_data.get("uvi", 0)
                solar_radiation = uvi * 100  # Adjusted multiplier
                
                data_points.append({
                    'Time': target_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'Temp *C': hourly_data.get("temp", 0),
                    'Humidity %': hourly_data.get("humidity", 0),
                    'Solar Radiation W/m2': solar_radiation
                })
            
            # Add small delay to avoid rate limiting
            if i > 1:  # Don't sleep after last request
                import time
                time.sleep(0.1)
        
        df = pd.DataFrame(data_points)
        print(f"✅ Successfully fetched {len(df)} hours of data")
        
        return df
        
    except requests.RequestException as e:
        print(f"❌ Error fetching data from OpenWeatherMap API: {e}")
        print(f"⚠️  Falling back to dummy data for testing...")
        return generate_dummy_data(hours)
    except Exception as e:
        print(f"❌ Error processing API data: {e}")
        print(f"⚠️  Falling back to dummy data for testing...")
        return generate_dummy_data(hours)


def generate_dummy_data(hours=24):
    """
    Generate dummy data untuk testing
    HAPUS fungsi ini saat sudah connect ke API asli
    """
    now = datetime.now()
    times = [now - timedelta(hours=i) for i in range(hours, 0, -1)]
    
    data = {
        'Time': [t.strftime('%Y-%m-%d %H:%M:%S') for t in times],
        'Temp *C': np.random.uniform(24, 30, hours),
        'Humidity %': np.random.uniform(70, 95, hours),
        'Solar Radiation W/m2': [
            np.random.uniform(0, 50) if t.hour < 6 or t.hour > 18
            else np.random.uniform(100, 800)
            for t in times
        ]
    }
    
    return pd.DataFrame(data)


def preprocess_data(df):
    """
    Preprocess data seperti saat training
    """
    # Convert Time to datetime
    df['Time'] = pd.to_datetime(df['Time'])
    df['Seconds'] = df['Time'].astype('int64') // 1e9
    
    # Select relevant columns
    solar_df = df[['Temp *C', 'Humidity %', 'Solar Radiation W/m2', 'Seconds']].copy()
    
    # Add cyclical time features
    day = 24 * 60 * 60
    year = (365.2425) * day
    
    solar_df['Day sin'] = np.sin(solar_df['Seconds'] * (2 * np.pi / day))
    solar_df['Day cos'] = np.cos(solar_df['Seconds'] * (2 * np.pi / day))
    solar_df['Year sin'] = np.sin(solar_df['Seconds'] * (2 * np.pi / year))
    solar_df['Year cos'] = np.cos(solar_df['Seconds'] * (2 * np.pi / year))
    
    # Drop the Seconds column
    solar_df = solar_df.drop('Seconds', axis=1)
    
    return solar_df


def df_to_X_inference(df, window_size=24):
    """
    Convert dataframe to model input format
    """
    data = df.to_numpy()
    
    if len(data) < window_size:
        raise ValueError(f"Need at least {window_size} rows, got {len(data)}")
    
    X = data[-window_size:]
    return X.reshape(1, window_size, data.shape[1])


def preprocess_model_input(X):
    """
    Preprocessing untuk input model
    Sesuaikan dengan preprocessing saat training
    """
    # Jika Anda punya normalization/standardization, tambahkan di sini
    return X


def predict_next_hour(model_path=MODEL_PATH, hours=24):
    """
    Main function untuk prediksi jam berikutnya
    """
    print("=" * 60)
    print("🌤️  SOLAR RADIATION HOURLY PREDICTION")
    print("=" * 60)
    print(f"📅 Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Load model
    print("📦 Loading LSTM model...")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    
    model = tf.keras.models.load_model(model_path)
    print("✅ Model loaded successfully")
    print()
    
    # 2. Fetch data dari API
    print(f"🌐 Fetching last {hours} hours of weather data...")
    df = fetch_weather_data_from_api(hours=hours)
    print(f"✅ Fetched {len(df)} data points")
    print()
    
    # 3. Preprocess data
    print("⚙️  Preprocessing data...")
    processed_df = preprocess_data(df)
    print("✅ Data preprocessed")
    print()
    
    # 4. Convert to model input
    print("🔄 Converting to model input format...")
    X_input = df_to_X_inference(processed_df, window_size=hours)
    X_input = preprocess_model_input(X_input)
    print(f"✅ Input shape: {X_input.shape}")
    print()
    
    # 5. Make prediction
    print("🔮 Making prediction...")
    prediction = model.predict(X_input, verbose=0).flatten()
    
    # 6. Calculate confidence intervals
    lower_mae = prediction - MAE_VALUE
    upper_mae = prediction + MAE_VALUE
    lower_rmse = prediction - RMSE_VALUE
    upper_rmse = prediction + RMSE_VALUE
    
    # 7. Format results
    next_hour = datetime.now() + timedelta(hours=1)
    next_hour_str = next_hour.strftime('%Y-%m-%d %H:%M:%S')
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'prediction_for': next_hour_str,
        'prediction': {
            'solar_radiation_w_m2': float(prediction[0]),
            'confidence_intervals': {
                'mae_lower': float(lower_mae[0]),
                'mae_upper': float(upper_mae[0]),
                'rmse_lower': float(lower_rmse[0]),
                'rmse_upper': float(upper_rmse[0])
            }
        },
        'input_data_summary': {
            'hours_used': hours,
            'time_range': {
                'start': df['Time'].min().isoformat(),
                'end': df['Time'].max().isoformat()
            },
            'avg_temperature': float(df['Temp *C'].mean()),
            'avg_humidity': float(df['Humidity %'].mean()),
            'avg_solar_radiation': float(df['Solar Radiation W/m2'].mean())
        }
    }
    
    # 8. Print results
    print("=" * 60)
    print("📊 PREDICTION RESULTS")
    print("=" * 60)
    print(f"🕐 Prediksi untuk: {next_hour_str}")
    print()
    print(f"☀️  Solar Radiation: {prediction[0]:.2f} W/m²")
    print()
    print("📈 Confidence Intervals:")
    print(f"   MAE Range : {lower_mae[0]:.2f} - {upper_mae[0]:.2f} W/m²")
    print(f"   RMSE Range: {lower_rmse[0]:.2f} - {upper_rmse[0]:.2f} W/m²")
    print()
    print("📊 Input Data Summary (Last 24 hours):")
    print(f"   Avg Temperature   : {results['input_data_summary']['avg_temperature']:.2f}°C")
    print(f"   Avg Humidity      : {results['input_data_summary']['avg_humidity']:.2f}%")
    print(f"   Avg Solar Radiation: {results['input_data_summary']['avg_solar_radiation']:.2f} W/m²")
    print("=" * 60)
    
    # 9. Save to log file
    save_prediction_log(results)
    
    return results


def save_prediction_log(results):
    """
    Save prediction results to JSON log file
    """
    try:
        # Load existing logs
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Add new result
        logs.append(results)
        
        # Keep only last 100 predictions
        logs = logs[-100:]
        
        # Save back
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
        
        print(f"💾 Results saved to {OUTPUT_FILE}")
    
    except Exception as e:
        print(f"⚠️  Warning: Could not save to log file: {e}")


if __name__ == "__main__":
    try:
        results = predict_next_hour()
        print("\n✅ Prediction completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during prediction: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
