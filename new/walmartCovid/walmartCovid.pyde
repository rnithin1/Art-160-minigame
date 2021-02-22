# Called when program starts, define initial environment properties.
add_library("sound")

from Tile import Tile
from Enemy import Enemy
import random

### GLOBAL VARIABLES ###

# Board Dimensions
boardDimension = 10
tileCount = boardDimension * boardDimension
playerLocation = 0
cartLocation = tileCount - 1
enemies = []

food_ground = [] # What is on the ground
food_held = [] # What the player picked up
food_cart = [] # What food is in the cart

# Setting default images for use. Might be bad convention now, will change later when we have more of the game
# figured out.
playerImage = "cobblestone"
defaultImage = "stone"
cartImage = "cart"

def setup():
    """
    Setup method called before game is initialized.
    """
    # Initial stuff
    size(700, 700) # Increase to make board bigger/smaller.
    global images, tiles, playerLocation, cartLocation, gamestate, enemies
    enemies = []
    images = loadImages()
    tiles = instantiateTiles(images, tileCount, boardDimension)
    playerLocation = 0
    cartLocation = tileCount - 1
    gamestate = 1 # Change to 0 for initial title screen?

    # Sounds
    global sf
    sf = SoundFile(this, "sounds/deposit_cart.wav")

    # Fonts
    global f
    f = createFont("Arial", 32)

    # Food global variables
    global food_ground, food_held, food_cart
    food_ground = [] # What is on the ground
    food_held = [] # What the player picked up
    food_cart = [] # What food is in the cart

    # Win conditions
    global has_lost, has_won, win_groceries, gamestate
    has_lost = False
    has_won = False
    win_groceries = 5

def loadImages():
    """
    Load images into Processing from directory.

    There's two ways of doing this:
        1. We follow the Tilex convention by loading in images of the form: "_.png"
        OR
        2. Explicitly load the images by name. I use convention 2 to reduce obscurity. Adding it to the dictionary means
        we can simply call images["name of image"] to draw it.
    """
    images = {}
    images["cobblestone"] = loadImage("images/cobbleStone.png")
    images["stone"] = loadImage("images/stone.png")
    images["virus"] = loadImage("images/virus.png")
    images["cart"] = loadImage("images/cart.png")
    images["food"] = loadImage("images/food.png")
    return images

def instantiateTiles(images, tileCount, dimension, defaultImage = "stone", startingLocation=0, cartLocation=boardDimension**2-1):
    """
    Takes in the defaultImage to instantiate the tiles to as well as the image array. By default, it
    loads in the files to "stone". The tileSize is simply the width of the board divided by the dimensions of the board.

    The function will return the tileArray in row-major form. The default playerLocation is 0.
    defaultImage -> string representing the image file
    images -> image array
    tileCount -> number of tiles in the board
    dimension -> board dimensions
    """
    tiles = []
    tileSize = width / dimension
    for _ in range(tileCount):
        tileWidth = (_ % dimension) * tileSize
        tileHeight = (_ / dimension) * tileSize
        tiles.append(Tile(tileWidth, tileHeight, images[defaultImage], tileSize))

    # Setting player and cart location.
    tiles[startingLocation].updateImage(images["cobblestone"])
    tiles[cartLocation].updateImage(images["cart"])

    # Setting enemy locations
    for _ in range(7):
        enemies.append(Enemy(random.randint(0, tileCount - 1), 10, 10, images["virus"], random.randint(0, 2), tiles, random.randint(1, 4), images[defaultImage]))

    # Setting food locations
    global food_ground
    for _ in range(2):
        loc = random.randint(0, tileCount - 1)
        tiles[loc].updateImage(images["food"])
        food_ground.append(loc)

    return tiles

def draw():
    """
    Draw is called on every frame and is what updates our game. To do so, it loops through the tiles array and shows each
    tile.
    """
    gamestate = checkGameState()
    if gamestate == 1: # Play state
        for _ in range(len(tiles)):
            tiles[_].showTile()

        for _ in range(len(enemies)):
            enemies[_].move()
            if enemies[_].pos in food_ground:
                food_ground.remove(enemies[_].pos)

        tiles[playerLocation].updateImage(images[playerImage])
        tiles[cartLocation].updateImage(images[cartImage])
        update_food()

        # Groceries list
        global f
        textFont(f, 32)
        fill(0)
        text("Groceries left: " + str(5 - len(food_cart)), 1 * width / 4 + 50, 100)

    if gamestate == 2: # Win state
        textFont(f, 64)
        fill(0)
        text("You win!\n Press 0 to restart", 1 * width / 4 - 50, height / 2)

    if gamestate == 3: # Lose state
        textFont(f, 64)
        fill(0)
        text("You lose!\n Press 0 to restart", 1 * width / 4 - 50, height / 2)

def keyPressed():
    """
    KeyPressed is invoked everytime a button on the keyboard is pressed. We make note of the current player's position
    and update the global playerLocation variable when the key is pressed. Then, we reset the initial location to the default
    image and set the playerLocation tile to the player's image.
    """
    global playerLocation, boardDimension, tileCount, playerImage, defaultImage, gamestate
    previousLocation = playerLocation
    if key == CODED:
        oldPlayerLocation = playerLocation

        if keyCode == RIGHT and check_bounds(playerLocation, playerLocation + 1):
            playerLocation += 1
        elif keyCode == LEFT and check_bounds(playerLocation, playerLocation - 1):
            playerLocation -= 1
        elif keyCode == DOWN and check_bounds(playerLocation, playerLocation + boardDimension):
            playerLocation += boardDimension
        elif keyCode == UP and check_bounds(playerLocation, playerLocation - boardDimension):
            playerLocation -= boardDimension

    ####### Cases #######
    if playerLocation == cartLocation:
        playerLocation = oldPlayerLocation
        if food_held:
            food_cart.append(food_held.pop())
            sf.play()

    if playerLocation in food_ground:
        food_ground.remove(playerLocation)
        food_held.append(playerLocation)

    playerLocation = playerLocation % tileCount
    tiles[previousLocation].updateImage(images[defaultImage])
    tiles[playerLocation].updateImage(images[playerImage])

    # Start the game over
    if key == "0":
        setup()

def update_food():
    if not food_ground:
        for _ in range(2):
            loc = random.randint(0, tileCount - 1)
            tiles[loc].updateImage(images["food"])
            food_ground.append(loc)

def check_bounds(old, new):
    print(new // boardDimension, old // boardDimension)
    if new > tileCount or new < 0:
        return False

    elif new // boardDimension == boardDimension - 1 and old // boardDimension == 0:
        return False

    elif old // boardDimension == boardDimension - 1 and new // boardDimension == 0:
        return False

    elif new % boardDimension == 0 and old % boardDimension == boardDimension - 1:
        return False

    elif old % boardDimension == 0 and new % boardDimension == boardDimension - 1:
        return False
    else:
        return True

def checkGameState():
    winCondition()
    global gamestate
    print(gamestate)
    if has_won:
        gamestate = 2
    elif has_lost:
        gamestate = 3
    else:
        gamestate = 1
    return gamestate

def winCondition():
    global has_won, has_lost
    if win_groceries - len(food_cart) == 0:
        has_won = True

    if playerLocation in [enemy.pos for enemy in enemies]:
        has_lost = True
