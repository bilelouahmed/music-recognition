from typing import List, Tuple, Optional


class SongHashPair:
    def __init__(self, hash: str, offset: float):
        self.hash = hash
        self.offset = offset

    def __repr__(self) -> str:
        return f"SongHashPair(hash={self.hash}, offset={self.offset})"

    def __str__(self) -> str:
        return f"SongHashPair(hash={self.hash}, offset={self.offset})"

    def __eq__(self, other) -> bool:
        return self.hash == other.hash and self.offset == other.offset

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def get_hash(self) -> str:
        return self.hash

    def get_offset(self) -> float:
        return self.offset

    def get_hash_pair(self) -> Tuple[str, float]:
        return (self.hash, self.offset)


class SongFingerprint:
    def __init__(
        self, song_id: Optional[int] = None, hash_pairs: List[SongHashPair] = []
    ):
        self.song_id = song_id
        self.hash_pairs = hash_pairs

    def __len__(self) -> int:
        return len(self.hash_pairs)

    def __iter__(self):
        for hash_pair in self.hash_pairs:
            yield hash_pair.get_hash_pair()

    def add_hash_pair(self, hash_pair: SongHashPair):
        self.hash_pairs.append(hash_pair)

    def get_song_id(self) -> str:
        return self.song_id

    def get_fingerprint(self) -> List[Tuple[str, float]]:
        return [hash_pair.get_hash_pair() for hash_pair in self.hash_pairs]

    def set_song_id(self, song_id: int):
        self.song_id = song_id
