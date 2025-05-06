from flask import Flask, render_template, request, jsonify
from app import musicgenerator
import os

app = Flask(__name__)

#initialize the music generator
generator = musicgenerator('data/data_moods.csv')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    data = request.json
    mood = data.get('mood', 'Calm')
    cultural_factor = float(data.get('cultural_factor', 1.0))
    count = int(data.get('count', 10))
    
    try:
        playlist = generator.create_playlist(mood, count, cultural_factor)
        return jsonify({'status': 'success', 'playlist': playlist})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)