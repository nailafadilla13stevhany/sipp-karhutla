from pathlib import Path
import pandas as pd

from .train_model import FEATURE_COLUMNS

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / 'dataset' / 'dummy_data.csv'


def load_patrol_data():
    import datetime
    now = datetime.date.today()
    return [
        {'id': 1, 'officer_name': 'Andi Saputra', 'location': 'Sebangau', 'patrol_date': str(now), 'latitude': -2.32, 'longitude': 113.90, 'status': 'Selesai'},
        {'id': 2, 'officer_name': 'Rina Maharani', 'location': 'Pulang Pisau', 'patrol_date': str(now), 'latitude': -2.68, 'longitude': 114.02, 'status': 'Berlangsung'},
    ]


def load_hotspots():
    df = pd.read_csv(DATASET_PATH)
    latest = df.groupby('location_name', as_index=False).tail(1)
    return latest.to_dict(orient='records')


def normalize_hotspot(row):
    return {
        'location_name': row['location_name'],
        'latitude': float(row['latitude']),
        'longitude': float(row['longitude']),
        'risk_level': row['risk_level'],
        'hotspot_count': int(max(1, round(float(row['Hotspot_Density_7D']) * 100))),
        'hotspot_density_7d': float(row['Hotspot_Density_7D']),
        'consecutive_dry_days': int(row['Consecutive_Dry_Days']),
    }
