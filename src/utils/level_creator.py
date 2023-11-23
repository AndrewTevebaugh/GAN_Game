import pygame
import numpy as np
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

current_type = tileType.OPEN
tileList = np.zeros((20,20), dtype=int)
pygame.init()
pygame.display.set_caption("Level Maker - Click to place, Scroll to change, Close window to save")
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
is_running = True

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

def update_screen(clicked):
  (y, x) = pygame.mouse.get_pos()
  for (row_idx, col_idx), tile in np.ndenumerate(tileList):
    if(x > col_idx*25 and x <= (col_idx + 1)*25 and y > row_idx*25 and y <= (row_idx + 1)*25):
      pygame.draw.rect(screen, GRAY, (row_idx*25, col_idx*25, 25, 25))
      pygame.draw.rect(screen, getTileColor(current_type), (row_idx*25, col_idx*25, 25, 25), border_radius=8)
      if(clicked):
        tileList[row_idx][col_idx] = int(current_type)
    else:
      pygame.draw.rect(screen, getTileColor(tile), (row_idx*25, col_idx*25, 25, 25))
    
clicked = False
while is_running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      is_running = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
      if event.button == 4:  # Scroll wheel up
        current_type = (5 + int(current_type) + 1)%5
      elif event.button == 5:  # Scroll wheel down
        current_type = (5 + int(current_type) - 1)%5
      elif event.button == 1:
        clicked = True
    elif event.type == pygame.MOUSEBUTTONUP:
      if event.button == 1:
        clicked = False

  update_screen(clicked)
  pygame.display.update()
  clock.tick(60)

pygame.quit()

#Confirm and then save map
print("Would you like to save this map? (Y/n)")
response = input().lower()
if(response == "n"):
  print("Are you sure you don't want to save? (y/N)")
  response = input().lower()
  if(response == "y"):
    exit()

print("Saving Map...")
np.savetxt("newLevel.txt", tileList.T, fmt='%d')
