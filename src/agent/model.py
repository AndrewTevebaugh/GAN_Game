import numpy as np
from src.utils.constants import *

class Agent:
    def __init__(self, w=0):
        self.numInputs = (PLAYER_VISION_RADIUS*2+1)**2 + 5
        self.numOutputs = 4
        self.score = 0
        self.outputs = [0, 0, 0, 0]
        self.X = 0
        self.Y = 0
        self.time_stopped = 0
        self.hazardCooldown = 0
        self.dims = np.array([self.numInputs, 15, 15, self.numOutputs])
        if w == 0:
            self.weights = []
            for i in range(self.dims.size-1):
                self.weights.append(np.random.rand(self.dims[i], self.dims[i+1])*10 - 5)
        else:
            self.weights = np.copy(w)

    def set_weights(self, w):
        for i in range(len(w)):
            self.weights[i] = np.copy(w[i])

    def get_weights(self):
        return self.weights

    def set_pos(self, posXY):
        self.X = posXY[0]
        self.Y = posXY[1]

    def get_pos(self):
        return (self.X, self.Y)

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

    def get_output(self, inputs):
        self.outputs = self.feed_forward(inputs)
        for i in range(len(self.outputs)):
            if self.outputs[i] <= 0:
                self.outputs[i] = 0
            else:
                self.outputs[i] = 1
        return self.outputs

    def feed_forward(self, inputs):
        layer = np.array(inputs)
        for w in self.weights:
            layer = np.dot(layer, w)
        return layer

    def mutate(self):
        rn = np.random.rand()
        lay = np.random.randint(len(self.dims)-1)
        row = np.random.randint(self.dims[lay])
        rw = np.random.rand(self.weights[lay].shape[1]) * 6-3
        self.weights[lay][row] += rw

def reproduce(p1, p2, o1, o2):

    lay = np.random.randint(len(p1.dims)-1)
    temp1 = p1.get_weights()
    temp2 = p2.get_weights()
    temp1[lay] = np.copy(p2.get_weights()[lay])
    temp2[lay] = np.copy(p1.get_weights()[lay])
    o1.set_weights(temp1)
    o2.set_weights(temp2)



    

    
