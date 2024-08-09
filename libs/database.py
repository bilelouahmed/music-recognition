import sqlite3
from typing import List, Tuple, Any


class SQLiteDatabase:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establishes a connection to the database."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> None:
        """Executes a SQL query."""
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_all(
        self, query: str, params: Tuple[Any, ...] = ()
    ) -> List[Tuple[Any, ...]]:
        """Executes a SELECT query and returns all results."""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query: str, params: Tuple[Any, ...] = ()) -> Tuple[Any, ...]:
        """Executes a SELECT query and returns a single result."""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def create_table(self, table_name: str, columns: List[str]) -> None:
        """Creates a new table."""
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.execute_query(query)

    def insert(self, table_name: str, data: dict) -> None:
        """Inserts data into a table."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, tuple(data.values()))

    def select(
        self, table_name: str, columns: List[str] = ["*"], condition: str = ""
    ) -> List[Tuple[Any, ...]]:
        """Selects data from a table."""
        query = f"SELECT {', '.join(columns)} FROM {table_name} {condition}"
        return self.fetch_all(query)

    def update(self, table_name: str, data: dict, condition: str) -> None:
        """Updates data in a table."""
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        self.execute_query(query, tuple(data.values()))

    def delete(self, table_name: str, condition: str) -> None:
        """Deletes data from a table."""
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.execute_query(query)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class FingerprintsDatabase(SQLiteDatabase):
    def __init__(self, db_name: str):
        super().__init__(db_name)

    def setup(self):
        """Initializes the database with necessary tables."""
        self.create_table(
            "songs",
            [
                "id INTEGER PRIMARY KEY AUTOINCREMENT",
                "title VARCHAR(50) NOT NULL",
                "artists VARCHAR(50)",
                "album VARCHAR(50)",
                "lyrics VARCHAR(1000)",
                "cover VARCHAR(100)",
                "url VARCHAR(100)",
            ],
        )

        self.create_table(
            "fingerprints",
            [
                "id INTEGER PRIMARY KEY AUTOINCREMENT",
                "song_id INTEGER",
                "hash VARCHAR(150) NOT NULL",
                "offset FLOAT NOT NULL",
                "FOREIGN KEY(song_id) REFERENCES songs(id)",
            ],
        )

        self.execute_query(
            "CREATE INDEX IF NOT EXISTS idx_fingerprints_hash ON fingerprints(hash)"
        )

    def check_existence(self, song_title: str, song_artist: str) -> bool:
        """
        Checks if a song already exists in the database based on its title and artist.

        :param song_title: The title of the song.
        :param song_artist: The artist of the song.
        :return: True if the song exists, False otherwise.
        """
        query = "SELECT COUNT(*) FROM songs WHERE title = ? AND artists = ?"
        result = self.fetch_one(query, (song_title, song_artist))
        return result[0] > 0

    def insert_song(self, song_details: dict) -> int:
        """
        Inserts a song into the songs table.

        :param song_details: A dictionary containing the song's details.
        :return: The ID of the inserted song.
        """
        self.insert("songs", song_details)
        return self.cursor.lastrowid  # Return the ID of the last inserted row

    def insert_fingerprint(
        self, song_id: int, fingerprints: List[Tuple[str, float]]
    ) -> None:
        """
        Inserts a list of fingerprints into the fingerprints table.

        :param song_id: The ID of the song to which the fingerprints belong.
        :param fingerprints: A list of tuples, each containing a fingerprint hash and its offset.
        """
        for hash_value, offset in fingerprints:
            data = {"song_id": song_id, "hash": hash_value, "offset": offset}
            self.insert("fingerprints", data)
