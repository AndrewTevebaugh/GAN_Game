import pygame
import numpy as np
import src.agent.model as ag
import src.game.movement as mv
import src.utils.levelHelper as lh
from src.utils.constants import *

class Game:
  def __init__(self, type):
    # Set up pygame stuff
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("GAN Game")
    self.clock = pygame.time.Clock()

    # Create agent instances
    self.agents = []
    for i in range(16):
      self.agents.append(ag.Agent())

    self.perf_time = TRIAL_TIME

    #TODO Add a configurable level loader
    # Loads map from save file
    self.tileList = np.loadtxt("src\\game\\levels\\testLevel.txt", dtype=int)
    for (row_idx, col_idx), tile in np.ndenumerate(self.tileList):
      if(tile == lh.tileType.START):
        self.start_pos = (col_idx*25, row_idx*25)
        for a in self.agents:
          a.set_pos((col_idx*25, row_idx*25))
      
      elif(tile == lh.tileType.DOOR):
        self.doorPos = (col_idx*25, row_idx*25)

    # Marks game as running
    self.round_complete = False
    self.is_running = True

  def handle_events(self):
    # Checks for new events
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.is_running = False

    self.keys = pygame.key.get_pressed()

    # Sets the FPS
    self.clock.tick(60)

  def update(self):
    radius = PLAYER_VISION_RADIUS
    inputs = np.zeros((radius*2+1)**2+5)
    
    for a in self.agents:
      a_col_idx = int(self.tileList.shape[1]*25 / (a.get_pos()[0]))
      a_row_idx = int(self.tileList.shape[0]*25 / (a.get_pos()[1]))
      for i in range(-radius, radius+1):
        for j in range(-radius, radius+1):
          if a_col_idx + j >= 0 and a_col_idx + j < SCREEN_WIDTH/PLAYER_WIDTH and a_row_idx + i >= 0 and a_row_idx + i < SCREEN_HEIGHT/PLAYER_HEIGHT:
            inputs[(2*radius+1)*(i+radius) + (j+radius)] = self.tileList[a_row_idx + i][a_col_idx + j]
          else:
            inputs[(2*radius+1)*(i+radius) + (j+radius)] = lh.tileType.WALL
      inputs[len(inputs)-5:] = [self.doorPos[0], self.doorPos[1], a.get_pos()[0], a.get_pos()[1], a.time_stopped]
      if self.perf_time == 0:
        a.set_pos(self.start_pos)

      new_pos = mv.update_position(a.get_pos()[0], a.get_pos()[1], a.get_output(inputs), self.tileList)
      ds = abs(new_pos[0] - a.get_pos()[0]) + abs(new_pos[1] - a.get_pos()[1])
      if ds == 0:
        a.time_stopped += 1
      elif a.time_stopped > 0:
        a.time_stopped -= 1
      a.set_pos(new_pos)
      pickUp_return = mv.check_pickUp(self.tileList, a.get_pos()[0], a.get_pos()[1], a.get_hazardCooldown())
      a.increment_score(pickUp_return[0])
      
      # Decrease score further away from door
      a.increment_score(-np.sqrt((self.doorPos[0]-a.get_pos()[0])**2 + (self.doorPos[1]-a.get_pos()[1])**2)/1000 - 3*a.time_stopped)
      a.set_hazardCooldown(pickUp_return[1]-1)

    if self.perf_time == 0:
      half = len(self.agents)//2
      self.agents.sort(key = lambda x: x.score)
      for i in range(half//2):
        ag.reproduce(self.agents[half+2*i], self.agents[half+2*i+1], self.agents[2*i], self.agents[2*i+1])
        self.agents[2*i].mutate()
        self.agents[2*i+1].mutate()
      self.perf_time = TRIAL_TIME
      print("Top score: ", self.agents[len(self.agents)-1].score)
      print("Bottom score: ", self.agents[0].score)
      self.tileList = np.loadtxt("src\\game\\levels\\testLevel.txt", dtype=int)
      for a in self.agents:
        a.set_score(0)
        a.time_stopped = 0

    else:
      self.perf_time -= 1

    

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.is_running = False

  def render(self):
    # Draws all of the map tiles
    for (row_idx, col_idx), tile in np.ndenumerate(self.tileList):
      pygame.draw.rect(self.screen, lh.getTileColor(tile), (col_idx*25, row_idx*25, 25, 25))

    # Draws the player
    for a in self.agents:
      pygame.draw.rect(self.screen, "pink", (a.get_pos()[0], a.get_pos()[1], PLAYER_WIDTH, PLAYER_HEIGHT))

    #actually renders the updates to the screen
    #pygame.display.set_caption("GAN Game - Score: " + str(int(self.score)))
    pygame.display.update()