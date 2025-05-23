import json
from game import Game

def main():
    game = Game()
    print(json.dumps(game.get_game_state(), ensure_ascii=False, indent=2))
    
    while True:
        current_player = game.get_current_player()
        
        if current_player.is_human:
            # Human player's turn
            command = input("Enter your command (in JSON format): ")
            result = game.handle_command(command)
            print(json.dumps(result, ensure_ascii=False, indent=2))
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
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
                # Wait for user's response after computer discards
                command = input("Enter your command (in JSON format) or press Enter to pass: ")
                if command.strip():
                    result = game.handle_command(command)
                else:
                    result = game.handle_command('{"action": "pass"}')
                print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
