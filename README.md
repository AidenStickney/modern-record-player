![Modern Record Player Logo](https://i.imgur.com/df6ZI8p.png)

## Introduction

This application integrates RFID technology with Spotify's playback features. Users can associate RFID tags with Spotify albums, playlists, or tracks. Scanning an RFID tag initiates playback of the linked Spotify content. It's designed to run on a Raspberry Pi and uses Flask, SQLAlchemy, and the Spotipy library, with dependencies managed via Pipenv.

## Features

- **RFID-Spotify Linking**: Map RFID tags to Spotify URIs.
- **Spotify Playback Control**: Start playing music on Spotify by scanning an RFID tag.
- **Web Interface**: Register and manage RFID-Spotify mappings through a web interface.
- **Authentication**: OAuth-based Spotify authentication.
- **Database Integration**: Uses SQLAlchemy for storing RFID-Spotify mappings.

## Installation

1. Clone the repository:
  ```bash
    git clone https://github.com/AidenStickney/modern-record-player.git
  ```
2. Navigate to the project directory:
  ```bash
    cd modern-record-player
  ```
3. Install Pipenv, if not already installed:
  ```bash
    pip install pipenv
  ```
4. Install dependencies using Pipenv:
  ```bash
    pipenv install
  ```

## Configuration

1. Set up environment variables in a `.env` file:
  - `SECRET_KEY`: Flask secret key.
  - `DB_LOCATION`: Database URI for SQLAlchemy.
  - `FLASK_DEBUG`: Enable/disable Flask debug mode.
  - `FLASK_PORT`: Port for the Flask application.
  - `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`: Spotify API credentials.
  
2. Run `load_dotenv()` to load these settings.

## Usage

1. Activate the Pipenv shell:
  ```bash
    pipenv shell
  ```
2. Start the Flask app:
  ```bash
    python app.py
  ```
3. Navigate to the provided URL to access the web interface.
4. Authenticate with Spotify.
5. Register new RFID tags and link them to Spotify URIs.

## Endpoints

- `/`: Start the authentication process.
- `/callback`: Handle Spotify authentication callbacks.
- `/register`: Register or update RFID-Spotify mappings.

## RFID Reading

RFID tags are read in non-blocking mode. When a tag is scanned, its ID is used to look up the associated Spotify URI and start playback.

## Spotify Playback

The application supports different Spotify URI types such as albums, playlists, and tracks. The playback is managed through the Spotipy client.

## Database Model

`RfidSpotifyMapping` table stores RFID tags and corresponding Spotify URIs.

## Security

Ensure that `SECRET_KEY` is set to a secure, random value to protect session data.

## Dependencies

- Flask
- Flask-SQLAlchemy
- Spotipy
- RPi.GPIO
- mfrc522
- python-dotenv

## Contributing

Contributions are welcome. Please submit pull requests for any enhancements.
