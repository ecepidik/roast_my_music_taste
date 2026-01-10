import os
from flask import Flask
import spotify_config as spotify_config
from dotenv import load_dotenv


def create_app():
    load_dotenv(f'.env.{os.getenv("ENV", "local")}')
    app = Flask('__name__')
    app.url_map.strict_slashes = False

    if os.getenv('SPOTIFY_CLIENT') and os.getenv('SPOTIFY_SECRET') and os.getenv('CALLBACK_REDIRECT_URI'):
        spotify_obj = spotify_config.spotify_config(spotify_secret=os.getenv('SPOTIFY_SECRET'),spotify_client= os.getenv('SPOTIFY_CLIENT'), callback_redirect_uri=os.getenv('CALLBACK_REDIRECT_URI'))
        
        app.config['SPOTIFY'] = spotify_obj

        from routes import bp as routes_bp
        app.register_blueprint(routes_bp)

    else:
        raise RuntimeError("Spotify credentials not provided.")
    
    return app
