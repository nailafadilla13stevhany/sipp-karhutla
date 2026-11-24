from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / 'model' / 'saved_model' / 'risk_model.joblib'

FEATURE_COLUMNS = [
    'Hotspot_Density_7D',
    'Consecutive_Dry_Days',
    'Historical_Fire_Frequency',
    'Patrol_Coverage_Gap',
    'NDVI_Dryness_Index',
    'Mean_Temp_Humidity_Ratio',
    'Wind_Speed_Mean_3D',
]


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError('Model belum dilatih. Jalankan: python model/train_model.py')
    return joblib.load(MODEL_PATH)


def predict(payload):
    import pandas as pd
    artifact = load_model()
    row = pd.DataFrame([{column: payload[column] for column in FEATURE_COLUMNS}])
    row = artifact['preprocessor'].transform(row)
    probabilities = artifact['model'].predict_proba(row)[0]
    index = int(probabilities.argmax())
    classes = list(artifact['model'].classes_)
    risk_level = str(classes[index])
    confidence = float(probabilities[index])
    return {
        'risk_level': risk_level,
        'confidence': confidence,
        'probabilities': {str(label): float(probabilities[i]) for i, label in enumerate(classes)},
    }
