import scipy.io
import matplotlib.pyplot as plt
import numpy as np

def getName(element):
    return element[0][0]

def getData(element):
    return element[-1]

def getDataLength(element):
    return element[-2][0][0]

def getFrequency(element):
    return element[2][0][0]

file_name = "230407-galv-s54_000"
mat = scipy.io.loadmat("tmp/{}.mat".format(file_name))
myList = list(mat.values())[3:]

elt = myList[0][0][0]
dataLength = getDataLength(elt)
frequency = getFrequency(elt)
maxTime = dataLength*frequency
t = np.arange(0, dataLength)*frequency

plt.figure()
plt.plot(t,getData(elt))
plt.xlabel("Time")
plt.ylabel(getName(elt))
plt.xlim([0, maxTime])
plt.show()


# for i in myList:
#     elt = i[0][0]
#     print("Name = {}".format(getName(elt)))
#     print("Length = {}".format(len(elt)))
#     print("")
#     plt.figure()
#     plt.plot(getData(elt))
#     plt.xlabel("Time")
#     plt.ylabel(getName(elt))
#     plt.show()