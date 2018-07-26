#!flask/bin/python

from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
from flask_cors import CORS
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import config
from functools import wraps
import youtube_dl

# data = {
#         id: 1,
#         videoId: "pM5To8YXHWE",
#         title: "Be Me See Me",
#         publishedAt: "2015-09-20T15:57:15.000Z",
#         },
# {
#         id: 2,
#         videoId: "I7w9otyiE9g",
#         title: "Young Thug - Digits [OFFICIAL AUDIO]",
#         publishedAt: "2016-03-25T04:03:28.000Z",
#         },
# {
#         id: 3,
#         videoId: "Tz6OUIjtM6E",
#         title:"Young Thug - Best Friend",
#         publishedAt: "2015-09-14T21:29:23.000Z",
#         }
# }

# FLASK APP INITIALIZATIONS
# =========================

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI_DEV
SECRET_KEY = config.SECRET_KEY
db = SQLAlchemy(app)
ma = Marshmallow(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# YOUTUBE DL CLASSES AND FUNCTIONS
# ================================

class MyLogger(object):
    """logs output from youtube """
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

ydl_opts = {
        'logger'                     : MyLogger(), # logs output by youtubedl
        'progress_hooks'             : [my_hook], # tells status in console
        # 'default-search'           : 'ytsearch', # search youtube if error in with url
        'youtube-skip-dash-manifest' : True, # skip recommended videos
        'restrict-filenames'         : True, # no ASCII ampersands or spaces
        'download'                   : False, # no download for test purposes
        'format'                     : 'bestaudio/best[ext!=webm]', # get the best quality
        'extractaudio'               : True,  # only keep the audio
        'audioformat'                : 'mp3',  # convert to mp3
        'outtmpl'                    : '%(id)s.mp3',    # name the file the ID of the video
        'noplaylist'                 : True,    # only download single song, not playlist
        }

def get_track(title):
    title = "ytsearch:" + title
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        track = ydl.download([title])
        meta = ydl.extract_info(title)
        return track

def get_info(title):
    title = "ytsearch:" + title
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(title)
        return info



# SQLALCHEMY DB MODELS
# ====================

class User(db.Model):
    """ Model storing information about the user. Currently it stores the users
         id, username, name, email and picture """
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(80))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)
    email = db.Column(db.String(250))
    picture = db.Column(db.String)

class Playlist(db.Model):
    """ Model storing information about the users playlist. Currently stores
        id, name, description, user_id. """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    description = db.Column(db.String(80))
    created_at = db.Column(db.DateTime)
    picture = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_relationship = db.relationship(User)
    song_relationship = db.relationship("Song", cascade="all, delete-orphan")


class Song(db.Model):
    """ Model storing the information about the users songs. Currently stores
        id, song name, artist, playlist id and user id. """
    id = db.Column(db.Integer, primary_key=True)
    videoId = db.Column(db.String, nullable=False)
    name = db.Column(db.String(250))
    publishedAt = db.Column(db.String)
    picture = db.Column(db.String)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_relationship = db.relationship(User)

# MARSHMALLOW SCHEMAS
# ===================

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User


class PlaylistSchema(ma.ModelSchema):
    class Meta:
        model = Playlist

class SongSchema(ma.ModelSchema):
    class Meta:
        model = Song


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY)
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# FLASK ROUTES
# ============

