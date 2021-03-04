from Enemy import Enemy
from Tile import Tile
import re
import os
import random
import Settings
import time
from Images import IMAGES
add_library("sound")

MENU_STATE = 0
PLAY_STATE = 1
WIN_STATE = 2
LOSE_STATE = 3
TITLE_STATE = 4

### Sounds can't be loaded in a different file ###
SOUND_DIRECTORY_NAME = "sounds/"
FOOD_DEPOSIT_NAME = SOUND_DIRECTORY_NAME + "deposit_cart.wav"
BACKGROUND_SOUNDS_NAME = SOUND_DIRECTORY_NAME + "backgroundSounds.wav"

IMAGE_DIRECTORY_NAME = "images/"
UNWALKABLE_DIRECTORY_NAME = IMAGE_DIRECTORY_NAME + "unwalkable/"
WALKABLE_DIRECTORY_NAME = IMAGE_DIRECTORY_NAME + "walkable/"

FOOD_DIRECTORY_NAME = "food/"

food_types = 6

###                        Walkable vs unwalkable                        ###
### Weird convention: use odd numbers to denote walkable tiles (floors), ###
### and even numbers to denote unwalkable tiles (walls)                  ###


class Game:
    """
    The Game Object keeps track of the general game state.
    This includes: the player, board, enemies, food, and cart.
    """
    # Create Settings variables and pass into the game function on initialization if you want to tweak the parameters.

    def __init__(self, gameSettings, gameWidth=700, gameHeight=700):
        self.gameSettings = gameSettings
        self.Board = Board(
            gameSettings['dimension'], gameWidth, gameSettings['map'])
        self.Player = Player(gameSettings['playerPosition'])
        self.Cart = Cart(gameSettings['cartPosition'])
        self.enemies = []
        self.foodLocations = []
        self.currentState = TITLE_STATE
        self.defaultFont = None
        self.gameWidth = gameWidth
        self.gameHeight = gameHeight
        self.images = None
        self.food_list = []
        self.currentLevel = 0  # The player always starts at level 0.
        self.food_types = food_types
        self.level = gameSettings['level']

    def restart(self):
        print("restart")
        self.Board = Board(
            self.gameSettings['dimension'], self.gameWidth, self.gameSettings['map'])
        self.Player = Player(self.gameSettings['playerPosition'])
        self.Cart = Cart(self.gameSettings['cartPosition'])
        self.enemies = []
        self.foodLocations = []
        self.currentState = PLAY_STATE
        self.food_list = []
        print("intialize base tiles")

        self.Board.initiateBaseTiles(self.images["TILE_IMAGE"])
        print("place player")
        self.Board.placePlayer(self.Player.position,
                               self.images["PLAYER_IMAGE"])

        print("place cart")
        self.Board.placeCart(self.Cart.position, self.images["CART_IMAGE"])

        print("initialize enemies")
        self.initializeEnemies(
            self.images["VIRUS_IMAGE"], self.images["TILE_IMAGE"])
        print("initlaoe foods")
        self.initializeFoods(self.images["FOOD_IMAGE"])

    def nextLevel(self):
        # Temporary restart method
        # After we refactor and add more levels, I'll update this method to increment from 1-10.
        self.gameSettings = getattr(Settings, "LEVEL" + str(self.level + 1))
        self.level = self.gameSettings["level"]
        self.restart()

    def start(self):
        self.Board.initiateBaseTiles(self.images["TILE_IMAGE"])
        self.Board.placePlayer(self.Player.position,
                               self.images["PLAYER_IMAGE"])
        self.Board.placeCart(self.Cart.position, self.images["CART_IMAGE"])
        self.initializeEnemies(
            self.images["VIRUS_IMAGE"], self.images["TILE_IMAGE"])
        self.initializeFoods(self.images["FOOD_IMAGE"])

    def initializeEnemies(self, ENEMY_IMAGE, DEFAULT_IMAGE):
        boardWidth, boardHeight = self.Board.dimension, self.Board.dimension
        for _ in range(self.gameSettings['enemyCount']):
            enemyPosition = random.randint(0, self.Board.tileCount - 1)
            while self.Board.mapValue(enemyPosition) in self.Board.unwalkable:
                enemyPosition = random.randint(0, self.Board.tileCount - 1)
            currentTileSet = self.Board.tiles
            enemyMoveTime = random.randint(3, 8) / 4.0
            print(enemyMoveTime)
            # Enemy objects handle updating the tileset to include their image.
            currentEnemy = Enemy(enemyPosition, boardWidth, boardHeight,
                                 ENEMY_IMAGE, currentTileSet, enemyMoveTime, self)
            self.enemies.append(currentEnemy)

    def initializeFoods(self, FOOD_IMAGE, foodCount=6, food_types=food_types):
        def partition(number):
            answer = set()
            answer.add((number,))
            for x in range(1, number):
                for y in partition(number - x):
                    answer.add(tuple(sorted((x,) + y)))
            return answer

        if not self.food_list:
            self.food_list = random.choice([tup for tup in partition(
                self.gameSettings['winFoodCount']) if len(tup) == food_types])

        leftover = 0
        if self.food_list:
            food_gen = random.choice(
                [tup for tup in partition(foodCount) if len(tup) == food_types])
            for i in range(1, len(self.food_list) + 1):
                for j in range(food_gen[i - 1]):
                    foodLocation = random.randint(0, self.Board.tileCount - 1)
                    while self.Board.mapValue(foodLocation) in self.Board.unwalkable:
                        foodLocation = random.randint(
                            0, self.Board.tileCount - 1)
                    self.Board.tiles[foodLocation].updateImage(
                        loadImage(IMAGE_DIRECTORY_NAME + FOOD_DIRECTORY_NAME + str(i) + ".png"))
                    self.foodLocations.append(foodLocation)
            print("Just made some foods")

        print("Just made some foods")

    def isValidMove(self, previousPosition, nextPosition):
        boardDimension = self.Board.dimension
        tileCount = self.Board.tileCount
        if nextPosition > tileCount or nextPosition < 0:
            return False
        elif nextPosition // boardDimension == boardDimension - 1 and previousPosition // boardDimension == 0:
            return False
        elif previousPosition // boardDimension == boardDimension - 1 and nextPosition // boardDimension == 0:
            return False
        elif nextPosition % boardDimension == 0 and previousPosition % boardDimension == boardDimension - 1:
            return False
        elif previousPosition % boardDimension == 0 and nextPosition % boardDimension == boardDimension - 1:
            return False
        else:
            return True

    def updateGameState(self):
        if self.gameSettings['winFoodCount'] == len(self.Cart.foodHeld):
            self.currentState = WIN_STATE
            output.println("game won in " +
                           str(time.time() - startTime) + " seconds")

        if self.Player.position in [enemy.pos for enemy in self.enemies]:
            self.currentState = LOSE_STATE
            output.println("game lost in " +
                           str(time.time() - startTime) + " seconds")


