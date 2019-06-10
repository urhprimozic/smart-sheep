import random
import numpy as np

"""Thanks to Micheal A. Nielsen, "Neural Networks and Deep Learning,
Determination Press,2015"""


# sigmoid function
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


"""
Since a project is not complicated and the only goal is machine learning, I decided not to use a classical approach.
Usually, there is some kind of chromosome system connecting GA and NN. But for this project, I am not using such 
complicated structures. GA is directly affecting the nets; weights and biases are being inherited.
"""

"""
Median nets don't use crossing-over. Instead, every bias/weight is somewhere between the biases/weights
 with the same index od its parents.
 """


class Median:
    def __init__(self, sizes, parent1=None, parent2=None):
        self.num_layers = len(sizes)
        self.num_layers = len(sizes)
        self.sizes = sizes
        if parent1 is None:
            self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
            self.weights = [np.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]
        else:
            self.biases = []
            for i in range(len(sizes[1:])):
                curr = np.vstack((parent1.biases[i].ravel(), parent2.biases[i].ravel()))
                self.biases.append(np.random.uniform(*curr).reshape(parent1.biases[i].shape))
            self.weights = []
            for i in range(len(parent1.weights)):
                curr = np.vstack((parent1.weights[i].ravel(), parent2.weights[i].ravel()))
                self.weights.append(np.random.uniform(*curr).reshape(parent1.weights[i].shape))

    def feed_forward(self, a):
        for b, w in zip(self.biases, self.weights):
            a = sigmoid(np.dot(w, a) + b)
        return a

    def save(self, file_str):
        file = open(file_str, "w")
        file.write(str(self.biases))
        file.write(str(self.weights))
        file.close()
