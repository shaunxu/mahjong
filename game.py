#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
麻将游戏主模块
包含游戏的核心逻辑，玩家和电脑的座位分配，以及初始手牌生成等功能
"""

import random
from enum import Enum
from typing import List, Dict, Tuple, Optional


class Wind(Enum):
    """风位枚举，代表东南西北四个方位"""
    EAST = "东"
    SOUTH = "南"
    WEST = "西"
    NORTH = "北"


class TileType(Enum):
    """麻将牌类型枚举"""
    WAN = "万"  # 万子
    TONG = "筒"  # 筒子
    TIAO = "条"  # 条子
    FENG = "风"  # 风牌（东南西北）
    DRAGON = "箭"  # 箭牌（中发白）


class Tile:
    """麻将牌类"""
    def __init__(self, tile_type: TileType, value: int):
        """
        初始化麻将牌
        :param tile_type: 牌的类型
        :param value: 牌的数值
        """
        self.tile_type = tile_type
        self.value = value

    def __str__(self) -> str:
        """返回牌的字符串表示"""
        if self.tile_type == TileType.FENG:
            feng_values = {1: "东", 2: "南", 3: "西", 4: "北"}
            return f"{feng_values[self.value]}{self.tile_type.value}"
        elif self.tile_type == TileType.DRAGON:
            dragon_values = {1: "中", 2: "发", 3: "白"}
            return f"{dragon_values[self.value]}{self.tile_type.value}"
        else:
            return f"{self.value}{self.tile_type.value}"

    def __eq__(self, other) -> bool:
        """判断两张牌是否相同"""
        if not isinstance(other, Tile):
            return False
        return self.tile_type == other.tile_type and self.value == other.value


class Player:
    """玩家类，包括真实玩家和电脑玩家"""
    def __init__(self, name: str, is_human: bool = False):
        """
        初始化玩家
        :param name: 玩家名称
        :param is_human: 是否为真实玩家
        """
        self.name = name
        self.is_human = is_human
        self.hand: List[Tile] = []  # 手牌
        self.wind: Optional[Wind] = None  # 风位

    def set_wind(self, wind: Wind) -> None:
        """设置玩家的风位"""
        self.wind = wind

    def add_tile(self, tile: Tile) -> None:
        """添加一张牌到手牌"""
        self.hand.append(tile)

    def sort_hand(self) -> None:
        """对手牌进行排序"""
        # 定义排序优先级
        def tile_sort_key(tile: Tile) -> Tuple:
            type_order = {
                TileType.WAN: 0,
                TileType.TONG: 1,
                TileType.TIAO: 2,
                TileType.FENG: 3,
                TileType.DRAGON: 4
            }
            return type_order[tile.tile_type], tile.value

        self.hand.sort(key=tile_sort_key)

    def display_hand(self) -> str:
        """显示玩家的手牌"""
        self.sort_hand()
        return " ".join(str(tile) for tile in self.hand)


class MahjongGame:
    """麻将游戏类，包含游戏的核心逻辑"""
    def __init__(self):
        """初始化游戏"""
        self.players: List[Player] = []
        self.tiles: List[Tile] = []  # 牌堆
        self.current_player_index = 0
        self.initialize_game()

    def initialize_game(self) -> None:
        """初始化游戏，创建玩家和牌堆"""
        # 创建玩家（1个真实玩家和3个电脑玩家）
        self.players = [
            Player("玩家", True),
            Player("电脑1"),
            Player("电脑2"),
            Player("电脑3")
        ]

        # 创建牌堆
        self.create_tiles()

        # 分配座位（随机分配东南西北）
        self.assign_seats()

        # 洗牌
        self.shuffle_tiles()

        # 发牌
        self.deal_initial_tiles()

    def create_tiles(self) -> None:
        """创建麻将牌堆"""
        self.tiles = []

        # 万、筒、条（1-9各4张）
        for tile_type in [TileType.WAN, TileType.TONG, TileType.TIAO]:
            for value in range(1, 10):
                for _ in range(4):  # 每种牌4张
                    self.tiles.append(Tile(tile_type, value))

        # 风牌（东南西北各4张）
        for value in range(1, 5):
            for _ in range(4):
                self.tiles.append(Tile(TileType.FENG, value))

        # 箭牌（中发白各4张）
        for value in range(1, 4):
            for _ in range(4):
                self.tiles.append(Tile(TileType.DRAGON, value))

    def shuffle_tiles(self) -> None:
        """洗牌"""
        random.shuffle(self.tiles)

    def assign_seats(self) -> None:
        """随机分配座位（东南西北）"""
        winds = list(Wind)
        random.shuffle(winds)

        for i, player in enumerate(self.players):
            player.set_wind(winds[i])
            # 如果是东风玩家，设为起始玩家
            if winds[i] == Wind.EAST:
                self.current_player_index = i

    def deal_initial_tiles(self) -> None:
        """发初始手牌，每人13张"""
        for _ in range(13):  # 每人13张牌
            for player in self.players:
                if self.tiles:  # 确保还有牌
                    player.add_tile(self.tiles.pop())

    def get_game_state(self) -> dict:
        """获取游戏状态的JSON格式数据"""
        game_state = {
            "remaining_tiles": len(self.tiles),
            "players": []
        }

        for player in self.players:
            player_state = {
                "name": player.name,
                "wind": player.wind.value if player.wind else None,
                "is_human": player.is_human
            }
            
            if player.is_human:
                player_state["hand"] = [str(tile) for tile in player.hand]
            else:
                player_state["hand_count"] = len(player.hand)
            
            game_state["players"].append(player_state)

        return game_state

    def get_available_actions(self) -> dict:
        """获取当前可用的游戏指令"""
        current_player = self.players[self.current_player_index]
        actions = {
            "available_commands": [
                {
                    "command": "draw",
                    "description": "摸牌"
                },
                {
                    "command": "discard",
                    "description": "打出一张牌",
                    "params": ["牌的索引（0-13）"]
                }
                # 后续可以添加更多指令，如吃碰杠等
            ],
            "current_player": current_player.name
        }
        return actions

    def display_game_status(self) -> None:
        """显示游戏状态（JSON格式）"""
        import json
        game_state = self.get_game_state()
        available_actions = self.get_available_actions()
        
        output = {
            "game_state": game_state,
            "available_actions": available_actions
        }
        
        print(json.dumps(output, ensure_ascii=False, indent=2))

    def draw_tile(self) -> Optional[Tile]:
        """摸牌"""
        if not self.tiles:
            return None
        return self.tiles.pop()

    def discard_tile(self, player: Player, tile_index: int) -> Optional[Tile]:
        """打出一张牌"""
        if not (0 <= tile_index < len(player.hand)):
            raise ValueError("无效的牌索引")
        return player.hand.pop(tile_index)

    def process_command(self, command_data: dict) -> dict:
        """处理玩家指令"""
        current_player = self.players[self.current_player_index]
        
        if not current_player.is_human:
            return {"error": "当前不是玩家回合"}

        try:
            if command_data.get("command") == "draw":
                tile = self.draw_tile()
                if tile:
                    current_player.add_tile(tile)
                    current_player.sort_hand()
                    return {"success": True, "message": f"摸到了 {str(tile)}"}
                else:
                    return {"error": "牌堆已空"}
                    
            elif command_data.get("command") == "discard":
                tile_index = command_data.get("params", [None])[0]
                if tile_index is None:
                    return {"error": "请指定要打出的牌的索引"}
                    
                try:
                    tile_index = int(tile_index)
                    discarded_tile = self.discard_tile(current_player, tile_index)
                    # TODO: 这里可以添加其他玩家是否可以吃碰杠的判断
                    self.current_player_index = (self.current_player_index + 1) % 4
                    return {"success": True, "message": f"打出了 {str(discarded_tile)}"}
                except ValueError as e:
                    return {"error": str(e)}
                    
            else:
                return {"error": "无效的指令"}
                
        except Exception as e:
            return {"error": str(e)}


def main():
    """主函数"""
    import json
    
    game = MahjongGame()

    # 东风玩家先摸牌
    while True:
        current_player = game.players[game.current_player_index]
        # 摸牌
        tile = game.draw_tile()
        if tile:
            current_player.add_tile(tile)
            current_player.sort_hand()
            print(f"{current_player.name} 摸到了 {str(tile)}")
        else:
            print(json.dumps({"error": "牌堆已空"}, ensure_ascii=False))
            break

        # 如果是电脑，直接打出刚摸到的牌
        if not current_player.is_human:
            # 默认打出刚摸到的最后一张
            discarded_tile = game.discard_tile(current_player, len(current_player.hand) - 1)
            print(f"{current_player.name} 打出了 {str(discarded_tile)}")
            game.display_game_status()
            # 电脑出牌后暂停，等待玩家输入
            break
        else:
            game.display_game_status()
            break

    # 用户输入循环
    while True:
        try:
            command = input()
            command_data = json.loads(command)
            
            # 处理指令
            result = game.process_command(command_data)
            print(json.dumps(result, ensure_ascii=False))
            
            if result.get("success"):
                game.display_game_status()
                # 如果玩家输入"过"，则继续让下一个电脑自动出牌
                if command_data.get("command") == "pass":
                    game.current_player_index = (game.current_player_index + 1) % 4
                    while True:
                        current_player = game.players[game.current_player_index]
                        if not current_player.is_human:
                            tile = game.draw_tile()
                            if tile:
                                current_player.add_tile(tile)
                                current_player.sort_hand()
                                print(f"{current_player.name} 摸到了 {str(tile)}")
                            else:
                                print(json.dumps({"error": "牌堆已空"}, ensure_ascii=False))
                                break
                            discarded_tile = game.discard_tile(current_player, len(current_player.hand) - 1)
                            print(f"{current_player.name} 打出了 {str(discarded_tile)}")
                            game.display_game_status()
                            # 电脑出牌后暂停，等待玩家输入
                            break
                        else:
                            game.display_game_status()
                            break
        except json.JSONDecodeError:
            print(json.dumps({"error": "指令格式错误，请使用JSON格式"}, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))


if __name__ == "__main__":
    main()