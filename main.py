# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

from typing import TypedDict
from enum import Enum
import random
import math

class Coordinate(TypedDict):
    x: int
    y: int

class Snake(TypedDict):
    id: str
    name: str
    health: int
    body: list[Coordinate]
    head: Coordinate
    length: int

class Board(TypedDict):
    height: int
    width: int
    food: list[Coordinate]
    hazards: list[Coordinate]
    snakes: list[Snake]
    you: Snake

class Game(TypedDict):
    id: str
    turn: int
    board: Board

class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "sameerbattlesnake",  # TODO: Your Battlesnake Username
        "color": "#888888",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: Game) -> dict:

    is_move_safe = {Direction.UP: True, Direction.DOWN: True, Direction.LEFT: True, Direction.RIGHT: True}

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
        is_move_safe[Direction.LEFT] = False

    elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
        is_move_safe[Direction.RIGHT] = False

    elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
        is_move_safe[Direction.DOWN] = False

    elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
        is_move_safe[Direction.UP] = False

    # Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    if my_head["x"] == board_width - 1:
        is_move_safe[Direction.RIGHT] = False
    
    if my_head["x"] == 0:
        is_move_safe[Direction.LEFT] = False

    if my_head["y"] == board_height - 1:
        is_move_safe[Direction.UP] = False

    if my_head["y"] == 0:
        is_move_safe[Direction.DOWN] = False

    # Step 2 - Prevent your Battlesnake from colliding with itself
    my_body = game_state['you']['body'] # array of coordinates
    right = my_head.copy()
    left = my_head.copy()
    up = my_head.copy()
    down = my_head.copy()

    right["x"] = right["x"] + 1
    left["x"] = left["x"] - 1
    up["y"] = up["y"] + 1
    down["y"] = down["y"] - 1

    if right in my_body:
        is_move_safe[Direction.RIGHT] = False

    if left in my_body:
        is_move_safe[Direction.LEFT] = False

    if up in my_body:
        is_move_safe[Direction.UP] = False
    
    if down in my_body:
        is_move_safe[Direction.DOWN] = False

    # Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    opponents = game_state['board']['snakes']
    for opponent in opponents:
        opponent_body = opponent['body']
        if right in opponent_body:
            is_move_safe[Direction.RIGHT] = False

        if left in opponent_body:
            is_move_safe[Direction.LEFT] = False

        if up in opponent_body:
            is_move_safe[Direction.UP] = False
        
        if down in opponent_body:
            is_move_safe[Direction.DOWN] = False

    # Are there any safe moves left?
    safe_moves: list[Direction] = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    # Choose a random move from the safe ones
    next_move = random.choice(safe_moves)

    # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
    foods = game_state['board']['food']

    # Add the current distance away from the head to each food
    for food in foods:
        food["distance"] = getDistance(my_head, food)

    # sort the foods from closest to furthest
    foods.sort(key=lambda food: food["distance"])

    # get nearest food to head
    nearestFood = foods[0]
    yDirection: Direction | None = None
    xDirection: Direction | None = None

    # determine if it needs to go right, left, or neither
    if nearestFood["x"] > my_head["x"]:
        xDirection = Direction.RIGHT
    elif nearestFood["x"] < my_head["x"]:
        xDirection = Direction.LEFT

    # determine if needs to go up, down, or neither
    if nearestFood["y"] > my_head["y"]:
        yDirection = Direction.UP
    elif nearestFood["y"] < my_head["y"]:
        yDirection = Direction.DOWN

    # update next_move
    if xDirection in safe_moves:
        next_move = xDirection

    if yDirection in safe_moves:
        next_move = yDirection
    
    print(f"MOVE {game_state['turn']}: {next_move.value}")
    return {"move": next_move.value}

def getDistance(coord1: Coordinate, coord2: Coordinate) -> float:
    return math.sqrt((coord2["x"] - coord1["x"]) ** 2 + (coord2["y"] - coord1["y"]) ** 2)

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
