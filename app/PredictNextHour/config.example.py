"""
Example Configuration File
Copy this to config.py and fill in your actual values
"""

# ===== OPENWEATHERMAP API CONFIGURATION =====
# Get your API key from: https://home.openweathermap.org/api_keys
# Note: You need to subscribe to "One Call API 3.0" which supports Timemachine

OPENWEATHERMAP_API_KEY = "your_api_key_here"

# Your location coordinates
# Find your coordinates: https://www.google.com/maps (right-click → coordinates)
LATITUDE = -6.2088    # Example: Jakarta, Indonesia
LONGITUDE = 106.8456  # Example: Jakarta, Indonesia

# ===== MODEL CONFIGURATION =====
MODEL_PATH = "../model/LSTM.keras"
MAE_VALUE = 25.4   # From your training results
RMSE_VALUE = 52.1  # From your training results
WINDOW_SIZE = 24   # Hours of historical data to use

# ===== API BEHAVIOR =====
# Request timeout in seconds
API_TIMEOUT = 10

# Delay between API calls to avoid rate limiting (seconds)
API_DELAY = 0.1

# Fallback to dummy data if API fails
FALLBACK_TO_DUMMY = True

# ===== UVI TO SOLAR RADIATION CONVERSION =====
# OpenWeatherMap provides UV Index, not direct solar radiation
# Adjust this multiplier based on your location and training data
UVI_MULTIPLIER = 100  # solar_radiation = uvi * UVI_MULTIPLIER

# Reference:
# UVI 0-2 (Low)       ≈ 0-200 W/m²
# UVI 3-5 (Moderate)  ≈ 200-400 W/m²
# UVI 6-7 (High)      ≈ 400-600 W/m²
# UVI 8-10 (Very High)≈ 600-800 W/m²
# UVI 11+ (Extreme)   ≈ 800+ W/m²

# ===== OUTPUT CONFIGURATION =====
OUTPUT_FILE = "predictions_log.json"
MAX_LOG_ENTRIES = 100  # Keep only last N predictions

# ===== LOGGING =====
VERBOSE = True  # Show detailed logs
