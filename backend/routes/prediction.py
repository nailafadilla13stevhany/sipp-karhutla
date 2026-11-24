from datetime import datetime, timezone
import math
from flask import Blueprint, jsonify, request
from services.model_service import predict_risk, FEATURE_COLUMNS
from services.recommendation_service import build_factors, build_recommendation

bp = Blueprint('prediction', __name__)

NUMERIC_RANGES = {
    'Hotspot_Density_7D': (0, 100000),
    'Consecutive_Dry_Days': (0, 3650),
    'Historical_Fire_Frequency': (0, 100000),
    'Patrol_Coverage_Gap': (0, 1),
    'NDVI_Dryness_Index': (0, 1),
    'Mean_Temp_Humidity_Ratio': (0, 100),
    'Wind_Speed_Mean_3D': (0, 500),
}


def validate(body):
    if not isinstance(body, dict):
        return None, 'Body harus berupa JSON object.'
    values = {}
    for key in FEATURE_COLUMNS:
        if key not in body:
            return None, f'Field {key} wajib diisi.'
        try:
            value = float(body[key])
        except (ValueError, TypeError):
            return None, f'Field {key} harus berupa angka.'
        low, high = NUMERIC_RANGES[key]
        if not math.isfinite(value) or not low <= value <= high:
            return None, f'Field {key} harus berada pada rentang {low} sampai {high}.'
        values[key] = value
    values['Consecutive_Dry_Days'] = int(values['Consecutive_Dry_Days'])
    values['location_name'] = str(body.get('location_name', 'Wilayah tidak bernama')).strip()[:150]
    observed_at = body.get('observed_at')
    if observed_at:
        try:
            parsed = datetime.fromisoformat(str(observed_at).replace('Z', '+00:00'))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            values['is_stale'] = (datetime.now(timezone.utc) - parsed).days > 7
        except ValueError:
            return None, 'Format observed_at tidak valid; gunakan ISO 8601.'
    else:
        values['is_stale'] = False
    return values, None


@bp.post('/api/predict')
def predict():
    payload, error = validate(request.get_json(silent=True))
    if error:
        return jsonify({'error': error}), 400
    try:
        result = predict_risk(payload)
    except FileNotFoundError as exc:
        return jsonify({'error': str(exc)}), 503
    except Exception:
        return jsonify({'error': 'Prediksi tidak dapat dilakukan. Periksa model dan input.'}), 500

    recommendation = build_recommendation(
        payload['location_name'], result['risk_level'], result['confidence'], payload,
        stale=payload['is_stale'],
    )
    return jsonify({
        **result,
        'location_name': payload['location_name'],
        'factors': build_factors(payload),
        'verification_status': recommendation['verification_status'],
        'recommendation': recommendation['recommendation'],
        'disclaimer': recommendation['disclaimer'],
    })
