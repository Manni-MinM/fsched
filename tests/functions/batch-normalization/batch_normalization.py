import sys
import numpy as np

class BatchNormalization:
    def __init__(self, epsilon=1e-5, momentum=0.9):
        self.epsilon = epsilon
        self.momentum = momentum
        self.running_mean = None
        self.running_var = None

    def forward(self, X, training=True):
        if self.running_mean is None:
            self.running_mean = np.mean(X, axis=0)
            self.running_var = np.var(X, axis=0)

        if training:
            batch_mean = np.mean(X, axis=0)
            batch_var = np.var(X, axis=0)

            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * batch_mean
            self.running_var = self.momentum * self.running_var + (1 - self.momentum) * batch_var

            X_normalized = (X - batch_mean) / np.sqrt(batch_var + self.epsilon)
        else:
            X_normalized = (X - self.running_mean) / np.sqrt(self.running_var + self.epsilon)

        return X_normalized

if __name__ == "__main__":
    size = int(sys.argv[1])
    print(size)
    bn = BatchNormalization()
    X = np.random.randn(size, 10)
    result = bn.forward(X)
    print(result)
