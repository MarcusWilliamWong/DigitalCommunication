'''
Author       : Eureke
Date         : 2023-02-07 02:33:13
LastEditors  : Marcus Wong
LastEditTime : 2023-02-07 18:19:45
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

# BPSK modulation
bit_len = 16 # 16 samples per bit, so sample rate = 1/16
fc = 0.125 # normalised carrier frequency because of Nyquist limit fc >= 2fs, so there will be 2 periods of carrier wave per bit
def BPSKmod(tx_bin, Nbits):
  # fill zeros
  for i in range(0):
    tx_bin = np.append(tx_bin, 0)
    Nbits += 1
  
  # initialisation
  s = np.copy(tx_bin)
  s_mod = np.empty(0)
  t = 0
  # based on IQ modulation
  for i in range(Nbits):
    for j in range(bit_len):
      # BPSK s(t):{0, 1} => {-1, 1}
      s_mod = np.append(s_mod, (2*s[i] - 1) * np.cos(2*np.pi*fc*t))
      t += 1
  print(s_mod.shape)

  return s_mod

s_mod = BPSKmod(tx_bin, Nbits)
plt.figure()
plt.title('Modulated signal')
plt.plot(s_mod)
plt.show()

plt.figure()
plt.title('Modulated signal in frequency domain')
plt.plot(np.abs(fft.fft(s_mod)))
plt.show()

# LPF initialise
numtaps = 128 # 32
cutoff = 0.1
lpf = np.flip(signal.firwin(numtaps, cutoff))

# initialise VCO, t = 0
volt = 0
VCOgain = 0.002
# f0 = 0.01
f0 = 0
c = 1
s = 0
c_delay = 0
s_delay = 0
# adjust
alpha = 0.132
freq = f0
phase = 0
# VCO output signal
sine = np.array([0], dtype=np.float64)
cosine = np.array([1], dtype=np.float64)
# mixer output
c_mixed_output = np.zeros(numtaps)
s_mixed_output = np.zeros(numtaps)
# LPF output
c_lpf_output = np.empty(0)
s_lpf_output = np.empty(0)

# Castas loop
for t in range(s_mod.shape[0]):
  c_delay = c
  s_delay = s
  # voltage controlled relation
  freq = f0 + VCOgain * volt
  phase += freq + (alpha * volt)
  while phase >= 2*np.pi:
    phase -= 2*np.pi
  while phase < 0:
    phase += 2*np.pi

  w0 = 2 * np.pi * freq
  # w0 = 2 * np.pi * freq
  # output
  c = c_delay * np.cos(w0) - s_delay * np.sin(w0)
  s = s_delay * np.cos(w0) + c_delay * np.sin(w0)
  # append new output
  cosine = np.append(cosine, c)
  sine = np.append(sine, s)

  # mixer
  c_mixed_output[t%numtaps] = s_mod[t] * c
  s_mixed_output[t%numtaps] = s_mod[t] * s

  # LPF
  c_lpf_output = np.append(c_lpf_output, np.sum(lpf * c_mixed_output))
  s_lpf_output = np.append(s_lpf_output, np.sum(lpf * s_mixed_output))

  # update error
  volt = c_lpf_output[-1] * s_lpf_output[-1]

  # loop filter, Cordic
  

print(c_lpf_output.shape)

# Sample judgement
s_demod_bin = np.zeros(Nbits)
for i in range(Nbits):
  t = i*bit_len + numtaps // 2
  s_demod_bin[i] = np.heaviside(c_lpf_output[i], 0)

print(s_demod_bin)
plt.figure()
plt.title('Demod signal')
plt.plot(s_demod_bin)
plt.show()