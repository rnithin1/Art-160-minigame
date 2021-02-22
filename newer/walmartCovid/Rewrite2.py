add_library("sound")
from Tile import Tile 
from Enemy import Enemy 
import random

MENU_STATE = 0
PLAY_STATE = 1
WIN_STATE = 2
LOSE_STATE = 3

DIRECTORY_NAME = "sounds/"
FOOD_DEPOSIT_NAME = DIRECTORY_NAME + "deposit_cart.wav"
FOOD_DEPOSIT = SoundFile(this, FOOD_DEPOSIT_NAME)

DIRECTORY_NAME = "images/"

PLAYER_IMAGE_NAME = DIRECTORY_NAME + "cobbleStone.png" 
TILE_IMAGE_NAME = DIRECTORY_NAME + "stone.png" 
VIRUS_IMAGE_NAME = DIRECTORY_NAME + "virus.png" 
CART_IMAGE_NAME = DIRECTORY_NAME + "cart.png"
FOOD_IMAGE_NAME = DIRECTORY_NAME + "food.png"

PLAYER_IMAGE = loadImage(PLAYER_IMAGE_NAME) 
TILE_IMAGE = loadImage(TILE_IMAGE_NAME)
VIRUS_IMAGE = loadImage(VIRUS_IMAGE_NAME)
CART_IMAGE = loadImage(CART_IMAGE_NAME)
FOOD_IMAGE = loadImage(FOOD_IMAGE_NAME)

DEFAULT = {
        "dimension" : 10,
        "playerPosition" : 0,
        "cartPosition" : 9,                       
        "enemyCount" : 5, 
        "foodCount" : 5,
        "winFoodCount" : 5
        } 

class Game:
    """
    The Game Object keeps track of the general game state.
    This includes: the player, board, enemies, food, and cart.
    """
    # Create Settings variables and pass into the game function on initialization if you want to tweak the parameters.
    def __init__(self, gameSettings = DEFAULT, gameWidth = 700, gameHeight = 700):
        self.gameSettings = gameSettings
        self.Board = Board(gameSettings['dimension'], gameWidth)
        self.Player = Player(gameSettings['playerPosition'])
        self.Cart = Cart(gameSettings['cartPosition'])
        self.enemies = []
        self.foodLocations = []
        self.currentState = PLAY_STATE
        self.defaultFont = None
        self.gameWidth = gameWidth
        self.gameHeight = gameHeight

    def start(self):
        self.Board.initiateBaseTiles()
        self.Board.placePlayer(self.Player.position)
        self.Board.placeCart(self.Cart.position)
        self.initializeEnemies()
        self.initializeFoods()

    def initializeEnemies(self):
        boardWidth, boardHeight = self.Board.dimension, self.Board.dimension
        enemyImage = VIRUS_IMAGE
        defaultImage = TILE_IMAGE

        for _ in range(self.gameSettings['enemyCount']):
            enemyPosition = random.randint(0, self.Board.tileCount - 1)
            enemyMoveType = random.randint(0, 2)
            currentTileSet = self.Board.tiles
            enemyMoveTime = random.randint(1, 4)
            # Enemy objects handle updating the tileset to include their image.
            currentEnemy = Enemy(enemyPosition, boardWidth, boardHeight, enemyImage, enemyMoveType, currentTileSet, enemyMoveTime, defaultImage)
            self.enemies.append(currentEnemy)

    def initializeFoods(self, foodCount = 3):
        for _ in range(foodCount):
            foodLocation = random.randint(0, self.Board.tileCount - 1)
            self.Board.tiles[foodLocation].updateImage(FOOD_IMAGE)
            self.foodLocations.append(foodLocation)


    def isValidMove(self, previousPosition, nextPosition):
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
        if self.Player.position in [enemy.pos for enemy in self.enemies]:
            self.currentState = LOSE_STATE

