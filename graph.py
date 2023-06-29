# Lib for graphs visualisation
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")

# Libs for stats
from scipy.stats import circmean, circvar

from static import Root, Side


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