class Board:
    # The board simply keeps track of visualizing the game.
    def __init__(self, dimension, gameWidth, mapLevel):

        self.radius = 2
        self.dimension = dimension
        self.tileCount = self.dimension**2
        self.width = gameWidth
        self.tileSize = gameWidth / dimension
        self.tiles = []
        self.map_level = mapLevel
        self.walkable = [int(x[:-4])
                         for x in os.listdir(WALKABLE_DIRECTORY_NAME)]
        self.unwalkable = [int(x[:-4])
                           for x in os.listdir(UNWALKABLE_DIRECTORY_NAME)]

    def initiateBaseTiles(self, tileImage):
        self.loadTileFromMap()
        for i in range(self.tileCount):
            tileX = (i % self.dimension) * self.tileSize
            tileY = (i / self.dimension) * self.tileSize
            self.tiles.append(
                Tile(tileX, tileY, self.imageFromMapIndex(i, tileImage), self.tileSize))

    def loadTileFromMap(self):
        f = open("map_{}.txt".format(self.map_level), "r")
        self.map_string = re.sub(r"[\n\t\s]*", "", f.read())
        f.close()

    def mapValue(self, index):
        return int(self.map_string[index])

    def imageFromMapIndex(self, index, tileImage):
        item = self.mapValue(index)
        if item in self.walkable:
            path = loadImage(WALKABLE_DIRECTORY_NAME + str(item) + ".png")
        elif item in self.unwalkable:
            path = loadImage(UNWALKABLE_DIRECTORY_NAME + str(item) + ".png")
        else:
            path = tileImage
        return path

    def placePlayer(self, playerLocation, PLAYER_IMAGE):
        self.tiles[playerLocation].updateImage(PLAYER_IMAGE)

    def placeCart(self, cartLocation, CART_IMAGE):
        self.tiles[cartLocation].updateImage(CART_IMAGE)

    def placeEnemy(self, enemyLocation, ENEMY_IMAGE):
        self.tiles[enemyLocation].updateImage(ENEMY_IMAGE)

    def placeFood(self, foodLocation, FOOD_IMAGE):
        self.tiles[foodLocation].updateImage(FOOD_IMAGE)


