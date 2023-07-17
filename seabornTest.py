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

def getGVSStarts(gvsDf):
    threshold = -0.11
    starts = []
    look = True
    for i in range(len(gvsDf['GVS'])):
        if look and gvsDf['GVS'][i]<=threshold:
            starts.append(gvsDf['Times'][i])
            look = False
        if not look and gvsDf['GVS'][i]>threshold:
            #starts.append(times[i])
            look = True
    return starts


def onpick(event):
    global tmp
    eventsArtist = event.artist
    tmp = event.ind[0]
    value = eventsArtist.get_positions()[tmp]
    print("Event {} : {}".format(tmp, value))


def onRelease(event):
    global s
    global tmp
    if tmp:
        s[tmp] = event.xdata
        s.sort()
        startEvents.set_positions(s)

        tmp = None
        event.canvas.draw()




if __name__ == "__main__":
    # GET
    filePath = "Data_thomas/230407-galv-s54-analyse/230407-galv-s54_000.smr"
    data = getDataFromSpike2(filePath)
    gvsDf, signalsDf, eventsDf = fromDataToDf(data)
    s = getGVSStarts(gvsDf)
    tmp = None

    # PRINT
    fig, ax = plt.subplots()
    sns.set_style('darkgrid')

    #sns.lineplot(x=gvsDf['Times'], y=gvsDf['GVS'], ax=ax)
    startEvents, = ax.eventplot(s, orientation='horizontal', colors='g', lineoffsets=0, picker=True, pickradius=5)

    ax.set(xlim=(0, gvsDf['Times'].iloc[-1]))
    fig.canvas.mpl_connect('pick_event', onpick)
    fig.canvas.mpl_connect('button_release_event', onRelease)
    plt.show()