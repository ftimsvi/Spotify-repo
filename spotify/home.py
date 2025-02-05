import datetime

import jwt
from flask import Blueprint, jsonify, request

from . import SECRET_KEY, get_db_connection

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

            cur.execute('SELECT * FROM Users WHERE user_id = %s and is_premium = %s',
                        (data['user_id'], True))
            user = cur.fetchone()

            if not user:
                return jsonify({'error': 'User not found or not premium'}), 400

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
                'SELECT * FROM USERS WHERE user_id = %s AND is_premium = %s', (data['user_id'], True))
            current_user = cur.fetchone()

            cur.execute(
                'SELECT * FROM Users WHERE user_id = %s and is_premium = %s', (user_id, True))
            followed_user = cur.fetchone()

            if not current_user or not followed_user:
                return jsonify({'error': 'User not found or not permium'}), 400

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
                'SELECT * FROM USERS WHERE user_id = %s AND is_premium = %s', (data['user_id'], True))
            user = cur.fetchone()

            cur.execute(
                'SELECT * FROM Artist WHERE artist_id = %s', (artist_id,))
            artist = cur.fetchone()

            if not artist or not user:
                return jsonify({'error': 'Artist not found'}), 400

            if user:
                cur.execute(
                    'SELECT user_id FROM Artist WHERE artist_id = %s', (artist_id,))
                artist_user_id = cur.fetchone()

                cur.execute(
                    'INSERT INTO FOLLOWING (user_id1_following, user_id2_followed) VALUES (%s, %s)',
                    (data['user_id'], artist_user_id))
                conn.commit()

                cur.close()
                conn.close()
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
                'SELECT * FROM Artist WHERE artist_id = %s', (artist_id,))
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
            'SELECT user_id, first_name, last_name FROM USERS WHERE user_id IN (SELECT user_id1_following FROM FOLLOWING WHERE user_id2_followed = %s)',
            (data['user_id'],))
        followers = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'followers': followers}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@home.route('/getUserFollowedArtists')
def getUserFollowedArtists():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT a.artist_id, u.first_name, u.last_name \
            FROM ARTIST a \
            JOIN USERS u ON a.user_id = u.user_id \
            WHERE artist_id IN (SELECT user_id2_followed FROM FOLLOWING WHERE user_id1_following = %s)',
            (data['user_id'],))
        followed_artists = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'followed_artists': followed_artists}), 200
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
            'SELECT user_id, first_name, last_name FROM USERS WHERE user_id IN (SELECT user_id2_followed FROM FOLLOWING WHERE user_id1_following = %s)',
            (data['user_id'],))
        followings = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'followings': followings}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@home.route('/createPlaylist', methods=['GET', 'POST'])
def createPlaylist():
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT * FROM Users WHERE user_id = %s and is_premium = %s', (data['user_id'], True))
            user = cur.fetchone()

            if not user:
                return jsonify({'error': 'User not found or not premium'}), 400

            json_file = request.get_json()
            name_of_playlist = json_file['name_of_playlist']
            type_of_playlist = json_file['type']

            cur.execute(
                'INSERT INTO PLAYLIST (user_id, name_of_playlist, type) VALUES (%s, %s, %s)',
                (data['user_id'], name_of_playlist, type_of_playlist))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Playlist created successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@home.route('/<int:playlist_id>/addTrackToPlaylist', methods=['GET', 'POST'])
