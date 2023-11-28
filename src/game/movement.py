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
  for (row_idx, col_idx), tile in np.ndenumerate(tileList):
    playerRect = pygame.Rect(newX, newY, 25, 25)
    tileRect = pygame.Rect(col_idx*25, row_idx*25, 25, 25)
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.WALL):
      fixX, fixY = 0, 0
      for (row_idx2, col_idx2), tile2 in np.ndenumerate(tileList):
        playerRect2X = pygame.Rect(oldX, newY, 25, 25)
        playerRect2Y = pygame.Rect(newX, oldY, 25, 25)
        tileRect2 = pygame.Rect(col_idx2*25, row_idx2*25, 25, 25)
        if(pygame.Rect.colliderect(playerRect2X, tileRect2) and tile2 == lh.tileType.WALL):
          fixX += 1
        if(pygame.Rect.colliderect(playerRect2Y, tileRect2) and tile2 == lh.tileType.WALL):
          fixY += 1
      if(fixX == 0):
        newX = oldX
      elif(fixY == 0):
        newY = oldY
      else:
        newX = oldX
        newY = oldY

  return (newX, newY)

def check_pickUp(tileList, posX, posY):
  playerRect = pygame.Rect(posX, posY, 25, 25)
  for (row_idx, col_idx), tile in np.ndenumerate(tileList):
    tileRect = pygame.Rect(col_idx*25, row_idx*25, 25, 25)
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.COIN):
      tileList[row_idx][col_idx] = lh.tileType.OPEN