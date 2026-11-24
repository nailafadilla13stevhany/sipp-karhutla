from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / 'dataset' / 'dummy_data.csv'
_PATROLS = [
    {'id': 1, 'officer_name': 'Andi Saputra', 'location': 'Sebangau', 'patrol_date': '2026-11-24', 'latitude': -2.32, 'longitude': 113.90, 'status': 'Selesai'},
    {'id': 2, 'officer_name': 'Rina Maharani', 'location': 'Pulang Pisau', 'patrol_date': '2026-11-24', 'latitude': -2.68, 'longitude': 114.02, 'status': 'Berlangsung'},
]


def load_hotspots():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f'Dataset tidak ditemukan: {DATASET_PATH}')
    frame = pd.read_csv(DATASET_PATH)
    latest = frame.groupby('location_name', sort=False).tail(1)
    result = []
    for row in latest.to_dict(orient='records'):
        item = {key: row[key] for key in (
            'location_name', 'latitude', 'longitude', 'Hotspot_Density_7D',
            'Consecutive_Dry_Days', 'Historical_Fire_Frequency', 'Patrol_Coverage_Gap',
            'NDVI_Dryness_Index', 'Mean_Temp_Humidity_Ratio', 'Wind_Speed_Mean_3D',
            'observed_at'
        )}
        item.update({
            'latitude': float(item['latitude']), 'longitude': float(item['longitude']),
            'Hotspot_Density_7D': float(item['Hotspot_Density_7D']),
            'Consecutive_Dry_Days': int(item['Consecutive_Dry_Days']),
            'Historical_Fire_Frequency': float(item['Historical_Fire_Frequency']),
            'Patrol_Coverage_Gap': float(item['Patrol_Coverage_Gap']),
            'NDVI_Dryness_Index': float(item['NDVI_Dryness_Index']),
            'Mean_Temp_Humidity_Ratio': float(item['Mean_Temp_Humidity_Ratio']),
            'Wind_Speed_Mean_3D': float(item['Wind_Speed_Mean_3D']),
            'risk_level': str(row['risk_level']),
            'hotspot_count': int(max(1, round(float(row['Hotspot_Density_7D']) * 100))),
            'hotspot_density_7d': float(row['Hotspot_Density_7D']),
            'consecutive_dry_days': int(row['Consecutive_Dry_Days']),
        })
        result.append(item)
    return result


def load_patrols():
    return list(_PATROLS)


def add_patrol(patrol):
    item = {'id': max((p['id'] for p in _PATROLS), default=0) + 1, **patrol}
    _PATROLS.append(item)
    return item
