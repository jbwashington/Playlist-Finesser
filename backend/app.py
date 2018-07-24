#!flask/bin/python

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api
from flask_cors import CORS
import youtube_dl

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

# FLASK APP INITIALIZATIONS
# =========================

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
ma = Marshmallow(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# SQLALCHEMY MODELS
# =================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_name = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='playlists')

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

class PlaylistSchema(ma.ModelSchema):
    class Meta:
        model = Playlist

# FLASK ROUTES
# ============

@app.route('/')
def index():
    return jsonify({'message' : 'wuz brackin'})

@app.route('/api/v1/user')
@app.route('/api/v1/users')
def get_one_user():
    one_user = User.query.first()
    user_schema = UserSchema()
    output = user_schema.dump(one_user).data # serialize python object into json
    return jsonify({'user' : output})

@app.route('/api/v1/track/<track_name>')
def get_track_info(track_name):
    track_info = get_info(track_name)
    return jsonify({ 'track_info' : track_info })

@app.route('/api/v1/track')
def query_track_info():
    track_name = request.args.get('q')
    track_info = get_info(track_name)
    return jsonify({ 'track_info' : track_info })

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
