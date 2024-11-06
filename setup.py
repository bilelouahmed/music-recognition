from core.database import FingerprintsDatabase
from core.store_songs import store_audio_folder
from termcolor import colored
import __init__


with FingerprintsDatabase() as db:
    db.setup()
    store_audio_folder(folder_path="data/songs", verbose=1)
    print(colored("Database initialized successfully.", color="green", attrs=["bold"]))
