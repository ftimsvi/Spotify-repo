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
            'SELECT T.track_id, U.first_name, U.last_name, T.name_of_track, T.age_category, T.lyric, T.length, T.date_of_release \
            FROM SUBSCRIBERS_LIKES_TRACKS SLT \
            JOIN TRACKS T ON SLT.track_id = T.track_id \
            JOIN ARTIST A ON T.artist_id = A.artist_id \
            JOIN USERS U ON A.user_id = U.user_id \
            WHERE SLT.user_id = %s',
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
            'SELECT A.album_id, AR.artist_id, U.first_name, U.last_name \
            FROM SUBSCRIBERS_LIKES_ALBUM SLA \
            JOIN ALBUMS A ON SLA.album_id = A.album_id \
            JOIN ARTIST AR ON A.artist_id = AR.artist_id \
            JOIN USERS U ON AR.user_id = U.user_id \
            WHERE SLA.user_id = %s',
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
            'SELECT P.playlist_id, P.name_of_playlist, U.first_name, U.last_name \
            FROM SUBSCRIBERS_LIKES_PLAYLIST SLP \
            JOIN PLAYLIST P ON SLP.playlist_id = P.playlist_id \
            JOIN Users U ON U.user_id = P.user_id \
            WHERE SLP.user_id = %s',
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


# get tracks that are liked by the friends of the user
@likes.route('/getTracksLikedByFriends')
def getTracksLikedByFriends():
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

        cur.execute(
            'SELECT user_id_receiver FROM FRIENDSHIP_REQUEST WHERE user_id_sender = %s and is_approved = %s',
            (data['user_id'], True))
        friends = cur.fetchall()

        tracks = []
        for friend in friends:
            cur.execute(
                'SELECT track_id FROM SUBSCRIBERS_LIKES_TRACKS WHERE user_id = %s',
                (friend,))
            tracks += cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'tracks': tracks}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400
