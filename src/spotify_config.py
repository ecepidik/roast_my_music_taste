class spotify_config:
    def __init__(self, spotify_secret, spotify_client, callback_redirect_uri='http://127.0.0.1:5000/spotify/auth/callback'):
        self.SPOTIFY_SECRET = spotify_secret
        self.SPOTIFY_CLIENT = spotify_client
        self.CALLBACK_REDIRECT_URI = callback_redirect_uri        
    