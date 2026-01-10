import os
from flask import Flask
from .config import spotify_config
from dotenv import load_dotenv
from .routes import bp as routes_bp


def create_app():
    load_dotenv(f'.env.{os.getenv("ENV", "local")}')
    app = Flask('__name__')
    app.url_map.strict_slashes = False

    if os.getenv('SPOTIFY_CLIENT') and os.getenv('SPOTIFY_SECRET') and os.getenv('CALLBACK_REDIRECT_URI'):
        spotify_obj = spotify_config(spotify_secret=os.getenv('SPOTIFY_SECRET'),spotify_client= os.getenv('SPOTIFY_CLIENT'), callback_redirect_uri=os.getenv('CALLBACK_REDIRECT_URI'))
        
        app.config['SPOTIFY'] = spotify_obj

        app.register_blueprint(routes_bp)

    else:
        raise RuntimeError("Spotify credentials not provided.")
    
    return app
