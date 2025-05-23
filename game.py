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
        # Create 3 computer players and 1 human player
        self.players = [
            Player("computer 1"),
            Player("computer 2"),
            Player("computer 3"),
            Player("human", is_human=True)
        ]
        
        # Randomly assign winds to players
        winds = [Seat.EAST, Seat.SOUTH, Seat.WEST, Seat.NORTH]
        random.shuffle(winds)
        for player, wind in zip(self.players, winds):
            player.seat = wind
            if wind == Seat.EAST:
                self.current_player_index = self.players.index(player)
    
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
            "players": [
                # Only show hand for human player
                p.to_dict(show_hand=p.is_human)
                for p in self.players
            ]
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
                    return {"status": "success", "message": "Drew a tile", "game_state": self.get_game_state()}
                return {"status": "error", "message": "No tiles left"}
            
            elif action == "discard":
                if tile_index is not None:
                    tile = self.get_current_player().discard(tile_index)
                    if tile:
                        self.next_player()
                        return {"status": "success", "message": f"Discarded {str(tile)}", "game_state": self.get_game_state()}
                return {"status": "error", "message": "Invalid tile index"}
            
            elif action in ["chi", "peng", "gang", "hu"]:
                return {"status": "info", "message": f"{action} not implemented yet"}
            
            elif action == "pass":
                self.next_player()
                return {"status": "success", "message": "Passed", "game_state": self.get_game_state()}
            
            return {"status": "error", "message": "Invalid command"}
        
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON format"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
