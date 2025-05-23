from enum import Enum
from typing import List
import random

class TileType(Enum):
    CHARACTERS = "万"  # 万子
    DOTS = "筒"        # 筒子
    BAMBOO = "条"      # 条子
    WIND = "风"        # 风牌
    DRAGON = "箭"      # 箭牌

class Tile:
    def __init__(self, tile_type: TileType, number: int):
        self.tile_type = tile_type
        self.number = number
    
    def __str__(self) -> str:
        if self.tile_type in [TileType.CHARACTERS, TileType.DOTS, TileType.BAMBOO]:
            nums = ["一", "二", "三", "四", "五", "六", "七", "八", "九"]
            return f"{nums[self.number - 1]}{self.tile_type.value}"
        elif self.tile_type == TileType.WIND:
            winds = ["东", "南", "西", "北"]
            return f"{winds[self.number-1]}风"
        else:  # Dragon
            dragons = ["红中", "发财", "白板"]
            return f"{dragons[self.number-1]}"
    
    def to_dict(self) -> dict:
        return {
            "type": self.tile_type.value,
            "number": self.number,
            "display": str(self)
        }

def create_tile_set() -> List[Tile]:
    tiles = []
    
    # Create number tiles (Characters, Dots, Bamboo)
    for tile_type in [TileType.CHARACTERS, TileType.DOTS, TileType.BAMBOO]:
        for number in range(1, 10):  # 1-9
            for _ in range(4):  # 4 of each
                tiles.append(Tile(tile_type, number))
    
    # Create wind tiles
    for number in range(1, 5):  # East(1), South(2), West(3), North(4)
        for _ in range(4):
            tiles.append(Tile(TileType.WIND, number))
    
    # Create dragon tiles
    for number in range(1, 4):  # Red(1), Green(2), White(3)
        for _ in range(4):
            tiles.append(Tile(TileType.DRAGON, number))
    
    random.shuffle(tiles)
    return tiles
