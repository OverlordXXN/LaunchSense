import os
import sys
import joblib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import train_launch_predictor

def main():
    print("Triggering drift-optimized production model retraining...")
    train_launch_predictor.main()
    
    from datetime import datetime
    models_dir = os.path.join('src', 'models')
    src_model = os.path.join(models_dir, 'kickstarter_launch_predictor.pkl')
    
    if os.path.exists(src_model):
        model = joblib.load(src_model)
        
        root_models_dir = 'models'
        os.makedirs(root_models_dir, exist_ok=True)
        
        day_str = datetime.now().strftime('%Y%m%d')
        daily_path = os.path.join(root_models_dir, f'model_{day_str}.joblib')
        recent_path = os.path.join(root_models_dir, 'model_recent.joblib')
        latest_path = os.path.join(root_models_dir, 'latest.joblib')
        
        joblib.dump(model, daily_path)
        joblib.dump(model, recent_path)
        joblib.dump(model, latest_path)
        
        print(f"Model saved incrementally: {daily_path}")
        print(f"Model saved as recent: {recent_path}")
        print(f"Model saved as latest: {latest_path}")
    else:
        print(f"Error: Expected model {src_model} not found.")

if __name__ == '__main__':
    main()
