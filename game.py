import json
from typing import List, Optional, Dict
import random
from tile import Tile, create_tile_set, TileType
from player import Player, Seat, MeldType

class Game:
    def __init__(self):
        self.players: List[Player] = []
        self.current_player_index = 0
        self.tiles: List[Tile] = []
        self.last_discarded_tile: Optional[Tile] = None
        self.waiting_player_index: Optional[int] = None
        self.players_waiting_response = []
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
    
    def start_waiting_for_responses(self, discarded_tile: Tile):
        self.last_discarded_tile = discarded_tile
        self.waiting_player_index = self.current_player_index
        # Create list of players to query in order, excluding the current player
        self.players_waiting_response = [
            (self.current_player_index + i) % 4 
            for i in range(1, 4)
        ]
    
    def get_next_waiting_player(self) -> Optional[Player]:
        if not self.players_waiting_response:
            return None
        return self.players[self.players_waiting_response[0]]
    
    def is_waiting_for_responses(self) -> bool:
        return bool(self.players_waiting_response)
    
    def handle_pass_response(self):
        if self.players_waiting_response:
            self.players_waiting_response.pop(0)
            if not self.players_waiting_response:
                # All players passed, move to the next player's turn
                self.waiting_player_index = None
                self.last_discarded_tile = None
                self.next_player()
    
    def get_game_state(self) -> Dict:
        current_player = self.get_current_player()
        state = {
            "remaining_tiles": len(self.tiles),
            "current_player": current_player.name,
            "players": [p.to_dict() for p in self.players]
        }
        
        if self.is_waiting_for_responses():
            next_waiting_player = self.get_next_waiting_player()
            state.update({
                "waiting_response": True,
                "last_discarded_tile": self.last_discarded_tile.to_dict() if self.last_discarded_tile else None,
                "waiting_player": next_waiting_player.name
            })
        
        return state
    
    def handle_command(self, command_str: str) -> Dict:
        try:
            command = json.loads(command_str)
            action = command.get("action", "")
            tile_index = command.get("tile_index")
            
            current_player = self.get_current_player()
            
            # If we're waiting for responses from other players
            if self.is_waiting_for_responses():
                next_waiting_player = self.get_next_waiting_player()
                # if current_player.name != next_waiting_player.name:
                #     return {"status": "error", "message": f"等待 {next_waiting_player.name} 响应"}
                
                if action == "pass":
                    self.handle_pass_response()
                    next_player = self.get_next_waiting_player()
                    if next_player:
                        return {
                            "status": "success", 
                            "message": f"过，等待 {next_player.name} 响应",
                            "game_state": self.get_game_state()
                        }
                    return {
                        "status": "success",
                        "message": "所有玩家均过",
                        "game_state": self.get_game_state()
                    }
                elif action == "chi":
                    tile_indices = command.get("tile_index", [])
                    if not isinstance(tile_indices, list):
                        return {"status": "error", "message": "吃牌需要指定两张手牌的索引"}
                    
                    if self.check_chi(next_waiting_player, tile_indices):
                        self.execute_chi(next_waiting_player, tile_indices)
                        return {
                            "status": "success",
                            "message": f"{next_waiting_player.name}吃牌成功，请出牌",
                            "game_state": self.get_game_state()
                        }
                    return {"status": "error", "message": "无效的吃牌操作"}
                    
                elif action == "peng":
                    tile_indices = command.get("tile_index", [])
                    if not isinstance(tile_indices, list):
                        return {"status": "error", "message": "碰牌需要指定两张手牌的索引"}
                    
                    if self.check_peng(next_waiting_player, tile_indices):
                        self.execute_peng(next_waiting_player, tile_indices)
                        return {
                            "status": "success",
                            "message": f"{next_waiting_player.name}碰牌成功，请出牌",
                            "game_state": self.get_game_state()
                        }
                    return {"status": "error", "message": "无效的碰牌操作"}
                elif action in ["gang", "hu"]:
                    return {"status": "info", "message": f"{action}功能尚未实现"}
                else:
                    return {"status": "error", "message": "只能选择 过、吃、碰、杠、胡"}
            
            # Normal turn actions
            if action == "draw":
                tile = self.draw_tile()
                if tile:
                    current_player.draw(tile)
                    return {"status": "success", "message": "摸了一张牌", "game_state": self.get_game_state()}
                return {"status": "error", "message": "牌堆已空"}
            
            elif action == "discard":
                if tile_index is not None:
                    tile = current_player.discard(tile_index)
                    if tile:
                        self.start_waiting_for_responses(tile)
                        next_waiting_player = self.get_next_waiting_player()
                        return {
                            "status": "success", 
                            "message": f"打出 {str(tile)}，等待 {next_waiting_player.name} 响应", 
                            "game_state": self.get_game_state()
                        }
                return {"status": "error", "message": "无效的牌索引"}
            
            elif action == "hidden_gang":
                tile_indices = command.get("tile_index", [])
                if not isinstance(tile_indices, list):
                    return {"status": "error", "message": "暗杠需要指定四张手牌的索引"}
                
                if self.check_hidden_gang(current_player, tile_indices):
                    self.execute_hidden_gang(current_player, tile_indices)
                    return {
                        "status": "success",
                        "message": "暗杠成功，请继续操作",
                        "game_state": self.get_game_state()
                    }
                return {"status": "error", "message": "无效的暗杠操作"}
            
            return {"status": "error", "message": "无效的指令"}
        
        except json.JSONDecodeError:
            return {"status": "error", "message": "无效的JSON格式"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_chi(self, player: Player, tiles_indices: List[int]) -> bool:
        return True
        # """检查吃牌操作是否合法"""
        # # 检查数组长度
        # if len(tiles_indices) != 2:
        #     return False
            
        # # 确保索引有效
        # if not all(0 <= idx < len(player.hand) for idx in tiles_indices):
        #     return False
            
        # # 获取玩家选择的牌和上家打出的牌
        # selected_tiles = [player.hand[idx] for idx in tiles_indices]
        # discarded_tile = self.last_discarded_tile
        
        # # 所有牌必须是同一种花色的数牌
        # all_tiles = selected_tiles + [discarded_tile]
        # tile_type = discarded_tile.tile_type
        # if not all(t.tile_type == tile_type for t in all_tiles) or \
        #    tile_type not in [TileType.CHARACTERS, TileType.DOTS, TileType.BAMBOO]:
        #     return False
            
        # # 获取所有数字并排序
        # numbers = sorted([t.number for t in all_tiles])
        
        # # 检查是否构成顺子
        # return numbers[1] == numbers[0] + 1 and numbers[2] == numbers[1] + 1
        
    def execute_chi(self, player: Player, tiles_indices: List[int]):
        """执行吃牌操作"""
        # 获取选中的牌
        selected_tiles = [player.hand[idx] for idx in sorted(tiles_indices, reverse=True)]
        
        # 从手牌中移除选中的牌
        for idx in sorted(tiles_indices, reverse=True):
            player.hand.pop(idx)
            
        # 添加副露
        tiles = selected_tiles + [self.last_discarded_tile]
        player.add_meld(MeldType.CHI, sorted(tiles, key=lambda x: x.number))
        
        # 清理等待状态
        self.waiting_player_index = None
        self.last_discarded_tile = None
        self.players_waiting_response.clear()
        
        # 设置当前玩家为吃牌的玩家
        self.current_player_index = self.players.index(player)

    def check_peng(self, player: Player, tiles_indices: List[int]) -> bool:
        return True
        # """检查碰牌操作是否合法"""
        # # 检查数组长度
        # if len(tiles_indices) != 2:
        #     return False
            
        # # 确保索引有效
        # if not all(0 <= idx < len(player.hand) for idx in tiles_indices):
        #     return False
            
        # # 获取玩家选择的牌和上家打出的牌
        # selected_tiles = [player.hand[idx] for idx in tiles_indices]
        # discarded_tile = self.last_discarded_tile
        
        # # 所有牌必须相同
        # return all(t.tile_type == discarded_tile.tile_type and 
        #           t.number == discarded_tile.number 
        #           for t in selected_tiles)

    def execute_peng(self, player: Player, tiles_indices: List[int]):
        """执行碰牌操作"""
        # 获取选中的牌
        selected_tiles = [player.hand[idx] for idx in sorted(tiles_indices, reverse=True)]
        
        # 从手牌中移除选中的牌
        for idx in sorted(tiles_indices, reverse=True):
            player.hand.pop(idx)
            
        # 添加副露
        tiles = selected_tiles + [self.last_discarded_tile]
        player.add_meld(MeldType.PENG, tiles)
        
        # 清理等待状态
        self.waiting_player_index = None
        self.last_discarded_tile = None
        self.players_waiting_response.clear()
        
        # 设置当前玩家为碰牌的玩家
        self.current_player_index = self.players.index(player)

    def check_hidden_gang(self, player: Player, tiles_indices: List[int]) -> bool:
        return True
        # """检查暗杠操作是否合法"""
        # # 检查数组长度
        # if len(tiles_indices) != 4:
        #     return False
            
        # # 确保索引有效
        # if not all(0 <= idx < len(player.hand) for idx in tiles_indices):
        #     return False
            
        # # 获取玩家选择的牌
        # selected_tiles = [player.hand[idx] for idx in tiles_indices]
        # first_tile = selected_tiles[0]
        
        # # 所有牌必须相同
        # return all(t.tile_type == first_tile.tile_type and 
        #           t.number == first_tile.number 
        #           for t in selected_tiles)

    def execute_hidden_gang(self, player: Player, tiles_indices: List[int]):
        """执行暗杠操作"""
        # 获取选中的牌
        selected_tiles = [player.hand[idx] for idx in sorted(tiles_indices, reverse=True)]
        
        # 从手牌中移除选中的牌
        for idx in sorted(tiles_indices, reverse=True):
            player.hand.pop(idx)
            
        # 添加暗杠到副露
        player.add_meld(MeldType.HIDDEN_GANG, selected_tiles)
