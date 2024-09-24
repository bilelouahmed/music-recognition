import __init__
import psycopg2
from psycopg2 import sql
from typing import List, Tuple, Any, Optional
from collections import Counter
import os
from models.song_fingerprint import SongHashPair, SongFingerprint


class PostgresDatabase:
    def __init__(
        self,
        dbname: str = os.getenv("POSTGRES_DB"),
        user: str = os.getenv("POSTGRES_USER"),
        password: str = os.getenv("POSTGRES_PASSWORD"),
        host: str = os.getenv("POSTGRES_HOST"),
        port: str = os.getenv("POSTGRES_PORT"),
    ):
        self.conn = None
        self.cursor = None
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connect(self):
        """Establishes a connection to the PostgreSQL database using environment variables."""
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
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
        query = sql.SQL("CREATE TABLE IF NOT EXISTS {table} ({fields})").format(
            table=sql.Identifier(table_name),
            fields=sql.SQL(", ").join(map(sql.SQL, columns)),
        )
        self.execute_query(query)

    def insert(self, table_name: str, data: dict) -> None:
        """Inserts data into a table."""
        columns = sql.SQL(", ").join(map(sql.Identifier, data.keys()))
        values = sql.SQL(", ").join(sql.Placeholder() * len(data))
        query = sql.SQL("INSERT INTO {table} ({columns}) VALUES ({values})").format(
            table=sql.Identifier(table_name), columns=columns, values=values
        )
        self.execute_query(query, tuple(data.values()))

    def select(
        self, table_name: str, columns: List[str] = ["*"], condition: str = ""
    ) -> List[Tuple[Any, ...]]:
        """Selects data from a table."""
        query = sql.SQL("SELECT {fields} FROM {table} {condition}").format(
            fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
            table=sql.Identifier(table_name),
            condition=sql.SQL(condition),
        )
        return self.fetch_all(query)

    def update(self, table_name: str, data: dict, condition: str) -> None:
        """Updates data in a table."""
        set_clause = sql.SQL(", ").join(
            [
                sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder())
                for k in data.keys()
            ]
        )
        query = sql.SQL("UPDATE {table} SET {set_clause} WHERE {condition}").format(
            table=sql.Identifier(table_name),
            set_clause=set_clause,
            condition=sql.SQL(condition),
        )
        self.execute_query(query, tuple(data.values()))

    def delete(self, table_name: str, condition: str) -> None:
        """Deletes data from a table."""
        query = sql.SQL("DELETE FROM {table} WHERE {condition}").format(
            table=sql.Identifier(table_name), condition=sql.SQL(condition)
        )
        self.execute_query(query)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class FingerprintsDatabase(PostgresDatabase):
    def __init__(self):
        super().__init__()

    def setup(self):
        """Initializes the database with necessary tables."""
        self.create_table(
            "songs",
            [
                "id SERIAL PRIMARY KEY",
                "title VARCHAR(50) NOT NULL",
                "artists VARCHAR(50)",
                "album VARCHAR(50)",
                "lyrics TEXT",
                "cover VARCHAR(100)",
                "url VARCHAR(100)",
            ],
        )

        self.create_table(
            "fingerprints",
            [
                "id SERIAL PRIMARY KEY",
                "song_id INTEGER REFERENCES songs(id)",
                "hash VARCHAR(150) NOT NULL",
                '"offset" FLOAT NOT NULL',
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
        query = "SELECT COUNT(*) FROM songs WHERE title = %s AND artists = %s"
        result = self.fetch_one(query, (song_title, song_artist))
        return result[0] > 0

    def insert_song(self, song_details: dict) -> int:
        """
        Inserts a song into the songs table.

        :param song_details: A dictionary containing the song's details.
        :return: The ID of the inserted song.
        """
        self.insert("songs", song_details)
        self.cursor.execute("SELECT LASTVAL()")
        return self.cursor.fetchone()[0]  # Return the ID of the last inserted row

    def insert_fingerprint(self, fingerprint: SongFingerprint):
        """
        Inserts a list of fingerprints into the fingerprints table.

        :param song_id: The ID of the song to which the fingerprints belong.
        :param fingerprints: A list of tuples, each containing a fingerprint hash and its offset.
        """
        song_id = fingerprint.get_song_id()

        for hash_value, offset in fingerprint:
            data = {"song_id": song_id, "hash": hash_value, "offset": offset}
            self.insert("fingerprints", data)

    def identify_song(
        self, query_fingerprints: List[Tuple[str, float]]
    ) -> List[Tuple[int, Optional[int]]]:
        """
        Identifies a song based on a list of fingerprint hashes.

        :param query_fingerprints: A list of tuples, each containing a fingerprint hash and its offset.
        :return: The title of the identified song.
        """
        query_hashes = [fp[0] for fp in query_fingerprints]

        if not query_hashes:
            raise ValueError("Empty fingerprint list provided.")

        query = """
        SELECT song_id
        FROM fingerprints
        WHERE hash = ANY(%s)
        """

        print(query_hashes)
        matching_rows = self.fetch_all(query, (query_hashes,))

        if not matching_rows:
            return None

        song_id_counts = Counter(row[0] for row in matching_rows)

        most_commons_song_id = song_id_counts.most_common(2)
        best_match_song_id = most_commons_song_id[0][0]
        second_best_match_song_id = (
            most_commons_song_id[1][0] if len(most_commons_song_id) > 1 else None
        )

        return (
            (best_match_song_id, second_best_match_song_id)
            if second_best_match_song_id
            else best_match_song_id
        )
