from neo.io import Spike2IO
import matplotlib.pyplot as plt
from pprint import pprint
import numpy as np
import time
# Import burst detection functions
from neurodsp.burst import detect_bursts_dual_threshold, compute_burst_stats
# Import utilities for loading and plotting data
from neurodsp.plts.time_series import plot_time_series, plot_bursts

tmp = 0
starts = []

def getDataFromSpike2(filePath):
    reader = Spike2IO(filename=filePath)
    data = reader.read()
    return data[0].segments[0]

def getAnalogSignalsSize(data):
    size = 0
    for signal in data.analogsignals:
        size += len(signal.array_annotations["channel_ids"])
    return size

def getEventsSize(data):
    size = 0
    for event in data.events:
        if len(event) > 0:
            size += 1
    return size

def getDataSize(data):
    return getAnalogSignalsSize(data) + getEventsSize(data)

def getMaxTime(data):
    max = -1
    for signal in data.analogsignals:
        if signal.times[-1] > max:
            max = signal.times[-1]
    return max

def getEventCount(event):
    return len(event)

def getAllEventCount(data):
    counts = {}
    for event in data.events:
        counts[event.name] = len(event)
    return counts

def plotData(data, plotEvents, plotSignals, withBurst=False):
    eventsSize = getEventsSize(data) if plotEvents else 0
    signalsSize = getAnalogSignalsSize(data) if plotSignals else 0
   
    dataSize = eventsSize + signalsSize
    fig, axs = plt.subplots(dataSize, sharex=True)

    maxTime = getMaxTime(data)
    i = 0
    if plotEvents:
        for event in data.events:
            if len(event) > 0:
                axs[i].hlines(1,0,maxTime)
                axs[i].eventplot(event.magnitude, orientation='horizontal', colors='b')
                axs[i].set(ylabel=event.name)
                i += 1
                print("Event {} done".format(event.name))

    if plotSignals:
        for signals in data.analogsignals:
            for j in range(len(signals.array_annotations["channel_ids"])):
                if withBurst:
                    amp_dual_thresh = (1,2)
                    f_range = (12,22)
                    if signals.array_annotations['channel_names'][j] == "GVS":
                        f_range = (1,5)

                    burst = getBurst(np.concatenate(signals[:,j].magnitude), signals._sampling_rate.magnitude, amp_dual_thresh, f_range)
                    plot_bursts(signals.times.magnitude, signals[:,j].magnitude, burst, axs[i])
                else:
                    times = np.linspace(0, signals.times.magnitude[-1], num=100001)
                    values = np.interp(times, signals.times.magnitude, signals[:,j].magnitude[:,0])
                    
                    axs[i].plot(times, values)
                axs[i].set(ylabel=signals.array_annotations['channel_names'][j], xlabel=None)
                i += 1
                print("Analog Signal {} done".format(signals.array_annotations['channel_names'][j]))
            
    plt.xlabel("Time (s)")
    plt.xlim([0, maxTime])
    plt.show()

def getBurst(data, fs, amp_dual_thresh, f_range):
    return detect_bursts_dual_threshold(data, fs, amp_dual_thresh, f_range)

def getBurstStats(burst, fs):
    return compute_burst_stats(burst, fs)

def getGVS(data):
    gvs = []
    times = []
    for signals in data.analogsignals:
        if "GVS" in signals.array_annotations["channel_names"]:
            i = np.where(signals.array_annotations["channel_names"] == "GVS")[0]
            gvs = signals[:,i].magnitude
            times = signals.times.magnitude
    return gvs, times

def getGVSStarts(gvs, times):
    threshold = -0.11
    starts = []
    look = True
    for i in range(len(gvs)):
        if look and gvs[i]<=threshold:
            starts.append(times[i])
            look = False
        if not look and gvs[i]>threshold:
            #starts.append(times[i])
            look = True
    return starts

def on_press(event):
    if event.inaxes == axs[0]:
        print("Press x : {}".format(event.xdata))
        global tmp
        tmp = nearestX(starts,event.xdata)
        print("Index press : {}".format(tmp))
    # event.canvas.figure.axes[0].clear()
    # event.canvas.figure.axes[0].hlines(1,0,times[-1])
    # event.canvas.figure.axes[0].eventplot(starts, orientation='horizontal', colors=color)
    # event.canvas.figure.axes[0].set(ylabel="Starts")
    # event.canvas.draw()

def on_release(event):
    if event.inaxes == axs[0]:
        global starts
        print("Release x : {}".format(event.xdata))
        print("Index release : {}".format(nearestX(starts,event.xdata)))
        
        starts[tmp] = event.xdata
        p.set_positions(starts)
        event.canvas.draw()

def nearestX(starts, x):
    #return min(enumerate(starts), key=lambda i: abs(i[1]-x))
    return min(range(len(starts)), key=lambda i: abs(starts[i]-x))

if __name__ == "__main__":
    filePath = "Data_thomas/230407-galv-s54-analyse/230407-galv-s54_000.smr"
    data = getDataFromSpike2(filePath)
    plotData(data, plotEvents=False, plotSignals=True, withBurst=False)


    # gvs, times = getGVS(data)
    # starts = getGVSStarts(gvs,times)

    # fig, axs = plt.subplots(2, sharex=True)
    # axs[0].hlines(1,0,times[-1])
    # p, = axs[0].eventplot(starts, orientation='horizontal', colors='b')
    # axs[0].set(ylabel="Starts")
    # axs[1].plot(times, gvs)
    # axs[1].set(ylabel="GVS")
    # plt.xlabel("Time (s)")
    # plt.xlim([0, times[-1]])
    # fig.canvas.mpl_connect('button_press_event', on_press)
    # fig.canvas.mpl_connect('button_release_event', on_release)
    # plt.show()





"""
data = 1 block
block = 1 segment
segment = list of analog signals + list of events

On pressed
Get the axe, get the x, get the nearest data if it's near with onPick()

Between
Draw a tmp point ?

On realease
Get the new x, change the data


Class ideas : (use self)
- Figure with settings like x and y axis range, all axes
- Axe with specific y axe range, data
Save the plot so you can change everything you need

TODO :
- Organiser mon code en classes [OK]
- Gérer l'affichage des signaux et events (menu avec des cases à cocher pour afficher ou non les graphes)
- Revoir l'affichage des bursts (xlabel)
- Gérer les inputs pour déplacer les events, en ajouter, en supprimer
- Exporter sur spike2 (pas possible à priori, voir export matlab)
"""