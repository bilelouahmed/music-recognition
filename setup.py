from libs.database import FingerprintsDatabase
from termcolor import colored

with FingerprintsDatabase("songs.db") as db:
    db.setup()
    print(colored("Database initialized successfully.", color="green", attrs=["bold"]))
