# Lib for graphs visualisation
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
matplotlib.use("TkAgg")

# Libs for stats
from scipy.stats import circmean, circvar

from static import Root, Side, Color

# date, subject, condition, side, root
class CircularGraph:
    def __init__(self, name):
        self.data = {}
        self.name = name
        self.stats = {}
        self.setupFigure()

    def setupFigure(self):
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.fig.suptitle(self.name)
        ax = self.fig.add_subplot(111, projection="polar")
        ax.set_theta_zero_location("N")  # theta=0 at the top
        ax.set_theta_direction(-1)  # theta increasing clockwise
        ax.set_yticklabels([])
        ax.set_rgrids([])
        ax.set_thetagrids([0, 90, 180, 270], ["0°", "90°", "180°", "270°"])
        ax.set_ylim(0, 1)

    def plotGraph(self):
        ax = self.fig.axes[0]
        i = 0
        for k in self.data.keys():
            mean = circmean(self.data[k])

            r = 1 - circvar(self.data[k])
            ax.plot(self.data[k], [1] * len(self.data[k]), "o", label=k, color=Color(i).name)
            ax.quiver(mean, 0, 0, r, label=k, color=Color(i).name, angles="xy", scale=2)
            i += 1

    def openTxtFile(self, filepath, name):
        df = pd.read_csv(filepath, sep=" ")
        self.data[name] = self.formatPhaseData(df)
        self.calcStats(name)

    def formatPhaseData(self, data):
        phase_numbers = []
        phase_tmp = 1
        row_to_delete = []

        # Look at all phases
        for i in range(data.shape[0]):
            # Check if it's not the first value
            if i != 0:
                # Test if the actual phase time is far away for the previous one
                if data.iloc[i, 0] - data.iloc[i - 1, 0] > 10:
                    time_tmp = data.iloc[i - 1, 0]
                    j=0
                    while time_tmp == data.iloc[i - 1, 0] :
                        # Select the phase to deletion
                        row_to_delete.append(i-1 - j)
                        j += 1
                        time_tmp = data.iloc[i - 1 - j, 0]
                    # Change cycle
                    phase_tmp += 1
            # Write the cycle number in a tmp array
            phase_numbers.append(phase_tmp)

        # Add cycle number to all phases
        data["Phase_Number"] = phase_numbers

        # Remove useless data between phases
        data = data.drop(row_to_delete)

        # Change angles to degree
        data["'S-S'_Phase"] = data["'S-S'_Phase"] * 360

        # Keep only angles
        angles = np.deg2rad(data["'S-S'_Phase"]).sort_values().array

        return angles
    
    def calcStats(self, label):
        if len(self.data[label]) > 0:
            # Nb phases
            n = len(self.data[label])
            self.stats["Number of observations"] = n
            # Mean vector
            mean = circmean(self.data[label])
            self.stats["Mean vector"] = np.rad2deg(mean)
            # Mean vector length
            r = 1 - circvar(self.data[label])
            self.stats["Length of mean vector"] = r
            # Rayleigh test Z
            Z = n * r * r
            self.stats["Rayleigh test (Z)"] = Z
            # Rayleigh test p
            p = self.rayleightest(self.data[label])
            self.stats["Rayleigh test (p)"] = p
            # Rao's spacing test U
            u = 0
            for i in range(n):
                t = 0
                if i == n - 1:
                    t = 2 * np.pi - self.data[label][i] + self.data[label][0]
                else:
                    t = self.data[label][i + 1] - self.data[label][i]
                u += abs(t - 2 * np.pi / n)
            u = 0.5 * u
            self.stats["Rao's spacing test (U)"] = u
    
    def rayleightest(self, data, axis=None, weights=None):
        n = np.size(data, axis=axis)
        Rbar = self._length(data, 1, 0.0, axis, weights)
        z = n * Rbar * Rbar

        # see [3] and [4] for the formulae below
        tmp = 1.0
        if n < 50:
            tmp = (
                1.0
                + (2.0 * z - z * z) / (4.0 * n)
                - (24.0 * z - 132.0 * z**2.0 + 76.0 * z**3.0 - 9.0 * z**4.0)
                / (288.0 * n * n)
            )

        p_value = np.exp(-z) * tmp
        return p_value

    def _length(self, data, p=1, phi=0.0, axis=None, weights=None):
        # Utility function for computing the generalized rectangular components
        # of the circular data.
        if weights is None:
            weights = np.ones((1,))
        try:
            weights = np.broadcast_to(weights, data.shape)
        except ValueError:
            raise ValueError("Weights and data have inconsistent shape.")

        C = np.sum(weights * np.cos(p * (data - phi)), axis) / np.sum(weights, axis)
        S = np.sum(weights * np.sin(p * (data - phi)), axis) / np.sum(weights, axis)

        return np.hypot(S, C)
# Create the figure to display all graphs
def setupFigure(name):
    nbRows = 2
    nbCols = 3

    fig = plt.figure(1, figsize=(nbCols * 4, nbRows * 3))
    i = 1
    for row in range(nbRows):
        for col in range(nbCols):
            ax = fig.add_subplot(nbRows, nbCols, i, projection="polar")
            ax.set_theta_zero_location("N")  # theta=0 at the top
            ax.set_theta_direction(-1)  # theta increasing clockwise
            ax.set_yticklabels([])
            ax.set_rgrids([])
            ax.set_thetagrids([0, 90, 180, 270], ["0°", "90°", "180°", "270°"])
            ax.set_ylim(0, 1)
            if row == 0:
                ax.set_title(Root(col).name)
            if col == 0:
                ax.set_ylabel(
                    "Side : {}".format(Side(row).name), fontsize=10, rotation=0, labelpad=100
                )

            i += 1
    fig.suptitle(name)
    return fig


def addOneGraph(ax, data, label, color, onlyVector):
    data = [x for x in data if str(x) != 'nan']
    mean = circmean(data)

    r = 1 - circvar(data)
    if not onlyVector:
        ax.plot(data, [1] * len(data), "o", label=label, color=color)
    ax.quiver(mean, 0, 0, r, label=label, color=color, angles="xy", scale=2)

def addAllGraphs(fig, data, label, color, onlyVector):
    for value, subplot in zip(data, fig.get_axes()):
        addOneGraph(subplot, value, label, color, onlyVector)


def displayFigure(fig):
    # Create the legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    fig.legend(
        by_label.values(),
        by_label.keys(),
        loc="lower left",
        frameon=False,
    )
    plt.tight_layout()
    plt.show()
