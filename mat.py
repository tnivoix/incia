import scipy.io
import matplotlib.pyplot as plt

file_name = "230407-galv-s54_000"
mat = scipy.io.loadmat("tmp/{}.mat".format(file_name))
for i in mat:
    print(i)
# plt.figure()
# plt.plot(signal.times, signal)
# plt.xlabel("Time")
# plt.ylabel(signal.array_annotations['channel_names'][0])
# plt.show()