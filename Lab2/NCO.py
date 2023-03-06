'''
Author       : Eureke
Date         : 2023-02-07 06:55:28
LastEditors  : Marcus Wong
LastEditTime : 2023-02-08 22:00:16
Description  : 
'''
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
# initialise
nsamples = 100
clock = np.empty(shape=(2, nsamples))
f0 = 1/32
p0 = 0
w0 = 2*np.pi*f0

# generate two branch of digital clock
for t in range(nsamples):
  clock[0, t] = np.cos(w0*t+p0)
  clock[1, t] = np.sin(w0*t+p0)

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax1.set_aspect(1)
ax1.plot(clock[0], clock[1])
ax1.plot(clock[0][0], clock[1][0], color='r')
ax1.set_xlabel('In-phase')
ax1.set_ylabel('Quadrature')

ax2 = fig.add_subplot(212)
ax2.plot(clock[0], color='r')
ax2.plot(clock[1])
ax2.legend(labels = ('cos', 'sin'))
ax2.set_xlabel('t')
ax2.set_ylabel('Amplitude')
plt.show()