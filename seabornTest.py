from neo.io import Spike2IO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


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
             gvsDf.index = signals.times.magnitude
             gvsDf[name] = values
        else:
             if signalsDf.empty:
                signalsDf.index = signals.times.magnitude
             signalsDf[name] = values

for event in data.events:
    name = event.name
    values = event.magnitude
    
    tmpDf = pd.DataFrame({name:values})
    eventsDf = pd.concat([eventsDf, tmpDf], axis = 1)

sample = signalsDf.sample(1000)
# plt.figure(figsize=(8,4))
# sns.set_style('darkgrid')
# sns.lineplot(data=sample, y='Lvr-Rost', x =sample.index, markersize=0.5)
# plt.show()

fig = px.line(sample, x=sample.index, y='Lvr-Rost')
fig.show()