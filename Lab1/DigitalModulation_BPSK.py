'''
Author       : Eureke
Date         : 2023-01-25 01:47:33
LastEditors  : Marcus Wong
LastEditTime : 2023-02-07 18:36:53
Description  : 
'''
import numpy as np
from matplotlib import pyplot as plt
from scipy import fft
from scipy import signal

def bin_array(num, m):
  # Convert a positive integer num into an m-bit bit vector
  return np.array(list(np.binary_repr(num).zfill(m))).astype(np.bool)

# Decimal to binary
id_num = 2635088 # 2807941  # 2633609 # 
Nbits = 24
tx_bin = bin_array(id_num, Nbits)
print(tx_bin)

# Show original signal
plt.figure()
plt.title('Original signal')
plt.plot(tx_bin)
plt.show()

tx_bin = np.append(tx_bin, [0, 0, 0, 0])
Nbits += 4

# BPSK modulation
# initialisation
bit_len = 16 # 16 samples per bit, so sample rate = 1/16
fc = 0.125 # normalised carrier frequency because of Nyquist limit fc >= 2fs, so there will be 2 periods of carrier wave per bit
s = np.copy(tx_bin)
s_mod = np.empty(0)
t = 0
# based on IQ modulation
for i in range(Nbits):
  for j in range(bit_len):
    # BPSK s(t):{0, 1} => {-1, 1}
    s_mod = np.append(s_mod, (2*s[i] - 1) * np.cos(2*np.pi*fc*t))
    t += 1

plt.figure()
plt.title('Modulated signal')
plt.plot(s_mod)
plt.show()

plt.figure()
plt.title('Modulated signal in frequency domain')
plt.plot(np.abs(fft.fft(s_mod)))
plt.show()

# Demodulation(coherent detection method)
s_demod_multi = np.empty(0)
t = 0
for i in range(Nbits):
  for j in range(bit_len):
    s_demod_multi = np.append(s_demod_multi, s_mod[t] * np.cos(2*np.pi*fc*t))
    t += 1

plt.figure()
plt.title('Signal after multiplicator')
plt.plot(s_demod_multi)
plt.show()

plt.figure()
plt.title('Signal after multiplicator in frequency domain')
plt.plot(np.abs(fft.fft(s_demod_multi)))
plt.show()

# Do filter, try tp change coeffients of fir filter
numtaps = 64 # 32
cutoff = 0.1
fir = signal.firwin(numtaps, cutoff)
s_demod_lpf = signal.lfilter(fir, 1, s_demod_multi)
s_demod_lpf = np.append(s_demod_lpf, -np.ones(numtaps//2))

plt.figure()
plt.title('Filtered signal')
plt.plot(s_demod_lpf)
plt.show()

plt.figure()
plt.title('Filtered signal in frequency domain')
plt.plot(np.abs(fft.fft(s_demod_lpf)))
plt.show()

# Sample judgement
s_demod_bin = np.empty(0)
for i in range(Nbits):
  t = (2*i+1)*bit_len//2 + numtaps // 2  # use median sample to judge original signal
  s_demod_bin = np.append(s_demod_bin, s_demod_lpf[t] > 0.0)
print(s_demod_bin[:24])

plt.figure()
plt.title('Demodulated signal')
plt.plot(s_demod_bin[:24])
plt.show()