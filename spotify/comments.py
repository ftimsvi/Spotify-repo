import datetime
from flask import Blueprint, jsonify, request
import jwt
from . import get_db_connection, SECRET_KEY

comments = Blueprint('comments', __name__)


@comments.route('/userCommentsTrack', methods=['GET', 'POST'])
def userCommentsTrack():
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT * FROM Users WHERE user_id = %s and is_premium = %s',
                (data['user_id'], True))
            user = cur.fetchone()

            if not user:
                return jsonify({'error': 'User not found or not premium'}), 400

            json_file = request.get_json()
            track_id = json_file['track_id']
            comment_text = json_file['comment_text']

            cur.execute(
                'INSERT INTO SUBSCRIBERS_COMMENTS_ON_TRACKS (user_id, track_id, comment_text, comment_time) VALUES (%s, %s, %s, %s)',
                (data['user_id'], track_id, comment_text, datetime.datetime.now()))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Comment added successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@comments.route('/deleteComment', methods=['DELETE'])
def deleteComment():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        json_file = request.get_json()
        comment_id = json_file['comment_id']

        cur.execute(
            'SELECT * FROM SUBSCRIBERS_COMMENTS_ON_TRACKS WHERE user_id = %s and comment_id = %s',
            (data['user_id'], comment_id))
        comment = cur.fetchone()

        if not comment:
            return jsonify({'error': 'Comment not found'}), 400

        cur.execute(
            'DELETE FROM SUBSCRIBERS_COMMENTS_ON_TRACKS WHERE user_id = %s and comment_id = %s',
            (data['user_id'], comment_id))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'message': 'Comment deleted successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@comments.route('/getCommentsOnTrack', methods=['GET', 'POST'])
def getCommentsOnTrack():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        json_file = request.get_json()
        track_id = json_file['track_id']

        cur.execute(
            'SELECT * FROM SUBSCRIBERS_COMMENTS_ON_TRACKS WHERE track_id = %s',
            (track_id,))
        comment = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'comments': comment}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@comments.route('/countCommentsOnTrack', methods=['GET', 'POST'])
def countCommentsOnTrack():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            json_file = request.get_json()
            track_id = json_file['track_id']

            cur.execute(
                'SELECT COUNT(*) FROM SUBSCRIBERS_COMMENTS_ON_TRACKS WHERE track_id = %s',
                (track_id,))
            comments_count = cur.fetchone()

            cur.close()
            conn.close()

            return jsonify({'comments': comments_count}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@comments.route('/userCommentsAlbum', methods=['GET', 'POST'])
def userCommentsAlbum():
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT * FROM Users WHERE user_id = %s and is_premium = %s',
                (data['user_id'], True))
            user = cur.fetchone()

            if not user:
                return jsonify({'error': 'User not found or not premium'}), 400

            json_file = request.get_json()
            album_id = json_file['album_id']
            comment_text = json_file['comment_text']

            cur.execute(
                'INSERT INTO SUBSCRIBERS_COMMENTS_ON_ALBUM (user_id, album_id, comment_text, comment_time) VALUES (%s, %s, %s, %s)',
                (data['user_id'], album_id, comment_text, datetime.datetime.now()))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Comment added successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@comments.route('/deleteCommentAlbum', methods=['DELETE'])
def deleteCommentAlbum():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        json_file = request.get_json()
        comment_id = json_file['comment_id']

        cur.execute(
            'SELECT * FROM SUBSCRIBERS_COMMENTS_ON_ALBUM WHERE user_id = %s and comment_id = %s',
            (data['user_id'], comment_id))
        comment = cur.fetchone()

        if not comment:
            return jsonify({'error': 'Comment not found'}), 400

        cur.execute(
            'DELETE FROM SUBSCRIBERS_COMMENTS_ON_ALBUM WHERE user_id = %s and comment_id = %s',
            (data['user_id'], comment_id))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'message': 'Comment deleted successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@comments.route('/getCommentsOnAlbum', methods=['GET', 'POST'])
def getCommentsOnAlbum():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        json_file = request.get_json()
        album_id = json_file['album_id']

        cur.execute(
            'SELECT * FROM SUBSCRIBERS_COMMENTS_ON_ALBUM WHERE album_id = %s',
            (album_id,))
        comment = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'comments': comment}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@comments.route('/countCommentsOnAlbum', methods=['GET', 'POST'])
def countCommentsOnAlbum():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            json_file = request.get_json()
            album_id = json_file['album_id']

            cur.execute(
                'SELECT COUNT(*) FROM SUBSCRIBERS_COMMENTS_ON_ALBUM WHERE album_id = %s',
                (album_id,))
            comments_count = cur.fetchone()

            cur.close()
            conn.close()

            return jsonify({'comments': comments_count}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@comments.route('/userCommentsPlaylist', methods=['GET', 'POST'])
def userCommentsPlaylist():
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT * FROM Users WHERE user_id = %s and is_premium = %s',
                (data['user_id'], True))
            user = cur.fetchone()

            if not user:
                return jsonify({'error': 'User not found or not premium'}), 400

            json_file = request.get_json()
            playlist_id = json_file['playlist_id']
            comment_text = json_file['comment_text']

            cur.execute(
                'INSERT INTO SUBSCRIBERS_COMMENTS_ON_PLAYLIST (user_id, playlist_id, comment_text, comment_time) VALUES (%s, %s, %s, %s)',
                (data['user_id'], playlist_id, comment_text, datetime.datetime.now()))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Comment added successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@comments.route('/deleteCommentPlaylist', methods=['DELETE'])
def deleteCommentPlaylist():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        json_file = request.get_json()
        comment_id = json_file['comment_id']

        cur.execute(
            'SELECT * FROM SUBSCRIBERS_COMMENTS_ON_PLAYLIST WHERE user_id = %s and comment_id = %s',
            (data['user_id'], comment_id))
        comment = cur.fetchone()

        if not comment:
            return jsonify({'error': 'Comment not found'}), 400

        cur.execute(
            'DELETE FROM SUBSCRIBERS_COMMENTS_ON_PLAYLIST WHERE user_id = %s and comment_id = %s',
            (data['user_id'], comment_id))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({'message': 'Comment deleted successfully'}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@comments.route('/getCommentsOnPlaylist', methods=['GET', 'POST'])
def getCommentsOnPlaylist():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        json_file = request.get_json()
        playlist_id = json_file['playlist_id']

        cur.execute(
            'SELECT * FROM SUBSCRIBERS_COMMENTS_ON_PLAYLIST WHERE playlist_id = %s',
            (playlist_id,))
        comment = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'comments': comment}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@comments.route('/countCommentsOnPlaylist', methods=['GET', 'POST'])
def countCommentsOnPlaylist():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            json_file = request.get_json()
            playlist_id = json_file['playlist_id']

            cur.execute(
                'SELECT COUNT(*) FROM SUBSCRIBERS_COMMENTS_ON_PLAYLIST WHERE playlist_id = %s',
                (playlist_id,))
            comments_count = cur.fetchone()

            cur.close()
            conn.close()

            return jsonify({'comments': comments_count}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400
