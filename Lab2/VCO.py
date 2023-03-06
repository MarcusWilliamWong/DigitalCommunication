'''
Author       : Eureke
Date         : 2023-02-08 22:00:00
LastEditors  : Marcus Wong
LastEditTime : 2023-02-08 23:32:57
Description  : 
'''
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
# initialise
nsamples = 500
clock = np.empty(shape=(2, nsamples))
fi = 1/64
p0 = 0
alpha = 0.05
volt = 0.1

# generate two branch of digital clock
for t in range(nsamples):
  f0 = fi + alpha * volt
  w0 = 2*np.pi*f0
  clock[0, t] = np.cos(w0*t+p0)
  clock[1, t] = np.sin(w0*t+p0)
  if (t == (nsamples // 2)):
    volt *= 10

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(clock[0], color='r')
ax.legend(labels = ('cos', 'sin'))
ax.set_xlabel('t')
ax.set_ylabel('Amplitude')
plt.show()