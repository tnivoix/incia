import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.widgets import CheckButtons
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
 
class Spike2Figure:
    def __init__(self, nbSignals, signalNames):
        self.fig = Figure(figsize=(5,5), dpi=100)
        #self.fig.subplots_adjust(right=0.9, bottom=0.25)
        self.nbSignals = nbSignals
        self.gs = self.fig.add_gridspec(nbSignals, 2, width_ratios=[5,1])
        self.signals = self.setupSignals(signalNames)
        self.showButton = self.setupShowButton(signalNames)
        self.fig.tight_layout()

    def setupSignals(self, signalNames):
        signals = {}
        for i in range(self.nbSignals):
            sharex = None
            if i > 0:
                sharex = signals[signalNames[i-1]].ax
            signals[signalNames[i]] = Signal(self, self.fig.add_subplot(self.gs[i, 0], sharex = sharex), signalNames[i], list(mcolors.TABLEAU_COLORS.values())[i])
            if i < self.nbSignals -1:
                signals[signalNames[i]].ax.get_xaxis().set_visible(False)
        return signals
    
    def setupShowButton(self, signalNames):
        self.showButton = Button(self, self.fig.add_subplot(self.gs[:, 1]), [True]*self.nbSignals, signalNames)

    def inverseVisible(self, signalName):
        self.signals[signalName].inverseVisible()

    def getVisibleSignals(self):
        signals = {}
        for key, value in self.signals.items():
            if value.visible:
                signals[key] = value
        return signals

    def arrangeRows(self):
        visibleSignals = self.getVisibleSignals()
        if len(visibleSignals) > 0:
            newGs = gridspec.GridSpec(len(visibleSignals),2, width_ratios=[5,1])
            i = 0
            for signal in visibleSignals.values():
                signal.ax.set_position(newGs[i,0].get_position(self.fig))
                i += 1
      
    def show(self):
        for subplot in self.signals.values():
            subplot.plot()
        self.fig.tight_layout()
        plt.show()

    def draw(self):
        self.fig.canvas.draw()

class Signal():
    def __init__(self, fig, ax, name, color):
        self.fig = fig
        self.ax = ax
        self.name = name
        self.visible = True
        self.dataX = []
        self.dataY = []
        self.color = color

    def setData(self, dataX, dataY):
        self.dataX = dataX
        self.dataY = dataY
    
    def inverseVisible(self):
        self.visible = not self.visible
        self.ax.set_visible(self.visible)
    
    def plot(self):
        self.ax.plot(self.dataX, self.dataY, color=self.color, marker="o")

class Button():
    def __init__(self, fig, ax, label, buttonNames):
        self.fig = fig
        self.ax = ax
        self.label = label
        self.buttonNames = buttonNames
        self.p = CheckButtons(ax, buttonNames, label).on_clicked(self.onClicked)
    
    def onClicked(self, label):
        print(label)
        self.fig.inverseVisible(label)
        self.fig.arrangeRows()
        self.fig.draw()


# if __name__ == "__main__":
#     fig = MyFigure(3, ["Ax1", "Ax2", "Ax3"])

#     x1 = np.array([0, 1, 2, 3])
#     y1 = np.array([5, 2, 8, 6])
#     fig.subplots["Ax1"].setData(x1, y1)
    
#     x2 = np.array([0, 1, 2, 3])
#     y2 = np.array([10, 2, 0, 12])
#     fig.subplots["Ax2"].setData(x2, y2)
    
#     x3 = np.array([0, 1, 2, 3])
#     y3 = np.array([0, 3, 2, 19])
#     fig.subplots["Ax3"].setData(x3, y3)

    
#     fig.show()