import pygame
import numpy as np
import src.agent.model as ag
import src.utils.levelHelper as lh
from src.utils.constants import *

# Updates Position based on player input
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

  # Check for out of bounds:
  if(newY < 0):
    newY = 0
  elif(newY > (SCREEN_HEIGHT - PLAYER_HEIGHT)):
    newY = (SCREEN_HEIGHT - PLAYER_HEIGHT)

  if(newX < 0):
    newX = 0
  elif(newX > (SCREEN_WIDTH - PLAYER_WIDTH)):
    newX = (SCREEN_WIDTH - PLAYER_WIDTH)

  return check_collisions(playerX, newX, playerY, newY, tileList)

# Checks if the player has run into any special tiles (walls)
def check_collisions(oldX, newX, oldY, newY, tileList):
  # Check for collisions with other tiles
  for (row_idx, col_idx), tile in np.ndenumerate(tileList):
    playerRect = pygame.Rect(newX, newY, 25, 25) # Need to remake rect in case position updated by previous tile
    tileRect = pygame.Rect(col_idx*25, row_idx*25, 25, 25) # Used for collision of tiles
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

def check_pickUp(agent_map, posX, posY, time_stopped, hazardCooldown, score, door_reached):
  playerRect = pygame.Rect(posX, posY, 25, 25)
  for (row_idx, col_idx), tile in np.ndenumerate(agent_map):
    tileRect = pygame.Rect(col_idx*25, row_idx*25, 25, 25)
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.COIN and agent_map[row_idx][col_idx] == lh.tileType.COIN):
      agent_map[row_idx][col_idx] = lh.tileType.TRAVERSED
      score += 250
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.HAZARD and hazardCooldown < 0):
      score -= 250
      hazardCooldown = 60
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.DOOR and door_reached != 1):
      score += 1000
      door_reached = 1
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.OPEN and door_reached != 1):
      agent_map[row_idx][col_idx] = lh.tileType.TRAVERSED
      score += 25
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.START):
      score -= 5
    if(pygame.Rect.colliderect(playerRect, tileRect) and tile == lh.tileType.TRAVERSED and door_reached != 1 and time_stopped > 20):
      score -= 1
  return (score, hazardCooldown, door_reached, agent_map)