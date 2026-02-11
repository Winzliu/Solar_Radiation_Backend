from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
import tensorflow as tf
from io import StringIO
import os

app = FastAPI(
    title="Solar Radiation Prediction API",
    description="API for predicting solar radiation using LSTM model",
    version="1.0.0"
)

# Add CORS middleware
origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001")
origins = [origin.strip() for origin in origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model configurations
MODELS_CONFIG = {
    "LSTM": {"path": "../model/LSTM.keras", "model": None},
    "GRU": {"path": "../model/GRU.keras", "model": None},
    "BI-LSTM": {"path": "../model/BI-LSTM.keras", "model": None},
}

# Metrics (Global for now, can be made per-model if needed)
# Metrics (Global for now, can be made per-model if needed)
MODEL_METRICS = {
    "LSTM": {"MAE": 22.31, "MSE": 2003.6, "RMSE": 44.7, "R2": 0.9},
    "GRU": {"MAE": 22.6, "MSE": 2048.33, "RMSE": 45.25, "R2": 0.9},
    "BI-LSTM": {"MAE": 22.9, "MSE": 1993.74, "RMSE": 44.6, "R2": 0.9},
}


class PreviousDataItem(BaseModel):
    radiation: float
    humidity: float
    temp: float
    date: str


class PredictionData(BaseModel):
    date: str
    rad_pred: List[float]
    Lower_MAE: List[float]
    Upper_MAE: List[float]
    Lower_RMSE: List[float]
    Upper_RMSE: List[float]


class PredictionResponse(BaseModel):
    model: str
    mae: float
    mse: float
    rmse: float
    r2: float
    prev: List[PreviousDataItem]
    pred: PredictionData
    model_metrics: dict


def load_models():
    """Load all available models"""
    print("Loading models...")
    for Name, config in MODELS_CONFIG.items():
        path = config["path"]
        if os.path.exists(path):
            try:
                config["model"] = tf.keras.models.load_model(path)
                print(f"Model {Name} loaded successfully from {path}")
            except Exception as e:
                print(f"Error loading model {Name} from {path}: {e}")
        else:
            print(f"Model file for {Name} not found at {path}")


def preprocess(X):
    """
    Preprocessing function for the input data
    You should implement the same preprocessing as used during training
    """
    # Example: Normalization or standardization
    # Modify this based on your actual preprocessing pipeline
    return X


def df_to_X_inference(df, window_size=24):
    """
    Convert dataframe to model input format
    Takes the last 'window_size' rows as input
    """
    data = df.to_numpy()
    
    if len(data) < window_size:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough data. Need at least {window_size} rows, got {len(data)}"
        )
    
    X = data[-window_size:]
    return X.reshape(1, window_size, data.shape[1])


