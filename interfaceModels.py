from matplotlib.figure import Figure
from matplotlib.widgets import CheckButtons
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
 
class Spike2Figure:
    def __init__(self, nbSignals, signalNames):
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.fig.subplots_adjust(right=0.9, bottom=0.25)
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
        return Button(self, self.fig.add_subplot(self.gs[:, 1]), [True]*self.nbSignals, signalNames)

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
                signal.ax.get_xaxis().set_visible(False)
                i += 1
            list(visibleSignals.values())[-1].ax.get_xaxis().set_visible(True)

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
        self.p = CheckButtons(ax, buttonNames, label)
        self.p.on_clicked(self.onClicked)
    
    def onClicked(self, label):
        self.fig.inverseVisible(label)
        self.fig.arrangeRows()
        self.fig.draw()
