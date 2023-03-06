'''
Author       : Eureke
Date         : 2023-01-24 08:32:01
LastEditors  : Marcus Wong
LastEditTime : 2023-01-25 23:37:04
Description  : QPSK, adjust from BPSK
'''
import numpy as np
from matplotlib import pyplot as plt
from scipy import fft
from scipy import signal

def bin_array(num, m):
  # Convert a positive integer num into an m-bit bit vector
  return np.array(list(np.binary_repr(num).zfill(m))).astype(np.bool)

id_num = 2635088
Nbits = 24
tx_bin = bin_array(id_num, Nbits)
print(tx_bin)

tx_bin = np.append(tx_bin, [0, 0, 0, 0])
Nbits += 4

plt.figure()
plt.title('Original signal')
plt.plot(tx_bin[:24])
plt.show()

# QPSK modulation
# initialise constants and variables
fc = 0.125
bit_len = 16
s = np.copy(tx_bin)
s_mod = np.empty(0)
t = 0

# based on IQ component, constellation diagram {45, 135, 225, 315}
# 4PSK, 1 Baud presents 2 bits, two bits into one group
for i in range(0, Nbits, 2):
  for j in range(bit_len):
    s_mod = np.append(s_mod, (2*s[i] - 1) * np.cos(2*np.pi*fc*t) + (2*s[i+1] - 1) * np.sin(2*np.pi*fc*t))
    t += 1

# Show modulated signal
plt.figure()
plt.title('Modulated signal')
plt.plot(s_mod)
plt.show()

# Use fft to frequency analyse
plt.figure()
plt.title('Modulated signal in frequency domain')
plt.plot(np.abs(fft.fft(s_mod)))
plt.show()

# Demodulation, using coherent detection, 
# First step: IQ components respectively multiply the carrier wave and qudrature carrier wave
s_demod_i = np.empty(0)
s_demod_q = np.empty(0)
t = 0

for i in range(0, Nbits, 2):
  for j in range(bit_len):
    s_demod_i = np.append(s_demod_i, s_mod[t]*np.cos(2*np.pi*fc*t))
    s_demod_q = np.append(s_demod_q, s_mod[t]*np.sin(2*np.pi*fc*t))
    t += 1

# Second step: use low-pass filter to filter harmonic wave
# initilise filter coefficients
numtaps = 64
fir = signal.firwin(numtaps, 0.1)

# IQ component do filter
s_filt_i = signal.lfilter(fir, 1, s_demod_i)
s_filt_i = np.append(s_filt_i, -np.ones(numtaps//2)/2)
s_filt_q = signal.lfilter(fir, 1, s_demod_q)
s_filt_q = np.append(s_filt_q, -np.ones(numtaps//2)/2)

plt.figure()
plt.title('Filtered signal')
plt.plot(s_filt_i, color = 'b')
plt.plot(s_filt_q, color = 'r')
plt.show()

# Sample judgement
# in fact, QPSK can be considered as two qudrature BPSK
s_demod_bin = np.empty(0)
for i in range(0, Nbits, 2):
  t = (i+1)*bit_len//2 + numtaps//2
  s_demod_bin = np.append(s_demod_bin, s_filt_i[t] > 0.0)
  s_demod_bin = np.append(s_demod_bin, s_filt_q[t] > 0.0)

s_demod_bin = s_demod_bin[:-1]
print(s_demod_bin)

plt.figure()
plt.title('Demodulated signal')
plt.plot(s_demod_bin[:24])
plt.show()