def addTrackToPlaylist(playlist_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT * FROM Users WHERE user_id = %s and is_premium = %s', (data['user_id'], True))
            user = cur.fetchone()

            if not user:
                return jsonify({'error': 'User not found or not premium'}), 400

            cur.execute(
                'SELECT * FROM PLAYLIST WHERE playlist_id = %s', (playlist_id,))
            playlist = cur.fetchone()

            if not playlist:
                return jsonify({'error': 'Playlist not found'}), 400

            json_file = request.get_json()
            track_id = json_file['track_id']

            cur.execute(
                'INSERT INTO PLAYLIST_HAS_TRACKS (playlist_id, track_id) VALUES (%s, %s)',
                (playlist_id, track_id))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Track added to playlist successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@home.route('/getAllPlaylists')
def getAllPlaylists():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM PLAYLIST')
    playlists = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({'playlists': playlists}), 200


@home.route('/getAllPlaylistsOfUser')
def getAllPlaylistsOfUser():
    token = request.headers.get('Authorization').split()[1]
    if not token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('SELECT * FROM PLAYLIST WHERE user_id = %s',
                    (data['user_id'],))
        playlists = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({'playlists': playlists}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


@home.route('/sendOrGetFriendshipRequest', methods=['GET', 'POST'])
def sendOrGetFriendshipRequest():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT delete_unapproved_requests();")
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()
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
            receiver_id = json_file['receiver_id']

            cur.execute(
                'INSERT INTO FRIENDSHIP_REQUEST (user_id_sender, user_id_receiver) VALUES (%s, %s)',
                (data['user_id'], receiver_id))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Friendship request sent successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400

    if request.method == 'GET':
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

            cur.execute('SELECT * FROM FRIENDSHIP_REQUEST WHERE user_id_receiver = %s and is_approved IS NULL',
                        (data['user_id'],))
            requests = cur.fetchall()

            cur.close()
            conn.close()

            return jsonify({'requests': requests}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@home.route('/approveFriendshipRequest', methods=['GET', 'POST'])
def approveFriendshipRequest():
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
            sender_id = json_file['sender_id']

            cur.execute('UPDATE FRIENDSHIP_REQUEST SET is_approved = %s WHERE user_id_sender = %s and user_id_receiver = %s',
                        (True, sender_id, data['user_id']))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({'message': 'Friendship request approved successfully'}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@home.route('/showPlaylistsToUser')
def showPlaylistsToUser():
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

        cur.execute('SELECT * FROM PLAYLIST')
        private_playlists = cur.fetchall()

        for playlist in private_playlists:
            cur.execute(
                'SELECT user_id_sender FROM FRIENDSHIP_REQUEST WHERE user_id_receiver = %s and is_approved = %s',
                (playlist[1], True))
            friends = cur.fetchall()

            if data['user_id'] not in friends:
                private_playlists.remove(playlist)

        cur.execute(
            'SELECT * FROM PLAYLIST WHERE type = %s', ('public',))
        public_playlists = cur.fetchall()

        playlists = private_playlists + public_playlists

        cur.close()
        conn.close()

        return jsonify({'playlists': playlists}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400


# get all information about all tracks
@home.route('/getAllTracks')
def getAllTracks():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT t.track_id, t.name_of_track, t.age_category, t.lyric, t.length, t.date_of_release, a.name_of_album, u.first_name, u.last_name \
            FROM TRACKS t \
            LEFT JOIN ALBUMS a ON t.album_id = a.album_id \
            JOIN ARTIST art ON t.artist_id = art.artist_id \
            JOIN USERS u ON art.user_id = u.user_id;')
    tracks = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({'tracks': tracks}), 200


@home.route('/searchTracks', methods=['GET'])
def searchTracks():

    query = request.args.get('query')
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT t.track_id, t.name_of_track, t.age_category, t.lyric, t.length, t.date_of_release, a.name_of_album, u.first_name, u.last_name \
        FROM TRACKS t \
        LEFT JOIN ALBUMS a ON t.album_id = a.album_id \
        JOIN ARTIST art ON t.artist_id = art.artist_id \
        JOIN USERS u ON art.user_id = u.user_id \
        WHERE t.name_of_track ILIKE %s;', ('%' + query + '%',)
    )
    tracks = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({'tracks': [
        {
            'track_id': track[0],
            'name_of_track': track[1],
            'age_category': track[2],
            'lyric': track[3],
            'length': track[4],
            'date_of_release': track[5],
            'name_of_album': track[6],
            'first_name': track[7],
            'last_name': track[8]
        } for track in tracks
    ]}), 200

@home.route('/searchUsers', methods=['GET'])
def searchUsers():
    query = request.args.get('query')
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT user_id, first_name, last_name, email, date_of_birth, country \
        FROM USERS \
        WHERE first_name ILIKE %s OR last_name ILIKE %s;', ('%' + query + '%', '%' + query + '%')
    )
    users = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({'users': [
        {
            'user_id': user[0],
            'first_name': user[1],
            'last_name': user[2],
            'email': user[3],
            'date_of_birth': user[4],
            'country': user[5]
        } for user in users
    ]}), 200

# @home.route('/recommendTracks', methods=['GET'])
# def recommendTracks():
#     user_id = request.args.get('user_id')
    
#     if not user_id:
#         return jsonify({'error': 'User ID parameter is required'}), 400

#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()

#         procedure_name = 'recommend_tracks'
#         procedure_params = (user_id,)  # Tuple for parameters

#         cur.execute(f"CALL {procedure_name}(%s::INT)", procedure_params)

#         refcursor = cur.fetchone()[0]  # Assuming the OUT parameter is at index 0

#         # Close the cursor and commit changes (if necessary)
#         cur.close()
#         conn.commit()  # Uncomment if your procedure modifies data
#     # except Exception as e:
#     #     cur.execute("ROLLBACK")
#     #     return jsonify({'error': str(e)}), 500
#     finally:
#         cur.close()
#         conn.close()

#     return jsonify({'tracks': [
#         {
#             'track_id': track[0],
#             'name_of_track': track[1],
#             'age_category': track[2],
#             'lyric': track[3],
#             'length': track[4],
#             'date_of_release': track[5],
#             'name_of_album': track[6],
#             'first_name': track[7],
#             'last_name': track[8]
#         } for track in tracks
#     ]}), 200

# @home.route('/recommend_tracks/<int:user_id>')
# def recommend_tracks(user_id):
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()

#         # Define procedure name and parameter (OUT parameter requires special handling)
#         procedure_name = 'recommend_tracks'
#         procedure_params = (int(user_id),)  # Tuple for parameters

#         # Call the stored procedure using `execute` (not `callproc`)
#         cur.execute(f"SELECT * FROM {procedure_name}(%s, OUT %s)", procedure_params)

#         # Fetch results from the OUT parameter (refcursor)
#         refcursor = cur.fetchone()[1]  # Assuming the OUT parameter is at index 1

#         # Fetch all rows from the refcursor
#         recommended_tracks = cur.fetchmany(rows=10)  # Fetch up to 10 tracks

#         # Close the cursor and commit changes (if necessary)
#         cur.close()
#         conn.commit()  # Uncomment if your procedure modifies data

#         # Format and return the recommended tracks as JSON
#         return jsonify({'tracks': recommended_tracks})

#     except Exception as e:
#         cur.execute("ROLLBACK")
#         return jsonify({'error': str(e)}), 500
