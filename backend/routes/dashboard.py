from flask import Blueprint, jsonify
from services.data_service import load_hotspots, load_patrols

bp = Blueprint('dashboard', __name__)


@bp.get('/api/dashboard')
def dashboard():
    hotspots = load_hotspots()
    counts = {'Low': 0, 'Medium': 0, 'High': 0}
    for item in hotspots:
        counts[item['risk_level']] = counts.get(item['risk_level'], 0) + 1
    return jsonify({
        'total_hotspots': sum(item['hotspot_count'] for item in hotspots),
        'low_risk': counts['Low'],
        'medium_risk': counts['Medium'],
        'high_risk': counts['High'],
        'total_patrols': len(load_patrols()),
        'source': 'synthetic demonstration dataset',
    })


@bp.get('/api/hotspots')
def hotspots():
    return jsonify(load_hotspots())
