from datetime import datetime, timezone
from flask import Blueprint, jsonify
from services.data_service import load_hotspots
from services.model_service import predict_risk
from services.recommendation_service import build_recommendation

bp = Blueprint('recommendations', __name__)


@bp.get('/api/recommendations')
def recommendations():
    output = []
    try:
        for hotspot in load_hotspots():
            result = predict_risk(hotspot)
            try:
                observed = datetime.fromisoformat(hotspot['observed_at'].replace('Z', '+00:00'))
                stale = (datetime.now(timezone.utc) - observed).days > 7
            except (ValueError, TypeError):
                stale = True
            item = build_recommendation(
                hotspot['location_name'], result['risk_level'], result['confidence'], hotspot, stale=stale
            )
            item.update({'latitude': hotspot['latitude'], 'longitude': hotspot['longitude']})
            output.append(item)
    except FileNotFoundError as exc:
        return jsonify({'error': str(exc)}), 503
    output.sort(key=lambda item: (item['priority'], -item['confidence']))
    return jsonify(output)
