import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, CheckButtons
import matplotlib.colors as mcolors
from abc import ABC, abstractmethod
 
class Figure:
    def __init__(self, nbRows, subplotNames):
        self.fig = plt.figure()
        self.fig.subplots_adjust(right=0.9, bottom=0.25)
        self.nbRows = nbRows
        self.gs = self.fig.add_gridspec(3, 2, width_ratios=[5,1])
        self.subplots = self.setupSubplots(subplotNames)
        plt.tight_layout()

    def setupSubplots(self, subplotNames):
        subplots = {}
        for i in range(self.nbRows):
            subplots[subplotNames[i]] = Row(self, self.fig.add_subplot(self.gs[i, 0]), subplotNames[i])
            subplots[subplotNames[i]].setColor(list(mcolors.TABLEAU_COLORS.values())[i])
        subplots["ButtonVisible"] = Button(self, self.fig.add_subplot(self.gs[:, 1]), [True]*self.nbRows, subplotNames)
        return subplots
    
    def inverseVisible(self, subplotName):
        self.subplots[subplotName].inverseVisible()

    def arrangeRows(self):
        ratios = self.gs.get_height_ratios()
        for i in range(len(ratios)):
            ratios[i] = 1 if list(self.subplots.values())[i].visible else 0
        self.gs.set_height_ratios(ratios)
        for i in range(len(ratios)):
            list(self.subplots.values())[i].ax.set_position(self.gs[i,0].get_position(self.fig))

    def show(self):
        for subplot in self.subplots.values():
            subplot.plot()
        plt.tight_layout()
        plt.show()

    def draw(self):
        self.fig.canvas.draw()

class Subplot(ABC):
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax

    @abstractmethod
    def plot(self):
        pass

class Row(Subplot):
    def __init__(self, fig, ax, name):
        super().__init__(fig,ax)
        self.name = name
        self.visible = True
        self.dataX = []
        self.dataY = []
        self.color = "blue"

    def setData(self, dataX, dataY):
        self.dataX = dataX
        self.dataY = dataY
    
    def setColor(self, color):
        self.color = color
    
    def inverseVisible(self):
        self.visible = not self.visible
        self.ax.set_visible(self.visible)
    
    def plot(self):
        self.ax.plot(self.dataX, self.dataY, color=self.color, marker="o")

class Button(Subplot):
    def __init__(self, fig, ax, label, buttonNames):
        super().__init__(fig,ax)
        self.label = label
        self.buttonNames = buttonNames
        self.p = CheckButtons(ax, buttonNames, label)
        self.p.on_clicked(self.onClicked)
    
    def onClicked(self, label):
        self.fig.inverseVisible(label)
        self.fig.arrangeRows()
        self.fig.draw()

    def plot(self):
        pass


if __name__ == "__main__":
    fig = Figure(3, ["Ax1", "Ax2", "Ax3"])

    x1 = np.array([0, 1, 2, 3])
    y1 = np.array([5, 2, 8, 6])
    fig.subplots["Ax1"].setData(x1, y1)
    
    x2 = np.array([0, 1, 2, 3])
    y2 = np.array([10, 2, 0, 12])
    fig.subplots["Ax2"].setData(x2, y2)
    
    x3 = np.array([0, 1, 2, 3])
    y3 = np.array([0, 3, 2, 19])
    fig.subplots["Ax3"].setData(x3, y3)

    
    fig.show()