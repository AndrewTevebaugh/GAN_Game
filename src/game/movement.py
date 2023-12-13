import pygame
import numpy as np
import src.agent.model as ag
import src.utils.levelHelper as lh
from src.utils.constants import *

def update_position(playerX, playerY, keys, tileList):
  if(keys[2] and not keys[3]):
    newY = playerY - 25.0 * PLAYER_VELOCITY
  elif(keys[3] and not keys[2]):
    newY = playerY + 25.0 * PLAYER_VELOCITY
  else:
    newY = playerY

  if(keys[1] and not keys[0]):
    newX = playerX + 25.0 * PLAYER_VELOCITY
  elif(keys[0] and not keys[1]):
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
  # Potentially might need to make this faster (get rid of nested for loop)
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

def check_pickUp(tileList, posX, posY, hazardCooldown, agent_map):
  door_reached = 0
  score = 0
  playerRect = pygame.Rect(posX, posY, 25, 25)
  for (row_idx, col_idx), tile in np.ndenumerate(tileList):
    tileRect = pygame.Rect(col_idx*25, row_idx*25, 25, 25)
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.COIN and agent_map[row_idx][col_idx] == 4):
      # tileList[row_idx][col_idx] = lh.tileType.OPEN
      agent_map[row_idx][col_idx] = 0
      score += 1
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.HAZARD and hazardCooldown < 0):
      score -= 1
      hazardCooldown = 60
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.DOOR):
      door_reached = 1
  return (score, hazardCooldown, door_reached, agent_map)