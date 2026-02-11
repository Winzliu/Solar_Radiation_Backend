"""
Script untuk testing API
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"


def test_root():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_health():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_predict(csv_file_path="fix_test.csv"):
    """Test prediction endpoint"""
    print("\n=== Testing Prediction Endpoint ===")
    
    try:
        with open(csv_file_path, "rb") as f:
            files = {"file": (csv_file_path, f, "text/csv")}
            response = requests.post(f"{BASE_URL}/predict", files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            pred_data = result['pred']
            print("\n=== Prediction Results ===")
            print(f"Date: {pred_data['date']}")
            print(f"Prediction: {pred_data['rad_pred']}")
            print(f"Lower MAE: {pred_data['Lower_MAE']}")
            print(f"Upper MAE: {pred_data['Upper_MAE']}")
            print(f"Lower RMSE: {pred_data['Lower_RMSE']}")
            print(f"Upper RMSE: {pred_data['Upper_RMSE']}")
            
            if 'model_metrics' in result:
                print("\n=== Model Metrics ===")
                print(json.dumps(result['model_metrics'], indent=2))
        else:
            print(f"Error: {response.text}")
    
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' tidak ditemukan")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    print("=" * 50)
    print("API Testing Script")
    print("=" * 50)
    
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "../data/fix_test.csv")
    
    # Test all endpoints
    test_root()
    test_health()
    test_predict(csv_path)
    
    print("\n" + "=" * 50)
    print("Testing Complete")
    print("=" * 50)
