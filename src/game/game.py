import pygame
import numpy as np
import src.agent.model as ag
import src.game.movement as mv
import src.utils.levelHelper as lh
from src.utils.constants import *

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class Game:
  # Initialize the game
  def __init__(self, type, torch_device):
    # DEBUG - Number correlates to agent being followed
    if(DEBUG_MODE > int(AGENT_CNT) or DEBUG_MODE < 0):
      print("Invalid Debug configuration!")
      exit()

    # Set up pytorch device
    self.torch_device = torch_device

    # Set up pygame stuff
    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    self.clock = pygame.time.Clock()

    # Loads map from save file
    self.tileList = np.loadtxt(MAP_STRING, dtype=float) # TODO Add a configurable level loader

    if(int(type) == 0):
      self.mode = 0

      self.score = 0
      self.hazardCooldown = 0
      self.finished = 0
      self.time_stopped = 0

      self.keys = [False, False, False, False]
      for (row_idx, col_idx), tile in np.ndenumerate(self.tileList):
        if(tile == lh.tileType.START):
          self.playerX = col_idx*25
          self.playerY = row_idx*25

      self.is_running = True
    else:
      self.mode = 1

      # Create agent instances
      self.agentList = []
      for i in range(AGENT_CNT):
        self.agentList.append(ag.Agent(self.torch_device))

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
          self.door_pos = (col_idx*25, row_idx*25)

      # Initialize agent map and set position to the start
      for agent in self.agentList:
        agent.map = np.loadtxt(MAP_STRING, dtype=float)
        agent.set_pos(self.start_pos)
        
      # Marks game as running
      self.is_running = True

  # Check for new events; For agent mode, this will just be X button and tick rate
  def handle_events(self):
    # Checks for new events
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.is_running = False

    if(self.mode == 0):
      temp_keys = pygame.key.get_pressed()
      self.keys[2] = temp_keys[pygame.K_w]
      self.keys[3] = temp_keys[pygame.K_s]
      self.keys[0] = temp_keys[pygame.K_a]
      self.keys[1] = temp_keys[pygame.K_d]

    # Sets the FPS
    self.clock.tick(FPS)

  # Update game state
  def update(self):
    # Number of tiles + door position, player position, and time that the agent hasn't moved
    inputs = np.zeros(AGENT_NN_NUM_INPUTS)
    
    if(self.mode == 1):
      for index, agent in enumerate(self.agentList):

        agent_pos = agent.get_pos()
        # Calculate inputs for next iteration
        a_col_idx = int(agent_pos[0]//25)
        a_row_idx = int(agent_pos[1]//25)
        for i in range(-AGENT_VISION_RADIUS, AGENT_VISION_RADIUS+1):
          for j in range(-AGENT_VISION_RADIUS, AGENT_VISION_RADIUS+1):
            if(a_col_idx + j >= 0 and a_col_idx + j < SCREEN_WIDTH/PLAYER_WIDTH and a_row_idx + i >= 0 and a_row_idx + i < SCREEN_HEIGHT/PLAYER_HEIGHT):
              inputs[(2*AGENT_VISION_RADIUS+1)*(i+AGENT_VISION_RADIUS) + (j+AGENT_VISION_RADIUS)] = agent.map[a_row_idx + i][a_col_idx + j]
              if(index == DEBUG_MODE-1 and DEBUG_MODE != 0):
                pygame.draw.rect(self.screen, lh.getTileColor(agent.map[a_row_idx + i][a_col_idx + j]), ((a_col_idx + j)*25, (a_row_idx + i)*25, 25, 25))
            else:
              inputs[(2*AGENT_VISION_RADIUS+1)*(i+AGENT_VISION_RADIUS) + (j+AGENT_VISION_RADIUS)] = lh.tileType.WALL
        # inputs[len(inputs)-5:] = [int(self.door_pos[0]//25), int(self.door_pos[1]//25), int(agent_pos[0]//25), int(agent_pos[1]//25), agent.get_delta_score()]
        old_inputs = torch.tensor(inputs, dtype=torch.float32, device=self.torch_device).unsqueeze(0)

        if self.perf_time == 0:
          agent.set_pos(self.start_pos)
        else:
          # Get new agent position based on model output
          if(agent.finished == 0 or True):
            action = agent.select_action(old_inputs)
            action_itm = action.item()
            new_pos = mv.update_position(agent_pos[0], agent_pos[1], action_itm, agent.map)
            agent.set_pos(new_pos)
            # Check item pick ups
            reward, new_hazardCooldown, door_reached, new_map = mv.check_pickUp(agent.map, agent_pos[0], agent_pos[1], agent.time_stopped, agent.get_hazardCooldown())
            reward = torch.tensor([reward], dtype=torch.int, device=self.torch_device)
            
            for i in range(-AGENT_VISION_RADIUS, AGENT_VISION_RADIUS+1):
              for j in range(-AGENT_VISION_RADIUS, AGENT_VISION_RADIUS+1):
                if(a_col_idx + j >= 0 and a_col_idx + j < SCREEN_WIDTH/PLAYER_WIDTH and a_row_idx + i >= 0 and a_row_idx + i < SCREEN_HEIGHT/PLAYER_HEIGHT):
                  inputs[(2*AGENT_VISION_RADIUS+1)*(i+AGENT_VISION_RADIUS) + (j+AGENT_VISION_RADIUS)] = new_map[a_row_idx + i][a_col_idx + j]
                else:
                  inputs[(2*AGENT_VISION_RADIUS+1)*(i+AGENT_VISION_RADIUS) + (j+AGENT_VISION_RADIUS)] = lh.tileType.WALL
            new_inputs = torch.tensor(inputs, dtype=torch.float32, device=self.torch_device).unsqueeze(0)

            # Log the transaction in replay memory
            agent.memory.push(old_inputs, action, new_inputs, reward)

            # Update the new state
            agent.map = new_map

            # Perform optimization on policy network
            agent.optimize_model()

            # Soft update of the target network's weights
            # θ′ ← τ θ + (1 −τ )θ′
            target_net_state_dict = agent.target_net.state_dict()
            policy_net_state_dict = agent.policy_net.state_dict()
            for key in policy_net_state_dict:
              target_net_state_dict[key] = policy_net_state_dict[key]*TAU + target_net_state_dict[key]*(1-TAU)
            agent.target_net.load_state_dict(target_net_state_dict)

            if new_pos[0] - agent_pos[0] + new_pos[1] - agent_pos[1] == 0:
              agent.time_stopped += 1
            else:
              agent.time_stopped = 0
          
            # Give Rewards
            agent.finished = door_reached # If agent reached door
            agent.increment_score(reward)
            agent.set_hazardCooldown(new_hazardCooldown)

      # If agent performance time is up, reset agents and level
      if self.perf_time == 0:
        half = len(self.agentList)//2
        self.agentList.sort(key = lambda x: x.score)
        self.top_score = self.agentList[AGENT_CNT-1].score
        self.perf_time = TRIAL_TIME + (self.gen_num//3) # Was //40 - determine the rate at which perf time increases
        self.gen_num += 1
        self.tileList = np.loadtxt(MAP_STRING, dtype=float)
        for agent in self.agentList:
          agent.steps_done = 0
          agent.set_score(0)
          agent.time_stopped = 0
          agent.coins = 0
          agent.map = np.loadtxt(MAP_STRING, dtype=float)

      # Otherwise, decrement time
      else:
        self.perf_time -= 1
    elif(self.mode == 0):
      old_pos = (self.playerX, self.playerY)
      (self.playerX, self.playerY) = mv.update_position(self.playerX, self.playerY, self.keys, self.tileList)

      if self.playerX - old_pos[0] + self.playerY - old_pos[1] == 0:
        self.time_stopped += 1
      else:
        self.time_stopped = 0
      print(self.time_stopped)
      (temp_score, self.hazardCooldown, self.finished, self.tileList) = mv.check_pickUp(self.tileList, self.playerX, self.playerY, self.time_stopped, self.hazardCooldown, self.score, self.finished)
      self.score = temp_score

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.is_running = False

  # Render tiles to the screen
  def render(self):
    # Draws all of the map tiles
    if(DEBUG_MODE == 0 or self.mode == 0):
      for (row_idx, col_idx), tile in np.ndenumerate(self.tileList):
        pygame.draw.rect(self.screen, lh.getTileColor(tile), (col_idx*25, row_idx*25, 25, 25))

    if(self.mode == 0):
      # Draws the player
      pygame.draw.rect(self.screen, "pink", (self.playerX, self.playerY, PLAYER_WIDTH, PLAYER_HEIGHT))

      #actually renders the updates to the screen
      pygame.display.set_caption("GAN Game - Score: " + str(int(self.score)))
    else:
      for agent in self.agentList:
        # Draws the player
        agent_pos = agent.get_pos()
        pygame.draw.rect(self.screen, "pink", (agent_pos[0], agent_pos[1], PLAYER_WIDTH, PLAYER_HEIGHT))
        
        if(DEBUG_MODE != 0):
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

    self.screen.fill((105,105,105)) # Clear screen before next draw
