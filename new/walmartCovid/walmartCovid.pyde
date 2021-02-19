# Called when program starts, define initial environment properties. 
from Tile import Tile

### GLOBAL VARIABLES ### 

# Board Dimensions 
boardDimension = 10
tileCount = boardDimension * boardDimension
playerLocation = 0 

# Setting default images for use. Might be bad convention now, will change later when we have more of the game 
# figured out. 
playerImage = "cobblestone"
defaultImage = "stone" 


def setup(): 
    """
    Setup method called before game is initialized.  
    """
    size(700, 700) # Increase to make board bigger/smaller. 
    global images, tiles
    images = loadImages()
    tiles = instantiateTiles(images, tileCount, boardDimension) 
    
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
    return images 

def instantiateTiles(images, tileCount, dimension, defaultImage = "stone", startingLocation = 0): 
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
    
    # Setting player location. 
    tiles[startingLocation].updateImage(images["cobblestone"]) 
    return tiles 
         
    
        
    
def draw(): 
    """
    Draw is called on every frame and is what updates our game. To do so, it loops through the tiles array and shows each 
    tile. 
    """
    for _ in range(len(tiles)):
        tiles[_].showTile()  
        
def keyPressed():
    """
    KeyPressed is invoked everytime a button on the keyboard is pressed. We make note of the current player's position 
    and update the global playerLocation variable when the key is pressed. Then, we reset the initial location to the default 
    image and set the playerLocation tile to the player's image. 
    """
    global playerLocation, boardDimension, tileCount, playerImage, defaultImage
    previousLocation = playerLocation 
    if key == CODED:
        if keyCode == RIGHT: playerLocation += 1 
        elif keyCode == LEFT: playerLocation -= 1
        elif keyCode == DOWN: playerLocation += boardDimension 
        elif keyCode == UP: playerLocation -= boardDimension 
        
    playerLocation = playerLocation % tileCount
    tiles[previousLocation].updateImage(images[defaultImage])
    tiles[playerLocation].updateImage(images[playerImage]) 
    

    
    
