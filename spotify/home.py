import datetime
from flask import Blueprint, request, jsonify
import jwt
from . import get_db_connection, SECRET_KEY

home = Blueprint('home', __name__)


@home.route('/<int:concert_id>/buyTicket', methods=['GET', 'POST'])
def buyTicket(concert_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT balance FROM Users WHERE user_id = %s', (data['user_id'],))
            balance = cur.fetchone()

            cur.execute(
                'SELECT cost FROM CONCERTS WHERE concert_id = %s', (concert_id,))
            price = cur.fetchone()

            if balance[0] < price[0]:
                return jsonify({'error': 'Insufficient funds'}), 400

            cur.execute(
                'INSERT INTO SUBSCRIBERS_BOUGHT_CONCERT (user_id, concert_id, date_of_payment) VALUES (%s, %s, %s)',
                (data['user_id'], concert_id, datetime.datetime.now()))
            conn.commit()

            cur.execute('UPDATE Users SET balance = balance - %s WHERE user_id = %s',
                        (price[0], data['user_id']))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Ticket bought successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@home.route('/getExpiredTickets')
def getExpiredTickets():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT concert_id FROM CONCERTS WHERE date_of_concert < %s', (datetime.datetime.now(),))
        expired_concerts = cur.fetchall()

        cur.execute(
            'SELECT concert_id FROM SUBSCRIBERS_BOUGHT_CONCERT WHERE user_id = %s', (data['user_id'],))
        bought_concerts = cur.fetchall()

        expired_tickets = []
        for concert in expired_concerts:
            if concert in bought_concerts:
                expired_tickets.append(concert)

        cur.close()
        conn.close()

        return jsonify({'expired_tickets': expired_tickets}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@home.route('/getNonExpiredTickets')
def getNonExpiredTickets():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT concert_id FROM CONCERTS WHERE date_of_concert > %s', (datetime.datetime.now(),))
        upcoming_concerts = cur.fetchall()

        cur.execute(
            'SELECT concert_id FROM SUBSCRIBERS_BOUGHT_CONCERT WHERE user_id = %s', (data['user_id'],))
        bought_concerts = cur.fetchall()

        tickets = []
        for concert in upcoming_concerts:
            if concert in bought_concerts:
                tickets.append(concert)

        cur.close()
        conn.close()

        return jsonify({'tickets': tickets}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@home.route('/<int:concert_id>/cancelTicket', methods=['GET', 'POST'])
def cancelTicket(concert_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT cost FROM CONCERTS WHERE concert_id = %s', (concert_id,))
            price = cur.fetchone()

            cur.execute(
                'SELECT * FROM SUBSCRIBERS_BOUGHT_CONCERT WHERE user_id = %s AND concert_id = %s',
                (data['user_id'], concert_id))
            ticket = cur.fetchone()

            if not ticket:
                return jsonify({'error': 'No ticket found'}), 400

            cur.execute('DELETE FROM SUBSCRIBERS_BOUGHT_CONCERT WHERE user_id = %s AND concert_id = %s',
                        (data['user_id'], concert_id))
            conn.commit()

            cur.execute('UPDATE Users SET balance = balance + %s WHERE user_id = %s',
                        (price[0], data['user_id']))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Ticket cancelled successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@home.route('/<int:user_id>/followUser', methods=['GET', 'POST'])
def followUser(user_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT * FROM USERS WHERE user_id = %s AND is_artist = %s', (data['user_id'], False))
            current_user = cur.fetchone()

            cur.execute(
                'SELECT * FROM Users WHERE user_id = %s', (user_id,))
            followed_user = cur.fetchone()

            if not followed_user:
                return jsonify({'error': 'User not found'}), 400

            if current_user:
                cur.execute(
                    'INSERT INTO FOLLOWING (user_id1_following, user_id2_followed) VALUES (%s, %s)',
                    (data['user_id'], user_id))
                conn.commit()

                cur.close()
                conn.close()
                return jsonify({'message': 'User followed successfully'}), 200
            return jsonify({'error': 'User not found'}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@home.route('/<int:artist_id>/followArtist', methods=['GET', 'POST'])
def followArtist(artist_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT * FROM USERS WHERE user_id = %s AND is_artist = %s', (data['user_id'], True))
            user = cur.fetchone()

            cur.execute(
                'SELECT * FROM Artists WHERE artist_id = %s', (artist_id,))
            artist = cur.fetchone()

            if not artist:
                return jsonify({'error': 'Artist not found'}), 400

            if user:
                cur.execute(
                    'INSERT INTO FOLLOWING (user_id1_following, user_id2_followed) VALUES (%s, %s)',
                    (data['user_id'], artist_id))
                conn.commit()

                cur.close()
                conn.close()
                return jsonify({'message': 'Artist followed successfully'}), 200

            return jsonify({'message': 'Artist followed successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@home.route('/<int:user_id>/unfollowUser', methods=['GET', 'POST'])
def unfollowUser(user_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT * FROM Users WHERE user_id = %s', (user_id,))
            user = cur.fetchone()

            if not user:
                return jsonify({'error': 'User not found'}), 400

            cur.execute('DELETE FROM FOLLOWING WHERE user_id1_following = %s AND user_id2_followed = %s',
                        (data['user_id'], user_id))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'User unfollowed successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@home.route('/<int:artist_id>/unfollowArtist', methods=['GET', 'POST'])
def unfollowArtist(artist_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT * FROM Artists WHERE artist_id = %s', (artist_id,))
            artist = cur.fetchone()

            if not artist:
                return jsonify({'error': 'Artist not found'}), 400

            cur.execute('DELETE FROM FOLLOWING WHERE user_id1_following = %s AND user_id2_followed = %s',
                        (data['user_id'], artist_id))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Artist unfollowed successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@home.route('/getUserFollowers')
def getUserFollowers():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT first_name, last_name FROM USERS WHERE user_id IN (SELECT user_id1_following FROM FOLLOWING WHERE user_id2_followed = %s)',
            (data['user_id'],))
        followers = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'followers': followers}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@home.route('/getUserFollowings')
def getUserFollowings():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT first_name, last_name FROM USERS WHERE user_id IN (SELECT user_id2_followed FROM FOLLOWING WHERE user_id1_following = %s)',
            (data['user_id'],))
        followings = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'followings': followings}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400
