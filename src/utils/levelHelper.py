from enum import IntEnum

WHITE = (0, 0, 0) # ERROR
GRAY = (99,99,99) # Traversed
BROWN = (69, 58, 34) # Open
BLACK = (0, 0, 0) # Wall
PURPLE = (86, 15, 148) # Start
TEAL = (13, 158, 190) # Exit
RED = (102, 6, 6) # Hazard
GOLD = (194, 193, 75) # Coin

class tileType(IntEnum):
  WALL = 0
  START = 1
  HAZARD = 2
  TRAVERSED = 4
  OPEN = 6
  COIN = 8
  DOOR = 9

def getTileColor(tile):
  if(tile == tileType.WALL):
    return BLACK
  elif(tile == tileType.START):
    return PURPLE
  elif(tile == tileType.HAZARD):
    return RED
  elif(tile == tileType.TRAVERSED):
    return GRAY
  elif(tile ==tileType.OPEN):
    return BROWN
  elif(tile == tileType.COIN):
    return GOLD
  elif(tile == tileType.DOOR):
    return TEAL
  else:
    return WHITE