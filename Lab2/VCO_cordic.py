'''
Author       : Eureke
Date         : 2023-02-04 14:30:33
LastEditors  : Marcus Wong
LastEditTime : 2023-02-07 11:39:20
Description  : 
'''
import numpy as np
import matplotlib.pyplot as plt

# VCO initialisation
# when t = 0, cosine output & sine outpute
c = 1
s = 0
c_delay = 0
s_delay = 0

# voltage controll frequency
volt = 0
VCOgain = 0.005

# sampling rate
bit_len = 16
fc = 0.125
f0 = 0.01
fi = 0

# VCO output
sine = np.array([0], dtype=np.float64)
cosine = np.array([1], dtype=np.float64)

# VCO, Cordic
for t in range(3):
  c_delay = c
  s_delay = s
  # voltage controlled relation
  # f0 = fi + alpha * volt
  # w0 = 2*np.pi*f0
  w0 = 2*np.pi*fc
  # output, rotate
  c = c_delay * np.cos(w0) - s_delay * np.sin(w0)
  s = s_delay * np.cos(w0) + c_delay * np.sin(w0)
  cosine = np.append(cosine, c)
  sine = np.append(sine, s)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_aspect(1)
ax.plot(cosine, sine)
plt.show()