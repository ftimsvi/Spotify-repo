import psycopg2
from flask import Flask

SECRET_KEY = 'you_will_never_guess'
masih_db_user = "admin"
masih_db_pass = "admin"

def get_db_connection():
    return psycopg2.connect(
        database='spotify_db',
        user=masih_db_user,
        password=masih_db_pass,
        host='localhost',
        port='5432'
    )


def create_app():
    app = Flask(__name__)
    app.config['secret_key'] = SECRET_KEY

    from .artist import artist
    from .auth import auth
    from .home import home
    from .likes import likes
    from .profile import profile
    from .comments import comments

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(profile, url_prefix='/profile')
    app.register_blueprint(artist, url_prefix='/artist')
    app.register_blueprint(home, url_prefix='/home')
    app.register_blueprint(likes, url_prefix='/likes')
    app.register_blueprint(comments, url_prefix='/comments')

    return app
