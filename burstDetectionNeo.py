from neo.io import Spike2IO
import matplotlib.pyplot as plt
from pprint import pprint
import numpy as np
import time
# Import burst detection functions
from neurodsp.burst import detect_bursts_dual_threshold, compute_burst_stats
# Import utilities for loading and plotting data
from neurodsp.plts.time_series import plot_time_series, plot_bursts


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

def plotData(data, withBurst=False):
    dataSize = getDataSize(data)
    fig, axs = plt.subplots(dataSize, sharex=True)

    maxTime = getMaxTime(data)
    i = 0
    for event in data.events:
        if len(event) > 0:
            axs[i].hlines(1,0,maxTime)
            axs[i].eventplot(event.magnitude, orientation='horizontal', colors='b')
            axs[i].set(ylabel=event.name)
            i += 1
            print("Event {} done".format(event.name))

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
                axs[i].plot(signals.times.magnitude, signals[:,j].magnitude)
            axs[i].set(ylabel=signals.array_annotations['channel_names'][j])
            i += 1
            print("Analog Signal {} done".format(signals.array_annotations['channel_names'][j]))
            
    plt.xlabel("Time (s)")
    plt.xlim([0, maxTime])
    plt.show()

def getBurst(data, fs, amp_dual_thresh, f_range):
    return detect_bursts_dual_threshold(data, fs, amp_dual_thresh, f_range)

def getBurstStats(burst, fs):
    return compute_burst_stats(burst, fs)

if __name__ == "__main__":
    filePath = "Data_thomas/230407-galv-s54-analyse/230407-galv-s54_000.smr"
    data = getDataFromSpike2(filePath)
    plotData(data,True)



# print("AnalogSignal 1 : {}".format(data[0].segments[0].analogsignals[0]))
# print(vars(data[0].segments[0].analogsignals[0]))
# print("Event 1 : {}".format(data[0].segments[0].events[0]))
# print(vars(data[0].segments[0].events[0]))




"""
data = 1 block
block = 1 segment
segment = list of analog signals + list of events
"""