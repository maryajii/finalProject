import pandas as pd
from flask import Flask, render_template, request, jsonify
from utils.process_data import load_and_preprocess_data, prepare_training_data
from utils.classify_mood import (train_mood_classifier, evaluate_classifier, 
                                save_classifier, load_classifier)
from utils.yt_api import get_youtube_links
from utils.thayers_model import cultural_adjusted_thayers
import joblib
import os
import json

#initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

class musicgenerator:
    def __init__(self, data_path):
        self.data_path = data_path
        self.model_path = 'models/mood_classifier.pkl'
        self.cache_path = 'cache/artist_origins.json'
        self.df, self.features = self._load_data()
        self.classifier = self._initialize_classifier()
        self.artist_origins = self._load_artist_origins()
    
    def _load_data(self):
        return load_and_preprocess_data(self.data_path)
    
    def _load_artist_origins(self):
        try:
            with open(self.cache_path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _initialize_classifier(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        try:
            classifier = load_classifier(self.model_path)
            if classifier is None:
                raise FileNotFoundError
            return classifier
        except (FileNotFoundError, EOFError):
            X_train, X_test, y_train, y_test = prepare_training_data(
                self.df, self.features)
            classifier = train_mood_classifier(X_train, y_train)
            evaluate_classifier(classifier, X_test, y_test)
            save_classifier(classifier, self.model_path)
            return classifier
    
    def get_songs_by_mood(self, mood, n=10, shuffle=True):
        mood_songs = self.df[self.df['mood'].str.lower() == mood.lower()]
        if len(mood_songs) == 0:
            return []
        
        if shuffle:
            pool_size = min(len(mood_songs), max(n*3, 20))
            top_songs = mood_songs.nlargest(pool_size, 'popularity')
            selected_songs = top_songs.sample(n=min(n, len(top_songs)))
        else:
            selected_songs = mood_songs.nlargest(n, 'popularity')
        
        return selected_songs.to_dict('records')
    
    def create_playlist(self, mood, n=10, cultural_factor=None, origin=None):
        songs = self.get_songs_by_mood(mood, n)
        
        if origin:
            songs = [s for s in songs if self.artist_origins.get(s['artist']) == origin]
        
        for song in songs:
            song['thayers'] = cultural_adjusted_thayers(
                song['valence'],
                song['energy'],
                cultural_factor,
                self.artist_origins.get(song['artist'])
            )
        
        return get_youtube_links(songs)

#initialize generator when app starts
generator = musicgenerator('data/data_moods_final.csv')

@app.route('/')
def home():
    """Render main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate playlist endpoint"""
    data = request.json
    try:
        playlist = generator.create_playlist(
            mood=data.get('mood', 'Happy'),
            n=int(data.get('count', 10)),
            cultural_factor=float(data.get('cultural_factor', 1.0)) if data.get('cultural_factor') else None,
            origin=data.get('origin')
        )
        return jsonify({'status': 'success', 'playlist': playlist})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/artists', methods=['GET'])
def list_artists():
    """Get unique artists for frontend filters"""
    artists = sorted(generator.df['artist'].unique().tolist())
    return jsonify(artists)

@app.route('/origins', methods=['GET'])
def list_origins():
    """Get available origin countries"""
    origins = sorted(set(generator.artist_origins.values()))
    return jsonify(origins)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
