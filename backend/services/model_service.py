from pathlib import Path
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / 'model' / 'saved_model' / 'risk_model.joblib'
FEATURE_COLUMNS = [
    'Hotspot_Density_7D', 'Consecutive_Dry_Days', 'Historical_Fire_Frequency',
    'Patrol_Coverage_Gap', 'NDVI_Dryness_Index', 'Mean_Temp_Humidity_Ratio',
    'Wind_Speed_Mean_3D',
]


def load_artifact():
    if not MODEL_PATH.exists():
        raise FileNotFoundError('Model belum dilatih. Dari root proyek jalankan: python model/train_model.py')
    return joblib.load(MODEL_PATH)


def predict_risk(payload):
    artifact = load_artifact()
    row = pd.DataFrame([{name: payload[name] for name in FEATURE_COLUMNS}], columns=FEATURE_COLUMNS)
    transformed = artifact['preprocessor'].transform(row)
    probabilities = artifact['model'].predict_proba(transformed)[0]
    index = int(probabilities.argmax())
    risk = artifact['label_encoder'].inverse_transform([index])[0]
    return {
        'risk_level': str(risk),
        'confidence': float(probabilities[index]),
        'probabilities': {str(name): float(probabilities[i]) for i, name in enumerate(artifact['label_encoder'].classes_)},
    }
