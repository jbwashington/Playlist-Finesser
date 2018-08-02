#!flask/bin/python

from flask import Flask, jsonify, request, make_response, render_template
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

# from functools import wraps
# from io import open
# import random
# import string
# import json
# from dicttoxml import dicttoxml
# import urllib

# from flask import Flask, render_template, request, redirect, url_for, flash, \
#             jsonify
#             from sqlalchemy import create_engine, asc
#             from sqlalchemy.orm import sessionmaker
#             from flask import session as login_session
#             from oauth2client.client import flow_from_clientsecrets
#             from oauth2client.client import FlowExchangeError
#             import httplib2
#             from flask import make_response
#             import requests

#             from database_setup import User, base, Playlist, Song

#             app = Flask(__name__)

#             GOOGLE_CLIENT_ID = json.loads(open(
#                     'client_secrets.json', 'r').read())['web']['client_id']
#             APPLICATION_NAME = "proj3"

#             # Connect to database
#             engine = create_engine('sqlite:///test.db')
#             base.metadata.bind = engine

#             db_session = sessionmaker(bind=engine)
#             session = db_session()

# songs = {
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

# users = {
#         "admin": true,
#         "name": "Admin",
#         "password": "sha256$I29AZENh$379d38bceb08af5506e35922a0461e77219c74fea801a4c6afa980586476581c",
#         "public_id": "1612813f-b6f7-41ce-a56e-fc952c5b926f"
#         },
# {
#         "admin": true,
#         "name": "jtothadub",
#         "password": "sha256$Sz9vmu8p$63959d458427e442ba9b6842591a0aa64cda0102fbcf1438b7efa20ed2e385ae",
#         "public_id": "6bdc8358-0fc0-472b-b5d8-930409f67d78"
#         }

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

# =========================
# MARSHMALLOW MODEL SCHEMAS
# =========================

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


# LOGIN ROUTES
# ============
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

# USER ROUTES
# ===========
@app.route('/api/v1')
@app.route('/api/v1/user')
@app.route('/api/v1/users', methods=['GET'])
def get_all_users():
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
    return jsonify({'message' : 'user %s deleted successfully!'})

# PLAYLIST ROUTES
# ---------------
@app.route('/api/v1/user/<int:user_id>/playlist', methods=['POST'])
@token_required
def create_playlist(current_user, user_id):
    """
    Creates a playlist.
    :param user_id: the ID of the user.
    :return: 200, playlist created successfully.
    """
    x = user_id
    user = session.query(User).filter_by(id=user_id).one()
    data = request.get_json()
    new_playlist = Playlist(name=data['name'],
                            description=data['description'],
                            user_id=x)
    db.session.add(new_playlist)
    db.session.commit()
    return jsonify({ 'message' : 'playlist %s created successfully %name'  })

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


# @app.route('/playlist/<int:playlist_id>/song/<int:song_id>/',
#            methods=['GET', 'POST'])
# def show_song(song_id, playlist_id):
#     """
#     Shows song with ID <song_id>.
#     :param playlist_id: the ID of the playlist.
#     :param song_id: ID of the song.
#     :return: show-song.html.
#     """
#     playlist = session.query(Playlist).filter_by(id=playlist_id).one()
#     song = session.query(Song).filter_by(id=song_id).one()
#     return render_template('show-song.html',
#                            song_id=song,
#                            playlist_id=playlist,
#                            login_session=login_session)


# @app.route('/playlist/<int:playlist_id>/song/<int:song_id>/json')
# def show_song_json(playlist_id, song_id):
#     """
#     JSON API for information about the songs.
#     :param playlist_id: the ID of the playlist.
#     :param song_id: the ID of the playlist.
#     :return:
#     """
#     song = session.query(Song).filter_by(id=song_id).one()
#     return jsonify(song=song.serialize)


