import numpy as np

# DEBUG Settings
DEBUG_MODE = 1

# Game Constants
MAP_STRING = "src\\game\\levels\\testLevel2.txt"
PLAYER_VELOCITY = 0.2 # 0.2
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_SIZE = 20
PLAYER_WIDTH = 25
PLAYER_HEIGHT = 25

# Agent Constants
AGENT_CNT = 32 # 32
TRIAL_TIME = 60*3
AGENT_VISION_RADIUS = 3
AGENT_NN_NUM_INPUTS = (AGENT_VISION_RADIUS*2+1)**2
AGENT_NN_NUM_OUTPUTS = 4
AGENT_NN_DIMENSIONS = np.array([AGENT_NN_NUM_INPUTS, 25, 25, 15, AGENT_NN_NUM_OUTPUTS])
AGENT_NN_CHANGE_RATE = 50

#DQN Stuff below

# BATCH_SIZE is the number of transitions sampled from the replay buffer
# GAMMA is the discount factor as mentioned in the previous section
# EPS_START is the starting value of epsilon
# EPS_END is the final value of epsilon
# EPS_DECAY controls the rate of exponential decay of epsilon, higher means a slower decay
# TAU is the update rate of the target network
# LR is the learning rate of the ``AdamW`` optimizer
BATCH_SIZE = 128
GAMMA = 0.99
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 1000
TAU = 0.005
LR = 1e-4