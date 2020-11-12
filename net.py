import torch.nn.functional as F
import torch
import random
import numpy
from tools import parse_cfg

params = parse_cfg('./settings.cfg')
RANDOM_SEED = params['random_seed']
if params['is_random_seed']:
    random.seed(RANDOM_SEED)
    numpy.random.seed(RANDOM_SEED)

class Snake_nn():
    def __init__(self, layers, weights):
        self.layers = layers
        if weights is None:
            self.init_weights()
        else:
            self.weights = weights

    def forward(self, X):
        '''
        Forward pass of network:
        Arguments:
            X => numpy.array of size (self.input_layer_size, 1)
        Return:
            z3 => numpy.array of size (self.output_layer_size, 1)
        '''
        a1 = self.weights[0]@X + self.weights[3]    
        z1 = F.leaky_relu(torch.from_numpy(a1)).numpy()
        a2 = self.weights[1]@z1 + self.weights[4]
        z2 = F.leaky_relu(torch.from_numpy(a2)).numpy()
        a3 = self.weights[2]@z2 + self.weights[5]
        z3 = torch.sigmoid(torch.from_numpy(a3)).numpy()
        return z3

    def __call__(self, X):
        return self.forward(X)

    def init_weights(self):
        '''
        Init weights for network randomly in range(-5, 5)
        '''
        self.weights1 = numpy.random.uniform(-1, 1, (self.layers[1], self.layers[0]))
        self.weights2 = numpy.random.uniform(-1, 1, (self.layers[2], self.layers[1]))
        self.weights3 = numpy.random.uniform(-1, 1, (self.layers[3], self.layers[2]))
        self.biases1 = numpy.random.uniform(-1, 1, (self.layers[1], 1))
        self.biases2 = numpy.random.uniform(-1, 1, (self.layers[2], 1))
        self.biases3 = numpy.random.uniform(-1, 1, (self.layers[3], 1))
        self.weights = [self.weights1, self.weights2, self.weights3, self.biases1, self.biases2, self.biases3] # Weights list