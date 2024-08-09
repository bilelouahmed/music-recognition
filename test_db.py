from libs.database import FingerprintsDatabase

with FingerprintsDatabase("songs.db") as db:
    print(db.select("songs", ["title", "artists", "album"]))
    print(db.check_existence("BZMOR", "TIF"))
