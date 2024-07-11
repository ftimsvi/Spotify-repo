from flask import Blueprint, jsonify, request
import jwt
from . import get_db_connection, SECRET_KEY

likes = Blueprint('likes', __name__)


@likes.route('/userLikesTrack', methods=['GET', 'POST'])
def userLikesTrack():
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

            cur.execute(
                'INSERT INTO SUBSCRIBERS_LIKES_TRACKS (user_id, track_id) VALUES (%s, %s)',
                (data['user_id'], track_id))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Track liked successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@likes.route('/getTracksLikedByUser')
def getTracksLikedByUser():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT track_id FROM SUBSCRIBERS_LIKES_TRACKS WHERE user_id = %s',
            (data['user_id'],))
        tracks = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'tracks': tracks}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@likes.route('/countLikesOfTrack', methods=['GET', 'POST'])
def countLikesOfTrack():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            json_file = request.get_json()
            track_id = json_file['track_id']

            cur.execute(
                'SELECT COUNT(*) FROM SUBSCRIBERS_LIKES_TRACKS WHERE track_id = %s',
                (track_id,))
            liked = cur.fetchone()

            cur.close()
            conn.close()

            return jsonify({'likes': liked}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@likes.route('/userLikesAlbum', methods=['GET', 'POST'])
def userLikesAlbum():
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

            cur.execute(
                'INSERT INTO SUBSCRIBERS_LIKES_ALBUM (user_id, album_id) VALUES (%s, %s)',
                (data['user_id'], album_id))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Album liked successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@likes.route('/getAlbumsLikedByUser')
def getAlbumsLikedByUser():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT album_id FROM SUBSCRIBERS_LIKES_ALBUM WHERE user_id = %s',
            (data['user_id'],))
        albums = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'albums': albums}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@likes.route('/countLikesOfAlbum', methods=['GET', 'POST'])
def countLikesOfAlbum():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            json_file = request.get_json()
            album_id = json_file['album_id']

            cur.execute(
                'SELECT COUNT(*) FROM SUBSCRIBERS_LIKES_ALBUM WHERE album_id = %s',
                (album_id,))
            liked = cur.fetchone()

            cur.close()
            conn.close()

            return jsonify({'likes': liked}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@likes.route('/userLikesPlaylist', methods=['GET', 'POST'])
def userLikesPlaylist():
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

            cur.execute(
                'INSERT INTO SUBSCRIBERS_LIKES_PLAYLIST (user_id, playlist_id) VALUES (%s, %s)',
                (data['user_id'], playlist_id))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Playlist liked successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@likes.route('/getPlaylistsLikedByUser')
def getPlaylistsLikedByUser():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT playlist_id FROM SUBSCRIBERS_LIKES_PLAYLIST WHERE user_id = %s',
            (data['user_id'],))
        playlists = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'playlists': playlists}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@likes.route('/countLikesOfPlaylist', methods=['GET', 'POST'])
def countLikesOfPlaylist():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            json_file = request.get_json()
            playlist_id = json_file['playlist_id']

            cur.execute(
                'SELECT COUNT(*) FROM SUBSCRIBERS_LIKES_PLAYLIST WHERE playlist_id = %s',
                (playlist_id,))
            liked = cur.fetchone()

            cur.close()
            conn.close()

            return jsonify({'likes': liked}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400
