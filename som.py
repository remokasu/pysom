from typing import List, Tuple

import numpy as np
from numpy import ndarray
from sklearn.metrics import silhouette_score


class SOM:
    def __init__(self, x_size: int, y_size: int, input_dim: int, epochs: int, learning_rate: float) -> None:
        """
        Initialize the Self-Organizing Map (SOM) with the given parameters.

        :param x_size: The number of nodes in the x dimension.
        :param y_size: The number of nodes in the y dimension.
        :param input_dim: The dimensionality of the input data.
        :param epochs: The number of epochs for training.
        :param learning_rate: The initial learning rate for weight updates.
        """
        self.x_size = x_size
        self.y_size = y_size
        self.input_dim = input_dim
        self.epochs = epochs
        self.learning_rate = learning_rate

        self.weights = np.random.rand(x_size, y_size, input_dim)

    def train(self, data: ndarray) -> None:
        """
        Train the SOM using the given input data.

        :param data: A 2D numpy array containing the input data.
        """
        for epoch in range(self.epochs):
            for sample in data:
                bmu, bmu_idx = self._find_bmu(sample)
                self._update_weights(sample, bmu, bmu_idx, epoch)

        self._compute_performance_metrics(data)

    def _find_bmu(self, sample: ndarray) -> Tuple[ndarray, Tuple[int, int]]:
        """
        Find the Best Matching Unit (BMU) for a given input sample.

        :param sample: A 1D numpy array representing the input sample.
        :return: A tuple containing the BMU and its index in the SOM grid.
        """
        distance_map = np.linalg.norm(self.weights - sample, axis=2)
        bmu_idx = np.unravel_index(np.argmin(distance_map), (self.x_size, self.y_size))
        bmu = self.weights[bmu_idx]
        return bmu, bmu_idx

    def _update_weights(self, sample: ndarray, bmu: ndarray, bmu_idx: Tuple[int, int], epoch: int) -> None:
        """
        Update the weights of the SOM nodes based on the given input sample and BMU.

        :param sample: A 1D numpy array representing the input sample.
        :param bmu: A 1D numpy array representing the BMU.
        :param bmu_idx: A tuple containing the index of the BMU in the SOM grid.
        :param epoch: The current epoch of training.
        """
        for x in range(self.x_size):
            for y in range(self.y_size):
                current_weight = self.weights[x, y, :]
                distance = np.linalg.norm(np.array([x, y]) - np.array(bmu_idx))
                sigma = self._decay_function(epoch)
                if distance <= sigma:
                    influence = np.exp(-distance ** 2 / (2 * sigma ** 2))
                    new_weight = current_weight + self.learning_rate * influence * (sample - current_weight)
                    self.weights[x, y, :] = new_weight

    def _decay_function(self, epoch: int) -> float:
        """
        Calculate the decay function value for the given epoch.

        :param epoch: The current epoch of training.
        :return: The decay function value for the given epoch.
        """
        return np.exp(-epoch / self.epochs) * max(self.x_size, self.y_size) / 2

    def _compute_performance_metrics(self, data: ndarray) -> None:
        """
        Compute performance metrics (quantization error, topological error, and silhouette coefficient) for the SOM.

        :param data: A 2D numpy array containing the input data.
        """
        bmus_idx = self._get_bmus(data)
        self.quantization_error = np.mean([np.linalg.norm(data[i] - self.weights[bmu]) for i, bmu in enumerate(bmus_idx)])
        self.topological_error = self._compute_topological_error(bmus_idx)

        cluster_labels = [y * self.x_size + x for x, y in bmus_idx]

        n_labels = len(set(cluster_labels))
        if 1 < n_labels < len(data):
            self.silhouette_coefficient = silhouette_score(data, cluster_labels)
        else:
            self.silhouette_coefficient = None

    def _get_bmus(self, data: ndarray) -> List[Tuple[int, int]]:
        """
        Get the Best Matching Units (BMUs) for each input sample in the given data.

        :param data: A 2D numpy array containing the input data.
        :return: A list of BMU indices in the SOM grid for each input sample.
        """
        return [self._find_bmu(sample)[1] for sample in data]

    def _compute_topological_error(self, bmus_idx: List[Tuple[int, int]]) -> float:
        """
        Compute the topological error for the SOM based on the given BMUs.

        :param bmus_idx: A list of BMU indices in the SOM grid.
        :return: The topological error for the SOM.
        """
        errors = 0
        for i, bmu in enumerate(bmus_idx[:-1]):
            next_bmu = bmus_idx[i + 1]
            if np.linalg.norm(np.array(bmu) - np.array(next_bmu)) > 1:
                errors += 1
        return errors / len(bmus_idx)
