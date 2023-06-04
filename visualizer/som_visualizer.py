from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm, colors
from matplotlib.collections import PatchCollection, RegularPolyCollection
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Patch, RegularPolygon

from som import SOM


class SOMVisualizer:
    def __init__(self, som: SOM, font_path: str | None = None):
        self.som: SOM = som
        self.font_path: str | None = font_path

        self.data: np.ndarray = som.data
        self.target: np.ndarray = som.target
        self.target_names: list = som.target_names
        self.topology: str = self.som._topology

        if self.font_path is not None:
            self.font_prop = FontProperties(fname=font_path)
        else:
            self.font_prop = FontProperties()  # This will use the default font properties.
        current_font_size = self.font_prop.get_size()
        self.font_prop.set_size(current_font_size * 2)

        self.fontsize = 11
        self.point_size = 200  # size of ○ on hex.

    def add_some_coloured_hexagons(self, umatrix: np.ndarray, colormap: str, ax):
        hex_height_coeff = np.sqrt(3)/2
        hex_radius = 0.58  # Adjust this value to control the gap between hexagons
        linewidth = 0.1
        patches = []
        for y in range(umatrix.shape[0]):
            for x in range(umatrix.shape[1]):
                hexagon = RegularPolygon(
                    (x + 0.5 * (y % 2), y * hex_height_coeff),
                    numVertices=6,
                    radius=hex_radius,
                    orientation=np.radians(0),
                    # alpha=0.2,
                    edgecolor='k',
                    linewidth=linewidth
                )
                patches.append(hexagon)
        pc = PatchCollection(patches, array=np.ravel(umatrix), cmap=colormap)
        ax.add_collection(pc)
        return ax

        # w = 10
        # n_centers = 0
        # pc = RegularPolyCollection(
        #     numsides=6,  # a hexagon
        #     rotation=0,
        #     sizes=(y * (1.3 * 2 * math.pi * w) ** 2 / x,),
        #     # edgecolors=(0, 0, 0, 1),
        #     array=np.ravel(umatrix),
        #     cmap=colormap,
        #     offsets=n_centers,
        #     transOffset=ax.transData,
        # )
        # ax.add_collection(pc, autolim=True)
        return ax

    def add_data_points(self):
        hex_height_coeff = np.sqrt(3)/2
        for i, data_point in enumerate(self.data):
            winner_node = tuple(self.som.winner(data_point))
            x = winner_node[1] + 0.5 * (winner_node[0] % 2)
            y = winner_node[0] * hex_height_coeff
            if self.target is not None and self.target_names is not None:
                color = plt.cm.tab10(float(self.target[i]) / len(self.target_names))
                plt.scatter(x, y, color=color, s=self.point_size, marker='o', edgecolors='k')
                plt.annotate(
                    self.target_names[self.target[i]],
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center',
                    fontsize=self.fontsize,
                    color='black',
                    bbox=dict(facecolor='white', edgecolor='white', boxstyle='round,pad=0.1', alpha=0.8)
                )
            else:
                plt.scatter(x, y, color='black', s=self.point_size, marker='o', edgecolors='k')

    def add_legend(self):
        legend_elements = [
            Patch(facecolor=plt.cm.tab10(float(i) / len(self.target_names)), edgecolor='k', label=self.target_names[i])
            for i in range(len(self.target_names))
        ]
        plt.legend(
            handles=legend_elements,
            loc='upper left',
            bbox_to_anchor=(1.05, 1),
            prop=self.font_prop
        )

    def plot_umatrix(self, colormap: str = 'bone_r', show_data_points: bool = False, show_legend: bool = True):
        """
        Plot the U-Matrix of the trained SOM.

        :param colormap: A string representing the colormap to be used for the U-Matrix visualization.
        :param show_data_points: A boolean indicating whether to show the data points on the U-Matrix.
        :param show_legend: A boolean indicating whether to show the legend for the data points.
        """

        umatrix: np.ndarray = self.som.distance_map().T
        width_padding = 10 if show_legend else 0  # Add extra space for the legend
        fig, ax = plt.subplots(figsize=(self.som.weights.shape[0] + width_padding, self.som.weights.shape[1]))

        ax = self.add_some_coloured_hexagons(umatrix, colormap, ax)
        if show_data_points:
            self.add_data_points()
        if show_legend and self.target is not None and self.target_names is not None:
            self.add_legend()

        xlim_padding = 1
        ylim_padding = 1
        ax.set_xlim(-xlim_padding, umatrix.shape[1] + 0.5 * (umatrix.shape[0] % 2) + xlim_padding)
        ax.set_ylim(-ylim_padding, umatrix.shape[0] * 0.75 + ylim_padding)
        ax.set_aspect('equal')
        plt.xticks([])
        plt.yticks([])
        plt.show()
