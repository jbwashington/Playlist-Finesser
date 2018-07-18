#!flask/bin/python
from flask import Flask, jsonify, json, request
from flask_restful import Resource, Api
from utils import get_info, get_track

app = Flask(__name__)
api = Api(app)

tracks = {}

class Track(Resource):
    def get(self, track_id):
        pass
    def put(self, track_id):
        pass
    def delete(self, track_id):
        pass

class Playlist(Resource):
    def delete(self, track_id):
        pass
    def post(self, track_id):
        pass

api.add_resource(Track, '/<string:track_id>')

if __name__ == '__main__':
    app.run(debug=True)