# login routes
# ------------
@app.route('/api/v1/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, SECRET_KEY)
        return jsonify({'token' : token.decode('UTF-8')})
    return make_response('could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

# user routes
# -----------
@app.route('/api/v1/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    """
    :return: json list of all users
    """
    if not current_user.admin:
        return jsonify({'message' : 'user not authorized to do that function!!!'})
    users = User.query.all()
    user_schema = UserSchema()
    output = []
    for  user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)
    # output = user_schema.dump(users).data # serialize python object into json
    return jsonify({'users' : output})

@app.route('/api/v1/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    """
    :return: json object of single user
    """
    if not current_user.admin:
        return jsonify({'message' : 'user not authorized to do that function!!!'})
    user = User.query.filter_by(public_id = public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin
    return jsonify({'user' : user_data})


@app.route('/api/v1/user', methods=['POST'])
@token_required
def create_user(current_user):
    """
    :return: http response 200, user created successfully
    """
    if not current_user.admin:
        return jsonify({'message' : 'user not authorized to do that function!!!'})
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    uuid4 = uuid.uuid4()
    new_user = User(public_id=str(uuid4), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    # users = User.query.order_by(asc(User.name)).all()
    # user_schema = UserSchema()
    # output = user_schema.dump(one_user).data # serialize python object into json
    return jsonify({'message' : 'new user created successfully!'})


@app.route('/api/v1/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):
    """
    :return: http response 200, user promoted to administrator
    """
    if not current_user.admin:
        return jsonify({'message' : 'user not authorized to do that function!!!'})
    user = User.query.filter_by(public_id = public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    user.admin = True
    db.session.commit()
    return jsonify({'message' : 'user promoted to admin successfully!'})

@app.route('/api/v1/user/<user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user):
    """
    :return: http response 200, user deleted successfully
    """
    if not current_user.admin:
        return jsonify({'message' : 'user not authorized to do that function!!!'})
    user = User.query.filter_by(public_id = public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message' : 'user deleted successfully!'})


# PLAYLIST ROUTES
# ===============
# @app.route('/api/v1/playlists', methods=['GET'])
# @token_required
# def get_all_playlists(current_user):
#     """
#     :return: json list of all playlists
#     """
#     playlists = playlist.query.order_by(asc(playlist.name)).all()
#     playlist_schema = playlistSchema()
#     output = playlist_schema.dump(one_playlist).data # serialize python object into json
#     return jsonify({'playlists' : output})

@app.route('/api/v1/playlist', methods=['GET'])
@token_required
def get_all_playlists(current_user):
    """
    :return: json object of all playlists of current user
    """
    playlists = playlist.query.filter_by(user_id=current_user.id).all()
    # playlist_schema = playlistSchema()
    # output = playlist_schema.dump(one_playlist).data # serialize python object into json
    output = []
    for playlist in playlists:
        playlist_data = {}
        playlist_data['id'] = playlist.id
        playlist_data['name'] = playlist.name
        output.append(playlist_data)
    return jsonify({'playlists' : output})

@app.route('/api/v1/playlist/<playlist_id>', methods=['GET'])
@token_required
def get_one_playlist(current_user, playlist_id):
    """
    :return: json object of single playlist
    """
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    if not playlist:
        return jsonify({'message' : 'no playlists found!'})
    playlist_data = {}
    playlist_data['id'] = playlist.id
    playlist_data['name'] = playlist.name
    return jsonify(playlist_data)

@app.route('/api/v1/playlist', methods=['POST'])
@token_required
def create_playlist(current_user):
    """
    :return: http response 200, playlist created successfully
    """
    data = request.get_json()
    new_playlist = Playlist(text=data['name'], user_id=current_user.id)
    db.session.add(new_playlist)
    db.session.commit()

    return jsonify({'message' : 'playlist created successfully!'})

    # playlists = playlist.query.order_by(asc(playlist.name)).all()
    # playlist_schema = playlistSchema()
    # output = playlist_schema.dump(one_playlist).data # serialize python object into json
    return jsonify({'message' : 'playlist added successfully!'})


# @app.route('/api/v1/playlist/<playlist_id>', methods=['PUT'])
# @token_required
# def update_playlist(current_user, playlist_id):
#     """
#     :return: http response 200, playlist name changed
#     """
#     playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
#     if not playlist:
#         return jsonify({'message' : 'no playlists found!'})

#     return jsonify({'message' : 'playlist updated successfully!'})


@app.route('/api/v1/playlist/<playlist_id>', methods=['DELETE'])
@token_required
def delete_playlist(current_user, playlist_id):
    """
    :return: http response 200, playlist deleted successfully
    """
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    if not playlist:
        return jsonify({'message' : 'no playlist found!'})

    db.session.delete(playlist)
    db.session.commit()
    return jsonify({'message' : 'playlist deleted!'})







# ==========================================
# ==========================================
# @app.route('/api/v1/track/<track_name>')
# def get_track_info(track_name):
#     track_info = get_info(track_name)
#     return jsonify({ 'track_info' : track_info })

# @app.route('/api/v1/track')
# def query_track_info():
#     track_name = request.args.get('q')
#     track_info = get_info(track_name)
#     return jsonify({ 'track_info' : track_info })

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
