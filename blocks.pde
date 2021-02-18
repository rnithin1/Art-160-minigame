import processing.sound.*;
import java.util.Collections;

status.BlockType GRASS = status.BlockType.GRASS;
status.BlockType BOXES = status.BlockType.BOXES;
status.BlockType PLAYER = status.BlockType.PLAYER;
status.BlockType DIRT = status.BlockType.DIRT;
status.BlockType FACING_RIGHT = status.BlockType.FACING_RIGHT;
status.BlockType FACING_RIGHT_BOX = status.BlockType.FACING_RIGHT_BOX;
status.BlockType FACING_LEFT = status.BlockType.FACING_LEFT;
status.BlockType FACING_LEFT_BOX = status.BlockType.FACING_LEFT_BOX;
status.BlockType BOMB = status.BlockType.BOMB;
status.BlockType TWO_BOXES_LEFT = status.BlockType.TWO_BOXES_LEFT;
status.BlockType TWO_BOXES_RIGHT = status.BlockType.TWO_BOXES_RIGHT;
status.BlockType THREE_BOXES_LEFT = status.BlockType.THREE_BOXES_LEFT;
status.BlockType THREE_BOXES_MIDDLE = status.BlockType.THREE_BOXES_MIDDLE;
status.BlockType THREE_BOXES_RIGHT = status.BlockType.THREE_BOXES_RIGHT;

int dimension = 20;
int tileCount = dimension*dimension; 
int tileSize = 0; 
int stateCount = 14;
int permutations = int(pow(2, tileCount)); 
int gamestate = 0; 
int replayvalue = 0; 
PFont Freight; 
int winTile = int (random(tileCount));
int pressCount = 0; 
int currTile = tileCount / 2;
int isHolding = 0;
int total_black = 5;
int curr_black = total_black;
int playerspawn = dimension + 5;
int has_won = 0;
int has_lost = 0;
int timer;
int wait = 50; // seconds
int is_stunned = 0;
int stun_timer;
int stun_wait = 2; // seconds
int total_bomb = 0;
int current_bomb = 0;
int last_box_placed;
int cooldown = 1;

int[] partition;
int partition_index;

status.BlockType playerstate = FACING_RIGHT;

SoundFile win;
SoundFile lose;
SoundFile pickup;
SoundFile drop;
SoundFile bomb;
PImage img[] = new PImage[stateCount]; 
PImage back;
Tile t[] = new Tile[tileCount]; 

void setup() {
  /********* Set up sound files and variables *********/
  back = loadImage("fortress.png");
  total_bomb = 0;
  curr_black = total_black;
  isHolding = 0;
  partition_index = 0;
  win = new SoundFile(this, "win.mp3");
  lose = new SoundFile(this, "lose.mp3");
  pickup = new SoundFile(this, "box_pickup.wav");
  drop = new SoundFile(this, "box_drop.wav");
  bomb = new SoundFile(this, "bomb.wav");
  playerstate = FACING_RIGHT;
  Freight = loadFont("FreightDispProBlack-Regular-60.vlw"); 
  println ("possible permutations: = "+permutations); 
  println ("winning tile " + winTile);
  size(760, 760);
  tileSize = width/dimension;
  gamestate = 0;
  gameState();
  
  setup_1();
}

