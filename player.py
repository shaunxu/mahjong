from typing import List, Optional, Dict, Tuple
from tile import Tile

class Seat:
    EAST = "east"
    SOUTH = "south"
    WEST = "west"
    NORTH = "north"

class MeldType:
    CHI = "chi"    # 吃
    PENG = "peng"  # 碰
    GANG = "gang"  # 杠

class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Tile] = []
        self.discarded: List[Tile] = []
        self.seat: str = ""
        self.melds: List[Dict] = []  # [{type: "chi/peng/gang", tiles: [Tile, Tile, Tile/Tile]}]
    
    def draw(self, tile: Tile):
        self.hand.append(tile)
    
    def discard(self, tile_index: int) -> Optional[Tile]:
        if 0 <= tile_index < len(self.hand):
            tile = self.hand.pop(tile_index)
            self.discarded.append(tile)
            return tile
        return None
    
    def add_meld(self, meld_type: str, tiles: List[Tile]):
        """添加一个副露(吃/碰/杠)"""
        self.melds.append({
            "type": meld_type,
            "tiles": tiles
        })
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "seat": self.seat,
            "hand": [t.to_dict() for t in self.hand],
            "discarded": [t.to_dict() for t in self.discarded],
            "melds": [{
                "type": m["type"],
                "tiles": [t.to_dict() for t in m["tiles"]]
            } for m in self.melds]
        }
