'''
Author       : Eureke
Date         : 2023-01-24 08:32:38
LastEditors  : Marcus Wong
LastEditTime : 2023-01-24 16:08:20
Description  : 
'''
import numpy as np
from matplotlib import pyplot as plt
from scipy import fft
from scipy import signal

def bin_array(num, m):
  # Convert a positive integer num into an m-bit bit vector
  return np.array(list(np.binary_repr(num).zfill(m))).astype(np.bool)

# import 24 bit digital data
id_num = 2635088
Nbits = 24
tx_bin = bin_array(id_num, Nbits)
print(tx_bin)

# BPSK modulation
# initialise constants and variables
fc = 0.125 # because of Nyquist limit, and normalised carrier frequency 1/8
bit_len = 16 # 16 samples per bit, so there will be 2 periods of carrier wave per bit
s = np.copy(tx_bin)
s_mod = np.empty(0)
t = 0

# based on IQ modulation
for i in range(Nbits):
  for j in range(bit_len):
    # BASK
    s_mod = np.append(s_mod, s[i] * np.cos(2*np.pi*fc*t))
    t += 1

# Show modulated signal
plt.figure()
plt.plot(s_mod)
plt.show()

# Use fft to frequency analyse
plt.figure()
plt.plot(np.abs(fft.fft(s_mod)))
plt.show()

