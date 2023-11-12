from pprint import pprint
import time
from neo.io import Spike2IO
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
import seaborn as sns
import matplotlib
import os

matplotlib.use("TkAgg", force=True)


class Spike2Fig:
    """
    Class used to create a matplotlib figure to plot all signals with starts and ends events.
    """

    def __init__(self):
        self.signalsDf = pd.DataFrame()
        self.eventsData = {}
        self.eventPlots = {}
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
        reader = Spike2IO(filename=filePath, try_signal_grouping=False)
        data = reader.read()
        print(
            "File {} read in {} seconds".format(filePath, round(time.time() - tmp, 2))
        )
        return data[0].segments[0]

    def clearDict(self, d):
        for k in d.keys():
            d[k] = [i for i in d[k] if i != 0]
        return d

    def getCleanData(self, filename):
        """
        Convert data read from the .smr file to DataFrame for analog signals and to dict for events (starts ans ends).
        """
        tmp = time.time()
        data = self.getDataFromSpike2(filename)
        eventsFile = filename[:-4] + ".csv"
        
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
                    n = name.replace("vr", "")
                    while len(values) < len(self.signalsDf["Times"]):
                        values = np.append(values, [0])
                    while len(values) > len(self.signalsDf["Times"]):
                       values = np.delete(values, -1, 0)
                    self.signalsDf[n] = values
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
        if os.path.isfile(eventsFile):
            self.eventsData = self.clearDict(pd.read_csv(eventsFile).to_dict('list'))
        else:
            for event in data.events:
                values = event.magnitude
                if "MS-" in event.name:
                    name = event.name.replace("MS-", "S_")
                    self.eventsData[name] = values.tolist()
                    self.eventsData[name.replace("S_", "E_")] = []
                if "S_" in event.name or "E_" in event.name:
                    self.eventsData[name] = values.tolist()
            if(len(self.eventsData) == 0):
                for s in self.signalsDf.keys():
                    if s != "Times" and s != "GVS":
                        self.eventsData["S_{}".format(s)] = []
                        self.eventsData["E_{}".format(s)] = []
        print("Data collected in {} seconds".format(round(time.time() - tmp, 2)))

        if "GVS" in self.signalsDf.columns and "S_GVS" not in list(self.eventsData.keys()):
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
        self.eventsData["S_GVS"] = s
        self.eventsData["E_GVS"] = e
        print("GVS bursts calculated in {} seconds".format(round(time.time() - tmp, 2)))

    def exportDataInTxt(self, filename):
        """
        Save all data (analog signals and start and end events) in a .txt file readable by spike2.
        """
        tmp = time.time()
        events = self.dictToDf(self.eventsData)
        df = pd.concat([self.signalsDf, events], axis=1)
        df = df.fillna(0)
        df.to_csv(filename, index=None, sep=",", mode="a")
        print(
            "File {} exported in {} seconds".format(filename, round(time.time() - tmp, 2))
        )

    def dictToDf(self, d):
        df = pd.DataFrame()
        for k, v in d.items():
            tmp = pd.DataFrame({k: v})
            df = pd.concat([df, tmp], axis=1)
        return df

    def saveEventsInCsv(self, savefile):
        tmp = time.time()
        events = self.dictToDf(self.eventsData)
        events = events.fillna(0)
        events.to_csv(savefile, index=None, sep=",")
        print(
            "File {} saved in {} seconds".format(savefile, round(time.time() - tmp, 2))
        )

    def computePhases(self, filePath):
        tmp = time.time()
        if "S_GVS" in self.eventsData.keys():
            gvs = self.eventsData["S_GVS"]
            filtered_dict = {k:v for (k,v) in self.eventsData.items() if "S_" in k and "GVS" not in k}
            for k, v in filtered_dict.items():
                if len(v) > 0:
                    times = []
                    phases = []
                    j = 0
                    while j - 1 < len(v) and v[j] < gvs[0]:
                            j +=1
                    stop = False
                    for i in range(len(gvs)):
                        if i < len(gvs) - 1:
                            period = gvs[i+1] - gvs[i]
                            while v[j] < gvs[i+1]:
                                times.append(gvs[i])
                                phases.append((v[j] - gvs[i]) / period)
                                if j + 1 >= len(v):
                                    stop = True
                                    break
                                else:
                                    j += 1
                            if stop:
                                break
                    # Export file
                    tmp = time.time()
                    events = pd.DataFrame({"Times":times,"'S-S'_Phase": phases})
                    events.to_csv("{}-Phase Ev-GVS & {}- mode 'S-S'.txt".format(filePath[:-4], k[2:]), index=None, sep=" ")
        print(
            "Phases computed in {} seconds".format(round(time.time() - tmp, 2))
        )




    def onpress(self, event):
        """
        When you click on the middle button of the mouse, you add a start event (above the Y axe) or a end event (below the Y axe) on the selected graph.
        """
        if event.inaxes and event.button == 2:
            axLabel = event.inaxes.yaxis.get_label().get_text()
            if event.ydata >= 0:
                axLabel = "S_" + axLabel
            else:
                axLabel = "E_" + axLabel
            self.eventsData[axLabel].append(event.xdata)
            self.eventsData[axLabel].sort()
            self.eventPlots[axLabel].set_positions(self.eventsData[axLabel])
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
                    axLabel = "S_" + axLabel
                if eventsArtist.get_label() == "Ends":
                    axLabel = "E_" + axLabel
                i = event.ind[0]
                del self.eventsData[axLabel][i]
                self.eventPlots[axLabel].set_positions(self.eventsData[axLabel])
                event.canvas.draw()

    def onrelease(self, event):
        """
        You will move the previously selected event at the released location (only on the X axe).
        """
        if event.inaxes:
            if self.axe == event.inaxes.yaxis.get_label().get_text():
                if self.startOrEnd == "Starts":
                    self.axe = "S_" + self.axe
                if self.startOrEnd == "Ends":
                    self.axe = "E_" + self.axe
                self.eventsData[self.axe][self.index] = event.xdata
                self.eventsData[self.axe].sort()
                self.eventPlots[self.axe].set_positions(self.eventsData[self.axe])
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

        if name not in self.signalsDf.keys():
            name = name[:2]+name[2:].lower()
        
        times = np.linspace(0, self.signalsDf["Times"].iloc[-1], num=100001)
        values = np.interp(times, self.signalsDf["Times"], self.signalsDf[name])
        df = pd.DataFrame({"Times": times, name: values})
        sns.lineplot(x=df["Times"], y=df[name], ax=ax)
        (self.eventPlots["S_"+name],) = ax.eventplot(
            self.eventsData["S_"+name],
            orientation="horizontal",
            colors="g",
            lineoffsets=0.25,
            linelengths=0.5,
            picker=True,
            pickradius=5,
            label="Starts",
        )
        (self.eventPlots["E_"+name],) = ax.eventplot(
            self.eventsData["E_"+name],
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
        sns.set_style("darkgrid")
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax1 = self.fig.add_subplot(211)
        self.ax2 = self.fig.add_subplot(212, sharex=self.ax1)

        name1 = "GVS" if "GVS" in self.signalsDf.columns else self.signalsDf.columns[1]
        name2 = self.signalsDf.columns[1] if self.signalsDf.columns[1] != name1 else self.signalsDf.columns[2]

        self.plotSignal(self.ax1, name1)
        self.plotSignal(self.ax2, name2)

        self.ax1.set(xlim=(0, self.signalsDf["Times"].iloc[-1]))

        self.fig.subplots_adjust(hspace=0.1)
        self.fig.legend(
            handles=[self.eventPlots["S_{}".format(name1)], self.eventPlots["E_{}".format(name1)]],
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
