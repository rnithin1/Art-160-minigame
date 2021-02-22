class Tile: 
    """
    Tile class that retains the x, y, image and size of the tile. 
    """
    def __init__(self, x, y, image, tileSize): 
        self.x = x 
        self.y = y 
        self.image = image
        self.tileSize = tileSize 
        
    def updateImage(self, newImage):
        """
        Changes the image located at the current tile to the new image. 
        """
        self.image = newImage 
        
    def showTile(self):
        """
        Shows the tile on the drawing board. 
        """
        if type(self.image) is int:
            return 
        else: 
            image(self.image, self.x, self.y, self.tileSize, self.tileSize) 
        
    
