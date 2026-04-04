import joblib
import os
from xgboost import XGBClassifier

def convert():
    model_path = os.path.join('models', 'aegis_champion_xgb.pkl')
    output_path = os.path.join('models', 'aegis_model.json')
    
    print(f"Loading model from {model_path}...")
    model = joblib.load(model_path)
    
    print(f"Saving model to {output_path}...")
    model.save_model(output_path)
    print("Done!")

if __name__ == '__main__':
    convert()
