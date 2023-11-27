import pygame
import numpy as np
import src.utils.levelHelper as lh
from src.utils.constants import *

def update_position(playerX, playerY, keys, tileList):
  if(keys[pygame.K_w] and not keys[pygame.K_s]):
    newY = playerY - 25.0 * PLAYER_VELOCITY
  elif(keys[pygame.K_s] and not keys[pygame.K_w]):
    newY = playerY + 25.0 * PLAYER_VELOCITY
  else:
    newY = playerY

  if(keys[pygame.K_d] and not keys[pygame.K_a]):
    newX = playerX + 25.0 * PLAYER_VELOCITY
  elif(keys[pygame.K_a] and not keys[pygame.K_d]):
    newX = playerX - 25.0 * PLAYER_VELOCITY
  else:
    newX = playerX

  return check_collisions(playerX, newX, playerY, newY, tileList)

def check_collisions(oldX, newX, oldY, newY, tileList):
  # Check for out of bounds:
  if(newY < 0):
    newY = 0
  elif(newY > (SCREEN_HEIGHT - PLAYER_HEIGHT)):
    newY = (SCREEN_HEIGHT - PLAYER_HEIGHT)

  if(newX < 0):
    newX = 0
  elif(newX > (SCREEN_WIDTH - PLAYER_WIDTH)):
    newX = (SCREEN_WIDTH - PLAYER_WIDTH)

  # Check for collisions with other tiles
  # TODO: currently super basic; planning on checking the direction player came from so you dont get stuck on the wall.
  playerRect = pygame.Rect(newX, newY, 25, 25)
  for (row_idx, col_idx), tile in np.ndenumerate(tileList):
    tileRect = pygame.Rect(col_idx*25, row_idx*25, 25, 25)
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.WALL):
      newX = oldX
      newY = oldY

  return (newX, newY)

def check_pickUp(tileList, posX, posY):
  playerRect = pygame.Rect(posX, posY, 25, 25)
  for (row_idx, col_idx), tile in np.ndenumerate(tileList):
    tileRect = pygame.Rect(col_idx*25, row_idx*25, 25, 25)
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.COIN):
      tileList[row_idx][col_idx] = lh.tileType.OPEN