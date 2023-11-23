from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import threading
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

load_dotenv()

# Constants
SECRET_KEY = os.getenv("SECRET_KEY")
DB_LOCATION = os.getenv("DB_LOCATION")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
FLASK_PORT = os.getenv("FLASK_PORT")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = "user-read-playback-state,user-modify-playback-state"

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DB_LOCATION
app.config['DEBUG'] = FLASK_DEBUG
db = SQLAlchemy(app)

class RfidSpotifyMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rfid_tag = db.Column(db.String(50), unique=True, nullable=False)
    spotify_uri = db.Column(db.String(200), nullable=False)
    uri_type = db.Column(db.String(50), nullable=False)

read_event = threading.Event()
read_event.set()

auth_state = {'token_info': None}
auth_manager = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, 
                            redirect_uri=REDIRECT_URI, scope=SCOPE, 
                            cache_path=".spotipyoauthcache")

@app.route('/')
def login():
    if auth_state['token_info']:
        return render_template('auth_message.html', message="Already authenticated")
    else:
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = auth_manager.get_access_token(code)
    auth_state['token_info'] = token_info
    return render_template('auth_message.html', message="Authenticated Successfully!")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return handle_post_request()
    else:
        return handle_get_request()

def handle_post_request():
    rfid_tag = request.form.get('rfid_tag')
    spotify_link = request.form.get('spotify_uri')
    spotify_uri, uri_type = parse_spotify_link(spotify_link)

    if spotify_uri:
        message = update_or_create_mapping(rfid_tag, spotify_uri, uri_type)
    else:
        message = "Invalid Spotify URL."

    return render_template('registered_rfid.html', message=message)

def parse_spotify_link(link):
    parsed_url = urlparse(link)
    path_components = parsed_url.path.strip("/").split('/')
    if len(path_components) >= 2:
        uri_type, spotify_id = path_components[:2]
        return f'spotify:{uri_type}:{spotify_id}', uri_type
    return None, None

def update_or_create_mapping(rfid_tag, spotify_uri, uri_type):
    existing_mapping = RfidSpotifyMapping.query.filter_by(rfid_tag=rfid_tag).first()
    if existing_mapping:
        existing_mapping.spotify_uri = spotify_uri
        existing_mapping.uri_type = uri_type
        message = "Mapping updated successfully!"
    else:
        new_mapping = RfidSpotifyMapping(rfid_tag=rfid_tag, spotify_uri=spotify_uri, uri_type=uri_type)
        db.session.add(new_mapping)
        message = "New mapping created successfully!"
    db.session.commit()
    read_event.set()
    return message

def handle_get_request():
    rfid_id = read_rfid_for_registration()
    return render_template('register_rfid.html', rfid_id=rfid_id)

def read_rfid_for_registration():
    read_event.clear()
    reader = SimpleMFRC522()
    id = reader.read_id_no_block()
    return id if id else None

def create_spotify_client():
    token_info = auth_state.get('token_info')
    return spotipy.Spotify(auth_manager=auth_manager)

def main_script():
    with app.app_context():
        try:
            reader = SimpleMFRC522()
            sp = create_spotify_client()
            if not sp:
                raise Exception("Failed to create Spotify client.")

            while True:
                if read_event.is_set():
                    id = reader.read_id_no_block()
                    if id:
                        print(id)
                        handle_spotify_playback(id, sp)
                    time.sleep(2)
                else:
                    time.sleep(0.1)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            GPIO.cleanup()

def handle_spotify_playback(id, sp):
    mapping = RfidSpotifyMapping.query.filter_by(rfid_tag=str(id)).first()
    if not mapping:
        return

    try:
        if mapping.uri_type == 'album':
            sp.start_playback(context_uri=mapping.spotify_uri)
        elif mapping.uri_type == 'playlist':
            sp.start_playback(context_uri=mapping.spotify_uri)
        elif mapping.uri_type == 'track':
            sp.start_playback(uris=[mapping.spotify_uri])
    except Exception as e:
        print(f"Playback error: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    flask_thread = threading.Thread(target=main_script)
    flask_thread.daemon = True
    flask_thread.start()
    app.run(host='0.0.0.0', port=FLASK_PORT)