def build_factors(payload):
    factors = []
    if payload['Hotspot_Density_7D'] >= 0.65:
        factors.append('Kepadatan titik panas tinggi')
    if payload['Consecutive_Dry_Days'] >= 25:
        factors.append('Wilayah mengalami periode kering panjang')
    if payload['Historical_Fire_Frequency'] >= 0.60:
        factors.append('Frekuensi kejadian historis tinggi')
    if payload['Patrol_Coverage_Gap'] >= 0.55:
        factors.append('Cakupan patroli memiliki kesenjangan')
    if payload['NDVI_Dryness_Index'] >= 0.65:
        factors.append('Indeks kekeringan vegetasi tinggi')
    if payload['Mean_Temp_Humidity_Ratio'] >= 0.65:
        factors.append('Rasio suhu terhadap kelembapan mendukung risiko')
    if payload['Wind_Speed_Mean_3D'] >= 10:
        factors.append('Kecepatan angin rata-rata meningkat')
    return factors or ['Tidak ada faktor dominan yang terdeteksi']


def build_recommendation(location_name, risk_level, confidence, payload):
    verification_status = 'Normal'
    if confidence < 0.60:
        verification_status = 'Perlu Verifikasi Petugas'

    if risk_level == 'High':
        priority = 1
        action = 'Prioritas utama untuk patroli dan verifikasi lapangan.'
    elif risk_level == 'Medium':
        priority = 2
        action = 'Lakukan pemantauan berkala dan siapkan verifikasi lapangan.'
    else:
        priority = 3
        action = 'Pertahankan pemantauan pencegahan secara rutin.'

    reasons = build_factors(payload)
    if confidence < 0.60:
        reasons.append('Keyakinan prediksi berada di bawah 60 persen')

    return {
        'location_name': location_name,
        'risk_level': risk_level,
        'confidence': confidence,
        'priority': priority,
        'recommendation': action,
        'reason': '; '.join(reasons),
        'verification_status': verification_status,
        'disclaimer': 'Rekomendasi merupakan bahan pertimbangan petugas, bukan keputusan otomatis untuk tindakan pemadaman.',
    }
