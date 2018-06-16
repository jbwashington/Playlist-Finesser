#!flask/bin/python
from flask import Flask, jsonify

app = Flask(__name__)

tracks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@app.route('/fin35/api/v1.0/tracks', methods=['GET'])
def get_tracks():
    return jsonify({'tracks': tracks})

if __name__ == '__main__':
    app.run(debug=True)
