import numpy as np

class Agent:
  def __init__(self):
    self.numInputs = 402
    self.numOutputs = 4
    self.dims = np.array([self.numInputs, 40, self.numOutputs])
    self.weights = []
    for i in range(self.dims.size-1)
        self.weights.append(np.random.rand(self.dims[i], self.dims[i+1]))

    def feed_forward(self, inputs):
        layer = np.array(inputs)
        for w in self.weights:
            layer = layer@w
        return np.argmax(layer)

    

    
