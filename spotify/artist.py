import jwt
from flask import Blueprint, jsonify, request

from . import SECRET_KEY, get_db_connection

artist = Blueprint('artist', __name__)


@artist.route('/becomeArtist', methods=['GET', 'POST'])
def becomeArtist():
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            json_file = request.get_json()
            bio = json_file['bio']

            cur.execute(
                'SELECT * FROM USERS WHERE is_premium = %s and user_id = %s', (True, data['user_id']))
            user = cur.fetchone()

            if user:
                cur.execute(
                    'UPDATE Users SET is_artist = %s WHERE user_id = %s', (True, data['user_id']))
                if bio:
                    cur.execute(
                        'INSERT INTO ARTIST (user_id, bio) VALUES (%s, %s)', (data['user_id'], bio))
                conn.commit()

                cur.close()
                conn.close()
                return jsonify({'message': 'You are now an artist'}), 200
            return jsonify({'message': 'Invalid credentials'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@artist.route('/getArtistsList')
def getArtistsList():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        '''
        SELECT u.first_name, u.last_name, a.bio 
        FROM Users u
        JOIN ARTIST a ON u.user_id = a.user_id 
        WHERE u.is_artist = %s
        ''', (True,)
    )
    artists = cur.fetchall()

    cur.close()
    conn.close()

    # Format the response
    artists_list = []
    for artist in artists:
        artist_dict = {
            'first_name': artist[0],
            'last_name': artist[1],
            'bio': artist[2]
        }
        artists_list.append(artist_dict)

    return jsonify({'artists': artists_list}), 200



@artist.route('/artist/<int:artist_id>')
def getArtist(artist_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        '''
        SELECT u.first_name, u.last_name, a.bio 
        FROM Users u
        JOIN ARTIST a ON u.user_id = a.user_id 
        WHERE a.artist_id = %s AND u.is_artist = %s
        ''', (artist_id, True)
    )
    artist = cur.fetchone()

    cur.close()
    conn.close()

    if artist:
        return jsonify({'artist': {
            'first_name': artist[0],
            'last_name': artist[1],
            'bio': artist[2]
        }}), 200
    else:
        return jsonify({'message': 'Artist not found'}), 404


@artist.route('/artist/<int:artist_id>/albums')
def getArtistAlbums(artist_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT A.album_id, A.name_of_album, COUNT(T.track_id) AS track_count \
        FROM ALBUMS A \
        LEFT JOIN TRACKS T ON A.album_id = T.album_id \
        WHERE A.artist_id = %s \
        GROUP BY A.album_id, A.name_of_album',
        (artist_id,))
    albums = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({'albums': albums}), 200


@artist.route('/artist/<int:artist_id>/album/<int:album_id>/tracks')
def getArtistAlbumTracks(artist_id, album_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT T.track_id, T.name_of_track, T.age_category, T.lyric, T.length, T.date_of_release \
        FROM TRACKS T \
        WHERE T.artist_id = %s AND T.album_id = %s',
        (artist_id, album_id))
    tracks = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({'tracks': tracks}), 200


@artist.route('/artist/<int:artist_id>/album/<int:album_id>/addTrack', methods=['GET', 'POST'])
def addTrack(artist_id, album_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            json_file = request.get_json()
            track_name = json_file['track_name']
            age_category = json_file['age_category']
            lyric = json_file['lyric']
            length = json_file['length']
            date_of_release = json_file['date_of_release']

            cur.execute(
                'SELECT * FROM USERS WHERE is_artist = %s and user_id = %s', (True, data['user_id']))
            user = cur.fetchone()

            if user:
                cur.execute(
                    'INSERT INTO TRACKS (artist_id, album_id, name_of_track, age_category, lyric, length, date_of_release) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (artist_id, album_id, track_name, age_category, lyric, length, date_of_release))
                conn.commit()

                cur.close()
                conn.close()
                return jsonify({'message': 'Track added successfully'}), 200
            return jsonify({'message': 'Invalid credentials'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@artist.route('/artist/<int:artist_id>/album/<int:album_id>/deleteTrack/<int:track_id>', methods=['GET', 'POST'])
def deleteTrack(artist_id, album_id, track_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT * FROM USERS WHERE is_artist = %s and user_id = %s', (True, data['user_id']))
            user = cur.fetchone()

            if user:
                cur.execute(
                    'DELETE FROM TRACKS WHERE artist_id = %s AND album_id = %s AND track_id = %s',
                    (artist_id, album_id, track_id))
                conn.commit()

                cur.close()
                conn.close()
                return jsonify({'message': 'Track deleted successfully'}), 200
            return jsonify({'message': 'Invalid credentials'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400


@artist.route('/artist/<int:artist_id>/addAlbum', methods=['GET', 'POST'])
def addAlbum(artist_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization')
        if not token or len(token.split()) < 2:
            return jsonify({'error': 'Missing token'}), 400
        token = token.split()[1]

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            json_file = request.get_json()
            name_of_album = json_file['name_of_album']
            tracks = json_file.get('tracks')

            if not name_of_album or not tracks or not isinstance(tracks, list) or len(tracks) == 0:
                return jsonify({'error': 'Album name and tracks are required'}), 400

            cur.execute(
                'SELECT * FROM USERS WHERE is_artist = %s and user_id = %s', (True, data['user_id']))
            user = cur.fetchone()

            if user:
                try:
                    cur.execute(
                        'INSERT INTO ALBUMS (artist_id, name_of_album) VALUES (%s, %s) RETURNING album_id',
                        (artist_id, name_of_album))
                    album_id = cur.fetchone()[0]

                    for track in tracks:
                        name_of_track = track.get('name_of_track')
                        age_category = track.get('age_category')
                        lyric = track.get('lyric')
                        length = track.get('length')
                        date_of_release = track.get('date_of_release')

                        if not name_of_track or not length or not date_of_release:
                            raise ValueError('Track details are incomplete')

                        cur.execute(
                            'INSERT INTO TRACKS (artist_id, album_id, name_of_track, age_category, lyric, length, date_of_release) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s)',
                            (artist_id, album_id, name_of_track, age_category, lyric, length, date_of_release))

                    conn.commit()

                    return jsonify({'message': 'Album and tracks added successfully'}), 200

                except Exception as e:
                    conn.rollback()
                    return jsonify({'error': str(e)}), 400
                finally:
                    cur.close()
                    conn.close()
            else:
                return jsonify({'message': 'Invalid credentials'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 400


@artist.route('/artist/<int:artist_id>/album/<int:album_id>/delete', methods=['DELETE'])
def deleteAlbum(artist_id, album_id):
    token = request.headers.get('Authorization')
    if not token or len(token.split()) < 2:
        return jsonify({'error': 'Missing token'}), 400
    token = token.split()[1]

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            'SELECT * FROM USERS WHERE is_artist = %s AND user_id = %s', (True, data['user_id']))
        user = cur.fetchone()

        if user:
            cur.execute(
                'SELECT * FROM ALBUMS WHERE album_id = %s AND artist_id = %s', (album_id, artist_id))
            album = cur.fetchone()

            if album:
                try:
                    cur.execute(
                        'DELETE FROM ALBUMS WHERE album_id = %s AND artist_id = %s', (album_id, artist_id))
                    conn.commit()

                    return jsonify({'message': 'Album and associated tracks deleted successfully'}), 200

                except Exception as e:
                    conn.rollback()
                    return jsonify({'error': str(e)}), 400
                finally:
                    cur.close()
                    conn.close()
            else:
                return jsonify({'error': 'Album not found or you do not have permission to delete it'}), 404
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Expired token'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 400


@artist.route('/artist/<int:artist_id>/addConcert', methods=['GET', 'POST'])
def addConcert(artist_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization')
        if not token or len(token.split()) < 2:
            return jsonify({'error': 'Missing token'}), 400
        token = token.split()[1]

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            json_file = request.get_json()
            date_of_concert = json_file['date_of_concert']
            cost = json_file['cost']

            if not date_of_concert or not cost:
                return jsonify({'error': 'Date of concert and cost are required'}), 400

            cur.execute(
                'SELECT * FROM USERS WHERE is_artist = %s and user_id = %s', (True, data['user_id']))
            user = cur.fetchone()

            if user:
                cur.execute(
                    'INSERT INTO CONCERTS (artist_id, date_of_concert, cost) VALUES (%s, %s, %s)',
                    (artist_id, date_of_concert, cost))
                conn.commit()

                cur.close()
                conn.close()
                return jsonify({'message': 'Concert added successfully'}), 200
            return jsonify({'message': 'Invalid credentials'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 400


@artist.route('/artist/<int:artist_id>/cancleConcert/<int:concert_id>', methods=['GET', 'POST'])
def cancleConcert(artist_id, concert_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization')
        if not token or len(token.split()) < 2:
            return jsonify({'error': 'Missing token'}), 400
        token = token.split()[1]

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute(
                'SELECT * FROM USERS WHERE is_artist = %s and user_id = %s', (True, data['user_id']))
            user = cur.fetchone()

            if user:
                cur.execute(
                    'SELECT 1 FROM CONCERTS WHERE concert_id = %s AND artist_id = %s',
                    (concert_id, artist_id))
                if cur.fetchone() is None:
                    return jsonify({"error": "Concert not found or does not belong to the artist"}), 404

                cur.execute(
                    'SELECT user_id, cost FROM SUBSCRIBERS_BOUGHT_CONCERT JOIN CONCERTS ON SUBSCRIBERS_BOUGHT_CONCERT.concert_id = CONCERTS.concert_id WHERE SUBSCRIBERS_BOUGHT_CONCERT.concert_id = %s',
                    (concert_id,))
                tickets = cur.fetchall()

                for ticket in tickets:
                    user_id, cost = ticket
                    cur.execute(
                        "UPDATE USERS SET balance = balance + %s WHERE user_id = %s", (cost, user_id))

                cur.execute(
                    'DELETE FROM CONCERTS WHERE artist_id = %s AND concert_id = %s',
                    (artist_id, concert_id))
                conn.commit()

                cur.close()
                conn.close()
                return jsonify({'message': 'Concert canceled successfully'}), 200
            return jsonify({'message': 'Invalid credentials'}), 401
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500


@artist.route('/artist/<int:artist_id>/genres')
def getArtistGenres(artist_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'SELECT geners_name FROM ARTIST_GENERS WHERE artist_id = %s',
        (artist_id,))
    genres = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({'genres': genres}), 200


@artist.route('/artist/<int:artist_id>/addGenre', methods=['GET', 'POST'])
def addGenre(artist_id):
    if request.method == 'POST':
        token = request.headers.get('Authorization').split()[1]
        if not token:
            return jsonify({'error': 'Missing token'}), 400

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            json_file = request.get_json()
            genre_name = json_file['genre_name']

            cur.execute(
                'SELECT * FROM USERS WHERE user_id = %s AND is_artist = %s', (artist_id, True))
            user = cur.fetchone()

            if user:
                cur.execute(
                    'INSERT INTO ARTIST_GENERS (artist_id, geners_name) VALUES (%s, %s)',
                    (artist_id, genre_name))
                conn.commit()

                cur.close()
                conn.close()
                return jsonify({'message': 'Genre added successfully'}), 200
            return jsonify({'error': 'Artist not found'}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Expired token'}), 400
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 400
