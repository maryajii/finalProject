from googleapiclient.discovery import build
from youtube_search import YoutubeSearch
import yaml
import os
import requests
from functools import lru_cache


def load_youtube_api_key():
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config['youtube_api_key']

def search_youtube_video(song_name, artist, api_key=None):
    if api_key:
        #use youtube API
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        query = f"{song_name} {artist} official audio"
        request = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=1,
            type='video'
        )
        response = request.execute()
        
        if response['items']:
            video_id = response['items'][0]['id']['videoId']
            return f"https://www.youtube.com/watch?v={video_id}"
    else:
        #fallback to unofficial API
        results = YoutubeSearch(f"{song_name} {artist}", max_results=1).to_dict()
        if results:
            return f"https://www.youtube.com{results[0]['url_suffix']}"
    
    return None


def get_youtube_links(song_list):
    api_key = load_youtube_api_key()
    links = []
    
    for song in song_list:
        link = search_youtube_video(song['name'], song['artist'], api_key)
        if link:
            links.append({
                'name': song['name'],
                'artist': song['artist'],
                'url': link
            })
    
    return links