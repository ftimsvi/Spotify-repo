import datetime

import jwt
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from . import SECRET_KEY, get_db_connection

auth = Blueprint('auth', __name__)

blacklist = set()


def token_required(f):
    def wrap(*args, **kwargs):
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 403

        try:
            if token in blacklist:
                return jsonify({'error': 'Token has been blacklisted!'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return wrap


@auth.route('')
def home():
    return 'Home'


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()

        json_file = request.get_json()

        email = json_file['email']
        password = json_file['password']

        # check if user exists
        cur.execute('SELECT user_id, end_premium, password FROM Users WHERE email = %s',
                    (email,))
        user = cur.fetchone()

        if user[1] is not None and user[1] < datetime.datetime.now().date():
            cur.execute(
                'UPDATE Users SET is_premium = %s, start_premium = %s, end_premium = %s WHERE email = %s',
                (False, None, None, email)
            )
            conn.commit()

            cur.close()
            conn.close()
            return jsonify({'message': 'Your premium subscription has expired'}), 401

        if user and check_password_hash(user[2], password):
            token = jwt.encode({
                'user_id': user[0],
                'exp': datetime.datetime.now() + datetime.timedelta(hours=24)
            }, SECRET_KEY, algorithm='HS256')

            return jsonify({'token': token}), 200

        return jsonify({'message': 'Invalid credentials'}), 401


@auth.route('/logout')
@token_required
def logout():
    token = request.headers.get('Authorization').split()[1]
    blacklist.add(token)
    return jsonify({'message': 'Successfully logged out'}), 200


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()

        json_file = request.get_json()

        first_name = json_file['first_name']
        last_name = json_file['last_name']
        password = json_file['password']
        date_of_birth = json_file['date_of_birth']
        email = json_file['email']
        country = json_file['country']
        print(first_name, last_name, password, date_of_birth, email, country)

        # check if user already exists
        cur.execute(
            'SELECT * FROM Users WHERE email = %s', (email,)
        )
        user = cur.fetchone()
        if user:
            return jsonify({'message': 'User already exists'}), 400
        elif len(str(email)) < 4:
            return jsonify({'message': 'Email must be at least 4 characters long'}), 400
        elif len(str(first_name) + str(last_name)) < 2:
            return jsonify({'message': 'Name must be at least 2 characters long'}), 400
        elif len(str(password)) < 7:
            return jsonify({'message': 'Password must be at least 7 characters long'}), 400
        else:
            hashed_password = generate_password_hash(
                password, method='pbkdf2:sha256')

        try:
            cur.execute("CALL insert_user(%s, %s, %s, %s, %s, %s);",
                    (first_name, last_name, hashed_password, date_of_birth, email, country))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({'message': 'User created successfully'}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({'error': str(e)}), 500

            cur.execute(
                'INSERT INTO USERS (first_name, last_name, password, date_of_birth, email, country) VALUES (%s, %s, %s, %s, %s, %s)',
                (first_name, last_name, hashed_password,
                 date_of_birth, email, country)
            )

            conn.commit()

            cur.close()
            conn.close()
            return jsonify({'message': 'User created successfully'}), 201
