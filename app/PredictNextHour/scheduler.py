"""
Script scheduler untuk menjalankan prediksi otomatis setiap jam
"""
import schedule
import time
from datetime import datetime
import predict_hourly


def run_prediction_job():
    """
    Job yang akan dijalankan setiap jam
    """
    print("\n" + "=" * 70)
    print(f"⏰ SCHEDULED PREDICTION JOB STARTED")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        # Run prediction
        results = predict_hourly.predict_next_hour()
        print("\n✅ Scheduled prediction completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error in scheduled prediction: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    Main scheduler function
    """
    print("=" * 70)
    print("🕐 SOLAR RADIATION PREDICTION SCHEDULER")
    print("=" * 70)
    print("📋 Configuration:")
    print("   - Prediction interval: Every hour")
    print("   - Using last 24 hours of data")
    print("   - Predictions logged to: predictions_log.json")
    print()
    print("🚀 Scheduler started!")
    print("   Press Ctrl+C to stop")
    print("=" * 70)
    
    # Schedule job setiap jam (at minute 0)
    schedule.every().hour.at(":00").do(run_prediction_job)
    
    # Alternative: Schedule setiap X menit untuk testing
    # schedule.every(5).minutes.do(run_prediction_job)
    
    # Run once immediately on startup
    print("\n🔄 Running initial prediction...")
    run_prediction_job()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Scheduler stopped by user")
        print("👋 Goodbye!")


if __name__ == "__main__":
    main()
