from flask import Flask, render_template, request, jsonify
import asyncio
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from database import (
    init_db, get_user, get_user_rentals, get_rental_payments,
    create_rental, add_payment, get_all_rentals,
    get_rental_by_id, get_rental_documents, is_admin,
    update_weekly_payment, get_rental_payment_info,
    get_all_overdue_rentals, get_all_active_rentals_with_info,
    complete_rental
)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')

# Upload folder
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'mp4', 'mov', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def async_run(coro):
    """Helper function to run async functions"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# ==================== USER ROUTES ====================

@app.route('/my-rentals')
def my_rentals():
    """User ijaralarini ko'rish"""
    user_id = request.args.get('user_id', type=int)
    return render_template('my_rentals.html', user_id=user_id)

@app.route('/api/my-rentals')
def api_my_rentals():
    """User ijaralarini olish API"""
    user_id = request.args.get('user_id', type=int)

    if not user_id:
        return jsonify({'error': 'User ID kerak'}), 400

    rentals = async_run(get_user_rentals(user_id))

    result = []
    for rental in rentals:
        rental_dict = dict(rental)
        payments = async_run(get_rental_payments(rental['id']))
        rental_dict['payments'] = [dict(p) for p in payments]

        total_paid = sum(p['amount'] for p in payments)
        rental_dict['total_paid'] = total_paid

        payment_info = async_run(get_rental_payment_info(rental['id']))
        if payment_info:
            rental_dict['paid_until'] = payment_info['paid_until']
            rental_dict['next_payment_date'] = payment_info['next_payment_date']
            rental_dict['overdue_days'] = payment_info['overdue_days']
            rental_dict['debt_amount'] = payment_info['debt_amount']

        result.append(rental_dict)

    return jsonify({'rentals': result})

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
def admin_panel():
    """Admin panel"""
    user_id = request.args.get('user_id', type=int)

    if not user_id or not async_run(is_admin(user_id)):
        return "Access Denied", 403

    return render_template('admin/index.html')