class Player:
    def __init__(self, position):
        self.position = position
        self.foodHeld = []


class Cart:
    def __init__(self, position):
        self.position = position
        self.foodHeld = []


# Game initialization
# Change params to game to use non-default settings -> see settings.py and the Game object.
Game = Game(Settings.LEVEL1)


def setup():
    # Sounds
    global FOOD_DEPOSIT
    global BACKGROUND_SOUNDS
    global output
    global startTime

    startTime = time.time()
    output = createWriter("output.txt")
    FOOD_DEPOSIT = SoundFile(this, FOOD_DEPOSIT_NAME)
    BACKGROUND_SOUNDS = SoundFile(this, BACKGROUND_SOUNDS_NAME)

    size(700, 700)

    Game.images = loadImages()
    Game.start()

# Window update method


def draw():
    print(Game.currentState)
    Game.updateGameState()
    currentGameState = Game.currentState
    gameFont = createFont("Arial", 32)
    if Game.currentState == TITLE_STATE:
        display_title_screen()

    else:
        if Game.currentState == PLAY_STATE:
            if (not BACKGROUND_SOUNDS.isPlaying()):
                BACKGROUND_SOUNDS.amp(.3)
                BACKGROUND_SOUNDS.play()
            for tile in Game.Board.tiles:
                tile.showTile()
            for enemy in Game.enemies:
                old_pos = enemy.pos
                enemy.move()
                if enemy.pos in Game.foodLocations:
                    Game.Board.tiles[enemy.pos].updateImage(
                        Game.Board.imageFromMapIndex(enemy.pos, Game.images["TILE_IMAGE"]))
                    Game.foodLocations.remove(enemy.pos)
            for enemy in Game.enemies:
                Game.Board.tiles[enemy.pos].updateImage(
                    Game.Board.imageFromMapIndex(enemy.pos, Game.images["VIRUS_IMAGE"]))
            if Game.Player.foodHeld:
                Game.Board.tiles[Game.Player.position].updateImage(
                    Game.images["PLAYER_BAG_IMAGE"])
            else:
                Game.Board.tiles[Game.Player.position].updateImage(
                    Game.images["PLAYER_IMAGE"])
            Game.Board.tiles[Game.Cart.position].updateImage(
                Game.images["CART_IMAGE"])

            textFont(gameFont, 32)
            fill(0)
            text("Groceries left: " + str(Game.gameSettings['winFoodCount'] - len(
                Game.Cart.foodHeld)), 1 * width / 4 + 50, 100)

            if len(Game.foodLocations) == 0:
                Game.initializeFoods(Game.images["FOOD_IMAGE"])

        if Game.currentState == WIN_STATE:  # Win state
            textFont(gameFont, 64)
            fill(0)
            text("You win!\nPress 1 to play\nnext level",
                 1 * width / 4 - 50, height / 2)

        if Game.currentState == LOSE_STATE:  # Lose state
            textFont(gameFont, 64)
            fill(0)
            text("You lose!\nPress 0 to restart",
                 1*width / 4 - 50, height / 2)


def loadImages():
    loadedImages = {}
    for imageName in IMAGES:
        imageLocation = IMAGES[imageName]
        loadedImages[imageName] = loadImage(imageLocation)
    return loadedImages


