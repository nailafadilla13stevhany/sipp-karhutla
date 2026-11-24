from pathlib import Path
import joblib
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / 'dataset' / 'dummy_data.csv'
MODEL_PATH = ROOT / 'model' / 'saved_model' / 'risk_model.joblib'
FEATURE_COLUMNS = [
    'Hotspot_Density_7D', 'Consecutive_Dry_Days', 'Historical_Fire_Frequency',
    'Patrol_Coverage_Gap', 'NDVI_Dryness_Index', 'Mean_Temp_Humidity_Ratio',
    'Wind_Speed_Mean_3D',
]


def main():
    data = pd.read_csv(DATASET_PATH)
    missing = set(FEATURE_COLUMNS + ['risk_level']) - set(data.columns)
    if missing:
        raise ValueError(f'Kolom dataset tidak lengkap: {sorted(missing)}')
    X = data[FEATURE_COLUMNS]
    labels = data['risk_level'].astype(str)
    encoder = LabelEncoder()
    y = encoder.fit_transform(labels)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    imputer = SimpleImputer(strategy='median')
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(imputer.fit_transform(X_train))
    X_test_scaled = scaler.transform(imputer.transform(X_test))
    model = XGBClassifier(
        objective='multi:softprob', num_class=len(encoder.classes_), n_estimators=120,
        max_depth=4, learning_rate=0.08, subsample=0.9, colsample_bytree=0.9,
        eval_metric='mlogloss', random_state=42, n_jobs=2,
    )
    model.fit(X_train_scaled, y_train)
    predictions = model.predict(X_test_scaled)

    print('Catatan: semua metrik berikut hanya mengukur data dummy sintetis, bukan performa lapangan.')
    print(f'Accuracy: {accuracy_score(y_test, predictions):.4f}')
    print(f'Precision macro: {precision_score(y_test, predictions, average="macro", zero_division=0):.4f}')
    print(f'Recall macro: {recall_score(y_test, predictions, average="macro", zero_division=0):.4f}')
    print(f'Macro F1-Score: {f1_score(y_test, predictions, average="macro", zero_division=0):.4f}')
    print('Confusion matrix (urut kelas encoder):')
    print(confusion_matrix(y_test, predictions))
    print('Classification report:')
    print(classification_report(y_test, predictions, target_names=encoder.classes_, zero_division=0))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({'preprocessor': {'imputer': imputer, 'scaler': scaler}, 'model': model, 'label_encoder': encoder}, MODEL_PATH)
    print(f'Model tersimpan di {MODEL_PATH}')


if __name__ == '__main__':
    main()
