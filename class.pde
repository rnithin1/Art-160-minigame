class Tile {
  int xpos, ypos, count; 
  status.BlockType tilestate;
  Tile(int x, int y, status.BlockType s) {
    xpos = x; 
    ypos = y; 
    tilestate = s;
    count = 0; 
  }
  void show() {
    switch(tilestate) {
    case GRASS: // grass
      image(img[0], xpos, ypos, tileSize, tileSize);
      break;
    case BOXES: // box
      image(img[1], xpos, ypos, tileSize, tileSize);
      break;
    case PLAYER: // player
      image(img[2], xpos, ypos, tileSize, tileSize);
      break;
    case DIRT: // dirt
      image(img[3], xpos, ypos, tileSize, tileSize);
      break;
    case FACING_RIGHT: // facing right
      image(img[4], xpos, ypos, tileSize, tileSize);
      break;
    case FACING_RIGHT_BOX: // facing right box
      image(img[5], xpos, ypos, tileSize, tileSize);
      break;
    case FACING_LEFT: // facing left
      image(img[6], xpos, ypos, tileSize, tileSize);
      break;
    case FACING_LEFT_BOX: // facing left box
      image(img[7], xpos, ypos, tileSize, tileSize);
      break;
    case BOMB: // bomb
      image(img[8], xpos, ypos, tileSize, tileSize);
      break;
    case TWO_BOXES_LEFT: 
      image(img[9], xpos, ypos, tileSize, tileSize);
      break;
    case TWO_BOXES_RIGHT: 
      image(img[10], xpos, ypos, tileSize, tileSize);
      break;
    case THREE_BOXES_LEFT: 
      image(img[11], xpos, ypos, tileSize, tileSize);
      break;
    case THREE_BOXES_MIDDLE: 
      image(img[12], xpos, ypos, tileSize, tileSize);
      break;
    case THREE_BOXES_RIGHT: 
      image(img[13], xpos, ypos, tileSize, tileSize);
      break;
    }
  }
}
