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
import copy
from floodFill import floodFill
from scoreMove import scoreMove

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
    snakes: list[Snake] # including self

class Game(TypedDict):
    id: str
    turn: int
    board: Board
    you: Snake

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
    moveOptions = {
        Direction.UP: {"isSafe": True, "ffScore": 0, "foodDirection": False, "calculatedScore": 0}, 
        Direction.DOWN: {"isSafe": True, "ffScore": 0, "foodDirection": False, "calculatedScore": 0}, 
        Direction.LEFT: {"isSafe": True, "ffScore": 0, "foodDirection": False, "calculatedScore": 0}, 
        Direction.RIGHT: {"isSafe": True, "ffScore": 0, "foodDirection": False, "calculatedScore": 0}, 
    }

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
        is_move_safe[Direction.LEFT] = False
        moveOptions[Direction.LEFT]["isSafe"] = False

    elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
        is_move_safe[Direction.RIGHT] = False
        moveOptions[Direction.RIGHT]["isSafe"] = False

    elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
        is_move_safe[Direction.DOWN] = False
        moveOptions[Direction.DOWN]["isSafe"] = False

    elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
        is_move_safe[Direction.UP] = False
        moveOptions[Direction.UP]["isSafe"] = False

    # Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    if my_head["x"] == board_width - 1:
        is_move_safe[Direction.RIGHT] = False
        moveOptions[Direction.RIGHT]["isSafe"] = False
    
    if my_head["x"] == 0:
        is_move_safe[Direction.LEFT] = False
        moveOptions[Direction.LEFT]["isSafe"] = False

    if my_head["y"] == board_height - 1:
        is_move_safe[Direction.UP] = False
        moveOptions[Direction.UP]["isSafe"] = False

    if my_head["y"] == 0:
        is_move_safe[Direction.DOWN] = False
        moveOptions[Direction.DOWN]["isSafe"] = False

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
        moveOptions[Direction.RIGHT]["isSafe"] = False

    if left in my_body:
        is_move_safe[Direction.LEFT] = False
        moveOptions[Direction.LEFT]["isSafe"] = False

    if up in my_body:
        is_move_safe[Direction.UP] = False
        moveOptions[Direction.UP]["isSafe"] = False
    
    if down in my_body:
        is_move_safe[Direction.DOWN] = False
        moveOptions[Direction.DOWN]["isSafe"] = False

    # Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    opponents = [
        snake
        for snake in game_state['board']['snakes']
        if snake["id"] != game_state["you"]["id"]
    ]

    for opponent in opponents:
        opponent_body = opponent['body']
        if right in opponent_body:
            is_move_safe[Direction.RIGHT] = False
            moveOptions[Direction.RIGHT]["isSafe"] = False

        if left in opponent_body:
            is_move_safe[Direction.LEFT] = False
            moveOptions[Direction.LEFT]["isSafe"] = False

        if up in opponent_body:
            is_move_safe[Direction.UP] = False
            moveOptions[Direction.UP]["isSafe"] = False

        if down in opponent_body:
            is_move_safe[Direction.DOWN] = False
            moveOptions[Direction.DOWN]["isSafe"] = False

    # Are there any safe moves left?
    safe_moves: list[Direction] = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}
    
    # Determine Flood Fill score for each direction
    grid = populateGrid(
        game_state["board"]["height"], 
        game_state["board"]["width"], 
        game_state["you"]["body"], 
        [opponent["body"] for opponent in opponents])
    
    bestDirection = safe_moves[0]
    maxScore = 0
    for direction in Direction:
        score = 0
        if direction in safe_moves:
            match direction:
                case Direction.RIGHT:
                    score = floodFill(copy.deepcopy(grid), my_head["x"] + 1, my_head["y"])
                    moveOptions[Direction.RIGHT]["ffScore"] = score
                    # print(f"RIGHT score: {score} | {moveOptions[Direction.RIGHT]["ffScore"]}")
                case Direction.LEFT:
                    score = floodFill(copy.deepcopy(grid), my_head["x"] - 1, my_head["y"])
                    moveOptions[Direction.LEFT]["ffScore"] = score
                    # print(f"LEFT score: {score} | {moveOptions[Direction.LEFT]["ffScore"]}")
                case Direction.UP:
                    score = floodFill(copy.deepcopy(grid), my_head["x"], my_head["y"] + 1)
                    moveOptions[Direction.UP]["ffScore"] = score
                    # print(f"UP score: {score} | {moveOptions[Direction.UP]["ffScore"]}")
                case _: # Direction.DOWN:
                    score = floodFill(copy.deepcopy(grid), my_head["x"], my_head["y"] - 1)
                    moveOptions[Direction.DOWN]["ffScore"] = score
                    # print(f"DOWN score: {score} | {moveOptions[Direction.DOWN]["ffScore"]}")
        else:
            score = -1

        if score > maxScore:
            maxScore = score
            bestDirection = direction
                    

    # Choose a random move from the safe ones
    next_move = random.choice(safe_moves)

    if bestDirection:
        next_move = bestDirection

    # Step 4 - Move towards food instead of random, to regain health and survive longer
    foods = game_state['board']['food']

    # Add the current distance away from the head to each food
    for food in foods:
        food["distance"] = getDistance(my_head, food)
        food["iAmClosest"] = iAmClosest(my_head, food, (opponent["head"] for opponent in opponents))

    # sort the foods from closest to furthest
    foods.sort(key=lambda food: food["distance"])

    # filter foods where I am closest
    iAmClosestFoods = [
        food 
        for food in foods 
        if food["iAmClosest"]
    ]


    # get nearest food to head
    nearestFood = foods[0]

    if len(iAmClosestFoods) > 0:
        nearestFood = iAmClosestFoods[0]

    yFoodDirection: Direction | None = None
    xFoodDirection: Direction | None = None

    # determine if it needs to go right, left, or neither
    if nearestFood["x"] > my_head["x"]:
        xFoodDirection = Direction.RIGHT
        moveOptions[Direction.RIGHT]["foodDirection"] = True
    elif nearestFood["x"] < my_head["x"]:
        xFoodDirection = Direction.LEFT
        moveOptions[Direction.LEFT]["foodDirection"] = True

    # determine if needs to go up, down, or neither
    if nearestFood["y"] > my_head["y"]:
        yFoodDirection = Direction.UP
        moveOptions[Direction.UP]["foodDirection"] = True
    elif nearestFood["y"] < my_head["y"]:
        yFoodDirection = Direction.DOWN
        moveOptions[Direction.DOWN]["foodDirection"] = True

    # update next_move
    if xFoodDirection in safe_moves:
        next_move = xFoodDirection

    if yFoodDirection in safe_moves:
        next_move = yFoodDirection

    # Calculate scores for each move
    boardArea = board_height * board_width
    for direction, inputs in moveOptions.items():
        moveOptions[direction]["calculatedScore"] = scoreMove(inputs, boardArea)
    # print(f"moveOptions: {moveOptions}")

    calculatedBestMove = max(
        moveOptions,
        key=lambda direction: moveOptions[direction]["calculatedScore"]
    )
    print(f"MOVE {game_state['turn']}: {calculatedBestMove.value}")
    return {"move": calculatedBestMove.value}
    
    print(f"MOVE {game_state['turn']}: {next_move.value}")
    return {"move": next_move.value}

def populateGrid(height: int, width: int, myBody: list[Coordinate], opponentBodies: list[list[Coordinate]]) -> list[list[bool]]:
    grid = [[False for _ in range(height)] for _ in range(width)]
    for coord in myBody:
        grid[coord["x"]][coord["y"]] = True

    for opponentBody in opponentBodies:
        for coord in opponentBody:
            grid[coord["x"]][coord["y"]] = True

    return grid

def getDistance(coord1: Coordinate, coord2: Coordinate) -> float:
    return math.sqrt((coord2["x"] - coord1["x"]) ** 2 + (coord2["y"] - coord1["y"]) ** 2)

def iAmClosest(my_head: Coordinate, food: Coordinate, opponentHeads: list[Coordinate]) -> bool:
    myDistance = getDistance(my_head, food)
    iAmClosest = True
    for opponentHead in opponentHeads:
        if getDistance(opponentHead, food) <= myDistance:
            iAmClosest = False
        
    return iAmClosest

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
