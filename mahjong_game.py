import json
import argparse
from game import Game

def format_tiles(tiles):
    if not isinstance(tiles, list):
        return "（隐藏）"
    return ", ".join(tile["display"] if isinstance(tile, dict) else str(tile) for tile in tiles)

def print_game_state_compact(game_state):
    wind_map = {"east": "东", "south": "南", "west": "西", "north": "北"}
    
    print(f"当前执行：{game_state['current_player']}")
    
    for player in game_state["players"]:
        wind_char = wind_map[player["seat"]]
        name = player["name"]
        print(f"【{wind_char}】{name}")
        print(f"  手牌：{format_tiles(player['hand'])}")
        # TODO: Add melds (开拍) display when implemented
        print(f"  开拍：")
        print(f"  弃牌：{format_tiles(player['discarded'])}")

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
        current_player = game.get_current_player()
        
        if current_player.is_human:
            # Human player's turn
            command = input("Enter your command (in JSON format): ")
            result = game.handle_command(command)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                if result["status"] == "success":
                    print_game_state_compact(result["game_state"])
                else:
                    print(f"错误：{result['message']}")
        else:
            # Computer player's turn
            # For now, just draw a tile and discard it
            result = game.handle_command('{"action": "draw"}')
            if result["status"] == "success":
                # Discard the last drawn tile
                result = game.handle_command(
                    json.dumps({
                        "action": "discard",
                        "tile_index": len(current_player.hand) - 1
                    })
                )
                if args.json:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    print_game_state_compact(result["game_state"])
                
                # Wait for user's response after computer discards
                command = input("Enter your command (in JSON format) or press Enter to pass: ")
                if command.strip():
                    result = game.handle_command(command)
                else:
                    result = game.handle_command('{"action": "pass"}')
                if args.json:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    if result["status"] == "success":
                        print_game_state_compact(result["game_state"])
                    else:
                        print(f"错误：{result['message']}")

if __name__ == "__main__":
    main()
