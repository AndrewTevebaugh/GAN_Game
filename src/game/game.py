import pygame
import numpy as np
import src.agent.model as ag
import src.game.movement as mv
import src.utils.levelHelper as lh
from src.utils.constants import *

class Game:
  # Initialize the game
  def __init__(self, type):
    # DEBUG - Number correlates to agent being followed
    self.debug = 24 # Must be between 1 and AGENT_CNT (inclusive), 0 to disable
    if(self.debug > int(AGENT_CNT) or self.debug < 0):
      print("Invalid Debug configuration!")
      exit()

    # Set up pygame stuff
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    self.clock = pygame.time.Clock()

    # Loads map from save file
    self.tileList = np.loadtxt("src\\game\\levels\\testLevel.txt", dtype=int) # TODO Add a configurable level loader

    if(int(type) == 0):
      pygame.display.set_caption("GAN Game")
      # Marks game as NOT running - User mode not implemented
      self.round_complete = False
      self.is_running = False
      self.mode = 0
      print("Manual Mode disabled")
    else:
      self.mode = 1
      # Create agent instances
      self.agentList = []
      for i in range(AGENT_CNT):
        self.agentList.append(ag.Agent())

      # Caption Stuff
      self.gen_num = 1
      self.top_score = 0
      self.perf_time = TRIAL_TIME
      pygame.display.set_caption("Gen number: " + str(self.gen_num) + ", Top Score: " + str(self.top_score) + ", Perf Time: "  + str(self.perf_time))

      # Determine and save Start and Finish locations
      for (row_idx, col_idx), tile in np.ndenumerate(self.tileList):
        if(tile == lh.tileType.START):
          self.start_pos = (col_idx*25, row_idx*25)
        elif(tile == lh.tileType.DOOR):
          self.doorPos = (col_idx*25, row_idx*25)

      # Initialize agent map and set position to the start
      for agent in self.agentList:
        agent.map = np.loadtxt("src\\game\\levels\\testLevel.txt", dtype=int)
        agent.set_pos(self.start_pos)
        
      # Marks game as running
      self.round_complete = False
      self.is_running = True

  # Check for new events; For agent mode, this will just be X button and tick rate
  def handle_events(self):
    # Checks for new events
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.is_running = False

    if(self.mode == 0):
      self.keys = pygame.key.get_pressed()

    # Sets the FPS
    self.clock.tick(60)

  # Update game state
  def update(self):
    # Radius of tiles that the agent can see
    radius = int(PLAYER_VISION_RADIUS)
    # Number of tiles + door position, player position, and time that the agent hasn't moved
    inputs = np.zeros((radius*2+1)**2+5)
    
    for index, agent in enumerate(self.agentList):
      agent_pos = agent.get_pos()
      # Calculate inputs for next iteration
      a_col_idx = int(agent_pos[0]//25)
      a_row_idx = int(agent_pos[1]//25)
      for i in range(-radius, radius+1):
        for j in range(-radius, radius+1):
          if(a_col_idx + j >= 0 and a_col_idx + j < SCREEN_WIDTH/PLAYER_WIDTH and a_row_idx + i >= 0 and a_row_idx + i < SCREEN_HEIGHT/PLAYER_HEIGHT):
            inputs[(2*radius+1)*(i+radius) + (j+radius)] = agent.map[a_row_idx + i][a_col_idx + j]
            if(index == self.debug-1 and self.debug != 0):
              pygame.draw.rect(self.screen, lh.getTileColor(agent.map[a_row_idx + i][a_col_idx + j]), ((a_col_idx + j)*25, (a_row_idx + i)*25, 25, 25))
          else:
            inputs[(2*radius+1)*(i+radius) + (j+radius)] = lh.tileType.WALL
      inputs[len(inputs)-5:] = [self.doorPos[0], self.doorPos[1], agent_pos[0], agent_pos[1], agent.time_stopped]
      
      if self.perf_time == 0:
        agent.set_pos(self.start_pos)
      else:
        # Get new agent position based on model output
        new_pos = mv.update_position(agent_pos[0], agent_pos[1], agent.get_output(inputs), agent.map)
        if new_pos[0] - agent_pos[0] + new_pos[1] - agent_pos[1] == 0:
          agent.time_stopped += 1
        else:
          agent.time_stopped = 0
        agent.set_pos(new_pos)

        # Check item pick ups
        pickUp_return = mv.check_pickUp(self.tileList, agent_pos[0], agent_pos[1], agent.get_hazardCooldown(), agent.map)
        
        # Give Rewards
        agent.finished = pickUp_return[2] # If agent reached door
        agent.coins += 10*pickUp_return[0] # If agent picked up a coin

        # Reward agent for moving to a new tile
        if(agent.map[int(agent_pos[1]//25)][int(agent_pos[0]//25)] == 0): # If agent hasn't been here tile will be OPEN (0)
          agent.map[int(agent_pos[1]//25)][int(agent_pos[0]//25)] = -1 # Once agent visits, set to VISITED (-1)
          agent.coins += 2 # Reward for new tile
        
        agent.set_score(10*agent.coins + 1000*agent.finished)
        # agent.increment_score((np.sqrt(((SCREEN_SIZE*25)**2)*2) - np.sqrt((self.doorPos[0]-agent_pos[0])**2 + (self.doorPos[1]-agent_pos[1])**2)))
        # if(agent.time_stopped > 15):
        #   agent.increment_score(-1*agent.time_stopped)

        agent.set_hazardCooldown(pickUp_return[1]-1)

    # If agent performance time is up, reset agents and level
    if self.perf_time == 0:
      half = len(self.agentList)//2
      self.agentList.sort(key = lambda x: x.score)
      self.top_score = self.agentList[AGENT_CNT-1].score
      for i in range(half//2):
        ag.reproduce(self.agentList[half+2*i], self.agentList[half+2*i+1], self.agentList[2*i], self.agentList[2*i+1])
        self.agentList[2*i].mutate()
        self.agentList[2*i+1].mutate()
      self.perf_time = TRIAL_TIME + 60*(self.gen_num//5) # Was //40
      self.gen_num += 1
      self.tileList = np.loadtxt("src\\game\\levels\\testLevel.txt", dtype=int)
      for agent in self.agentList:
        agent.set_score(0)
        agent.time_stopped = 0
        agent.coins = 0
        agent.map = np.loadtxt("src\\game\\levels\\testLevel.txt", dtype=int)

    # Otherwise, decrement time
    else:
      self.perf_time -= 1

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.is_running = False

  # Render tiles to the screen
  def render(self):
    # Draws all of the map tiles
    if(self.debug == 0):
      for (row_idx, col_idx), tile in np.ndenumerate(self.tileList):
        pygame.draw.rect(self.screen, lh.getTileColor(tile), (col_idx*25, row_idx*25, 25, 25))

    for agent in self.agentList:
      # Draws the player
      agent_pos = agent.get_pos()
      pygame.draw.rect(self.screen, "pink", (agent_pos[0], agent_pos[1], PLAYER_WIDTH, PLAYER_HEIGHT))
      
      if(self.debug != 0):
        # Set up the text to draw score on top of player
        font = pygame.font.Font(None, 18) # Set font for text
        text = str(int(agent.score))
        text_color = (255, 255, 255)
        text_surface = font.render(text, True, text_color)

        # Blit the text onto the screen
        self.screen.blit(text_surface, (agent.get_pos()[0], agent.get_pos()[1]+6))

    # Actually renders the updates to the screen
    pygame.display.set_caption("Gen number: " + str(self.gen_num) + ", Top Score: " + str(int(self.top_score)) + ", Perf Time: "  + str(self.perf_time))
    pygame.display.update()

    self.screen.fill((0, 0, 0)) # Clear screen before next draw
