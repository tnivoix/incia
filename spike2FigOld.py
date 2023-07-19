from neo.io import Spike2IO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pprint import pprint
from static import Side, Root

class Spike2Fig():
    
    def __init__(self):
        self.gvsDf = pd.DataFrame()
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
            reader = Spike2IO(filename=filePath)
            data = reader.read()
            print("File {} read".format(filePath))
            return data[0].segments[0]


    def getCleanData(self, filename):
        data = self.getDataFromSpike2(filename)

        for signals in data.analogsignals:
            for j in range(len(signals.array_annotations["channel_ids"])):
                name = signals.array_annotations["channel_names"][j]
                values = signals[:,j].magnitude

                if name == "GVS":
                    self.gvsDf['Times'] = signals.times.magnitude
                    self.gvsDf[name] = values
                else:
                    if self.signalsDf.empty:
                        self.signalsDf['Times'] = signals.times.magnitude
                    self.signalsDf[name.replace("vr","")] = values

        for event in data.events:
            name = event.name.replace("MS-","")
            if name[0] in [s.name for s in Side] and name[2:] in [r.name for r in Root]:
                values = event.magnitude
                self.startData[name] = values.tolist()
                self.endData[name] = []

    def getGVSStartsEnds(self):
        threshold = -0.001
        s = []
        e = []
        lookStart = True
        lookEnd = False 
        for i in range(len(self.gvsDf['GVS'])):
            if lookStart and self.gvsDf['GVS'][i]<=threshold:
                s.append(self.gvsDf['Times'][i])
                lookStart = False
            if not lookStart and self.gvsDf['GVS'][i]>threshold:
                lookStart = True

            if lookEnd and self.gvsDf['GVS'][i]<= -threshold:
                e.append(self.gvsDf['Times'][i])
                lookEnd = False
            if not lookEnd and self.gvsDf['GVS'][i]> -threshold:
                lookEnd = True
        self.startData["GVS"] = s
        self.endData["GVS"] = e


    def onpress(self, event):
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
        df = self.gvsDf if name == "GVS" else self.signalsDf
        sns.lineplot(x=df['Times'], y=df[name], ax=ax)
        self.startPlots[name], = ax.eventplot(self.startData[name], orientation='horizontal', colors='g', lineoffsets=0.25, linelengths=0.5, picker=True, pickradius=5, label="Starts")
        self.endPlots[name], = ax.eventplot(self.endData[name], orientation='horizontal', colors='r', lineoffsets=-0.25, linelengths=0.5, picker=True, pickradius=5, label="Ends")

    def setupFig(self):
        sns.set_style('darkgrid')
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, sharex=True)

        self.plotSignal(self.ax1, "GVS")
        self.plotSignal(self.ax2, "L-Rost")

        self.ax1.set(xlim=(0, max(self.gvsDf['Times'].iloc[-1], self.signalsDf['Times'].iloc[-1])))
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.fig.canvas.mpl_connect('button_press_event', self.onpress)
        self.fig.canvas.mpl_connect('button_release_event', self.onrelease)
        plt.subplots_adjust(hspace=0.1)
        plt.legend(handles=[self.startPlots["GVS"], self.endPlots["GVS"]], bbox_to_anchor=(0.5, -0.3), loc='lower center', ncol=2)
        self.fig.tight_layout() 
        plt.show()


if __name__ == "__main__":
    myFig = Spike2Fig()
    filePath = "Data_thomas/230407-galv-s54-analyse/230407-galv-s54_000.smr"
    myFig.getCleanData(filePath)
    myFig.getGVSStartsEnds()
    myFig.setupFig()