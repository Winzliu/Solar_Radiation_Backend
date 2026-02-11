# Solar Radiation Prediction API

API untuk memprediksi radiasi solar menggunakan model LSTM.

## Setup

### 1. Buat Virtual Environment

```bash
python -m venv venv
```

### 2. Aktivasi Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Pastikan Model Ada

Pastikan file model (`LSTM.keras`, `GRU.keras`, dll) ada di direktori `../model/`.

API akan otomatis mencari file berikut pada saat startup:

- `../model/LSTM.keras`
- `../model/GRU.keras`
- `../model/BI-LSTM.keras`

### 5. Update MAE dan RMSE

Buka file `app.py` dan update nilai `MAE_VALUE` dan `RMSE_VALUE` sesuai dengan hasil training model Anda:

```python
MAE_VALUE = 50.0  # Ganti dengan nilai MAE dari training
RMSE_VALUE = 70.0  # Ganti dengan nilai RMSE dari training
```

## Menjalankan API

```bash
python app.py
```

atau

```bash
uvicorn app:app --reload
```

API akan berjalan di: `http://localhost:8000`

## Dokumentasi API (OpenAPI/Swagger)

Setelah API berjalan, buka:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

## Endpoints

### 1. Root Endpoint

- **URL**: `GET /`
- **Deskripsi**: Informasi dasar API

### 2. Health Check

- **URL**: `GET /health`
- **Deskripsi**: Cek status API dan model

### 3. Prediction

- **URL**: `POST /predict?model={model_name}`
- **Deskripsi**: Prediksi radiasi solar dari CSV file.
- **Query Parameter**: `model` (opsional, default: `LSTM`). Pilihan: `LSTM`, `GRU`, `BI-LSTM`.
- **Input**: File CSV dengan format:
    ```
    Time;Temp *C;Humidity %;Solar Radiation W/m2;Date
    2020-01-01 09:00:00;26.8;86.41;158;2020-01-01
    ...
    ```
- **Output**: JSON dengan data 24 jam terakhir dan hasil prediksi.
    ```json
    {
      "model": "LSTM",
      "prev": [
        {
          "radiation": 158.0,
          "humidity": 86.41,
          "temp": 26.8,
          "date": "2020-01-01 09:00:00"
        },
        ...
      ],
      "pred": {
        "date": "2020-01-01 10:00:00",
        "rad_pred": [123.45],
        "Lower_MAE": [73.45],
        "Upper_MAE": [173.45],
        "Lower_RMSE": [53.45],
        "Upper_RMSE": [193.45]
      }
    }
    ```

## Testing API

### Menggunakan cURL

```bash
# Prediksi menggunakan LSTM (default)
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@fix_test.csv"

# Prediksi menggunakan GRU
curl -X POST "http://127.0.0.1:8000/predict?model=GRU" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@fix_test.csv"
```

### Menggunakan Python

```python
import requests

url = "http://localhost:8000/predict"
files = {"file": open("fix_test.csv", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Menggunakan Swagger UI

1. Buka http://localhost:8000/docs
2. Klik pada endpoint `/predict`
3. Klik "Try it out"
4. Upload file CSV
5. Klik "Execute"

## Format Data Input

File CSV harus memiliki kolom berikut:

- `Time`: Datetime (format: YYYY-MM-DD HH:MM:SS)
- `Temp *C`: Temperature dalam Celsius
- `Humidity %`: Persentase kelembaban
- `Solar Radiation W/m2`: Radiasi solar (akan diprediksi)
- `Date`: Tanggal (format: YYYY-MM-DD)

**Minimal 24 baris data diperlukan untuk prediksi.**

## Preprocessing Data

API akan otomatis melakukan preprocessing berikut:

1. Sorting data berdasarkan waktu
2. Konversi waktu ke Unix timestamp (seconds)
3. Ekstraksi fitur siklikal:
    - Day sin/cos (pola harian)
    - Year sin/cos (pola tahunan)
4. Mengambil 24 data terakhir sebagai input model (window size)

## Catatan Penting

- Pastikan model `LSTM.keras` kompatibel dengan TensorFlow 2.15.0
- Update nilai MAE dan RMSE sesuai dengan hasil training
- Jika ada preprocessing khusus saat training, update fungsi `preprocess()` di `app.py`
- File CSV harus menggunakan delimiter semicolon (`;`)

## Troubleshooting

### Model tidak ditemukan

```
FileNotFoundError: Model file not found at ./LSTM.keras
```

**Solusi**: Pastikan file `LSTM.keras` ada di direktori yang sama dengan `app.py`

### Data tidak cukup

```
Not enough data. Need at least 24 rows
```

**Solusi**: Upload file CSV dengan minimal 24 baris data

### Error parsing CSV

```
Error processing CSV
```

**Solusi**: Pastikan format CSV sesuai dan menggunakan delimiter semicolon (`;`)
