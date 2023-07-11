import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = [8,5]
plt.rcParams.update({'font.size':18})

#Create a simple signal with two frequencies
data_step   = 0.001
t           = np.arange(start=0,stop=1,step=data_step)
f_clean     = np.sin(2*np.pi*50*t) + np.sin(2*np.pi*120*t)
f_noise     = f_clean + 2.5*np.random.randn(len(t))

plt.plot(t,f_noise,color='c',linewidth=1.5,label='Noisy')
plt.plot(t,f_clean,color='k',linewidth=2,label='Clean')
plt.legend()
plt.show()

from scipy.fft import rfft,rfftfreq

n    = len(t)
yf   = rfft(f_noise)
xf   = rfftfreq(n,data_step)

plt.plot(xf,np.abs(yf))
plt.show()

yf_abs      = np.abs(yf) 
indices     = yf_abs>300   # filter out those value under 300
yf_clean    = indices * yf # noise frequency will be set to 0

plt.plot(xf,np.abs(yf_clean))
plt.show()

from scipy.fft import irfft

new_f_clean = irfft(yf_clean)

plt.plot(t,new_f_clean)
plt.ylim(-6,8)
plt.show()