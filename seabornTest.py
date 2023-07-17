from neo.io import Spike2IO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pprint import pprint


def getDataFromSpike2(filePath):
        reader = Spike2IO(filename=filePath)
        data = reader.read()
        print("File {} read".format(filePath))
        return data[0].segments[0]


def fromDataToDf(data):
    gvsDf = pd.DataFrame()
    signalsDf = pd.DataFrame()

    for signals in data.analogsignals:
        for j in range(len(signals.array_annotations["channel_ids"])):
            name = signals.array_annotations["channel_names"][j]
            values = signals[:,j].magnitude

            if name == "GVS":
                gvsDf['Times'] = signals.times.magnitude
                gvsDf[name] = values
            else:
                if signalsDf.empty:
                    signalsDf['Times'] = signals.times.magnitude
                signalsDf[name] = values

    starts = {}
    for event in data.events:
        name = event.name
        values = event.magnitude
        starts[name] = values
    
    return gvsDf, signalsDf, starts

def getGVSStartsEnds(gvsDf):
    global starts
    global ends
    threshold = -0.001
    s = []
    e = []
    lookStart = True
    lookEnd = False 
    for i in range(len(gvsDf['GVS'])):
        if lookStart and gvsDf['GVS'][i]<=threshold:
            s.append(gvsDf['Times'][i])
            lookStart = False
        if not lookStart and gvsDf['GVS'][i]>threshold:
            lookStart = True

        if lookEnd and gvsDf['GVS'][i]<= -threshold:
            e.append(gvsDf['Times'][i])
            lookEnd = False
        if not lookEnd and gvsDf['GVS'][i]> -threshold:
            lookEnd = True
    starts["GVS"] = s
    ends["GVS"] = e


def onpress(event):
    if event.inaxes and event.button == 2:
        axLabel = event.inaxes.yaxis.get_label().get_text()
        if event.ydata >= 0:
            global starts
            starts[axLabel].append(event.xdata)
            starts[axLabel].sort()
            startPlots[axLabel].set_positions(starts[axLabel])
        else:
            global ends
            ends[axLabel].append(event.xdata)
            ends[axLabel].sort()
            endPlots[axLabel].set_positions(ends[axLabel])
        event.canvas.draw()


def onpick(event):
    axLabel = event.mouseevent.inaxes.yaxis.get_label().get_text()
    if event.mouseevent.button == 1:
        global index
        global label
        global axe
        eventsArtist = event.artist
        index = event.ind[0]
        label = eventsArtist.get_label()
        axe = axLabel

        value = eventsArtist.get_positions()[index]
        print("Event {} : {} on axe {} : {}".format(index, value, axe, label))
    if event.mouseevent.button == 3:
        eventsArtist = event.artist
        if eventsArtist.get_label() == "Starts":
            global starts
            i = event.ind[0]
            

            del starts[axLabel][i]
            startPlots[axLabel].set_positions(starts[axLabel])
        if eventsArtist.get_label() == "Ends":
            global ends
            i = event.ind[0]
            del ends[axLabel][i]
            endPlots[axLabel].set_positions(ends[axLabel])
        event.canvas.draw()

def onrelease(event):
    global starts
    global ends
    global index
    global label
    global axe
    if axe == event.inaxes.yaxis.get_label().get_text():
        if label == "Starts":
            starts[axe][index] = event.xdata
            starts[axe].sort()
            startPlots[axe].set_positions(starts[axe])
        if label == "Ends":
            ends[axe][index] = event.xdata
            ends[axe].sort()
            endPlots[axe].set_positions(ends[axe])

        index = None
        label = None
        axe = None
        event.canvas.draw()




if __name__ == "__main__":
    # GET
    filePath = "Data_thomas/230407-galv-s54-analyse/230407-galv-s54_000.smr"
    data = getDataFromSpike2(filePath)
    gvsDf, signalsDf, oldStarts = fromDataToDf(data)
    starts = {}
    ends = {}
    getGVSStartsEnds(gvsDf)

    for name in signalsDf.keys():
        print(name)

    index = None
    label = None
    axe = None

    startPlots = {}
    endPlots = {}

    # PRINT
    sns.set_style('darkgrid')
    fig, (ax1, ax2) = plt.subplots(2, sharex=True)


    sns.lineplot(x=gvsDf['Times'], y=gvsDf['GVS'], ax=ax1)
    startPlots["GVS"], = ax1.eventplot(starts["GVS"], orientation='horizontal', colors='g', lineoffsets=0.25, linelengths=0.5, picker=True, pickradius=5, label="Starts")
    endPlots["GVS"], = ax1.eventplot(ends["GVS"], orientation='horizontal', colors='r', lineoffsets=-0.25, linelengths=0.5, picker=True, pickradius=5, label="Ends")

    # sns.lineplot(x=signalsDf['Times'], y=signalsDf['Lvr-Rost'], ax=ax2)
    # startPlots["GVS"], = ax2.eventplot(starts["GVS"], orientation='horizontal', colors='g', lineoffsets=0.25, linelengths=0.5, picker=True, pickradius=5, label="Starts")
    # endPlots["GVS"], = ax2.eventplot(ends["GVS"], orientation='horizontal', colors='r', lineoffsets=-0.25, linelengths=0.5, picker=True, pickradius=5, label="Ends")

    ax1.set(xlim=(0, gvsDf['Times'].iloc[-1]))
    fig.canvas.mpl_connect('pick_event', onpick)
    fig.canvas.mpl_connect('button_press_event', onpress)
    fig.canvas.mpl_connect('button_release_event', onrelease)
    plt.show()

    # TODO : creates starts and ends for 6 signals