void setup_1() {
  
  /* Set up basic field */
  
  for (int i = 0; i < stateCount; i++) {
    img[i] = loadImage(i+".png");
  }
  for (int j = 0; j < tileCount; j++) {
    t[j] = new Tile((j%dimension)*tileSize, (j/dimension)*tileSize, GRASS);
  }
  
  /********* Get partition of dimension_size to create blocks *********/
  
  ArrayList<int[]> possible_partitions = getAllUniqueParts(dimension);
  Collections.shuffle(possible_partitions);
  partition = possible_partitions.get(0);
  IntList to_shuffle = new IntList(partition.length);
  for (int i = 0; i < partition.length; i++) {
    to_shuffle.append(partition[i]);
  }
  to_shuffle.shuffle(this);
  println(to_shuffle);
  partition = to_shuffle.array();
  
  /********* Figure out where to place boxes *********/
  
  IntList il = IntList.fromRange(dimension + 1, tileCount - 3 * dimension);
  il.shuffle(this);
  for (int i = 1; i < il.size(); i++) {
    for (int j = i; j < il.size(); j++) {
      il.set(j, il.get(j) + 3);//(int(random(1, 3)) * 3));
    }
  }
  
  partition_index = min(partition.length, partition_index + total_black);
  for (int i = 0; i < partition_index; i++) {
    if (partition[i] == 1) { // single box
      t[il.get(i)].tilestate = BOXES;
    } else if (partition[i] == 2) { // double box
      if ((il.get(i) + 1) % dimension == 0) {
        t[il.get(i) - 1].tilestate = TWO_BOXES_LEFT;
        t[il.get(i)].tilestate = TWO_BOXES_RIGHT;
      } else {
        t[il.get(i)].tilestate = TWO_BOXES_LEFT;
        t[il.get(i) + 1].tilestate = TWO_BOXES_RIGHT;
      }
    } else if (partition[i] == 3) { // treble box
      if ((il.get(i) + 1) % dimension == 0) {
        t[il.get(i) - 2].tilestate = THREE_BOXES_LEFT;
        t[il.get(i) - 1].tilestate = THREE_BOXES_MIDDLE;
        t[il.get(i)].tilestate = THREE_BOXES_RIGHT;
      } else {
        t[il.get(i) - 1].tilestate = THREE_BOXES_LEFT;
        t[il.get(i)].tilestate = THREE_BOXES_MIDDLE;
        t[il.get(i) + 1].tilestate = THREE_BOXES_RIGHT;
      }
    }
  }
  
  currTile = int(random(dimension + 1, tileCount - dimension));
  while (t[currTile].tilestate != GRASS) currTile = int(random(dimension + 1, tileCount - dimension));
  t[currTile].tilestate = playerstate;
  
  /********* Set top row to be dirt *********/
  
  for (int i = 0; i < dimension; i++) {
    t[i].tilestate = DIRT; 
  }
  //for (int i = 0; i < dimension - 1; i++) {
  //  t[i].tilestate = 1; 
  //}
  
}

void draw() { 
  if (gamestate == 0) {
    background(back);
  } else {
    background(0);
    for (int s = 0; s < tileCount; s++) {
      t[s].show();
    }
    wipe();
    if (curr_black == 1) {
      total_bomb++;
  
      IntList il = IntList.fromRange(dimension + 1, tileCount - 3 * dimension);
      il.shuffle(this);
      for (int i = 1; i < il.size(); i++) {
        for (int j = i; j < il.size(); j++) {
          il.set(j, il.get(j) + 3); //(int(random(1, 3)) * 3));
        }
      }
      int partition_index_new = min(partition.length, partition_index + total_black - 1);
      for (int i = partition_index; i < partition_index_new; i++) {
        if (partition[i] == 1) { // single box
          t[il.get(i)].tilestate = BOXES;
        } else if (partition[i] == 2) { // double box
          if ((il.get(i) + 1) % dimension == 0) {
            t[il.get(i) - 1].tilestate = TWO_BOXES_LEFT;
            t[il.get(i)].tilestate = TWO_BOXES_RIGHT;
          } else {
            t[il.get(i)].tilestate = TWO_BOXES_LEFT;
            t[il.get(i) + 1].tilestate = TWO_BOXES_RIGHT;
          }
        } else if (partition[i] == 3) { // treble box
          if ((il.get(i) + 1) % dimension == 0) {
            t[il.get(i) - 2].tilestate = THREE_BOXES_LEFT;
            t[il.get(i) - 1].tilestate = THREE_BOXES_MIDDLE;
            t[il.get(i)].tilestate = THREE_BOXES_RIGHT;
          } else {
            t[il.get(i) - 1].tilestate = THREE_BOXES_LEFT;
            t[il.get(i)].tilestate = THREE_BOXES_MIDDLE;
            t[il.get(i) + 1].tilestate = THREE_BOXES_RIGHT;
          }
        }
      }
      partition_index = partition_index_new;
      
      current_bomb = total_bomb;
      while (current_bomb > 0) {
        int tile = int(random(2 * dimension + 1, tileCount - dimension));
        if (t[tile].tilestate == GRASS) {
          t[tile].tilestate = BOMB;
          current_bomb--;
        }
      }
      curr_black = total_black;
      
    }
    if (gamestate == 1) {
      textFont(Freight); 
      textAlign(CENTER);
      fill(0); 
      text ("Time remaining: " + (wait - (millis() - timer) / 1000), width/2, (7*height)/8); 
      if ((wait - (millis() - timer) / 1000) == 0) {
        gamestate = 3; 
        has_lost = 1;
      }
    }
    if (is_stunned == 1) {
      if (stun_wait - (millis() - stun_timer) / 1000 < 0) {
        is_stunned = 0;
      }
    }
    
  }
  gameState();
}
//interaction
void mousePressed() {

}

