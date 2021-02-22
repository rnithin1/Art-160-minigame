add_library("sound")
from Tile import Tile 
from Enemy import Enemy 
from Images import IMAGES
import random

MENU_STATE = 0
PLAY_STATE = 1
WIN_STATE = 2
LOSE_STATE = 3

DIRECTORY_NAME = "sounds/"
FOOD_DEPOSIT_NAME = DIRECTORY_NAME + "deposit_cart.wav"
FOOD_DEPOSIT = SoundFile(this, FOOD_DEPOSIT_NAME)


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
        self.images = None 

    def restart(self): 
        self.Board = Board(self.gameSettings['dimension'], self.gameWidth)
        self.Player = Player(self.gameSettings['playerPosition'])
        self.Cart = Cart(self.gameSettings['cartPosition'])
        self.enemies = []
        self.foodLocations = []
        self.currentState = PLAY_STATE
        
        self.Board.initiateBaseTiles(self.images["TILE_IMAGE"])
        self.Board.placePlayer(self.Player.position, self.images["PLAYER_IMAGE"])
        self.Board.placeCart(self.Cart.position, self.images["CART_IMAGE"])
        self.initializeEnemies(self.images["VIRUS_IMAGE"], self.images["TILE_IMAGE"])
        self.initializeFoods(self.images["FOOD_IMAGE"])
        
    def start(self):
        self.Board.initiateBaseTiles(self.images["TILE_IMAGE"])
        self.Board.placePlayer(self.Player.position, self.images["PLAYER_IMAGE"])
        self.Board.placeCart(self.Cart.position, self.images["CART_IMAGE"])
        self.initializeEnemies(self.images["VIRUS_IMAGE"], self.images["TILE_IMAGE"])
        self.initializeFoods(self.images["FOOD_IMAGE"])

    def initializeEnemies(self, ENEMY_IMAGE, DEFAULT_IMAGE):
        boardWidth, boardHeight = self.Board.dimension, self.Board.dimension
        for _ in range(self.gameSettings['enemyCount']):
            enemyPosition = random.randint(0, self.Board.tileCount - 1)
            enemyMoveType = random.randint(0, 2)
            currentTileSet = self.Board.tiles
            enemyMoveTime = random.randint(1, 4)
            # Enemy objects handle updating the tileset to include their image.
            currentEnemy = Enemy(enemyPosition, boardWidth, boardHeight, ENEMY_IMAGE, enemyMoveType, currentTileSet, enemyMoveTime, DEFAULT_IMAGE)
            self.enemies.append(currentEnemy)

    def initializeFoods(self, FOOD_IMAGE, foodCount = 3):
        for _ in range(foodCount):
            foodLocation = random.randint(0, self.Board.tileCount - 1)
            self.Board.tiles[foodLocation].updateImage(FOOD_IMAGE)
            self.foodLocations.append(foodLocation)


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

    def initiateBaseTiles(self, tileImage):
        for _ in range(self.tileCount):
            tileX = (_ % self.dimension) * self.tileSize
            tileY = (_ / self.dimension) * self.tileSize
            self.tiles.append(Tile(tileX, tileY, tileImage, self.tileSize))

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
# Change params to game to use non-default settings -> see settings.py and the Game object. By default, it uses the defaultSettings.
Game = Game()
def setup():
    size(700, 700)
    Game.images = loadImages()
    Game.start()

# Window update method
def draw():
    Game.updateGameState()
    currentGameState = Game.currentState
    gameFont = createFont("Arial", 32)
    if Game.currentState == PLAY_STATE:
        for tile in Game.Board.tiles:
            tile.showTile()
            
        for enemy in Game.enemies:
                enemy.move()
                if enemy.pos in Game.foodLocations:
                    Game.foodLocations.remove(enemy.pos)

        Game.Board.tiles[Game.Player.position].updateImage(Game.images["PLAYER_IMAGE"])
        Game.Board.tiles[Game.Cart.position].updateImage(Game.images["CART_IMAGE"])
        if len(Game.foodLocations) == 0:
            Game.initializeFoods(2)

        textFont(gameFont, 32)
        fill(0)
        text("Groceries left: " + str(Game.gameSettings['winFoodCount'] - len(Game.Cart.foodHeld)), 1 * width / 4 + 50, 100)

    if Game.currentState == WIN_STATE: # Win state
        textFont(gameFont, 64)
        fill(0)
        text("You win!\n Press 0 to restart", 1 * width / 4 - 50, height / 2)

    if Game.currentState == LOSE_STATE: # Lose state
        textFont(gameFont, 64)
        fill(0)
        text("You lose!\n Press 0 to restart", 1 * width / 4 - 50, height / 2)
        
def loadImages():
    loadedImages = {} 
    for imageName in IMAGES: 
        imageLocation = IMAGES[imageName] 
        loadedImages[imageName] = loadImage(imageLocation) 
    return loadedImages

def keyPressed():
    if key == "0": 
        Game.restart()
    previousPlayerPosition = Game.Player.position
    boardDimension = Game.Board.dimension
    if key == CODED:
        if keyCode == RIGHT and Game.isValidMove(previousPlayerPosition, previousPlayerPosition + 1):
            Game.Player.position += 1
        elif keyCode == LEFT and Game.isValidMove(previousPlayerPosition, previousPlayerPosition - 1):
            Game.Player.position -= 1
        elif keyCode == DOWN and Game.isValidMove(previousPlayerPosition, previousPlayerPosition + boardDimension):
            Game.Player.position += boardDimension
        elif keyCode == UP and Game.isValidMove(previousPlayerPosition, previousPlayerPosition - boardDimension):
            Game.Player.position -= boardDimension

    if Game.Player.position == Game.Cart.position:
        Game.Player.position = previousPlayerPosition
        if Game.Player.foodHeld:
            Game.Cart.foodHeld.append(Game.Player.foodHeld.pop())
            FOOD_DEPOSIT.play()

    if Game.Player.position in Game.foodLocations:
        Game.foodLocations.remove(Game.Player.position)
        Game.Player.foodHeld.append(Game.Player.position)
        
    if len(Game.foodLocations) == 0: Game.initializeFoods(Game.images["FOOD_IMAGE"])

    Game.Player.position = Game.Player.position % Game.Board.tileCount
    Game.Board.tiles[previousPlayerPosition].updateImage(Game.images["TILE_IMAGE"])
    Game.Board.tiles[Game.Player.position].updateImage(Game.images["PLAYER_IMAGE"])
