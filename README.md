# Music Recognition App (WIP)

## Description

This project is a music identification application, similar to Shazam, that captures audio, processes it into a spectrogram, and uses a fingerprint database to identify songs by listening to a 10-second clip. Built in Python, it leverages Streamlit for the user interface and a PostgreSQL database to match audio fingerprints.

If you find this project interesting, please consider giving it a ⭐ on GitHub. Your support is greatly appreciated !

## Features

### Song Identification

1. Capture a 10-second audio snippet from a microphone.
2. Transform the audio signal into a spectrogram and extract key points.
3. Create audio fingerprints for quick comparison.
4. Identify songs by matching fingerprints against a database.
5. User interface with Streamlit for easy identification.

### Song Addition

1. Add new songs to the database by capturing their audio fingerprint.
2. Automatically store song fingerprints along with their metadata in the database for future identification.

## Requirements

- Python 3.x (Tested on Python 3.9.6)

## Setting up and running the project

This app requires Python 3.x.x (tested on 3.9.6) or Docker (which includes the setup for the PostgreSQL database used to store and retrieve audio fingerprints).

Regardless of your preferred setup method, you must first clone the repository and install the dependencies :

```
git clone https://github.com/bilelouahmed/music-recognition
cd music-recognition
```

### Running with Docker

1. Start the database and application containers :

    ```
    docker-compose up
    ```

    This command will automatically set up the PostgreSQL database and the application within containers, simplifying the setup process.

2. Open your browser and go to http://localhost:8501 to view the app interface.

### Running without Docker

1. Install required dependencies :

    ```
    pip install -r requirements.txt
    ```

2. Install and configure PostgreSQL :

    - Install [PostgreSQL](https://www.postgresql.org/download/) locally on your machine.
    - Start the PostgreSQL service.

3. Create a .env file in the root directory and set the following environment variables for the database connection :

    ```
    POSTGRES_DB=<your_database_name>
    POSTGRES_USER=<your_username>
    POSTGRES_PASSWORD=<your_password> 
    POSTGRES_HOST=<your_database_host>
    POSTGRES_PORT=<your_database_port>
    ```

4. Run the setup script :

    ```
    python3 setup.py
    ```
    
    This will initialize your database and other necessary components.

5. Launch the app :

    ```
    streamlit run app.py
    ```

6. Open your browser and navigate to http://localhost:8501 to view the app interface.


## Project Structure

├── core/
│   ├── __init__.py                # Initialization file for the core module
│   ├── audio_capture.py           # Microphone audio capture functionality
│   ├── audio_processing.py        # Audio processing and spectrogram creation
│   ├── database.py                # Audio fingerprint database management
│   └── store_songs.py             # Functions for storing song data in the database
├── data/
│   ├── recordings/                # Temporarily saved audio files
│   └── songs/                     # Stored songs and their fingerprints
├── models/
│   └── song_fingerprint.py        # Model for managing song fingerprints
├── notebooks/
│   └── database.ipynb             # Jupyter notebook for database management and testing
├── utils/
│   └── audio_utils.py             # Utility functions for audio processing
├── README.md                      # Project documentation
├── __init__.py                    # Root initialization file
├── main.py                        # Main entry point for the application
├── setup.py                       # Setup script for installation and configuration
├── .env                           # Environment variables for database configuration
├── .gitignore                     # Git ignore file
├── Dockerfile                     # Dockerfile for setting up the app and database container
├── docker-compose.yml             # Docker Compose file for container orchestration
└── database.dbml                  # Database schema file (DBML format)


## Improvements

Potential future improvements include :

- Enhanced Fingerprint Matching : Implement more robust matching algorithms or consider alternative hashing techniques for increased accuracy.
- Noise Reduction : Integrate noise filtering techniques to improve performance in noisy environments thanks to Machine Learning.
- Extended Database Features : Add song metadata and advanced search capabilities for richer song information and recommendations.
- Performance Optimization : Use optimized data structures and algorithms to handle larger fingerprint databases efficiently.