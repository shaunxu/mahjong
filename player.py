from typing import List, Optional
from tile import Tile

class Seat:
    EAST = "east"
    SOUTH = "south"
    WEST = "west"
    NORTH = "north"

class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Tile] = []
        self.discarded: List[Tile] = []
        self.seat: str = ""
    
    def draw(self, tile: Tile):
        self.hand.append(tile)
    
    def discard(self, tile_index: int) -> Optional[Tile]:
        if 0 <= tile_index < len(self.hand):
            tile = self.hand.pop(tile_index)
            self.discarded.append(tile)
            return tile
        return None
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "seat": self.seat,
            "hand": [t.to_dict() for t in self.hand],
            "discarded": [t.to_dict() for t in self.discarded]
        }