def process_csv_data(csv_content: str) -> pd.DataFrame:
    """Process the uploaded CSV file"""
    try:
        # Read CSV with semicolon delimiter
        df_test = pd.read_csv(StringIO(csv_content), delimiter=";")
        
        # Set index and sort
        df_test.index = df_test['Time']
        df_test = df_test.sort_index()
        df_test = df_test.reset_index(drop=True)
        
        # Convert Time to datetime and then to seconds
        df_test['Time'] = pd.to_datetime(df_test['Time'])
        df_test['Seconds'] = df_test['Time'].astype('int64') // 1e9
        
        # Select relevant columns
        solar_df_test = df_test[['Temp *C', 'Humidity %', 'Solar Radiation W/m2', 'Seconds']]
        
        # Add cyclical time features
        day = 24 * 60 * 60
        year = (365.2425) * day
        
        solar_df_test['Day sin'] = np.sin(solar_df_test['Seconds'] * (2 * np.pi / day))
        solar_df_test['Day cos'] = np.cos(solar_df_test['Seconds'] * (2 * np.pi / day))
        solar_df_test['Year sin'] = np.sin(solar_df_test['Seconds'] * (2 * np.pi / year))
        solar_df_test['Year cos'] = np.cos(solar_df_test['Seconds'] * (2 * np.pi / year))
        
        # Drop the Seconds column
        solar_df_test = solar_df_test.drop('Seconds', axis=1)
        
        return solar_df_test
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    load_models()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Solar Radiation Prediction API",
        "endpoints": {
            "docs": "/docs",
            "predict": "/predict",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    loaded_models = [name for name, config in MODELS_CONFIG.items() if config["model"] is not None]
    return {
        "status": "healthy",
        "loaded_models": loaded_models,
        "total_models": len(MODELS_CONFIG)
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(model: str = "LSTM", file: UploadFile = File(...)):
    """
    Predict solar radiation from uploaded CSV file
    
    The CSV file should have the following columns:
    - Time: Datetime in format 'YYYY-MM-DD HH:MM:SS'
    - Temp *C: Temperature in Celsius
    - Humidity %: Humidity percentage
    - Solar Radiation W/m2: Solar radiation (this will be predicted)
    - Date: Date in format 'YYYY-MM-DD'
    
    The file should contain at least 24 rows of data.
    """
    # Select model
    model_name = model.upper()
    if model_name not in MODELS_CONFIG:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid model name. Choose from: {', '.join(MODELS_CONFIG.keys())}"
        )
    
    selected_model_obj = MODELS_CONFIG[model_name]["model"]
    if selected_model_obj is None:
        raise HTTPException(
            status_code=500, 
            detail=f"Model {model_name} is not loaded. Check if the file exists."
        )
    
    # Check file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read file content
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        
        # Read the original CSV to get date information
        df_original = pd.read_csv(StringIO(csv_content), delimiter=";")
        df_original['Time'] = pd.to_datetime(df_original['Time'])
        
        # Process the CSV data for prediction
        solar_df_test = process_csv_data(csv_content)
        
        # Get the last 24 rows for previous data
        if len(solar_df_test) < 24:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough data. Need at least 24 rows, got {len(solar_df_test)}"
            )
        
        # Extract previous 24 hours data
        prev_data = []
        last_24_indices = range(len(solar_df_test) - 24, len(solar_df_test))
        
        for i in last_24_indices:
            prev_data.append({
                "radiation": float(df_original.iloc[i]['Solar Radiation W/m2']),
                "humidity": float(df_original.iloc[i]['Humidity %']),
                "temp": float(df_original.iloc[i]['Temp *C']),
                "date": df_original.iloc[i]['Time'].strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Convert to model input format
        X2_test_data = df_to_X_inference(solar_df_test, window_size=24)
        
        # Preprocess
        X2_test_data = preprocess(X2_test_data)
        
        # Make prediction
        test_predictions = selected_model_obj.predict(X2_test_data).flatten()
        
        # Get the date for prediction (next hour after last data point)
        last_date = df_original.iloc[-1]['Time']
        pred_date = (last_date + pd.Timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Get metrics for the selected model
        metrics = MODEL_METRICS.get(model_name, {"MAE": 0, "MSE": 0, "RMSE": 0, "R2": 0})
        mae = metrics["MAE"]
        rmse = metrics["RMSE"]

        # Create results with confidence intervals
        test_results = {
            "model": model_name,
            "mae": metrics["MAE"],
            "mse": metrics["MSE"],
            "rmse": metrics["RMSE"],
            "r2": metrics["R2"],
            "prev": prev_data,
            "pred": {
                "date": pred_date,
                "rad_pred": test_predictions.tolist(),
                "Lower_MAE": (test_predictions - mae).tolist(),
                "Upper_MAE": (test_predictions + mae).tolist(),
                "Lower_RMSE": (test_predictions - rmse).tolist(),
                "Upper_RMSE": (test_predictions + rmse).tolist()
            },
            "model_metrics": MODEL_METRICS
        }
        
        return test_results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
