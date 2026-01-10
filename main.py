import os
import sys
from flask import Flask, request, redirect, url_for, make_response
import requests
import spotify_config
import base64
from dotenv import load_dotenv

load_dotenv(f'.env.{os.getenv("ENV", "local")}')
app = Flask('__name__')
app.url_map.strict_slashes = False

@app.route('/', methods=['GET'])
def landing_page():
    return redirect(url_for('get_current_song'))

@app.route('/songs/current')
def get_current_song():
    access_token = request.cookies.get('access_token')
    if not access_token:
        return redirect(url_for('spotify_auth'))

    print("Fetching current song from Spotify...")
    res = requests.get('https://api.spotify.com/v1/me/player/currently-playing',
                        headers={'Authorization': 'Bearer ' + access_token})
    if res.status_code != 200 or res.json().get("item") is None:
        return "No song is currently playing.", 200
    
    data = res.json()
    return data.get("item").get("name"), 200

@app.route('/spotify/auth')
def spotify_auth():
    print("Initiating Spotify authentication...")
    return redirect(f'https://accounts.spotify.com/authorize?client_id={app.config["SPOTIFY"].SPOTIFY_CLIENT}&response_type=code&redirect_uri={app.config["SPOTIFY"].CALLBACK_REDIRECT_URI}&scope=user-read-currently-playing')

@app.route('/spotify/auth/callback')
def spotify_auth_callback():
    print("Handling Spotify authentication callback...")
    request_code = request.args.get('code')

    auth_header = base64.b64encode((app.config['SPOTIFY'].SPOTIFY_CLIENT + ':' + app.config['SPOTIFY'].SPOTIFY_SECRET).encode('utf-8')).decode('utf-8')

    url = f'https://accounts.spotify.com/api/token'
    res = requests.post(url, data={
        'grant_type': 'authorization_code',
        'code': request_code,
        'redirect_uri': app.config['SPOTIFY'].CALLBACK_REDIRECT_URI,
    }, headers={'Authorization': 'Basic ' + auth_header, 'Content-Type': 'application/x-www-form-urlencoded'})
    
    data = res.json()
    access_token = data.get('access_token')
    
    resp = make_response(redirect(url_for('get_current_song')))
    resp.set_cookie('access_token', access_token)
    return resp


if __name__ == '__main__':
    print(os.getenv('ENV'))
    if os.getenv('SPOTIFY_CLIENT') and os.getenv('SPOTIFY_SECRET'):
        spotify_obj = spotify_config.spotify_config(os.getenv('SPOTIFY_CLIENT'), os.getenv('SPOTIFY_SECRET'))
        app.config['SPOTIFY'] = spotify_obj
        app.run(debug=True)

    else:
        print("Spotify credentials not provided. Exiting.")
        sys.exit(1)
