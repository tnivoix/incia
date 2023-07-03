import scipy.io
import matplotlib.pyplot as plt
import numpy as np
import pickle 
import os
import random

# Import burst detection functions
from neurodsp.burst import detect_bursts_dual_threshold, compute_burst_stats

# Import utilities for loading and plotting data
from neurodsp.plts.time_series import plot_time_series, plot_bursts
from neurodsp.timefrequency.hilbert import amp_by_time

def getEltByNb(list, eltNb):
    return list[eltNb][0][0]

def getEltByName(list, name):
    for elt in list:
        e = elt[0][0]
        if getName(e) == name:
            return e

def getName(element):
    return element[0][0]

def getData(element):
    return element[-1]

def getDataLength(element):
    return element[-2][0][0]

def getFrequency(element):
    return element[2][0][0]

def separateBurst(data, time, burst):
    newData = []
    newTime = []
    lineData = []
    lineTime = []
    for i in range(len(data)):
        if burst[i]:
            lineData.append(data[i])
            lineTime.append(time[i])
        else:
            if len(lineData)>0:
                newData.append(lineData)
                newTime.append(lineTime)
                lineData=[]
                lineTime=[]
    return newData, newTime

def cleanChannels(channels):
    clean = {}
    for e in channels:
        channel = {}
        channel["Name"] = e[0][0][0][0]
        channel["Data"] = np.concatenate(e[0][0][-1])
        if len(e[0][0]) == 9:
            channel["Frequency"] = e[0][0][2][0][0]
        clean[e[0][0][0][0]] = channel
    return clean

def getChannelsFromMatlab(fileName):
    matLabFolder = "tmp/"
    mat = scipy.io.loadmat("{}{}.mat".format(matLabFolder, fileName))
    myList = list(mat.values())[3:]
    return cleanChannels(myList)

def saveChannels(channels, fileName):
    with open("{}.pkl".format(fileName), 'wb+') as f:
        pickle.dump(channels, f)
        print("File {}.pkl saved".format(fileName))

def loadChannels(fileName):
    with open("{}.pkl".format(fileName), 'rb') as f:
        loadChannels = pickle.load(f)
        print("File {}.pkl loaded".format(fileName))
        return loadChannels

def getAllChannels(fileName):
    save_folder = "channels/"
    channels = {}
    if os.path.isfile("{}{}.pkl".format(save_folder, fileName)):
        channels = loadChannels("{}{}".format(save_folder, fileName))
    else:
        channels = getChannelsFromMatlab(fileName)
        saveChannels(channels, "{}{}".format(save_folder, fileName))

    return channels

def plotData(name, data, time, burst=None):
    if burst is not None:
        plot_bursts(time, data, burst, labels=['Data', 'Detected Burst'])
    else:
        plt.plot(time, data)
    plt.xlabel("Time")
    plt.ylabel(name)
    plt.xlim([time[0], time[-1]])
    plt.show()

def getBurst(data, fs, amp_dual_thresh, f_range):
    return detect_bursts_dual_threshold(data, fs, amp_dual_thresh, f_range)

def getBurstStats(burst, fs):
    return compute_burst_stats(burst, fs)

def getPhases(gvs):
    time = np.arange(0,len(gvs["Data"]))*gvs["Frequency"]
    amp_dual_thresh = (1,2)
    f_range = (1,5)
    burst = getBurst(gvs["Data"], 1/gvs["Frequency"], amp_dual_thresh, f_range)
    phases, timePhases = separateBurst(gvs["Data"], time, burst)
    return phases, timePhases

if __name__ == "__main__":
    file_name = "230407-galv-s54_000"
    channels = getAllChannels(file_name)
    for c in channels.keys():
        print(c)
    gvs = channels["GVS"]
    phases, timePhases = getPhases(gvs)

    phase = np.array(phases[0])
    time = np.array(timePhases[0])
    start = time[0]
    end = time[-1]

    R_Caud = channels["Rvr-Caud"]
    #data = R_Caud["Data"][int(start/R_Caud["Frequency"]):int(end/R_Caud["Frequency"])]
    #time = (np.arange(0,len(R_Caud["Data"]))*R_Caud["Frequency"])[int(start/R_Caud["Frequency"]):int(end/R_Caud["Frequency"])]

    data = R_Caud["Data"]
    time = (np.arange(0,len(R_Caud["Data"]))*R_Caud["Frequency"])


    amp_dual_thresh1 = (1,2)
    f_range1 = (12,22)


    burst = getBurst(data, 1/R_Caud["Frequency"], amp_dual_thresh1, f_range1)
    burst_stats = getBurstStats(burst, 1/R_Caud["Frequency"])


    for key, val in burst_stats.items():
        print('{:15} \t: {}'.format(key, val))

    plotData("R Caud Phase 1", data, time, burst)

"""
Il faut des fréquences écartées pour avoir de grands bursts.

GOOD
Tresh = (1.9934078290370691, 0.8897211729293858)
Freq = (9.903038949852569,19.20552144874666)
n_bursts                : 9

GOOD
Tresh = (3.08737421328206, 0.6047442880439077)
Freq = (8.106323680106607,18.039349358052732)
n_bursts                : 9

MID Il a bien les débuts mais les bursts sont petits
Tresh = (0.6741061546987686, 4.911717271069134)
Freq = (24.97996673303694,31.437340788085823)
n_bursts                : 10

MID
Tresh = (0.6745392859854893, 3.7433288310052246)
Freq = (14.220715516760597,21.925703937838577)
n_bursts                : 14

MID
Tresh = (3.8447554283646923, 0.6703361646686343)
Freq = (24.285935446543377,13.36613745355465)
n_bursts                : 14

BAD
Tresh = (3.073466784838541, 1.2571926556715376)
Freq = (22.160890074539495,20.209846194503783)
n_bursts                : 9

BAD
Tresh = (2.893239855604112, 3.4267919214056533)
Freq = (32.333335190181955,42.990037684309584)
n_bursts                : 9
"""

"""
0.01
0.01
0.5
0.5
"""