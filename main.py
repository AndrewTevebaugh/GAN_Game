import sys
import pygame
from src.game.game import Game

import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple, deque
from itertools import count

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

# from src.gan.generate import generate_levels

if __name__ == "__main__":
  # Uncomment the following lines when you are ready to use the GAN-generated levels
  # print("Generating levels with GAN...")
  # generate_levels()
  # print("Levels generated successfully.")
  # set up matplotlib
  is_ipython = 'inline' in matplotlib.get_backend()
  if is_ipython:
    from IPython import display

  plt.ion()
  # if GPU is to be used
  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  if torch.cuda.is_available():
    num_episodes = 600
  else:
    num_episodes = 50

  print("Running the game...")
  
  # Initialize Pygame
  pygame.init()

  # Get runtime type (0 for human, 1 for agent)
  run_type = sys.argv[1]

  # Set up the game
  game = Game(run_type, torch_device=device)
  # game.initialize()

  # Run the game loop
  while game.is_running:
    game.handle_events()
    game.update()
    game.render()

    if game.gen_num > num_episodes:
      break

  # Clean up Pygame
  pygame.quit()
  # print("Final score: " + str(int(game.score)))

# Ignore this for now
episode_durations = []

def plot_durations(show_result=False):
    plt.figure(1)
    durations_t = torch.tensor(episode_durations, dtype=torch.float)
    if show_result:
        plt.title('Result')
    else:
        plt.clf()
        plt.title('Training...')
    plt.xlabel('Episode')
    plt.ylabel('Duration')
    plt.plot(durations_t.numpy())
    # Take 100 episode averages and plot them too
    if len(durations_t) >= 100:
        means = durations_t.unfold(0, 100, 1).mean(1).view(-1)
        means = torch.cat((torch.zeros(99), means))
        plt.plot(means.numpy())

    plt.pause(0.001)  # pause a bit so that plots are updated
    if is_ipython:
        if not show_result:
            display.display(plt.gcf())
            display.clear_output(wait=True)
        else:
            display.display(plt.gcf())