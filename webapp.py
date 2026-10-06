from flask import Flask, render_template, request, jsonify, session
from functools import wraps
import os
from database import get_all_scooters, get_scooter, get_user_rentals, get_rental_payments
import asyncio

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

@app.route('/')
def index():
    user_id = request.args.get('user_id')
    if user_id:
        session['user_id'] = user_id
    return render_template('index.html')

@app.route('/api/scooters')
@async_route
async def api_scooters():
    scooters = await get_all_scooters()
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

@app.route('/rental/<int:rental_id>')
def rental_detail(rental_id):
    return render_template('rental_detail.html', rental_id=rental_id)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
