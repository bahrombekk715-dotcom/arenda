from flask import Flask, render_template, request, jsonify, session, redirect
from functools import wraps
import os
from database import (
    get_all_scooters, get_scooter, get_user_rentals, get_rental_payments,
    add_scooter, update_scooter, delete_scooter, update_scooter_status,
    get_all_rentals, get_stats, is_admin, create_rental, add_document,
    get_rental_documents, add_payment, complete_rental, get_all_users,
    get_all_scooters_admin
)
import asyncio

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

_bot_ref = None

def set_bot(bot):
    global _bot_ref
    _bot_ref = bot

def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({'error': 'Access denied'}), 403
        return f(*args, **kwargs)
    return wrapped

# ==================== USER ROUTES ====================

@app.route('/')
def index():
    user_id = request.args.get('user_id')
    if user_id:
        session['user_id'] = user_id
    return render_template('index.html', user_id=user_id)

@app.route('/my-rentals')
def my_rentals():
    user_id = session.get('user_id') or request.args.get('user_id')
    if user_id:
        session['user_id'] = user_id
    return render_template('my_rentals.html', user_id=user_id)

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@async_route
async def admin_dashboard():
    user_id = request.args.get('user_id')
    if not user_id or not await is_admin(int(user_id)):
        return "Access Denied", 403
    session['user_id'] = user_id
    session['is_admin'] = True
    return render_template('admin/dashboard.html')

@app.route('/admin/scooters')
def admin_scooters():
    if not session.get('is_admin'):
        return redirect('/admin')
    return render_template('admin/scooters.html')

@app.route('/admin/rentals')
def admin_rentals():
    if not session.get('is_admin'):
        return redirect('/admin')
    return render_template('admin/rentals.html')

@app.route('/admin/users')
def admin_users():
    if not session.get('is_admin'):
        return redirect('/admin')
    return render_template('admin/users.html')

@app.route('/admin/notify')
def admin_notify():
    if not session.get('is_admin'):
        return redirect('/admin')
    return render_template('admin/notify.html')

# ==================== API ROUTES ====================

@app.route('/api/scooters')
@async_route
async def api_scooters():
    scooters = await get_all_scooters()
    return jsonify([dict(s) for s in scooters])

@app.route('/api/admin/scooters_all')
@async_route
async def api_all_scooters():
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403
    scooters = await get_all_scooters_admin()
    return jsonify([dict(s) for s in scooters])

@app.route('/api/scooter/<int:scooter_id>')
@async_route
async def api_scooter(scooter_id):
    scooter = await get_scooter(scooter_id)
    if scooter:
        return jsonify(dict(scooter))
    return jsonify({'error': 'Scooter not found'}), 404

@app.route('/api/my-rentals')
@async_route
async def api_my_rentals():
    user_id = session.get('user_id') or request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 401
    rentals = await get_user_rentals(int(user_id))
    result = []
    for rental in rentals:
        rental_dict = dict(rental)
        payments = await get_rental_payments(rental['id'])
        rental_dict['payments'] = [dict(p) for p in payments]
        result.append(rental_dict)
    return jsonify(result)

@app.route('/api/rental/create', methods=['POST'])
@async_route
async def api_create_rental():
    data = request.json
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    rental_id = await create_rental(
        int(user_id), data['scooter_id'], data['rental_type'], data['total_price']
    )
    return jsonify({'rental_id': rental_id, 'success': True})

# Admin API
@app.route('/api/admin/stats')
@async_route
async def api_admin_stats():
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403
    stats = await get_stats()
    return jsonify(stats)

@app.route('/api/admin/rentals')
@async_route
async def api_admin_rentals():
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403
    rentals = await get_all_rentals()
    return jsonify([dict(r) for r in rentals])

@app.route('/api/admin/users')
@async_route
async def api_admin_users():
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403
    users = await get_all_users()
    return jsonify([dict(u) for u in users])

@app.route('/api/admin/scooter/add', methods=['POST'])
@async_route
async def api_admin_add_scooter():
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403
    data = request.json
    scooter_id = await add_scooter(
        data['name'], data['model'],
        float(data['price_weekly']), float(data['price_monthly']),
        data.get('image_url')
    )
    return jsonify({'scooter_id': scooter_id, 'success': True})

@app.route('/api/admin/scooter/<int:scooter_id>/update', methods=['PUT'])
@async_route
async def api_admin_update_scooter(scooter_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403
    data = request.json
    await update_scooter(
        scooter_id, data['name'], data['model'],
        float(data['price_weekly']), float(data['price_monthly']),
        data.get('image_url')
    )
    return jsonify({'success': True})

@app.route('/api/admin/scooter/<int:scooter_id>/delete', methods=['DELETE'])
@async_route
async def api_admin_delete_scooter(scooter_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403
    await delete_scooter(scooter_id)
    return jsonify({'success': True})

@app.route('/api/admin/rental/<int:rental_id>/complete', methods=['POST'])
@async_route
async def api_admin_complete_rental(rental_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403
    await complete_rental(rental_id)
    return jsonify({'success': True})

# Notify API
@app.route('/api/admin/notify/broadcast', methods=['POST'])
@async_route
async def api_notify_broadcast():
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403
    data = request.json
    message_text = data.get('message', '').strip()
    if not message_text:
        return jsonify({'error': 'Empty message'}), 400
    if not _bot_ref:
        return jsonify({'error': 'Bot not connected'}), 503
    users = await get_all_users()
    sent = 0
    for user in users:
        try:
            await _bot_ref.send_message(user['user_id'], message_text, parse_mode='HTML')
            sent += 1
        except Exception:
            pass
    return jsonify({'success': True, 'sent': sent})

@app.route('/api/admin/notify/single', methods=['POST'])
@async_route
async def api_notify_single():
    if not session.get('is_admin'):
        return jsonify({'error': 'Access denied'}), 403
    data = request.json
    user_id = data.get('user_id')
    message_text = data.get('message', '').strip()
    if not user_id or not message_text:
        return jsonify({'error': 'Missing fields'}), 400
    if not _bot_ref:
        return jsonify({'error': 'Bot not connected'}), 503
    try:
        await _bot_ref.send_message(int(user_id), message_text, parse_mode='HTML')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
