from pprint import pprint
import time
from neo.io import Spike2IO
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
import seaborn as sns
import matplotlib

matplotlib.use("TkAgg", force=True)


class Spike2Fig:
    """
    Class used to create a matplotlib figure to plot all signals with starts and ends events.
    """

    def __init__(self):
        self.signalsDf = pd.DataFrame()
        self.startData = {}
        self.endData = {}
        self.startPlots = {}
        self.endPlots = {}
        self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.index = None
        self.startOrEnd = None
        self.axe = None

    def getDataFromSpike2(self, filePath):
        """
        Read a file .smr and get all data.
        """
        tmp = time.time()
        reader = Spike2IO(filename=filePath)
        data = reader.read()
        print(
            "File {} read in {} seconds".format(filePath, round(time.time() - tmp, 2))
        )
        return data[0].segments[0]

    def getCleanData(self, filename):
        """
        Convert data read from the .smr file to DataFrame for analog signals and to dict for events (starts ans ends).
        """
        tmp = time.time()
        data = self.getDataFromSpike2(filename)
        oldGVS = []
        oldGVSTimes = []
        gvsReady = False
        for signals in data.analogsignals:
            for j in range(len(signals.array_annotations["channel_ids"])):
                name = signals.array_annotations["channel_names"][j]
                values = signals[:, j].magnitude
                if name == "GVS":
                    oldGVS = values[:, 0]
                    oldGVSTimes = signals.times.magnitude
                    gvsReady = True
                else:
                    if self.signalsDf.empty:
                        self.signalsDf["Times"] = signals.times.magnitude
                    self.signalsDf[name.replace("vr", "")] = values
                if gvsReady and not self.signalsDf.empty:
                    # execTime = self.getGVSStartsEnds(oldGVS, oldGVSTimes)
                    if len(oldGVSTimes) == len(self.signalsDf["Times"]):
                        self.signalsDf["GVS"] = oldGVS
                    else:
                        newGVS = np.interp(
                            self.signalsDf["Times"].tolist(), oldGVSTimes, oldGVS
                        )
                        self.signalsDf["GVS"] = newGVS
                    gvsReady = False

        for event in data.events:
            values = event.magnitude
            if "MS-" in event.name:
                name = event.name.replace("MS-", "")
                self.startData[name] = values.tolist()
                self.endData[name] = []
            if "S_" in event.name:
                name = event.name.replace("S_", "")
                self.startData[name] = values.tolist()
            if "E_" in event.name:
                name = event.name.replace("E_", "")
                self.endData[name] = values.tolist()

        print("Data collected in {} seconds".format(round(time.time() - tmp, 2)))

        if "GVS" not in list(self.startData.keys()):
            self.getGVSStartsEnds(oldGVS, oldGVSTimes)

    def getGVSStartsEnds(self, gvs, times):
        """
        Compute all starts and ends for the GVS.
        """
        tmp = time.time()
        threshold = -0.001
        s = []
        e = []
        lookStart = True
        lookEnd = False
        for i in range(len(gvs)):
            if lookStart and gvs[i] <= threshold:
                s.append(times[i])
                lookStart = False
            if not lookStart and gvs[i] > threshold:
                lookStart = True

            if lookEnd and gvs[i] <= -threshold:
                e.append(times[i])
                lookEnd = False
            if not lookEnd and gvs[i] > -threshold:
                lookEnd = True
        self.startData["GVS"] = s
        self.endData["GVS"] = e
        print("GVS bursts calculated in {} seconds".format(round(time.time() - tmp, 2)))

    def saveDataInTxt(self, filename):
        """
        Save all data (analog signals and start and end events) in a .txt file readable by spike2.
        """
        tmp = time.time()
        s = pd.DataFrame()
        for k, v in self.startData.items():
            sTmp = pd.DataFrame({k: v})
            s = pd.concat([s, sTmp], axis=1)
        s = s.add_prefix("S_")
        e = pd.DataFrame()
        for k, v in self.endData.items():
            eTmp = pd.DataFrame({k: v})
            e = pd.concat([e, eTmp], axis=1)
        e = e.add_prefix("E_")
        df = pd.concat([self.signalsDf, s, e], axis=1)
        df = df.fillna(0)
        df.to_csv(filename, index=None, sep=",", mode="a")
        print(
            "File {} saved in {} seconds".format(filename, round(time.time() - tmp, 2))
        )

    def onpress(self, event):
        """
        When you click on the middle button of the mouse, you add a start event (above the Y axe) or a end event (below the Y axe) on the selected graph.
        """
        if event.inaxes and event.button == 2:
            axLabel = event.inaxes.yaxis.get_label().get_text()
            if event.ydata >= 0:
                self.startData[axLabel].append(event.xdata)
                self.startData[axLabel].sort()
                self.startPlots[axLabel].set_positions(self.startData[axLabel])
            else:
                self.endData[axLabel].append(event.xdata)
                self.endData[axLabel].sort()
                self.endPlots[axLabel].set_positions(self.endData[axLabel])
            event.canvas.draw()

    def onpick(self, event):
        """
        When you click on an event with the left click, you will move it where you release your click (only on the X axe).
        When you click on an event with the right click, you will delete it.
        """
        if event.mouseevent.inaxes:
            axLabel = event.mouseevent.inaxes.yaxis.get_label().get_text()
            if event.mouseevent.button == 1:
                eventsArtist = event.artist
                self.index = event.ind[0]
                self.startOrEnd = eventsArtist.get_label()
                self.axe = axLabel
            if event.mouseevent.button == 3:
                eventsArtist = event.artist
                if eventsArtist.get_label() == "Starts":
                    i = event.ind[0]
                    del self.startData[axLabel][i]
                    self.startPlots[axLabel].set_positions(self.startData[axLabel])
                if eventsArtist.get_label() == "Ends":
                    i = event.ind[0]
                    del self.endData[axLabel][i]
                    self.endPlots[axLabel].set_positions(self.endData[axLabel])
                event.canvas.draw()

    def onrelease(self, event):
        """
        You will move the previously selected event at the released location (only on the X axe).
        """
        if event.inaxes:
            if self.axe == event.inaxes.yaxis.get_label().get_text():
                if self.startOrEnd == "Starts":
                    self.startData[self.axe][self.index] = event.xdata
                    self.startData[self.axe].sort()
                    self.startPlots[self.axe].set_positions(self.startData[self.axe])
                if self.startOrEnd == "Ends":
                    self.endData[self.axe][self.index] = event.xdata
                    self.endData[self.axe].sort()
                    self.endPlots[self.axe].set_positions(self.endData[self.axe])

                self.index = None
                self.startOrEnd = None
                self.axe = None
                event.canvas.draw()

    def plotSignal(self, ax, name):
        """
        Plot the given axe with the analog signal and the start en end events.
        """
        tmp = time.time()
        ax.clear()
        times = np.linspace(0, self.signalsDf["Times"].iloc[-1], num=100001)
        values = np.interp(times, self.signalsDf["Times"], self.signalsDf[name])
        df = pd.DataFrame({"Times": times, name: values})
        sns.lineplot(x=df["Times"], y=df[name], ax=ax)
        (self.startPlots[name],) = ax.eventplot(
            self.startData[name],
            orientation="horizontal",
            colors="g",
            lineoffsets=0.25,
            linelengths=0.5,
            picker=True,
            pickradius=5,
            label="Starts",
        )
        (self.endPlots[name],) = ax.eventplot(
            self.endData[name],
            orientation="horizontal",
            colors="r",
            lineoffsets=-0.25,
            linelengths=0.5,
            picker=True,
            pickradius=5,
            label="Ends",
        )
        print("Axe {} ploted in {} seconds".format(name, round(time.time() - tmp, 2)))

    def setupFig(self):
        """
        Create the Figure with 2 axes, the GVS and the L-Rost.
        """
        nbSignals = len(self.signalsDf.keys())-1

        sns.set_style("darkgrid")
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.fig.subplots_adjust(right=0.9, bottom=0.25)
        self.gs = self.fig.add_gridspec(nbSignals, 2, width_ratios=[5,1])

        
        i=0
        first = None
        for k in self.signalsDf.keys():
            if k != "Times":
                ax = self.fig.add_subplot(self.gs[i, 0], sharex = first)
                self.plotSignal(ax, k)
                if i < nbSignals -1:
                    ax.get_xaxis().set_visible(False)
                if i == 0:
                    first = ax
                    ax.set(xlim=(0, self.signalsDf["Times"].iloc[-1]))
                i += 1

        # self.fig.axes

        # self.ax1 = self.fig.add_subplot(211)
        # self.ax2 = self.fig.add_subplot(212, sharex=self.ax1)

        # self.plotSignal(self.ax1, "GVS")
        # self.plotSignal(self.ax2, "L-Rost")

        self.fig.subplots_adjust(hspace=0.1)
        self.fig.legend(
            handles=[self.startPlots["GVS"], self.endPlots["GVS"]],
            bbox_to_anchor=(0.5, -0.3),
            loc="lower center",
            ncol=2,
        )
        self.fig.tight_layout()


if __name__ == "__main__":
    myFig = Spike2Fig()
    filePath = "Data_thomas/230407-galv-s54-analyse/230407-galv-s54_000.smr"
    myFig.getCleanData(filePath)
    myFig.setupFig()
