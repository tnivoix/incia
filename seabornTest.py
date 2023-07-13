from neo.io import Spike2IO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def getDataFromSpike2(filePath):
        reader = Spike2IO(filename=filePath)
        data = reader.read()
        print("File {} read".format(filePath))
        return data[0].segments[0]

filePath = "Data_thomas/230407-galv-s54-analyse/230407-galv-s54_000.smr"
data = getDataFromSpike2(filePath)

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
    starts = pd.DataFrame({"Start":starts})
    return starts

s = getGVSStarts(gvsDf)

fig, ax = plt.subplots()
sns.set_style('darkgrid')
#g = sns.lineplot(data = s, x="Start", y=[1]*len(s), linestyle='', marker=6, markersize=20, markerfacecolor='red')
sns.lineplot(x=gvsDf['Times'], y=gvsDf['GVS'], ax=ax)
ax.eventplot(s["Start"], orientation='horizontal', colors='g', lineoffsets=0, picker=True, pickradius=5)
ax.set(xlim=(0, gvsDf['Times'].iloc[-1]))

def onpick(event):
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    points = tuple(zip(xdata[ind], ydata[ind]))
    print('onpick points:', points)


fig.canvas.mpl_connect('pick_event', onpick)
#g.axhline(1)
plt.show()


# yf   = rfft(np.array(signalsDf['Lvr-Rost']))
# yf_abs      = np.abs(yf) 
# indices     = yf_abs>300   # filter out those value under 300
# yf_clean    = indices * yf # noise frequency will be set to 0
# clean = irfft(yf_clean)

#sample = signalsDf

# plt.figure(figsize=(8,4))
# sns.set_style('darkgrid')
# #sns.lineplot(x='Times', y='value', hue='variable', data=pd.melt(signalsDf, ['Times']))
# #sns.lineplot(x=signalsDf['Times'], y=signalsDf['Lvr-Rost'])
# #sns.lineplot(x=sample['Times'], y=sample['Lvr-Rost'])
# plt.show()