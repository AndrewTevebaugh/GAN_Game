from enum import IntEnum

GRAY = (99,99,99)
BROWN = (69, 58, 34)
BLACK = (0, 0, 0)
TEAL = (13, 158, 190)
RED = (102, 6, 6)
GOLD = (194, 193, 75)
PURPLE = (86, 15, 148)

class tileType(IntEnum):
  OPEN = 10
  TRAVERSED = -9
  WALL = -10000
  DOOR = 1000
  HAZARD = -1000
  COIN = 100
  START = -100

def getTileColor(tile):
  if(tile == tileType.WALL):
    return BLACK
  elif(tile == tileType.DOOR):
    return TEAL
  elif(tile == tileType.HAZARD):
    return RED
  elif(tile == tileType.COIN):
    return GOLD
  elif(tile == tileType.START):
    return PURPLE
  else:
    return BROWN