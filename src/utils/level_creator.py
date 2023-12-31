import pygame
import numpy as np
import levelHelper as lh

types = [lh.tileType.WALL, lh.tileType.START, lh.tileType.HAZARD, lh.tileType.OPEN, lh.tileType.COIN, lh.tileType.DOOR]
typeIdx = 0

current_type = lh.tileType.OPEN
tileList = np.zeros((20,20), dtype=int)
pygame.init()
pygame.display.set_caption("Level Maker - Click to place, Scroll to change, Close window to save")
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
is_running = True


def update_screen(clicked):
  (y, x) = pygame.mouse.get_pos()
  for (row_idx, col_idx), tile in np.ndenumerate(tileList):
    if(x > col_idx*25 and x <= (col_idx + 1)*25 and y > row_idx*25 and y <= (row_idx + 1)*25):
      pygame.draw.rect(screen, lh.GRAY, (row_idx*25, col_idx*25, 25, 25))
      pygame.draw.rect(screen, lh.getTileColor(current_type), (row_idx*25, col_idx*25, 25, 25), border_radius=8)
      if(clicked):
        tileList[row_idx][col_idx] = int(current_type)
    else:
      pygame.draw.rect(screen, lh.getTileColor(tile), (row_idx*25, col_idx*25, 25, 25))
    
clicked = False
while is_running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      is_running = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
      if event.button == 4:  # Scroll wheel up
        typeIdx = (typeIdx + 1) % 6
        current_type = types[typeIdx]
      elif event.button == 5:  # Scroll wheel down
        typeIdx = (typeIdx - 1) % 6
        current_type = types[typeIdx]
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
