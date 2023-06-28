from neo.io import Spike2IO
import matplotlib.pyplot as plt
from pprint import pprint

datafile = "tmp/230407-galv-s54_000.smr"

reader = Spike2IO(filename=datafile)
data = reader.read()

for signal in data[0].segments[0].analogsignals:
    pprint(vars(signal))
    plt.figure()
    plt.plot(signal.times, signal)
    plt.xlabel("Time")
    plt.ylabel(signal.array_annotations['channel_names'][0])
    plt.show()