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
                elif action == "open_gang":
                    tile_indices = command.get("tile_index", [])
                    if not isinstance(tile_indices, list):
                        return {"status": "error", "message": "明杠需要指定三张手牌的索引"}
                    
                    if self.check_open_gang(next_waiting_player, tile_indices):
                        self.execute_open_gang(next_waiting_player, tile_indices)
                        return {
                            "status": "success",
                            "message": f"{next_waiting_player.name}明杠成功，请继续操作",
                            "game_state": self.get_game_state()
                        }
                    return {"status": "error", "message": "无效的明杠操作"}
                elif action == "hu":
                    # 检查是否能胡牌
                    if self.check_hu(next_waiting_player, is_self_drawn=False):
                        # 把当前打出的牌加入到胡牌玩家的手牌中
                        next_waiting_player.draw(self.last_discarded_tile)
                        # 从打出玩家的弃牌堆中移除这张牌
                        discard_player = self.players[self.waiting_player_index]
                        if discard_player.discarded and discard_player.discarded[-1] == self.last_discarded_tile:
                            discard_player.discarded.pop()
                        
                        # 修改游戏状态，让所有玩家的手牌可见
                        final_state = self.get_game_state()
                        final_state["game_over"] = True
                        final_state["winner"] = next_waiting_player.name
                        final_state["win_type"] = "点炮"
                        return {
                            "status": "success",
                            "message": f"恭喜 {next_waiting_player.name} 胡牌！",
                            "game_state": final_state
                        }
                    return {"status": "error", "message": "不符合胡牌条件"}
                else:
                    return {"status": "error", "message": "只能选择 过、吃、碰、明杠、胡"}
            
            # Normal turn actions
            if action == "draw":
                tile = self.draw_tile()
                if tile:
                    current_player.draw(tile)
                    # # 检查自摸胡牌
                    # if self.check_hu(current_player, is_self_drawn=True):
                    #     final_state = self.get_game_state()
                    #     final_state["game_over"] = True
                    #     final_state["winner"] = current_player.name
                    #     final_state["win_type"] = "自摸"
                    #     return {
                    #         "status": "success",
                    #         "message": f"恭喜 {current_player.name} 自摸！",
                    #         "game_state": final_state
                    #     }
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
            
            elif action == "hu":
                # 检查自摸胡牌
                if self.check_hu(current_player, is_self_drawn=True):
                    final_state = self.get_game_state()
                    final_state["game_over"] = True
                    final_state["winner"] = current_player.name
                    final_state["win_type"] = "自摸"
                    return {
                        "status": "success",
                        "message": f"恭喜 {current_player.name} 自摸！",
                        "game_state": final_state
                    }
            
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
        
        # 保存上家打出的牌和打出这张牌的玩家
        discarded_tile = self.last_discarded_tile
        discard_player = self.players[self.waiting_player_index]
        
        # 从手牌中移除选中的牌
        for idx in sorted(tiles_indices, reverse=True):
            player.hand.pop(idx)
            
        # 从上家的弃牌列表中移除这张牌
        if discard_player.discarded and discard_player.discarded[-1] == discarded_tile:
            discard_player.discarded.pop()
        
        # 清理等待状态
        self.waiting_player_index = None
        self.last_discarded_tile = None
        self.players_waiting_response.clear()
        
        # 添加副露
        tiles = selected_tiles + [discarded_tile]
        player.add_meld(MeldType.CHI, sorted(tiles, key=lambda x: x.number))
        
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
        
        # 保存上家打出的牌和打出这张牌的玩家
        discarded_tile = self.last_discarded_tile
        discard_player = self.players[self.waiting_player_index]
        
        # 从手牌中移除选中的牌
        for idx in sorted(tiles_indices, reverse=True):
            player.hand.pop(idx)
            
        # 从上家的弃牌列表中移除这张牌
        if discard_player.discarded and discard_player.discarded[-1] == discarded_tile:
            discard_player.discarded.pop()
        
        # 清理等待状态
        self.waiting_player_index = None
        self.last_discarded_tile = None
        self.players_waiting_response.clear()
        
        # 添加副露
        tiles = selected_tiles + [discarded_tile]
        player.add_meld(MeldType.PENG, tiles)
        
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

    def check_open_gang(self, player: Player, tiles_indices: List[int]) -> bool:
        return True
        # """检查明杠操作是否合法"""
        # # 检查数组长度
        # if len(tiles_indices) != 3:
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

    def execute_open_gang(self, player: Player, tiles_indices: List[int]):
        """执行明杠操作"""
        # 获取选中的牌
        selected_tiles = [player.hand[idx] for idx in sorted(tiles_indices, reverse=True)]
        
        # 保存上家打出的牌和打出这张牌的玩家
        discarded_tile = self.last_discarded_tile
        discard_player = self.players[self.waiting_player_index]
        
        # 从手牌中移除选中的牌
        for idx in sorted(tiles_indices, reverse=True):
            player.hand.pop(idx)
            
        # 从上家的弃牌列表中移除这张牌
        if discard_player.discarded and discard_player.discarded[-1] == discarded_tile:
            discard_player.discarded.pop()
        
        # 清理等待状态
        self.waiting_player_index = None
        self.last_discarded_tile = None
        self.players_waiting_response.clear()
        
        # 添加明杠到副露，包含上家打出的牌
        tiles = selected_tiles + [discarded_tile]
        player.add_meld(MeldType.OPEN_GANG, tiles)
        
        # 设置当前玩家为明杠的玩家
        self.current_player_index = self.players.index(player)

    def check_hu(self, player: Player, is_self_drawn: bool = False) -> bool:
        """
        检查玩家是否胡牌
        is_self_drawn: 是否自摸
        """
        all_tiles = player.hand.copy()
        if is_self_drawn:
            # 自摸时检查手牌
            return self.is_hu(all_tiles)
        else:
            # 点炮时加入打出的牌
            if self.last_discarded_tile:
                all_tiles.append(self.last_discarded_tile)
                return self.is_hu(all_tiles)
        return False

    def is_hu(self, tiles: List[Tile]) -> bool:
        return True
        # """
        # 检查一手牌是否构成和牌
        # 基本和牌规则：4组顺子或刻子 + 1对将牌
        # """
        # if len(tiles) != 14:  # 必须是14张牌
        #     return False
            
        # # 对牌进行排序
        # tiles.sort(key=lambda x: (x.tile_type.value, x.number))
        
        # # 枚举所有可能的将牌
        # for i in range(len(tiles) - 1):
        #     if i > 0 and tiles[i].tile_type == tiles[i-1].tile_type and tiles[i].number == tiles[i-1].number:
        #         continue  # 跳过重复的将牌
            
        #     if i < len(tiles) - 1 and tiles[i].tile_type == tiles[i+1].tile_type and tiles[i].number == tiles[i+1].number:
        #         # 找到一对将牌，创建剩余牌的副本
        #         remain_tiles = tiles.copy()
        #         # 移除将牌
        #         remain_tiles.pop(i+1)
        #         remain_tiles.pop(i)
                
        #         # 检查剩余牌是否能组成4组顺子或刻子
        #         if self._can_form_melds(remain_tiles):
        #             return True
                    
        # return False

    def _can_form_melds(self, tiles: List[Tile]) -> bool:
        """
        检查给定的牌是否能组成顺子或刻子
        """
        if not tiles:  # 所有牌都已经组合完成
            return True
            
        if len(tiles) < 3:  # 剩余牌不足3张
            return False
            
        first_tile = tiles[0]
        
        # 尝试组成刻子
        if (len(tiles) >= 3 and 
            all(t.tile_type == first_tile.tile_type and t.number == first_tile.number 
                for t in tiles[1:3])):
            # 移除这个刻子后递归检查剩余的牌
            return self._can_form_melds(tiles[3:])
        
        # 尝试组成顺子（仅对数字牌）
        if (first_tile.tile_type in [TileType.CHARACTERS, TileType.DOTS, TileType.BAMBOO] and 
            first_tile.number <= 7):  # 确保有足够的空间形成顺子
            
            # 查找后续两张牌
            next_tiles = []
            remaining = tiles[1:]
            
            for i in range(2):
                found = False
                for j, t in enumerate(remaining):
                    if (t.tile_type == first_tile.tile_type and 
                        t.number == first_tile.number + i + 1):
                        next_tiles.append(t)
                        remaining = remaining[:j] + remaining[j+1:]
                        found = True
                        break
                if not found:
                    break
            
            if len(next_tiles) == 2:  # 找到完整的顺子
                new_tiles = remaining
                return self._can_form_melds(new_tiles)
        
        return False
