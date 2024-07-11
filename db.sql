CREATE TABLE USERS (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    password VARCHAR(256) NOT NULL,
    date_of_birth DATE NOT NULL,
	email VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(50) NOT NULL,
    balance DECIMAL(10, 2) DEFAULT 0.00 CHECK (balance >= 0),
    is_premium BOOLEAN DEFAULT FALSE,
    start_premium DATE,
    end_premium DATE,
    is_artist BOOLEAN DEFAULT FALSE,
    CHECK (date_of_birth <= CURRENT_DATE),
    CHECK (start_premium <= end_premium OR end_premium IS NULL)
);

-- Index on is_premium to optimize queries filtering by subscription status
CREATE INDEX idx_users_is_premium ON USERS(is_premium);

-- Index on is_artist to optimize queries filtering by artist status
CREATE INDEX idx_users_is_artist ON USERS(is_artist);



CREATE TABLE ARTIST (
    artist_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    bio TEXT,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE
);

-- Index on user_id for faster joins
CREATE INDEX idx_artist_user_id ON ARTIST(user_id);



CREATE TABLE TRACKS (
    track_id SERIAL PRIMARY KEY,
    artist_id INT NOT NULL,
    album_id INT,
    name_of_track VARCHAR(100) NOT NULL,
    age_category VARCHAR(50),
    lyric TEXT,
    length INT,
    date_of_release DATE,
    FOREIGN KEY (artist_id) REFERENCES ARTIST(artist_id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES ALBUMS(album_id) ON DELETE SET NULL
);

-- Index on artist_id for faster joins
CREATE INDEX idx_tracks_artist_id ON TRACKS(artist_id);

-- Index on album_id for faster joins
CREATE INDEX idx_tracks_album_id ON TRACKS(album_id);



CREATE TABLE ALBUMS (
    album_id SERIAL PRIMARY KEY,
    artist_id INT NOT NULL,
    name_of_album VARCHAR(100) NOT NULL,
    FOREIGN KEY (artist_id) REFERENCES ARTIST(artist_id) ON DELETE CASCADE
);

-- Index on artist_id for faster joins
CREATE INDEX idx_album_artist_id ON ALBUMS(artist_id);



CREATE TABLE CONCERTS (
    concert_id SERIAL PRIMARY KEY,
    artist_id INT NOT NULL,
    date_of_concert DATE NOT NULL,
    cost DECIMAL(10, 2) NOT NULL CHECK (cost >= 0),
    FOREIGN KEY (artist_id) REFERENCES ARTIST(artist_id) ON DELETE CASCADE
);

-- Index on artist_id for faster joins
CREATE INDEX idx_concerts_artist_id ON CONCERTS(artist_id);



CREATE TABLE GENERS (
    geners_name VARCHAR(50) PRIMARY KEY,
    description TEXT
);

-- Index on geners_name for faster lookups
CREATE INDEX idx_geners_name ON GENERS(geners_name);



CREATE TABLE ARTIST_GENERS (
    artist_id INT NOT NULL,
    geners_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (artist_id, geners_name),
    FOREIGN KEY (artist_id) REFERENCES ARTIST(artist_id) ON DELETE CASCADE,
    FOREIGN KEY (geners_name) REFERENCES GENERS(geners_name) ON DELETE CASCADE
);



CREATE TABLE TRACKS_GENERS (
    track_id INT NOT NULL,
    geners_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (track_id, geners_name),
    FOREIGN KEY (track_id) REFERENCES TRACKS(track_id) ON DELETE CASCADE,
    FOREIGN KEY (geners_name) REFERENCES GENERS(geners_name) ON DELETE CASCADE
);



CREATE TABLE SUBSCRIBERS_BOUGHT_CONCERT (
    user_id INT NOT NULL,
    concert_id INT NOT NULL,
    date_of_payment DATE NOT NULL,
    PRIMARY KEY (user_id, concert_id),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
    FOREIGN KEY (concert_id) REFERENCES CONCERTS(concert_id) ON DELETE CASCADE
);

-- Index on sub_id for faster joins
CREATE INDEX idx_subscribers_bought_concert_sub_id ON SUBSCRIBERS_BOUGHT_CONCERT(user_id);

-- Index on concert_id for faster joins
CREATE INDEX idx_subscribers_bought_concert_concert_id ON SUBSCRIBERS_BOUGHT_CONCERT(concert_id);

-- Index on date_of_payment for faster searches by payment date
CREATE INDEX idx_subscribers_bought_concert_date_of_payment ON SUBSCRIBERS_BOUGHT_CONCERT(date_of_payment);



CREATE TABLE SUBSCRIBERS_LIKES_TRACKS (
	user_id INT NOT NULL,
    track_id INT NOT NULL,
    PRIMARY KEY (user_id, track_id),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES TRACKS(track_id) ON DELETE CASCADE
);

-- Index on user_id for faster joins
CREATE INDEX idx_subscribers_likes_tracks_sub_id ON SUBSCRIBERS_LIKES_TRACKS(user_id);

-- Index on track_id for faster joins
CREATE INDEX idx_subscribers_likes_tracks_track_id ON SUBSCRIBERS_LIKES_TRACKS(track_id);



CREATE TABLE FOLLOWING (
    user_id1_following INT NOT NULL,
    user_id2_followed INT NOT NULL,
    PRIMARY KEY (user_id1_following, user_id2_followed),
    FOREIGN KEY (user_id1_following) REFERENCES USERS(user_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id2_followed) REFERENCES USERS(user_id) ON DELETE CASCADE
);

-- Index on user_id1_following for faster joins
CREATE INDEX idx_following_user_id1_following ON FOLLOWING(user_id1_following);

-- Index on user_id2_followed for faster joins
CREATE INDEX idx_following_user_id2_followed ON FOLLOWING(user_id2_followed);



CREATE TABLE SUBSCRIBERS_COMMENTS_ON_TRACKS (
    user_id INT NOT NULL,
    track_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    comment_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, track_id, comment_time),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES TRACKS(track_id) ON DELETE CASCADE
);

-- Index on user_id for faster joins
CREATE INDEX idx_sub_comments_sub_id ON SUBSCRIBERS_COMMENTS_ON_TRACKS(user_id);

-- Index on track_id for faster joins
CREATE INDEX idx_sub_comments_track_id ON SUBSCRIBERS_COMMENTS_ON_TRACKS(track_id);



CREATE TABLE SUBSCRIBERS_LIKES_ALBUM (
    user_id INT NOT NULL,
    album_id INT NOT NULL,
    PRIMARY KEY (user_id, album_id),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES ALBUMS(album_id) ON DELETE CASCADE
);

-- Index on user_id for faster joins
CREATE INDEX idx_likes_album_user_id ON SUBSCRIBERS_LIKES_ALBUM(user_id);

-- Index on album_id for faster joins
CREATE INDEX idx_likes_album_album_id ON SUBSCRIBERS_LIKES_ALBUM(album_id);