void gameStateCheck() {
  //win condition 
  for (int i = 0; i < dimension; i++) {
    if (!(t[i].tilestate == BOXES 
              || t[i].tilestate == TWO_BOXES_LEFT 
              || t[i].tilestate == TWO_BOXES_RIGHT 
              || t[i].tilestate == THREE_BOXES_LEFT 
              || t[i].tilestate == THREE_BOXES_MIDDLE 
              || t[i].tilestate == THREE_BOXES_RIGHT)) {
      return; 
    }
  }
  gamestate = 2;
  has_won = 1;
}

void gameState () {
  switch(gamestate) {
  case 0:
    textFont(Freight); 
    textAlign(CENTER);
    fill(0, 0, 0); 
    textSize(50);
    text ("You're responsible for\n organizing the munitions\n depot at the Fortress!\n\nPick up and drop all the boxes\n onto the dirt, or\n your supervisors will get \nmad!\n Use WASD to move.\n Drop boxes with E.", width/2, height/7); 
    break; 
  case 1:
    //play state
    gameStateCheck();
    break;
  case 2:
    //win state
    if (has_won == 1) {
      win.play();
      has_won = 0;
    }
    t[currTile].tilestate = FACING_RIGHT;
    textFont(Freight); 
    textAlign(CENTER);
    fill(255, 128, 0); 
    text ("You win!", width/2, height/2+20);
    text ("Press Zero to play again", width/2, height/2+178);
    break;
   case 3:
    //lose state
    if (has_lost == 1) {
      lose.play();
      has_lost = 0;
    }
    t[currTile].tilestate = FACING_RIGHT;
    textFont(Freight); 
    textAlign(CENTER);
    fill(255, 128, 0); 
    text ("You lose!", width/2, height/2+20);
    text ("Press Zero to play again", width/2, height/2+178);
    break;
  }
}

