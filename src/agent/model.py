import numpy as np
from src.utils.constants import *
from src.agent.model_v2 import *
import random

# Get number of actions from gym action space
n_actions = 4
action_space = [0, 1, 2, 3]

# Get the number of state observations
n_observations = (AGENT_VISION_RADIUS*2+1)**2

class Agent:
  def __init__(self, device):
    self.map = np.zeros((SCREEN_SIZE, SCREEN_SIZE))
    self.posXY = (0, 0)
    self.outputs = [0, 0, 0, 0]
    self.score = 0
    self.steps_done = 0
    self.device = device

    # DQN Model objects
    self.policy_net = DQN(n_observations, n_actions)
    self.target_net = DQN(n_observations, n_actions)
    self.target_net.load_state_dict(self.policy_net.state_dict())
    self.optimizer = optim.AdamW(self.policy_net.parameters(), lr=LR, amsgrad=True)
    self.memory = ReplayMemory(10000)

    # Helpers
    self.hazardCooldown = 0
    self.finished = 0
    self.time_stopped = 0

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

  def select_action(self, state):
    global action_space
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * math.exp(-1. * self.steps_done / EPS_DECAY)
    self.steps_done += 1
    if sample > eps_threshold:
      with torch.no_grad():
        # t.max(1) will return the largest column value of each row.
        # second column on max result is index of where max element was
        # found, so we pick action with the larger expected reward.
        return self.policy_net(state).max(1).indices.view(1, 1)
    else:
      return torch.tensor([[random.choice(action_space)]], device=self.device, dtype=torch.long)

  def optimize_model(self):
    if len(self.memory) < BATCH_SIZE:
      return
    transitions = self.memory.sample(BATCH_SIZE)
    # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
    # detailed explanation). This converts batch-array of Transitions
    # to Transition of batch-arrays.
    batch = Transition(*zip(*transitions))

    # Compute a mask of non-final states and concatenate the batch elements
    # (a final state would've been the one after which simulation ended)
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
    # columns of actions taken. These are the actions which would've been taken
    # for each batch state according to policy_net
    state_action_values = self.policy_net(state_batch).gather(1, action_batch)

    # Compute V(s_{t+1}) for all next states.
    # Expected values of actions for non_final_next_states are computed based
    # on the "older" target_net; selecting their best reward with max(1).values
    # This is merged based on the mask, such that we'll have either the expected
    # state value or 0 in case the state was final.
    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    with torch.no_grad():
      next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1).values
    # Compute the expected Q values
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    # Compute Huber loss
    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

    # Optimize the model
    self.optimizer.zero_grad()
    loss.backward()
    # In-place gradient clipping
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    self.optimizer.step()

