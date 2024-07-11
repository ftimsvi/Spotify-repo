from flask import Flask
import psycopg2

SECRET_KEY = 'you_will_never_guess'


def get_db_connection():
    return psycopg2.connect(
        database='spotify_db',
        user='postgres',
        password='PGAdmin',
        host='localhost',
        port='5432'
    )


def create_app():
    app = Flask(__name__)
    app.config['secret_key'] = SECRET_KEY

    from .auth import auth
    from .profile import profile
    from .artist import artist
    from .home import home
    from .likes import likes

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(profile, url_prefix='/profile')
    app.register_blueprint(artist, url_prefix='/artist')
    app.register_blueprint(home, url_prefix='/home')
    app.register_blueprint(likes, url_prefix='/likes')

    return app
