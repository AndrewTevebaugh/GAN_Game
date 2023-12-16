import numpy as np
from src.utils.constants import *

class Agent:
  def __init__(self, w=0):
    self.map = np.zeros((SCREEN_SIZE, SCREEN_SIZE))
    self.posXY = (0, 0)
    self.outputs = [0, 0, 0, 0]
    self.score = 0

    # Helpers
    self.hazardCooldown = 0
    self.finished = 0
    self.time_stopped = 0

    if w == 0:
      self.weights = []
      for i in range(AGENT_NN_DIMENSIONS.size-1):
        self.weights.append(np.random.rand(AGENT_NN_DIMENSIONS[i], AGENT_NN_DIMENSIONS[i+1])*AGENT_NN_CHANGE_RATE - AGENT_NN_CHANGE_RATE//2) #*10 -5
    else:
      self.weights = np.copy(w)

  def set_weights(self, weights):
    for i, w in enumerate(weights):
      self.weights[i] = np.copy(w)

  def get_weights(self):
    return self.weights

  def set_pos(self, posXY):
    self.posXY = posXY

  def get_pos(self):
    return self.posXY

  def insert_disp(self, disp):
    np.roll(self.disp_x_history, -1)
    self.disp_x_history[len(self.disp_x_history)-1] = disp[0]
    np.roll(self.disp_y_history, -1)
    self.disp_y_history[len(self.disp_y_history)-1] = disp[1]

  def get_recent_displacement(self):
    sum_x = np.sum(self.disp_x_history)
    sum_y = np.sum(self.disp_y_history)
    return np.sqrt(sum_x**2 + sum_y**2)

  def set_hazardCooldown(self, hc):
    self.hazardCooldown = hc

  def get_hazardCooldown(self):
    return self.hazardCooldown

  def increment_score(self, s):
    self.score += s

  def set_score(self, s):
    self.score = s

  def get_score(self):
    return self.score

  def get_output(self, inputs):
    temp_output = self.feed_forward(inputs)
    self.outputs = np.heaviside(temp_output, 0) # Binary Step activation on output
    return self.outputs

  def feed_forward(self, inputs):
    layer = np.array(inputs)
    for idx, w in enumerate(self.weights):
      layer = layer @ w
      if(idx < len(self.weights) - 1):
        layer = np.fmax(np.zeros(layer.shape), layer) # ReLU activation on hidden layers
    return layer

  def mutate(self):
    # rn = np.random.rand()
    lay = np.random.randint(len(AGENT_NN_DIMENSIONS)-1) # Choose random layer to mutate
    row = np.random.randint(AGENT_NN_DIMENSIONS[lay]) # Choose a random row to mutate all weights for a node
    # col = np.random.randint(self.weights[lay].shape[1]) # Choose a random column to mutate one weight for a node
    rw = np.random.rand(self.weights[lay].shape[1])*AGENT_NN_CHANGE_RATE - AGENT_NN_CHANGE_RATE//2
    # self.weights[lay][row][col] += rw
    self.weights[lay][row] += rw
    # self.weights[lay][row] += rw

def reproduce(p1, p2, o1, o2):
  lay = np.random.randint(len(AGENT_NN_DIMENSIONS)-1)
  lay2 = np.random.randint(len(AGENT_NN_DIMENSIONS)-1)
  temp1 = p1.get_weights()
  temp2 = p2.get_weights()
  temp1[lay] = np.copy(p2.get_weights()[lay])
  temp1[lay2] = np.copy(p1.get_weights()[lay2])
  temp2[lay] = np.copy(p1.get_weights()[lay])
  temp2[lay2] = np.copy(p2.get_weights()[lay2])
  o1.set_weights(temp1)
  o2.set_weights(temp2)
