# import pandas as pd
# from utils.process_data import load_and_preprocess_data, prepare_training_data
# from utils.classify_mood import (train_mood_classifier, evaluate_classifier, 
#                                      save_classifier, load_classifier, predict_mood)
# from utils.yt_api import get_youtube_links
# from utils.thayers_model import cultural_adjusted_thayers 
# import joblib
# import os
# import random
# import json

# class musicgenerator:
#     def __init__(self, data_path):
#         self.data_path = data_path
#         self.model_path = 'models/mood_classifier.pkl'
#         self.df, self.features = load_and_preprocess_data(data_path)
#         self.classifier = self._initialize_classifier()
        
#     def _initialize_classifier(self):
#         os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
#         #load and train classifier
#         try:
#             classifier = load_classifier(self.model_path)
#             if classifier is None:
#                 raise FileNotFoundError
#             return classifier
#         except (FileNotFoundError, EOFError):
#             #if model doesn't exist or is corrupted, train a new one
#             X_train, X_test, y_train, y_test = prepare_training_data(
#                 self.df, self.features)
#             classifier = train_mood_classifier(X_train, y_train)
#             evaluate_classifier(classifier, X_test, y_test)
#             save_classifier(classifier, self.model_path)
#             return classifier
    
#     # Add this to your MusicGenerator class
#     def save_artist_origin(self, artist, origin):
#         self.artist_origins[artist] = origin
#         with open(self.cache_path, 'w') as f:
#             json.dump(self.artist_origins, f)


#     def get_songs_by_mood(self, mood, n=10, shuffle=True):
#         #filter songs by mood
#         mood_songs = self.df[self.df['mood'].str.lower() == mood.lower()]
#         if len(mood_songs) == 0:
#             return []
        
#         #choose top songs by popularity
#         top_songs = mood_songs.sort_values('popularity', ascending=False).head(n)
        
#         # Sort by popularity first
#         sorted_songs = mood_songs.sort_values('popularity', ascending=False)
    
#         if shuffle:  # Shuffle songs if the shuffle parameter is True
#             # Get more songs than needed so we can randomize from a larger pool
#             pool_size = min(len(sorted_songs), max(n*3, 20))  # Take 3x needed or 20, whichever is smaller
#             top_songs = sorted_songs.head(pool_size)
            
#             # Randomly select n songs from the top pool
#             selected_songs = top_songs.sample(n=n, replace=False)
#         else:
#             # Just take the top n songs
#             selected_songs = sorted_songs.head(n)


#         #make song list
#         songs = []
#         for _, row in top_songs.iterrows():
#             songs.append({
#                 'name': row['name'],
#                 'artist': row['artist'],
#                 'album': row['album'],
#                 'mood': row['mood'],
#                 'valence': row['valence'],
#                 'energy': row['energy']
#             })
        
#         return songs
    
#     def analyse_with_thayers(self, valence, energy, cultural_factor=1.0):
#         return cultural_adjusted_thayers(valence, energy, cultural_factor)
    
#     # def create_playlist(self, mood, n=10, cultural_factor=1.0):
#     #     #get songs by mood
#     #     songs = self.get_songs_by_mood(mood, n)
        
#     #     #Thayer's analysis
#     #     for song in songs:
#     #         song['thayers_mood'] = self.analyse_with_thayers(
#     #             song['valence'], song['energy'], cultural_factor)
        
#     #     #get youtube links
#     #     playlist = get_youtube_links(songs)
        
#     #     return playlist



#     # app.py (class improvements)
#     def create_playlist(self, mood, n=10, cultural_factor=None, origin_filter=None):
#         songs = self.get_songs_by_mood(mood, n)
        
#         if origin_filter:
#             songs = [s for s in songs if s.get('origin') == origin_filter]
        
#         if cultural_factor:
#             for song in songs:
#                 analysis = self.analyse_with_thayers(
#                     song['valence'],
#                     song['energy'],
#                     cultural_factor,
#                     song.get('origin')
#                 )
#                 song.update(analysis)
        
#         return get_youtube_links(songs)


# # if __name__ == "__main__":
# #     #initialize generator
# #     generator = musicgenerator('data/data_moods.csv')
    
# #     #example usage
# #     target_mood = "Sad"  # Can be "Happy", "Sad", "Energetic", "Calm"
# #     cultural_factor = 1.2  # Adjust for cultural differences (1.0 is standard)
    
# #     print(f"\nCreating {target_mood} playlist...")
# #     playlist = generator.create_playlist(target_mood, cultural_factor=cultural_factor)
    
# #     print("\nGenerated Mood Playlist:")
# #     for i, song in enumerate(playlist, 1):
# #         print(f"{i}. {song['name']} by {song['artist']}")
# #         print(f"   YouTube: {song['url']}")
# #         # print(f"   Thayer's Mood: {song['thayers_mood']}\n")



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

# Initialize Flask app
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
        """Load and preprocess dataset"""
        return load_and_preprocess_data(self.data_path)
    
    def _load_artist_origins(self):
        """Load cached artist origin data"""
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

# Initialize generator (only once when app starts)
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