@app.route('/api/admin/create-rental', methods=['POST'])
def api_admin_create_rental():
    """Admin yangi ijara yaratadi"""
    try:
        user_identifier = request.form.get('user_id')
        scooter_name = request.form.get('scooter_name')
        weekly_payment = float(request.form.get('weekly_payment'))
        full_name = request.form.get('full_name', '').strip()

        # User ID ni topish (telefon yoki ID bo'lishi mumkin)
        if user_identifier.startswith('+') or len(user_identifier) == 12:
            # Telefon raqami
            from database import get_user_by_phone
            user = async_run(get_user_by_phone(user_identifier))
            if not user:
                return jsonify({'success': False, 'message': 'Bunday telefon raqamli user topilmadi'}), 404
            user_id = user['user_id']
        else:
            # Telegram ID
            user_id = int(user_identifier)
            user = async_run(get_user(user_id))
            if not user:
                return jsonify({'success': False, 'message': 'Bunday user topilmadi'}), 404

        if full_name:
            from database import update_user_profile
            async_run(update_user_profile(user_id, full_name=full_name))

        # Fayllarni saqlash
        scooter_image_path = None
        passport_image_path = None
        video_file_path = None

        if 'scooter_image' in request.files:
            file = request.files['scooter_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"scooter_{int(datetime.now().timestamp())}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                scooter_image_path = f'/static/uploads/{filename}'

        if 'passport_image' in request.files:
            file = request.files['passport_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"passport_{int(datetime.now().timestamp())}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                passport_image_path = f'/static/uploads/{filename}'

        if 'video_file' in request.files:
            file = request.files['video_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"video_{int(datetime.now().timestamp())}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                video_file_path = f'/static/uploads/{filename}'

        # Ijarani yaratish
        rental_id = async_run(create_rental(
            user_id, scooter_name, weekly_payment,
            scooter_image_path, passport_image_path, video_file_path
        ))

        return jsonify({
            'success': True,
            'rental_id': rental_id,
            'message': 'Ijara muvaffaqiyatli yaratildi!'
        })

    except Exception as e:
        print(f"Error creating rental: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/add-payment', methods=['POST'])
def api_admin_add_payment():
    """Admin to'lov kiritadi"""
    try:
        data = request.json
        user_identifier = data.get('user_id')
        amount = float(data.get('amount'))

        print(f"Payment request: user={user_identifier}, amount={amount}")

        # User ID ni topish
        if user_identifier.startswith('+') or len(user_identifier) == 12:
            from database import get_user_by_phone
            user = async_run(get_user_by_phone(user_identifier))
            if not user:
                return jsonify({'success': False, 'message': 'User topilmadi'}), 404
            user_id = user['user_id']
        else:
            user_id = int(user_identifier)

        print(f"User ID: {user_id}")

        # User'ning faol ijarasini topish
        rentals = async_run(get_user_rentals(user_id, active_only=True))
        print(f"Active rentals found: {len(rentals) if rentals else 0}")

        if not rentals:
            return jsonify({'success': False, 'message': 'Bu userda faol ijara yo\'q'}), 404

        rental_id = rentals[0]['id']
        print(f"Rental ID: {rental_id}")

        # To'lov qo'shish
        async_run(add_payment(rental_id, amount))
        print(f"Payment added successfully to rental {rental_id}")

        return jsonify({
            'success': True,
            'message': 'To\'lov muvaffaqiyatli kiritildi!'
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error adding payment: {e}")
        print(f"Full error: {error_details}")
        return jsonify({'success': False, 'message': f'Xatolik: {str(e)}'}), 500

@app.route('/api/admin/rentals')
def api_admin_rentals():
    """Barcha ijaralarni olish"""
    try:
        rentals = async_run(get_all_rentals())
        return jsonify([dict(r) for r in rentals])
    except Exception as e:
        print(f"Error loading rentals: {e}")
        return jsonify([]), 500

@app.route('/api/admin/rental/<int:rental_id>')
def api_admin_rental_details(rental_id):
    """Bitta ijarani batafsil olish"""
    try:
        rental = async_run(get_rental_by_id(rental_id))
        documents = async_run(get_rental_documents(rental_id))
        payments = async_run(get_rental_payments(rental_id))

        # User ma'lumotlarini qo'shamiz
        user = async_run(get_user(rental['user_id']))
        rental_dict = dict(rental)
        rental_dict['full_name'] = user['full_name'] if user else 'N/A'
        rental_dict['phone'] = user['phone'] if user else 'N/A'

        return jsonify({
            'rental': rental_dict,
            'documents': dict(documents) if documents else None,
            'payments': [dict(p) for p in payments]
        })
    except Exception as e:
        print(f"Error loading rental details: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/update-weekly-payment', methods=['POST'])
def api_admin_update_weekly_payment():
    """Haftalik to'lovni o'zgartirish"""
    try:
        data = request.json
        rental_id = int(data.get('rental_id'))
        new_amount = float(data.get('amount'))

        async_run(update_weekly_payment(rental_id, new_amount))

        return jsonify({
            'success': True,
            'message': 'Haftalik to\'lov o\'zgartirildi!'
        })
    except Exception as e:
        print(f"Error updating payment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/overdue-rentals')
def api_admin_overdue_rentals():
    """Kechikkan to'lovlar ro'yxati"""
    try:
        overdue = async_run(get_all_overdue_rentals())
        return jsonify(overdue)
    except Exception as e:
        print(f"Error loading overdue rentals: {e}")
        return jsonify([]), 500


@app.route('/api/admin/active-rentals')
def api_admin_active_rentals():
    """Barcha aktiv ijaralar to'lov info bilan"""
    try:
        rentals = async_run(get_all_active_rentals_with_info())
        return jsonify(rentals)
    except Exception as e:
        print(f"Error loading active rentals: {e}")
        return jsonify([]), 500


@app.route('/api/admin/rental/<int:rental_id>/payment-info')
def api_admin_rental_payment_info(rental_id):
    """Bitta ijarani to'lov holati"""
    try:
        info = async_run(get_rental_payment_info(rental_id))
        if not info:
            return jsonify({'error': 'Topilmadi'}), 404
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/complete-rental', methods=['POST'])
def api_admin_complete_rental():
    """Skuter topshirildi - ijarani yakunlash"""
    try:
        data = request.json
        rental_id = int(data.get('rental_id'))

        async_run(complete_rental(rental_id))

        return jsonify({
            'success': True,
            'message': 'Ijara muvaffaqiyatli yakunlandi!'
        })
    except Exception as e:
        print(f"Error completing rental: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    async_run(init_db())
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
