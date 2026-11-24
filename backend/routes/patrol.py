from datetime import date
from flask import Blueprint, jsonify, request
from services.data_service import load_patrols, add_patrol

bp = Blueprint('patrol', __name__)


@bp.route('/api/patrol', methods=['GET', 'POST'])
def patrol():
    if request.method == 'GET':
        return jsonify(load_patrols())
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({'error': 'Body harus berupa JSON object.'}), 400
    required = ('officer_name', 'location', 'patrol_date', 'latitude', 'longitude', 'status')
    missing = [key for key in required if body.get(key) in (None, '')]
    if missing:
        return jsonify({'error': 'Field wajib belum diisi: ' + ', '.join(missing)}), 400
    try:
        latitude, longitude = float(body['latitude']), float(body['longitude'])
        patrol_date = date.fromisoformat(str(body['patrol_date']))
    except (ValueError, TypeError):
        return jsonify({'error': 'Koordinat atau tanggal tidak valid.'}), 400
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return jsonify({'error': 'Koordinat berada di luar rentang yang valid.'}), 400
    status = str(body['status']).strip()
    if status not in {'Selesai', 'Berlangsung', 'Terjadwal'}:
        return jsonify({'error': 'Status harus Selesai, Berlangsung, atau Terjadwal.'}), 400
    item = add_patrol({
        'officer_name': str(body['officer_name']).strip()[:150],
        'location': str(body['location']).strip()[:150],
        'patrol_date': patrol_date.isoformat(),
        'latitude': latitude,
        'longitude': longitude,
        'status': status,
    })
    return jsonify(item), 201
