import sys
import numpy as np


def generate_and_compute_eigen(size):
    matrix = np.random.random((size, size))
    eigenvalues, eigenvectors = np.linalg.eig(matrix)

    return eigenvectors

def handler(event):
    size = event.get("size")
    return generate_and_compute_eigen(size)


if __name__ == "__main__":
    event = {"size": int(sys.argv[1])}
    res = handler(event)
    print(res)
