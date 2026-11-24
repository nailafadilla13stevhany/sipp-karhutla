from pathlib import Path
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / 'model' / 'saved_model' / 'risk_model.joblib'
FEATURE_COLUMNS = [
    'Hotspot_Density_7D', 'Consecutive_Dry_Days', 'Historical_Fire_Frequency',
    'Patrol_Coverage_Gap', 'NDVI_Dryness_Index', 'Mean_Temp_Humidity_Ratio',
    'Wind_Speed_Mean_3D',
]


def predict(features):
    if not MODEL_PATH.exists():
        raise FileNotFoundError('Model belum tersedia. Jalankan python model/train_model.py dari root proyek.')
    missing = [column for column in FEATURE_COLUMNS if column not in features]
    if missing:
        raise ValueError('Fitur wajib tidak tersedia: ' + ', '.join(missing))
    artifact = joblib.load(MODEL_PATH)
    frame = pd.DataFrame([{column: float(features[column]) for column in FEATURE_COLUMNS}])
    preprocessor = artifact['preprocessor']
    transformed = preprocessor['scaler'].transform(preprocessor['imputer'].transform(frame))
    probabilities = artifact['model'].predict_proba(transformed)[0]
    classes = artifact['label_encoder'].classes_
    index = int(probabilities.argmax())
    return {
        'risk_level': str(classes[index]),
        'confidence': float(probabilities[index]),
        'probabilities': {str(label): float(probabilities[i]) for i, label in enumerate(classes)},
    }


if __name__ == '__main__':
    example = dict(zip(FEATURE_COLUMNS, [0.8, 35, 0.75, 0.7, 0.8, 0.8, 14]))
    print(predict(example))
