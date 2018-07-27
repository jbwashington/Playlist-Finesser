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

@app.route('/fb_disconnect')
def fb_disconnect():
    """
    Revoke a current user's token and reset their login_session on Facebook.
    Only disconnect a connected user.
    :return: response.
    """
    facebook_id = login_session['facebook_id']
    # The access token must have me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % \
            (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/g-connect', methods=['POST'])
def google_connect():
    """ Connects and authorizes user against Google's Google+ API. """

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
            % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != GOOGLE_CLIENT_ID:
        response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
                json.dumps('Current user is already connected.'),
                200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'
    # see if user exists, if it doesn't make a new one
    user_id = get_user_id(data["email"])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
            '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/disconnect/')
def disconnect():
    """ Disconnects the user based on login_session['provider'] """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            g_disconnect()
            del login_session['gplus_id']
            del login_session['credentials']

        if login_session['provider'] == 'facebook':
            fb_disconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('home'))
    else:
        flash("You were not logged out.")
        return redirect(url_for('home'))


@app.route('/fb-connect', methods=['GET', 'POST'])
def fb_connect():
    """ Connects and authorizes user against Facebook's API. """

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('facebook_secrets.json', 'r').read())[
            'web']['app_id']
    app_secret = json.loads(
            open('facebook_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=' \
            'fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=' \
            '%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    # let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&' \
            'height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
            '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/g-disconnect')
def g_disconnect():
    """
    Revoke a current user's token and reset their login_session
    Only disconnect a connected user.
    :return: response.
    """

    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
                json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
                json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# USER ROUTES
# -----------
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
