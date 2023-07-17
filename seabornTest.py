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
    eventsDf = pd.DataFrame()

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

    for event in data.events:
        name = event.name
        values = event.magnitude
        
        tmpDf = pd.DataFrame({name:values})
        eventsDf = pd.concat([eventsDf, tmpDf], axis = 1)
    
    return gvsDf, signalsDf, eventsDf

def getGVSStartsEnds(gvsDf):
    threshold = -0.001
    starts = []
    ends = []
    lookStart = True
    lookEnd = False 
    for i in range(len(gvsDf['GVS'])):
        if lookStart and gvsDf['GVS'][i]<=threshold:
            starts.append(gvsDf['Times'][i])
            lookStart = False
        if not lookStart and gvsDf['GVS'][i]>threshold:
            lookStart = True

        if lookEnd and gvsDf['GVS'][i]<= -threshold:
            ends.append(gvsDf['Times'][i])
            lookEnd = False
        if not lookEnd and gvsDf['GVS'][i]> -threshold:
            lookEnd = True
    return starts, ends

def onpress(event):
    if event.inaxes and event.button == 2:
        if event.ydata >= 0:
            global s
            s.append(event.xdata)
            s.sort()
            startEvents.set_positions(s)
        else:
            global e
            e.append(event.xdata)
            e.sort()
            endEvents.set_positions(e)
        event.canvas.draw()


def onpick(event):
    if event.mouseevent.button == 1:
        global tmp
        global label
        eventsArtist = event.artist
        tmp = event.ind[0]
        label = eventsArtist.get_label()
        value = eventsArtist.get_positions()[tmp]
        print("Event {} : {}".format(tmp, value))
    if event.mouseevent.button == 3:
        eventsArtist = event.artist
        if eventsArtist.get_label() == "Starts":
            global s
            i = event.ind[0]
            del s[i]
            startEvents.set_positions(s)
        if eventsArtist.get_label() == "Ends":
            global e
            i = event.ind[0]
            del e[i]
            endEvents.set_positions(e)
        event.canvas.draw()

def onrelease(event):
    global s
    global e
    global tmp
    global label
    if tmp:
        if label == "Starts":
            s[tmp] = event.xdata
            s.sort()
            startEvents.set_positions(s)
        if label == "Ends":
            e[tmp] = event.xdata
            e.sort()
            endEvents.set_positions(e)

        tmp = None
        label = None
        event.canvas.draw()




if __name__ == "__main__":
    # GET
    filePath = "Data_thomas/230407-galv-s54-analyse/230407-galv-s54_000.smr"
    data = getDataFromSpike2(filePath)
    gvsDf, signalsDf, eventsDf = fromDataToDf(data)
    s, e = getGVSStartsEnds(gvsDf)

    tmp = None
    label = None

    # PRINT
    fig, ax = plt.subplots()
    sns.set_style('darkgrid')

    sns.lineplot(x=gvsDf['Times'], y=gvsDf['GVS'], ax=ax)
    startEvents, = ax.eventplot(s, orientation='horizontal', colors='g', lineoffsets=0.25, linelengths=0.5, picker=True, pickradius=5, label="Starts")
    endEvents, = ax.eventplot(e, orientation='horizontal', colors='r', lineoffsets=-0.25, linelengths=0.5, picker=True, pickradius=5, label="Ends")

    ax.set(xlim=(0, gvsDf['Times'].iloc[-1]))
    fig.canvas.mpl_connect('pick_event', onpick)
    fig.canvas.mpl_connect('button_press_event', onpress)
    fig.canvas.mpl_connect('button_release_event', onrelease)
    plt.show()