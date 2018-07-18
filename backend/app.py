#!flask/bin/python

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
ma = Marshmallow(app)

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


@app.route('/')
def index():
    one_user = User.query.first()
    user_schema = UserSchema()
    output = user_schema.dump(one_user).data # serialize python object into json
    return jsonify({'user' : output})

if __name__ == '__main__':
    app.run(debug=True)
