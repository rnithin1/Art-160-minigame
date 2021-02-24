import time


class Enemy:
    """
    Tile class that retains the x, y, image and size of the tile. 
    """

    def __init__(self, pos, x, y, image, move, tiles, moveTime, defaultImage, Game):
        """
        pos is position, x is width of board, y height of board, is image is the enemy sprite, imgSize is the size
        of this sprite, move is 0, 1, 2 for doesn't move, move vertically, and move right,
        tiles is the array of tiles this enemy is apart of, moveTime is frequency of movement
        """
        self.pos = pos
        self.boardWidth = x
        self.boardLength = y
        self.boardSize = (x*y)
        self.image = image
        self.moveType = move
        self.tiles = tiles
        self.moveTime = moveTime
        self.defaultImage = defaultImage
        self.lastMove = time.time()
        self.tiles[pos].updateImage(self.image)
        self.Game = Game # Reference to the parent game

    def move(self):
        timeSinceMoved = time.time() - self.lastMove
        if self.move == 0 or timeSinceMoved < self.moveTime:
            return
        prevPos = self.pos
        if self.moveType == 1:
            newPos = (self.pos + self.boardLength) % self.boardSize
        else:
            newPos = (self.pos + 1) % self.boardSize
            
        if self.Game.Board.mapValue(newPos) in self.Game.Board.unwalkable:
            return
            
        self.tiles[newPos].updateImage(self.image)
        self.tiles[prevPos].updateImage(self.Game.Board.imageFromMapIndex(prevPos, self.Game.images["TILE_IMAGE"]))
        #self.tiles[prevPos].updateImage(self.defaultImage)
        self.lastMove = time.time()
        self.pos = newPos