void keyPressed() {
  if (gamestate == 2 || gamestate == 3) {
    if (key == '0') {
      gamestate = 0;
      setup();
    }
  } else if (is_stunned == 0) {
    if (gamestate == 0) {
      timer = millis(); 
      gamestate = 1;
    }
    
    if ((key == 'e' || key == 'E') && isHolding > 0) {
      println("Here");
      holding_check();  
    }
    
    if (key == 'w' || key == 'W' || (key == CODED && keyCode == UP)) {
      t[currTile].tilestate = GRASS;
      if (currTile < 2 * dimension && isHolding == 0) {
        if ((millis() - last_box_placed) / 1000 > cooldown) {
          if (t[currTile - dimension].tilestate == BOXES) {
            t[currTile - dimension].tilestate = DIRT;
            if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
            if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
            isHolding = 1;
            pickup.play();
          } else if (t[currTile - dimension].tilestate == TWO_BOXES_LEFT) {
            t[currTile - dimension].tilestate = DIRT;
            t[currTile - dimension + 1].tilestate = DIRT;
            if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
            if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
            isHolding = 2;
            pickup.play();
          } else if (t[currTile - dimension].tilestate == TWO_BOXES_RIGHT) {
            t[currTile - dimension - 1].tilestate = DIRT;
            t[currTile - dimension].tilestate = DIRT;
            if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
            if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
            isHolding = 2;
            pickup.play();
          } else if (t[currTile - dimension].tilestate == THREE_BOXES_LEFT) {
            t[currTile - dimension].tilestate = DIRT;
            t[currTile - dimension + 1].tilestate = DIRT;
            t[currTile - dimension + 2].tilestate = DIRT;
            if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
            if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
            isHolding = 3;
            pickup.play();
          } else if (t[currTile - dimension].tilestate == THREE_BOXES_MIDDLE) {
            t[currTile - 1 - dimension].tilestate = DIRT;
            t[currTile - dimension].tilestate = DIRT;
            t[currTile + 1 - dimension].tilestate = DIRT;
            if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
            if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
            isHolding = 3;
            pickup.play();
          } else if (t[currTile - dimension].tilestate == THREE_BOXES_RIGHT) {
            t[currTile - 2 - dimension].tilestate = DIRT;
            t[currTile - 1 - dimension].tilestate = DIRT;
            t[currTile - dimension].tilestate = DIRT;
            if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
            if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
            isHolding = 3;
            pickup.play();
          }
        }
        currTile += dimension; 
      }
      else if (currTile < 2 * dimension && isHolding > 0) {
        if (isHolding == 1) {
          if (t[currTile - dimension].tilestate == DIRT) {
            t[currTile - dimension].tilestate = BOXES;
            isHolding = 0;
            drop.play();
            last_box_placed = millis();
            if (playerstate == FACING_RIGHT_BOX) playerstate = FACING_RIGHT;
            if (playerstate == FACING_LEFT_BOX) playerstate = FACING_LEFT;
          }
          currTile += dimension; 
        } else if (isHolding == 2) {
          if (t[currTile - dimension].tilestate == DIRT && t[currTile - dimension + 1].tilestate == DIRT) {
            t[currTile - dimension].tilestate = TWO_BOXES_LEFT;
            t[currTile - dimension + 1].tilestate = TWO_BOXES_RIGHT;
            isHolding = 0;
            drop.play();
            last_box_placed = millis();
            if (playerstate == FACING_RIGHT_BOX) playerstate = FACING_RIGHT;
            if (playerstate == FACING_LEFT_BOX) playerstate = FACING_LEFT;
          }
          currTile += dimension; 
        } else if (isHolding == 3) {
          if (t[currTile - dimension].tilestate == DIRT 
                    && t[currTile - dimension + 1].tilestate == DIRT && t[currTile - dimension + 2].tilestate == DIRT) {
            t[currTile - dimension].tilestate = THREE_BOXES_LEFT;
            t[currTile - dimension + 1].tilestate = THREE_BOXES_MIDDLE;
            t[currTile - dimension + 2].tilestate = THREE_BOXES_RIGHT;
            isHolding = 0;
            drop.play();
            last_box_placed = millis();
            if (playerstate == FACING_RIGHT_BOX) playerstate = FACING_RIGHT;
            if (playerstate == FACING_LEFT_BOX) playerstate = FACING_LEFT;
          }
          currTile += dimension; 
        }
      }
      if (isHolding > 0 && (t[currTile - dimension].tilestate == BOXES || 
                            t[currTile - dimension].tilestate == TWO_BOXES_LEFT || 
                            t[currTile - dimension].tilestate == TWO_BOXES_RIGHT || 
                            t[currTile - dimension].tilestate == THREE_BOXES_LEFT || 
                            t[currTile - dimension].tilestate == THREE_BOXES_MIDDLE || 
                            t[currTile - dimension].tilestate == THREE_BOXES_RIGHT)) {
  
        currTile += dimension; 
      }
      currTile -= dimension;
      
      if (t[currTile].tilestate == BOMB) {
        // stun 2 seconds
        stun_timer = millis(); 
        is_stunned = 1;
        bomb.play();
      }
      
      if (isHolding == 0) {
        if (t[currTile].tilestate == BOXES) {
          curr_black--;
          isHolding = 1;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == TWO_BOXES_LEFT) {
          curr_black--;
          isHolding = 2;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == TWO_BOXES_RIGHT) {
          curr_black--;
          isHolding = 2;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_LEFT) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_MIDDLE) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_RIGHT) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        }
      }
      
      
      t[currTile].tilestate = playerstate;
    }
    if (key == 'a' || key == 'A' || (key == CODED && keyCode == LEFT)) {
      t[currTile].tilestate = GRASS;
      if (currTile % dimension == 0) {
        currTile += dimension; 
      }
      if (isHolding > 0 && (t[currTile - 1].tilestate == BOXES || 
                            t[currTile - 1].tilestate == TWO_BOXES_LEFT || 
                            t[currTile - 1].tilestate == TWO_BOXES_RIGHT || 
                            t[currTile - 1].tilestate == THREE_BOXES_LEFT || 
                            t[currTile - 1].tilestate == THREE_BOXES_MIDDLE || 
                            t[currTile - 1].tilestate == THREE_BOXES_RIGHT)) {
        currTile += 1; 
      }
      currTile -= 1;
      if (t[currTile].tilestate == BOMB) {
        // stun 2 seconds
        stun_timer = millis(); 
        is_stunned = 1;
        bomb.play();
      }
      if (isHolding == 0) {
        if (t[currTile].tilestate == BOXES) {
          curr_black--;
          isHolding = 1;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == TWO_BOXES_LEFT) {
          curr_black--;
          isHolding = 2;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == TWO_BOXES_RIGHT) {
          curr_black--;
          isHolding = 2;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_LEFT) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_MIDDLE) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_RIGHT) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        }
      }
      
      if (isHolding == 0) {
        playerstate = FACING_LEFT;
      } else if (isHolding > 0) {
        playerstate = FACING_LEFT_BOX;
      }
      t[currTile].tilestate = playerstate;
    }
    if (key == 's' || key == 'S' || (key == CODED && keyCode == DOWN)) {
      t[currTile].tilestate = GRASS;
      if (currTile + dimension >= tileCount) {
        currTile -= dimension; 
      }
      if (isHolding > 0 && (t[currTile + dimension].tilestate == BOXES || 
                            t[currTile + dimension].tilestate == TWO_BOXES_LEFT || 
                            t[currTile + dimension].tilestate == TWO_BOXES_RIGHT || 
                            t[currTile + dimension].tilestate == THREE_BOXES_LEFT || 
                            t[currTile + dimension].tilestate == THREE_BOXES_MIDDLE || 
                            t[currTile + dimension].tilestate == THREE_BOXES_RIGHT)) {
        currTile -= dimension; 
      }
      currTile += dimension;
      if (t[currTile].tilestate == BOMB) {
        // stun 2 seconds
        stun_timer = millis(); 
        is_stunned = 1;
        bomb.play();
      }
      if (isHolding == 0) {
        if (t[currTile].tilestate == BOXES) {
          curr_black--;
          isHolding = 1;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == TWO_BOXES_LEFT) {
          curr_black--;
          isHolding = 2;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == TWO_BOXES_RIGHT) {
          curr_black--;
          isHolding = 2;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_LEFT) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_MIDDLE) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_RIGHT) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        }
      }
      t[currTile].tilestate = playerstate;
    }
    if (key == 'd' || key == 'D' || (key == CODED && keyCode == RIGHT)) {
      t[currTile].tilestate = GRASS;
      if (currTile % dimension == dimension - 1) {
        currTile -= dimension; 
      }
      if (isHolding > 0 && (t[currTile + 1].tilestate == BOXES || 
                            t[currTile + 1].tilestate == TWO_BOXES_LEFT || 
                            t[currTile + 1].tilestate == TWO_BOXES_RIGHT || 
                            t[currTile + 1].tilestate == THREE_BOXES_LEFT || 
                            t[currTile + 1].tilestate == THREE_BOXES_MIDDLE || 
                            t[currTile + 1].tilestate == THREE_BOXES_RIGHT)) {
        currTile -= 1; 
      }
      currTile += 1;
      if (t[currTile].tilestate == BOMB) {
        // stun 2 seconds
        stun_timer = millis(); 
        is_stunned = 1;
        bomb.play();
      }
      if (isHolding == 0) {
        if (t[currTile].tilestate == BOXES) {
          curr_black--;
          isHolding = 1;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == TWO_BOXES_LEFT) {
          curr_black--;
          isHolding = 2;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == TWO_BOXES_RIGHT) {
          curr_black--;
          isHolding = 2;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_LEFT) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_MIDDLE) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        } else if (t[currTile].tilestate == THREE_BOXES_RIGHT) {
          curr_black--;
          isHolding = 3;
          if (playerstate == FACING_RIGHT) playerstate = FACING_RIGHT_BOX;
          if (playerstate == FACING_LEFT) playerstate = FACING_LEFT_BOX;
          pickup.play();
        }
      }
      if (isHolding == 0) {
        playerstate = FACING_RIGHT;
      } else if (isHolding > 0) {
        playerstate = FACING_RIGHT_BOX;
      }
      t[currTile].tilestate = playerstate;
    }
  }
}