class Board:
    # The board simply keeps track of visualizing the game.
    def __init__(self, dimension, gameWidth):

        self.dimension = dimension
        self.tileCount = self.dimension**2
        self.width = gameWidth
        self.tileSize = gameWidth / dimension
        self.tiles = []

    def initiateBaseTiles(self):
        for _ in range(self.tileCount):
            tileX = (_ % self.dimension) * self.tileSize
            tileY = (_ / self.dimension) * self.tileSize
            self.tiles.append(Tile(tileX, tileY, TILE_IMAGE, self.tileSize))

    def placePlayer(self, playerLocation):
        self.tiles[playerLocation].updateImage(PLAYER_IMAGE)

    def placeCart(self, cartLocation):
        self.tiles[cartLocation].updateImage(CART_IMAGE)

    def placeEnemy(self, enemyLocation):
        self.tiles[enemyLocation].updateImage(Images.ENEMY_IMAGE)

    def placeFood(self, foodLocation):
        self.tiles[foodLocation].updateImage(Images.FOOD_IMAGE)

class Player:
    def __init__(self, position):
        self.position = position
        self.foodHeld = []

class Cart:
    def __init__(self, position):
        self.position = position
        self.foodHeld = []

# Game initialization
# Change params to game to use non-default settings -> see settings.py and the Game object. By default, it uses the defaultSettings.
Game = Game()
def setup():
    size(700, 700)
    Game.start()

# Window update method
def draw():
    currentGameState = Game.currentState
    gameFont = createFont("Arial", 32)
    # Game.updateGameState()
    if Game.currentState == PLAY_STATE:
        pass 
        for tile in Game.Board.tiles:
            image(TILE_IMAGE, tile.x, tile.y, tile.tileSize, tile.tileSize)
        # for enemy in Game.enemies:
        #         enemy.move()
        #         if enemy.pos in Game.foodLocations:
        #             Game.foodLocations.remove(enemy.pos)

        # Game.Board.tiles[Game.Player.position].updateImage(Images.PLAYER_IMAGE)
        # Game.Board.tiles[Game.Cart.position].updateImage(Images.CART_IMAGE)
        # if len(Game.foodLocations) == 0:
        #     Game.initializeFoods(2)

        # textFont(font, 32)
        # fill(0)
        # text("Groceries left: " + str(Game.gameSettings['winFoodCount'] - len(Game.Cart.foodHeld)), 1 * Game.gameWidth / 4 + 50, 100)

    # if self.currentState == WIN_STATE: # Win state
    #     textFont(font, 64)
    #     fill(0)
    #     text("You win!\n Press 0 to restart", 1 * Game.gameWidth / 4 - 50, Game.gameHeight / 2)

    # if self.currentState == LOSE_STATE: # Lose state
    #     textFont(font, 64)
    #     fill(0)
    #     text("You lose!\n Press 0 to restart", 1 * Game.gameWidth / 4 - 50, Game.gameHeight / 2)

def keyPressed():
    previousPlayerPosition = Game.Player.position
    if key == CODED:
        if keyCode == RIGHT and Game.isValidMove(previousPlayerPosition, previousPlayerPosition + 1):
            Game.Player.position += 1
        elif keyCode == LEFT and Game.isValidMove(playerLocation, previousPlayerPosition - 1):
            Game.Player.position -= 1
        elif keyCode == DOWN and Game.isValidMove(previousPlayerPosition, previousPlayerPosition + boardDimension):
            Game.Player.position += boardDimension
        elif keyCode == UP and Game.isValidMove(previousPlayerPosition, previousPlayerPosition - boardDimension):
            Game.Player.position -= boardDimension

    if Game.Player.position == Game.Cart.position:
        Game.Player.position = previousPlayerPosition
        if Game.Player.foodHeld:
            Game.Cart.foodHeld.append(Game.Player.foodHeld.pop())
            Sounds.FOOD_DEPOSIT.play()

    if Game.Player.position in Game.foodLocations:
        Game.foodLocations.remove(Game.Player.position)
        Game.Player.foodHeld.append(Game.Player.position)

    Game.Player.position = Game.Player.position % Game.Board.tileCount
    Game.Board.tiles[previousPlayerLocation].updateImage(Images.DEFAULT_IMAGE)
    Game.Board.tiles[Game.Player.position].updateImage(Images.PLAYER_IMAGE)
    if key == "0": setup()
