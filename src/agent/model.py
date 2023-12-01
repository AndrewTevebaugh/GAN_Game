import numpy as np

class Agent:
    def __init__(self, w=0):
        self.numInputs = 25 + 4
        self.numOutputs = 4
        self.score = 0
        self.outputs = [0, 0, 0, 0]
        self.X = 0
        self.Y = 0
        self.hazardCooldown = 0
        self.dims = np.array([self.numInputs, 40, self.numOutputs])
        if w == 0:
            self.weights = []
            for i in range(self.dims.size-1):
                self.weights.append(np.random.rand(self.dims[i], self.dims[i+1])*4 - 2)
        else:
            self.weights = np.copy(w)

    def set_weights(self, w):
        self.weights = np.copy(w)

    def get_weights(self):
        return self.weights

    def set_pos(self, posXY):
        self.X = posXY[0]
        self.Y = posXY[1]

    def get_pos(self):
        return (self.X, self.Y)

    def set_hazardCooldown(self, hc):
        self.hazardCooldown = hc

    def get_hazardCooldown(self):
        return self.hazardCooldown

    def increment_score(self, s):
        self.score += s

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
        lay = np.random.randint(len(self.dims))
        w = np.randint(len(self.dims[lay]))
        self.weights[lay][w] = rn

def reproduce(p1, p2, o1, o2):

    lay = np.random.randint(len(p1.dims))
    temp1 = np.copy(p1.get_weights())
    temp2 = np.copy(p2.get_weights())
    temp1[lay] = np.copy(p2.get_weights()[lay])
    temp2[lay] = np.copy(p1.get_weights()[lay])
    o1.set_weights(temp1)
    o2.set_weights(temp2)



    

    