void holding_check() {
  if (isHolding == 1) { // single box
    if (playerstate == FACING_RIGHT_BOX) {
      if ((currTile + 1) % dimension == 0) {
        if (t[currTile + 1 - dimension].tilestate == GRASS) {
          t[currTile + 1 - dimension].tilestate = BOXES;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else {
        if (t[currTile + 1].tilestate == GRASS) {
          t[currTile + 1].tilestate = BOXES;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      }
    } else if (playerstate == FACING_LEFT_BOX) {
      if (currTile % dimension == 0) {
        if (t[currTile - 1 + dimension].tilestate == GRASS) {
          t[currTile - 1 + dimension].tilestate = BOXES;
          isHolding = 0; 
          playerstate = FACING_LEFT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else {
        if (t[currTile - 1].tilestate == GRASS) {
          t[currTile - 1].tilestate = BOXES;
          isHolding = 0; 
          playerstate = FACING_LEFT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      }
    }
  } else if (isHolding == 2) { // double box
    if (playerstate == FACING_RIGHT_BOX) {
      if ((currTile + 1) % dimension == 0) {
        if (t[currTile + 1 - dimension].tilestate == GRASS && t[currTile + 2 - dimension].tilestate == GRASS) {
          t[currTile + 1 - dimension].tilestate = TWO_BOXES_LEFT;
          t[currTile + 2 - dimension].tilestate = TWO_BOXES_RIGHT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else if ((currTile + 2) % dimension == 0) {
        if (t[currTile + 1].tilestate == GRASS && t[currTile + 2 - dimension].tilestate == GRASS) {
          t[currTile + 1].tilestate = TWO_BOXES_LEFT;
          t[currTile + 2 - dimension].tilestate = TWO_BOXES_RIGHT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else {
        if (t[currTile + 1].tilestate == GRASS && t[currTile + 2].tilestate == GRASS) {
          t[currTile + 1].tilestate = TWO_BOXES_LEFT;
          t[currTile + 2].tilestate = TWO_BOXES_RIGHT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      }
    } else if (playerstate == FACING_LEFT_BOX) {
      if (currTile % dimension == 0) {
        if (t[currTile - 1 + dimension].tilestate == GRASS && t[currTile - 2 + dimension].tilestate == GRASS) {
          t[currTile - 1 + dimension].tilestate = TWO_BOXES_RIGHT;
          t[currTile - 2 + dimension].tilestate = TWO_BOXES_LEFT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else if ((currTile - 1) % dimension == 0) {
        if (t[currTile - 1].tilestate == GRASS && t[currTile - 2 + dimension].tilestate == GRASS) {
          t[currTile - 1].tilestate = TWO_BOXES_RIGHT;
          t[currTile - 2 + dimension].tilestate = TWO_BOXES_LEFT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else {
        if (t[currTile - 1].tilestate == GRASS && t[currTile - 2].tilestate == GRASS) {
          t[currTile - 1].tilestate = TWO_BOXES_RIGHT;
          t[currTile - 2].tilestate = TWO_BOXES_LEFT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      }
    }
  } else if (isHolding == 3) { // treble box
    if (playerstate == FACING_RIGHT_BOX) {
      if ((currTile + 1) % dimension == 0) {
        if (t[currTile + 1 - dimension].tilestate == GRASS && t[currTile + 2 - dimension].tilestate == GRASS && t[currTile + 3 - dimension].tilestate == GRASS) {
          t[currTile + 1 - dimension].tilestate = THREE_BOXES_LEFT;
          t[currTile + 2 - dimension].tilestate = THREE_BOXES_MIDDLE;
          t[currTile + 3 - dimension].tilestate = THREE_BOXES_RIGHT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else if ((currTile + 2) % dimension == 0) {
        if (t[currTile + 1].tilestate == GRASS && t[currTile + 2 - dimension].tilestate == GRASS && t[currTile + 3 - dimension].tilestate == GRASS) {
          t[currTile + 1].tilestate = THREE_BOXES_LEFT;
          t[currTile + 2 - dimension].tilestate = THREE_BOXES_MIDDLE;
          t[currTile + 3 - dimension].tilestate = THREE_BOXES_RIGHT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else if ((currTile + 3) % dimension == 0) {
        if (t[currTile + 1].tilestate == GRASS && t[currTile + 2].tilestate == GRASS && t[currTile + 3 - dimension].tilestate == GRASS) {
          t[currTile + 1].tilestate = THREE_BOXES_LEFT;
          t[currTile + 2].tilestate = THREE_BOXES_MIDDLE;
          t[currTile + 3 - dimension].tilestate = THREE_BOXES_RIGHT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else {
        if (t[currTile + 1].tilestate == GRASS && t[currTile + 2].tilestate == GRASS && t[currTile + 3].tilestate == GRASS) {
          t[currTile + 1].tilestate = THREE_BOXES_LEFT;
          t[currTile + 2].tilestate = THREE_BOXES_MIDDLE;
          t[currTile + 3].tilestate = THREE_BOXES_RIGHT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      }
    } else if (playerstate == FACING_LEFT_BOX) {
      if (currTile % dimension == 0) {
        if (t[currTile - 1 + dimension].tilestate == GRASS && t[currTile - 2 + dimension].tilestate == GRASS && t[currTile - 3 + dimension].tilestate == GRASS) {
          t[currTile - 1 + dimension].tilestate = THREE_BOXES_RIGHT;
          t[currTile - 2 + dimension].tilestate = THREE_BOXES_MIDDLE;
          t[currTile - 3 + dimension].tilestate = THREE_BOXES_LEFT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else if ((currTile - 1) % dimension == 0) {
        if (t[currTile - 1].tilestate == GRASS && t[currTile - 2 + dimension].tilestate == GRASS && t[currTile - 3 + dimension].tilestate == GRASS) {
          t[currTile - 1].tilestate = THREE_BOXES_RIGHT;
          t[currTile - 2 + dimension].tilestate = THREE_BOXES_MIDDLE;
          t[currTile - 3 + dimension].tilestate = THREE_BOXES_LEFT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else if ((currTile - 2) % dimension == 0) {
        if (t[currTile - 1].tilestate == GRASS && t[currTile - 2].tilestate == GRASS && t[currTile - 3 + dimension].tilestate == GRASS) {
          t[currTile - 1].tilestate = THREE_BOXES_RIGHT;
          t[currTile - 2].tilestate = THREE_BOXES_MIDDLE;
          t[currTile - 3 + dimension].tilestate = THREE_BOXES_LEFT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      } else {
        if (t[currTile - 1].tilestate == GRASS && t[currTile - 2].tilestate == GRASS && t[currTile - 3].tilestate == GRASS) {
          t[currTile - 1].tilestate = THREE_BOXES_RIGHT;
          t[currTile - 2].tilestate = THREE_BOXES_MIDDLE;
          t[currTile - 3].tilestate = THREE_BOXES_LEFT;
          isHolding = 0; 
          playerstate = FACING_RIGHT;
          curr_black++;
          t[currTile].tilestate = playerstate;
          drop.play();
        }
      }
    }
  }
}

void wipe() {
  for (int i = dimension; i < tileCount; i++) {
    if (t[i].tilestate == TWO_BOXES_LEFT 
              && !(t[i + 1].tilestate == TWO_BOXES_RIGHT || t[i + 1 - dimension].tilestate == TWO_BOXES_RIGHT)) {
      t[i].tilestate = GRASS; 
    }
    if (t[i].tilestate == TWO_BOXES_RIGHT 
              && !(t[i - 1].tilestate == TWO_BOXES_LEFT || t[i - 1 + dimension].tilestate == TWO_BOXES_LEFT)) {
      t[i].tilestate = GRASS; 
    }
    if (t[i].tilestate == THREE_BOXES_LEFT
              && !((t[i + 1].tilestate == THREE_BOXES_MIDDLE && t[i + 2].tilestate == THREE_BOXES_RIGHT)
                 || (t[i + 1].tilestate == THREE_BOXES_MIDDLE && t[i + 2 - dimension].tilestate == THREE_BOXES_RIGHT)
                 || (t[i + 1 - dimension].tilestate == THREE_BOXES_MIDDLE && t[i + 2 - dimension].tilestate == THREE_BOXES_RIGHT))) {
      t[i].tilestate = GRASS; 
    }
    if (t[i].tilestate == THREE_BOXES_MIDDLE
              && !((t[i - 1].tilestate == THREE_BOXES_LEFT && t[i + 1].tilestate == THREE_BOXES_RIGHT)
                 || (t[i - 1].tilestate == THREE_BOXES_LEFT && t[i + 1 - dimension].tilestate == THREE_BOXES_RIGHT)
                 || (t[i - 1 + dimension].tilestate == THREE_BOXES_LEFT && t[i + 1].tilestate == THREE_BOXES_RIGHT))) {
      t[i].tilestate = GRASS; 
    }
    if (t[i].tilestate == THREE_BOXES_RIGHT
              && !((t[i - 2].tilestate == THREE_BOXES_LEFT && t[i - 1].tilestate == THREE_BOXES_MIDDLE)
                 || (t[i - 2 + dimension].tilestate == THREE_BOXES_LEFT && t[i - 1 + dimension].tilestate == THREE_BOXES_MIDDLE)
                 || (t[i - 2 + dimension].tilestate == THREE_BOXES_LEFT && t[i - 1].tilestate == THREE_BOXES_MIDDLE))) {
      t[i].tilestate = GRASS; 
    }
  }
}
