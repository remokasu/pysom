import unittest

import numpy as np
from sklearn import datasets
from sklearn.datasets import load_iris

from som import SOM


class TestSOM(unittest.TestCase):

    def setUp(self):
        self.iris_data = datasets.load_iris()
        self.som = SOM(self.iris_data, 10, 10, input_dim=4, epochs=100, learning_rate=0.5, initial_radius=5.0, final_radius=1.0)

    def test_initialize_weights_randomly(self):
        self.som.initialize_weights_randomly()
        self.assertIsNotNone(self.som.weights)
        self.assertEqual(self.som.weights.shape, (10, 10, 4))

    def test_initialize_weights_with_pca(self):
        self.som.standardize_data()
        self.som.initialize_weights_with_pca()
        self.assertIsNotNone(self.som.weights)
        self.assertEqual(self.som.weights.shape, (10, 10, 4))

    def test_train(self):
        self.som.standardize_data()
        self.som.initialize_weights_randomly()
        self.som.train()
        self.assertIsNotNone(self.som.quantization_error)
        self.assertIsNotNone(self.som.topological_error)
        self.assertIsNotNone(self.som.silhouette_coefficient)

    def test_winner(self):
        self.som.standardize_data()
        self.som.initialize_weights_randomly()
        self.som.train()
        test_data = np.array([[5.1, 3.5, 1.4, 0.2], [6.5, 3.0, 5.2, 2.0]])
        winner_coords = self.som.winner(test_data)
        self.assertEqual(winner_coords.shape, (2, 2))

    def test_distance_map(self):
        self.som.standardize_data()
        self.som.initialize_weights_randomly()
        self.som.train()
        distance_map = self.som.distance_map()
        self.assertEqual(distance_map.shape, (10, 10))

    def test_shuffle_each_epoch_enabled(self):
        data = np.array([
            [1, 1],
            [1, 0],
            [0, 1],
            [0, 0],
            [0.5, 0.5]
        ])

        som = SOM(
            data=data,
            x_size=2,
            y_size=2,
            input_dim=2,
            epochs=1,
            learning_rate=0.5,
            initial_radius=5.0,
            final_radius=1.0,
            shuffle_each_epoch=True
        )
        original_data = data.copy()

        som.train()
        assert not np.array_equal(som.data, original_data), "Data should be shuffled when shuffle_each_epoch is enabled."

    def test_shuffle_each_epoch_disabled(self):
        data = np.array([
            [1, 1],
            [1, 0],
            [0, 1],
            [0, 0],
            [0.5, 0.5]
        ])

        som = SOM(
            data=data,
            x_size=2,
            y_size=2,
            input_dim=2,
            epochs=1,
            learning_rate=0.5,
            initial_radius=5.0,
            final_radius=1.0,
            shuffle_each_epoch=False
        )
        original_data = data.copy()

        som.train()
        assert np.array_equal(som.data, original_data), "Data should not be shuffled when shuffle_each_epoch is disabled."

    def test_shuffle_preserves_data_target_combination(self):
        iris = load_iris()
        som = SOM(
            data=iris,
            x_size=2,
            y_size=2,
            input_dim=4,
            epochs=1,
            learning_rate=0.5,
            initial_radius=5.0,
            final_radius=1.0,
            shuffle_each_epoch=True
        )

        original_data = som.data.copy()
        original_target = som.target.copy()

        som.train()

        shuffled_data = som.data
        shuffled_target = som.target

        # for i in range(len(original_data)):
        #     shuffled_index = np.where((shuffled_data == original_data[i]).all(axis=1))[0][0]
        #     assert original_target[i] == shuffled_target[shuffled_index], "Data and target combination should be preserved during shuffling."

        for i in range(len(original_data)):
            original_index = np.where((original_data == shuffled_data[i]).all(axis=1))[0][0]
            assert original_target[original_index] == shuffled_target[i], "Data and target combination should be preserved during shuffling."

if __name__ == '__main__':
    unittest.main()