def keyPressed():
    if Game.currentState == TITLE_STATE and key == "0":
        Game.currentState = PLAY_STATE

    if (key != CODED):
        output.println("key pressed: " + str(key))
    if key == "q":
        output.println("game played for " +
                       str(time.time()-startTime) + " seconds")
        output.flush()
        output.close()
        exit()
    if key == "0" and Game.currentState == LOSE_STATE:
        Game.restart()
    if key == "1" and Game.currentState == WIN_STATE:
        Game.nextLevel()
    previousPlayerPosition = Game.Player.position
    boardDimension = Game.Board.dimension
    if key == CODED:
        if keyCode == RIGHT and Game.isValidMove(previousPlayerPosition, previousPlayerPosition + 1):
            Game.Player.position += 1
            output.println("key pressed: right")
        elif keyCode == LEFT and Game.isValidMove(previousPlayerPosition, previousPlayerPosition - 1):
            Game.Player.position -= 1
            output.println("key pressed: left")
        elif keyCode == DOWN and Game.isValidMove(previousPlayerPosition, previousPlayerPosition + boardDimension):
            Game.Player.position += boardDimension
            output.println("key pressed: down")
        elif keyCode == UP and Game.isValidMove(previousPlayerPosition, previousPlayerPosition - boardDimension):
            Game.Player.position -= boardDimension
            output.println("key pressed: up")

    if Game.Board.mapValue(Game.Player.position) in Game.Board.unwalkable:
        Game.Player.position = previousPlayerPosition

    if Game.Player.position == Game.Cart.position:
        Game.Player.position = previousPlayerPosition
        if Game.Player.foodHeld:
            Game.Cart.foodHeld.append(Game.Player.foodHeld.pop())
            FOOD_DEPOSIT.play()
            output.println("item placed in cart in " +
                           str(time.time() - startTime) + " seconds")

    if Game.Player.position in Game.foodLocations:
        Game.foodLocations.remove(Game.Player.position)
        Game.Player.foodHeld.append(Game.Player.position)
        output.println("item picked up in " +
                       str(time.time() - startTime) + " seconds")

    Game.Player.position = Game.Player.position % Game.Board.tileCount
    print(Game.Board.mapValue(previousPlayerPosition))

    Game.Board.tiles[previousPlayerPosition].updateImage(
        Game.Board.imageFromMapIndex(previousPlayerPosition, Game.images["TILE_IMAGE"]))
    Game.Board.tiles[Game.Player.position].updateImage(
        Game.images["PLAYER_IMAGE"])


def display_title_screen():
    title = loadImage("images/display/title_screen.png")
    background(title)
    gameFont = createFont("Arial", 32)
    textFont(gameFont, 64)
    fill(0)
    text("Coronavirus\noutbreak in\nWalmart!", 1 * width / 4 - 50, height / 4)
    text("Press 0 to start.", 1 * width / 4 - 50, 3 * height / 4)


def get_radius(r=Game.Board.radius):
    x = Game.Player.position % Game.Board.dimension
    y = Game.Player.position // Game.Board.dimension
    x_bound_l = max(x - r, (x // Game.Board.dimension) * Game.Board.dimension)
    x_bound_r = min(x + r, (x // Game.Board.dimension + 1)
                    * Game.Board.dimension - 1)
    y_bound_u = max(y - r * Game.Board.dimension, y % Game.Board.dimension)
    y_bound_d = min(y + r * Game.Board.dimension,
                    Game.Board.dimension**2 - 1 - (y % Game.Board.dimension))
    #print(int(x_bound_l), int(x_bound_r), int(y_bound_u), int(y_bound_d))

    tiles = []
    coords = []
    for j in range(y - r, y + r + 1):
        for i in range(x_bound_l, x_bound_r + 1, 1):
            c = j * Game.Board.dimension + i
            if c >= 0 and c < Game.Board.dimension**2:
                tiles.append(c)

    for j in range(y - r, y + r + 1):
        temp = []
        for i in range(x - r, x + r + 1, 1):
            if j * Game.Board.dimension + i in tiles:
                temp.append(j * Game.Board.dimension + i)
            else:
                temp.append(-1)
        coords.append(temp)

    for i in range(2*r+1):
        for j in range(2*r+1):
            print(coords[i][j])
    print("W")

    for i in range(2*Game.Board.radius + 1):
        for j in range(2*Game.Board.radius + 1):
            c = j * Game.Board.dimension + i
            if coords[i][j] >= 0:
                tileX = (c % Game.Board.dimension) * Game.Board.tileSize
                tileY = (c / Game.Board.dimension) * Game.Board.tileSize
                Game.Board.tiles[c].setApparentPos(tileX, tileY)

    return tiles, coords
