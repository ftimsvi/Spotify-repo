import datetime

import jwt
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from . import SECRET_KEY, get_db_connection

profile = Blueprint('profile', __name__)


@profile.route('')
def home():
    token = request.headers.get('Authorization').split()[1]
    print(token)
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT first_name, last_name, date_of_birth, email, country, balance FROM Users WHERE user_id = %s', (data['user_id'],))

        user = cur.fetchone()

        cur.close()
        conn.close()

        return jsonify({'user': user}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@profile.route('/changePassword', methods=['GET', 'POST'])
def changePassword():
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute('SELECT password FROM Users WHERE user_id = %s',
                        (data['user_id'],))
            user = cur.fetchone()

            json_file = request.get_json()
            old_password = json_file['old_password']
            new_password = json_file['new_password']

            if user and check_password_hash(user[0], old_password):
                cur.execute('UPDATE Users SET password = %s WHERE user_id = %s',
                            (generate_password_hash(new_password), data['user_id']))
                conn.commit()

                cur.close()
                conn.close()
                return jsonify({'message': 'Password changed successfully'}), 200

            return jsonify({'message': 'Invalid credentials'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@profile.route('/updateBalance', methods=['GET', 'POST'])
def updateBalance():
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute('SELECT balance FROM Users WHERE user_id = %s',
                        (data['user_id'],))
            user = cur.fetchone()

            json_file = request.get_json()
            balance = json_file['balance']

            if user:
                cur.execute('UPDATE Users SET balance = %s WHERE user_id = %s',
                            (int(balance) + user[0], data['user_id']))
                conn.commit()

                cur.close()
                conn.close()
                return jsonify({'message': 'Balance updated successfully'}), 200

            return jsonify({'message': 'Invalid credentials'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@profile.route('/upgradeToPremium', methods=['GET', 'POST'])
def upgradeToPremium():
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute('SELECT * FROM Users WHERE user_id = %s',
                        (data['user_id'],))
            user = cur.fetchone()

            json_file = request.get_json()
            premium_duration = json_file['premium_duration']
            if premium_duration == 90:
                value = 140
            elif premium_duration == 60:
                value = 100
            elif premium_duration == 30:
                value = 60
            else:
                return jsonify({'message': 'Invalid day of subscription duration.'}), 401

            if user:
                cur.execute('UPDATE Users SET balance = %s, is_premium = %s, start_premium = %s, end_premium = %s WHERE user_id = %s',
                            (user[7]-value, True, datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=int(premium_duration)), data['user_id']))
                conn.commit()

                cur.close()
                conn.close()
                return jsonify({'message': 'Upgraded to premium successfully'}), 200
            return jsonify({'message': 'User is already premium'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


# @profile.route('/deleteAccount', methods=['DELETE'])
# def deleteAccount():
#     token = request.headers.get('Authorization').split()[1]
#     if not token:
#         return jsonify({'error': 'Missing token'}), 400

#     try:
#         data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

#         conn = get_db_connection()
#         cur = conn.cursor()

#         cur.execute('SELECT * FROM Users WHERE user_id = %s',
#                     (data['user_id'],))
#         user = cur.fetchone()

#         if user:
#             cur.execute('DELETE FROM Users WHERE user_id = %s',
#                         (data['user_id'],))
#             conn.commit()

#             cur.close()
#             conn.close()
#             return jsonify({'message': 'Account deleted successfully'}), 200
#         return jsonify({'message': 'Invalid credentials'}), 401
#     except jwt.ExpiredSignatureError:
#         return jsonify({'error': 'Expired token'}), 400

@profile.route('/deleteAccount', methods=['DELETE'])
def deleteAccount():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()
        print(data['user_id'])
        # Call delete_user function
        deleted = cur.execute('SELECT delete_user(%s::INT)', (data['user_id'],))
        print(deleted)
        # Check function return value (boolean)
        if deleted:
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({'message': 'Account deleted successfully'}), 200
        else:
            return jsonify({'message': 'User not found'}), 404  # Account not found
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400

