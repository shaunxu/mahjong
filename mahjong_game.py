import json
import argparse
from game import Game

def format_tiles(tiles):
    return ", ".join(tile["display"] if isinstance(tile, dict) else str(tile) for tile in tiles)

def format_melds(melds):
    meld_types = {"chi": "吃", "peng": "碰", "hidden_gang": "暗杠", "open_gang": "明杠"}
    formatted = []
    for meld in melds:
        meld_type = meld_types.get(meld["type"], meld["type"])
        tiles = format_tiles(meld["tiles"])
        formatted.append(f"{meld_type}[{tiles}]")
    return " ".join(formatted)

def print_game_state_compact(game_state):
    wind_map = {"east": "东", "south": "南", "west": "西", "north": "北"}
    
    if game_state.get("game_over"):
        print("\n=== 游戏结束 ===")
        print(f"赢家: {game_state['winner']}")
        print(f"和牌方式: {game_state['win_type']}")
    elif game_state.get("waiting_response"):
        print(f"\n等待 {game_state['waiting_player']} 响应")
        if game_state['last_discarded_tile']:
            print(f"上家打出：{game_state['last_discarded_tile']['display']}")
    else:
        print(f"\n当前执行：{game_state['current_player']}")
    print("-" * 50)
    
    for player in game_state["players"]:
        wind_char = wind_map[player["seat"]]
        name = player["name"]
        print(f"【{wind_char}】{name}")
        print(f"  手牌：{format_tiles(player['hand'])}")
        print(f"  副露：{format_melds(player['melds'])}")
        print(f"  弃牌：{format_tiles(player['discarded'])}")
    print("-" * 50)

def print_available_actions(game_state):
    if game_state.get("game_over"):
        print("\n游戏已结束")
        return
        
    print("\n可用操作：")
    if game_state.get("waiting_response"):
        print("1. 过：{'action': 'pass'}")
        print("2. 吃：{'action': 'chi'}")
        print("3. 碰：{'action': 'peng'}")
        print("4. 明杠：{'action': 'open_gang', 'tile_index': [数字1, 数字2, 数字3]}")
        print("5. 胡：{'action': 'hu'}")
    else:
        print("1. 摸牌：{'action': 'draw'}")
        print("2. 打出：{'action': 'discard', 'tile_index': 数字}")
        print("3. 暗杠：{'action': 'hidden_gang', 'tile_index': [数字1, 数字2, 数字3, 数字4]}")
        print("4. 胡：{'action': 'hu'} (自摸)")

def main():
    parser = argparse.ArgumentParser(description="麻将游戏")
    parser.add_argument("--json", action="store_true", help="以JSON格式显示游戏状态")
    args = parser.parse_args()

    game = Game()
    if args.json:
        print(json.dumps(game.get_game_state(), ensure_ascii=False, indent=2))
    else:
        print_game_state_compact(game.get_game_state())
    
    while True:
        game_state = game.get_game_state()
        
        # 如果游戏已结束，显示最终状态并退出
        if game_state.get("game_over"):
            if args.json:
                print(json.dumps(game_state, ensure_ascii=False, indent=2))
            else:
                print_game_state_compact(game_state)
            print("\n游戏结束！")
            break
            
        # 显示当前状态
        if game_state.get("waiting_response"):
            print(f"\n轮到 {game_state['waiting_player']} 响应")
        else:
            print(f"\n轮到 {game_state['current_player']} 行动")
        print_available_actions(game_state)
        
        command = input("请输入操作(JSON格式): ")
        result = game.handle_command(command)
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result["status"] == "success":
                print(f"\n{result['message']}")
                print_game_state_compact(result["game_state"])
            else:
                print(f"\n错误：{result['message']}")

if __name__ == "__main__":
    main()
