from flask import Flask, request, session
from datetime import timedelta
from fullyPost import config

fullyPost = Flask(__name__)

fullyPost.config['SECRET_KEY'] = config.SECRET_KEY
fullyPost.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=config.PERMANENT_SESSION_LIFETIME)
fullyPost.config['SEND_FILE_MAX_AGE_DEFAULT'] = config.SEND_FILE_MAX_AGE_DEFAULT
# fullyPost.config['SESSION_COOKIE_SECURE'] = config.SESSION_COOKIE_SECURE
# fullyPost.config['SESSION_COOKIE_HTTPONLY'] = config.SESSION_COOKIE_HTTPONLY
# fullyPost.config['SESSION_COOKIE_SAMESITE'] = config.SESSION_COOKIE_SAMESITE

fullyPost.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
fullyPost.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
fullyPost.config['SQLALCHEMY_POOL_RECYCLE'] = config.SQLALCHEMY_POOL_RECYCLE
fullyPost.config['SQLALCHEMY_POOL_SIZE'] = config.SQLALCHEMY_POOL_SIZE

from fullyPost.views.authentication import auth
from fullyPost.views.home import home
from fullyPost.views.search import search
from fullyPost.views.profile import profile
from fullyPost.views.posts import posts
from fullyPost.views.settings import settings

fullyPost.register_blueprint(auth)
fullyPost.register_blueprint(home)
fullyPost.register_blueprint(search)
fullyPost.register_blueprint(profile)
fullyPost.register_blueprint(posts)
fullyPost.register_blueprint(settings)


@fullyPost.before_request
def apply_request():
    session['host'] = request.host_url

@fullyPost.after_request
def apply_caching(response):
    response.headers['Strict-Transport-Security'] = config.Strict_Transport_Security
    response.headers['X-XSS-Protection']= config.X_XSS_Protection
    response.headers['X-Frame-Options'] = config.X_Frame_Options
    response.headers['X-Content-Type-Options'] = config.X_Content_Type_Options
    if response.headers.get('Cache-Control') != config.MAX_CACHE_CONTROL:
        response.headers["Cache-Control"] = config.Cache_Control
    
    return response