from flask import Flask, render_template, request, jsonify
import asyncio
import os
from datetime import datetime
from database import (
    get_all_scooters, get_scooter, create_rental,
    get_user_rentals, get_rental_payments, get_user
)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')

def async_run(coro):
    """Helper function to run async functions"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/')
def index():
    """Skuterlar katalogi - qora fon zamonaviy dizayn"""
    user_id = request.args.get('user_id', type=int)
    scooters = async_run(get_all_scooters())
    return render_template('index.html', scooters=scooters, user_id=user_id)

@app.route('/my-rentals')
def my_rentals():
    """Userning ijaralari va to'lovlari"""
    user_id = request.args.get('user_id', type=int)

    if not user_id:
        return "User ID kerak", 400

    user = async_run(get_user(user_id))
    rentals = async_run(get_user_rentals(user_id))

    # Har bir ijara uchun to'lovlarni olamiz
    rentals_data = []
    for rental in rentals:
        rental_dict = dict(rental)
        payments = async_run(get_rental_payments(rental['id']))
        rental_dict['payments'] = [dict(p) for p in payments]

        # Jami to'langan summani hisoblaymiz
        total_paid = sum(p['amount'] for p in payments if p['status'] == 'paid')
        rental_dict['total_paid'] = total_paid
        rental_dict['remaining'] = rental_dict['total_price'] - total_paid

        rentals_data.append(rental_dict)

    return render_template('my_rentals.html',
                         rentals=rentals_data,
                         user_id=user_id,
                         user=user)

@app.route('/api/scooters')
def api_scooters():
    """Barcha mavjud skuterlarni olish"""
    scooters = async_run(get_all_scooters())
    return jsonify([dict(s) for s in scooters])

@app.route('/api/my-rentals')
def api_my_rentals():
    """Userning ijaralarini olish"""
    user_id = request.args.get('user_id', type=int)

    if not user_id:
        return jsonify({'error': 'User ID kerak'}), 400

    rentals = async_run(get_user_rentals(user_id))

    # Har bir ijara uchun to'lovlarni qo'shamiz
    result = []
    for rental in rentals:
        rental_dict = dict(rental)
        payments = async_run(get_rental_payments(rental['id']))
        rental_dict['payments'] = [dict(p) for p in payments]

        # Jami to'langan va qoldiq
        total_paid = sum(p['amount'] for p in payments if p['status'] == 'paid')
        rental_dict['total_paid'] = total_paid
        rental_dict['remaining'] = rental_dict['total_price'] - total_paid

        result.append(rental_dict)

    return jsonify(result)

@app.route('/api/rent', methods=['POST'])
def rent_scooter():
    """Skuter ijaraga olish API"""
    data = request.json
    user_id = data.get('user_id')
    scooter_id = data.get('scooter_id')
    rental_type = data.get('rental_type')

    if not all([user_id, scooter_id, rental_type]):
        return jsonify({'success': False, 'message': 'Ma\'lumotlar to\'liq emas'}), 400

    scooter = async_run(get_scooter(scooter_id))
    if not scooter:
        return jsonify({'success': False, 'message': 'Skuter topilmadi'}), 404

    if scooter['status'] != 'available':
        return jsonify({'success': False, 'message': 'Skuter band'}), 400

    # Narxni aniqlash
    if rental_type == 'weekly':
        total_price = scooter['price_weekly']
    else:
        total_price = scooter['price_monthly']

    # Ijarani yaratish
    rental_id = async_run(create_rental(user_id, scooter_id, rental_type, total_price))

    return jsonify({
        'success': True,
        'message': 'Skuter muvaffaqiyatli ijaraga olindi!',
        'rental_id': rental_id
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
