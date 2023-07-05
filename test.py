import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, CheckButtons
 
class Figure:
    def __init__(self, nbRows):
        self.fig = plt.figure()
        self.fig.subplots_adjust(right=0.9, bottom=0.25)
        self.nbRows = nbRows
        self.gs = fig.add_gridspec(3, 2, width_ratios=[5,1])
        self.subplots = self.setupSubplots()

    def setupSubplots(self):
        subplots = []
        for i in range(self.nbRows):
            subplots.append(Subplot(self.fig.add_subplot(gs[i, 0])))
        subplots.append(self.fig.add_subplot(gs[:, 1]))
        return subplots

class Subplot:
    def __init__(self, ax):
        self.fig = plt.figure()
        self.label = ""
        self.ax = ax
        self.visible = True
        self.dataX = []
        self.dataY = []

fig = plt.figure()

gs = fig.add_gridspec(3, 2, width_ratios=[5,1])
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[1, 0])
ax3 = fig.add_subplot(gs[2, 0])
axB = fig.add_subplot(gs[:, 1])

fig.subplots_adjust(right=0.9, bottom=0.25)
 
x1 = np.array([0, 1, 2, 3])
y1 = np.array([5, 2, 8, 6])
ax1.plot(x1, y1, color="blue", marker="o")
 
x2 = np.array([0, 1, 2, 3])
y2 = np.array([10, 2, 0, 12])
ax2.plot(x2, y2, color="green", marker="o")
 
x3 = np.array([0, 1, 2, 3])
y3 = np.array([0, 3, 2, 19])
ax3.plot(x3, y3, color="yellow", marker="o")

lines = [ax1, ax2, ax3]
labels = ["ax1", "ax2", "ax3"]
 
 
def func(label):
    index = labels.index(label)
    lines[index].set_visible(not lines[index].get_visible())
    ratios = gs.get_height_ratios()
    ratios[index] = (ratios[index]-1)*-1
    gs.set_height_ratios(ratios)
    for i in range(len(lines)):
        lines[i].set_position(gs[i,0].get_position(fig))
    fig.canvas.draw()
 
 
label = [True, True, True]

plot_button = CheckButtons(axB, labels, label)
plot_button.on_clicked(func)

plt.tight_layout()
plt.show()

if __name__ == "__main__":
    fig = Figure(3)