from flask import Blueprint, request, redirect, url_for, make_response, current_app, jsonify
import requests
import base64

bp = Blueprint('routes', __name__)

@bp.route('/', methods=['GET'])
def landing_page():
    return redirect(url_for('routes.get_current_song'))
@bp.route('/songs/current')
def get_current_song():
    print("Retrieving current song from Spotify...")
    access_token = request.cookies.get('access_token')
    if not access_token:
        return redirect(url_for('routes.spotify_auth'))
    print("Fetching current song from Spotify...")
    res = requests.get('https://api.spotify.com/v1/me/player/currently-playing',
                        headers={'Authorization': 'Bearer ' + access_token})
    
    if res.status_code == 204 or not res.content:
        return "No song is currently playing.", 200
    elif res.status_code != 200:
        return f"Error fetching current song: {res.status_code} - {res.text}", res.status_code
    else:
        current = res.json()
        item = current["item"]
        track_payload = {
            "id": item.get("id"),
            "name": item.get("name"),
            "artists": [a["name"] for a in item.get("artists", [])],
            "album": (item.get("album") or {}).get("name"),
            "explicit": item.get("explicit"),
            "popularity": item.get("popularity")
        }

        roast = current_app.config['SONG_ROASTER'].roast_track(track_payload)
        return jsonify({"track": track_payload, "roast": roast}), 200

@bp.route('/spotify/auth')
def spotify_auth():
    print("Initiating Spotify authentication...")
    return redirect(f'https://accounts.spotify.com/authorize?client_id={current_app.config["SPOTIFY"].SPOTIFY_CLIENT}&response_type=code&redirect_uri={current_app.config["SPOTIFY"].CALLBACK_REDIRECT_URI}&scope=user-read-currently-playing')

@bp.route('/spotify/auth/callback')
def spotify_auth_callback():
    print("Handling Spotify authentication callback...")
    request_code = request.args.get('code')
    auth_header = base64.b64encode((current_app.config['SPOTIFY'].SPOTIFY_CLIENT + ':' + current_app.config['SPOTIFY'].SPOTIFY_SECRET).encode('utf-8')).decode('utf-8')
    url = f'https://accounts.spotify.com/api/token'
    res = requests.post(url, data={
        'grant_type': 'authorization_code',
        'code': request_code,
        'redirect_uri': current_app.config['SPOTIFY'].CALLBACK_REDIRECT_URI,
    }, headers={'Authorization': 'Basic ' + auth_header, 'Content-Type': 'application/x-www-form-urlencoded'})
    
    data = res.json()
    access_token = data.get('access_token')
    
    resp = make_response(redirect(url_for('routes.get_current_song')))
    resp.set_cookie('access_token', access_token)
    return resp