# @app.route('/playlist/<int:playlist_id>/song/<int:song_id>/xml')
# def show_song_xml(playlist_id, song_id):
#     """
#     XML API for information about the songs.
#     :param playlist_id: the ID of the playlist.
#     :param song_id: the ID of the playlist.
#     :return:
#     """
#     song = session.query(Song).filter_by(id=song_id).one()
#     response = make_response(dicttoxml([song.serialize]))
#     response.headers['Content-Type'] = 'application/xml'
#     return response


# @app.route('/playlist/<int:playlist_id>/song/create/', methods=['GET', 'POST'])
# @login_required
# def add_song_to_playlist(playlist_id):
#     """
#     Creates a song in the playlist with ID <playlist_id>.
#     :param playlist_id: the ID of the playlist.
#     :return: show_playlist.
#     """
#     playlist = session.query(Playlist).filter_by(id=playlist_id).one()

#     if login_session['user_id'] != playlist.user_id:
#         return "<script> function myFunction() {alert('You are not " \
#                "authorized to edit this user.')};" \
#                " </script><body onload='myFunction()''>"

#     if request.method == 'POST':
#         song_to_add = Song(song_name=request.form['songname'],
#                            artist=request.form['artistname'],
#                            playlist_id=playlist_id,
#                            user_id=playlist.user_id)
#         session.add(song_to_add)
#         session.commit()
#         flash("{0} added to {1}".format(song_to_add.song_name, playlist.name))
#         return redirect(url_for('show_playlist',
#                                 playlist_id=playlist_id))
#     else:
#         return render_template('add-song-to-playlist.html',
#                                playlist_id=playlist_id)


# @app.route('/playlist/<int:playlist_id>/song/<int:song_id>/edit/',
#            methods=['GET', 'POST'])
# @login_required
# def edit_song(song_id, playlist_id):
#     """
#     Edits song with the ID <song_id>.
#     :param playlist_id: the ID of the playlist.
#     :param song_id: the ID of the song.
#     :return: show_song.
#     """
#     playlist = session.query(Playlist).filter_by(id=playlist_id).one()
#     song_to_edit = session.query(Song).filter_by(id=song_id).one()
#     playlists = session.query(Playlist).order_by(asc(Playlist.name))

#     if login_session['user_id'] != song_to_edit.user_id:
#         return "<script> function myFunction() {alert('You are not " \
#                "authorized to edit this user.')};" \
#                " </script><body onload='myFunction()''>"

#     if request.method == 'POST':
#         if request.form['picture']:
#             song_to_edit.picture = request.form['picture']
#         if request.form['name']:
#             song_to_edit.song_name = request.form['name']
#         if request.form['artist']:
#             song_to_edit.artist = request.form['artist']
#         session.add(song_to_edit)
#         session.commit()
#         return redirect(url_for('show_song', song_id=song_id, playlist_id=playlist_id))
#     else:
#         return render_template('edit-song.html', song_id=song_to_edit.id,
#                                song_to_edit=song_to_edit,
#                                playlist_id=playlist_id,
#                                playlists=playlists)


# @app.route('/playlist/song/<int:song_id>/delete/', methods=['GET', 'POST'])
# @login_required
# def delete_song(song_id):
#     """
#     Deletes a song with ID <song_id>
#     :param song_id: the ID of the song.
#     :return: show_playlist.
#     """
#     song_to_delete = session.query(Song).filter_by(id=song_id).one()

#     if login_session['user_id'] != song_to_delete.user_id:
#         return "<script> function myFunction() {alert('You are not " \
#                "authorized to edit this user.')};" \
#                " </script><body onload='myFunction()''>"

#     if request.method == 'POST':
#         session.delete(song_to_delete)
#         session.commit()
#         return redirect(url_for('show_playlist',
#                                 playlist_id=song_to_delete.playlist_id))
#     else:
#         return render_template('delete-song.html', song_id=song_id,
#                                song_to_delete=song_to_delete)







@app.route('/api/play/<string:video_id>')
def create_youtube_link_from_video_id(video_id):
    url = 'https://www.youtube.com/watch?v=%s' % video_id
    return render_template('song.html', url=url, video_id=video_id)






















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
