from .model_service import FEATURE_COLUMNS


def build_factors(payload):
    factors = []
    if payload.get('Hotspot_Density_7D', 0) >= 0.65:
        factors.append('Kepadatan titik panas tinggi')
    if payload.get('Consecutive_Dry_Days', 0) >= 25:
        factors.append('Wilayah mengalami periode kering panjang')
    if payload.get('Historical_Fire_Frequency', 0) >= 0.60:
        factors.append('Frekuensi kejadian historis tinggi')
    if payload.get('Patrol_Coverage_Gap', 0) >= 0.55:
        factors.append('Cakupan patroli memiliki kesenjangan')
    if payload.get('NDVI_Dryness_Index', 0) >= 0.65:
        factors.append('Indeks kekeringan vegetasi tinggi')
    if payload.get('Mean_Temp_Humidity_Ratio', 0) >= 0.65:
        factors.append('Rasio suhu terhadap kelembapan mendukung risiko')
    if payload.get('Wind_Speed_Mean_3D', 0) >= 10:
        factors.append('Kecepatan angin rata-rata meningkat')
    return factors or ['Tidak ada faktor dominan yang terdeteksi']


def build_recommendation(location_name, risk_level, confidence, payload, stale=False):
    incomplete = any(payload.get(column) is None for column in FEATURE_COLUMNS)
    needs_verification = stale or incomplete or confidence < 0.60
    if risk_level == 'High':
        priority, action = 1, 'Prioritas utama patroli dan verifikasi lapangan.'
    elif risk_level == 'Medium':
        priority, action = 2, 'Pemantauan berkala dan verifikasi kondisi lapangan.'
    else:
        priority, action = 3, 'Pemantauan pencegahan rutin.'
    reasons = build_factors(payload)
    if stale:
        reasons.append('Data pengamatan lebih lama dari 7 hari')
    if incomplete:
        reasons.append('Data input tidak lengkap')
    if confidence < 0.60:
        reasons.append('Keyakinan prediksi di bawah 60 persen')
    return {
        'location_name': location_name,
        'risk_level': risk_level,
        'confidence': float(confidence),
        'priority': priority,
        'recommendation': action,
        'reason': '; '.join(reasons),
        'verification_status': 'Perlu Verifikasi Petugas' if needs_verification else 'Normal',
        'disclaimer': 'Rekomendasi hanya bahan pertimbangan petugas; bukan keputusan otomatis untuk tindakan pemadaman.',
    }
