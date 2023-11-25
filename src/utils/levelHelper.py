from enum import IntEnum

GRAY = (99,99,99)
BROWN = (69, 58, 34)
BLACK = (0, 0, 0)
TEAL = (13, 158, 190)
RED = (102, 6, 6)
GOLD = (194, 193, 75)

class tileType(IntEnum):
  OPEN = 0
  WALL = 1
  DOOR = 2
  HAZARD = 3
  COIN = 4

def getTileColor(tile):
  if(tile == tileType.WALL):
    return BLACK
  elif(tile == tileType.DOOR):
    return TEAL
  elif(tile == tileType.HAZARD):
    return RED
  elif(tile == tileType.COIN):
    return GOLD
  else:
    return BROWN