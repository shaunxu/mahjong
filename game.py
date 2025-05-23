import json
from typing import List, Optional, Dict
import random
from tile import Tile, create_tile_set
from player import Player, Seat

class Game:
    def __init__(self):
        self.players: List[Player] = []
        self.current_player_index = 0
        self.tiles: List[Tile] = []
        self._initialize_players()
        self._initialize_game()
    
    def _initialize_players(self):
        # Create 4 players with fixed wind positions
        winds = [Seat.EAST, Seat.SOUTH, Seat.WEST, Seat.NORTH]
        self.players = []
        
        for i, wind in enumerate(winds):
            player = Player(f"玩家{i+1}")
            player.seat = wind
            self.players.append(player)
            
        # First player (East) starts the game
        self.current_player_index = 0

    def _initialize_game(self):
        # Create and shuffle tiles
        self.tiles = create_tile_set()
        
        # Deal 13 tiles to each player
        for _ in range(13):
            for player in self.players:
                player.draw(self.tiles.pop())
    
    def get_current_player(self) -> Player:
        return self.players[self.current_player_index]
    
    def draw_tile(self) -> Optional[Tile]:
        if self.tiles:
            return self.tiles.pop()
        return None
    
    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % 4
    
    def get_game_state(self) -> Dict:
        current_player = self.get_current_player()
        return {
            "remaining_tiles": len(self.tiles),
            "current_player": current_player.name,
            "players": [p.to_dict() for p in self.players]
        }
    
    def handle_command(self, command_str: str) -> Dict:
        try:
            command = json.loads(command_str)
            action = command.get("action", "")
            tile_index = command.get("tile_index")
            
            if action == "draw":
                tile = self.draw_tile()
                if tile:
                    self.get_current_player().draw(tile)
                    return {"status": "success", "message": "摸了一张牌", "game_state": self.get_game_state()}
                return {"status": "error", "message": "牌堆已空"}
            
            elif action == "discard":
                if tile_index is not None:
                    tile = self.get_current_player().discard(tile_index)
                    if tile:
                        self.next_player()
                        return {"status": "success", "message": f"打出 {str(tile)}", "game_state": self.get_game_state()}
                return {"status": "error", "message": "无效的牌索引"}
            
            elif action in ["chi", "peng", "gang", "hu"]:
                return {"status": "info", "message": f"{action}功能尚未实现"}
            
            elif action == "pass":
                self.next_player()
                return {"status": "success", "message": "过", "game_state": self.get_game_state()}
            
            return {"status": "error", "message": "无效的指令"}
        
        except json.JSONDecodeError:
            return {"status": "error", "message": "无效的JSON格式"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
