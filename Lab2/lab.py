import numpy as np
from matplotlib import pyplot as plt
from scipy import signal


def cordic_vco(in_phase, quadrature, fi, v):
    alpha = 0.01
    f0 = fi + alpha * v
    cos_f0 = np.cos(f0)
    sin_f0 = np.sin(f0)
    in_phase_new = in_phase * cos_f0 - quadrature * sin_f0
    quadrature_new = in_phase * sin_f0 + quadrature * cos_f0
    return in_phase_new, quadrature_new, f0

def demodulation(rx_mixed, bit_len, numtaps, fc, Nbits, id_num):
    # b1 = signal.firwin(numtaps, 0.1)
    # rx_lpf = signal.lfilter(b1, 1, rx_mixed)
    # rx_lpf = np.append(rx_lpf, np.ones(numtaps//2))
    # rx_lpf = np.append(rx_lpf, np.ones(numtaps//2))
    # rx_lpf = rx_lpf[2 * bit_len:]

    # rx_bin = np.heaviside(rx_mixed, 0)
    # rx_bin = np.empty(0)
    # for i in range(0, Nbits):
    #     t = (2 * i + 1) * bit_len // 2
    #     rx_bin = np.append(rx_bin, rx_mixed[t] > 0.0)
        
    
    rx_bin = np.empty(0)
    for i in range(0, Nbits):
        # t = (2 * i + 1) * bit_len // 2 + numtaps//2
        t = i * bit_len // 2 + numtaps//2
        rx_bin = np.append(rx_bin, np.heaviside(rx_mixed[t], 0))
    return rx_bin

def bin_array(num, m):
    return np.array(list(np.binary_repr(num).zfill(m))).astype(np.bool)

# Import 24-bit digital data
id_num = 2635088
Nbits = 24
tx_bin = bin_array(id_num, Nbits)

print(tx_bin)
plt.figure()
plt.title('Original signal')
plt.plot(tx_bin)
plt.show()

for i in range(6):
    tx_bin = np.append(tx_bin, 0)
    Nbits += 1

fc = 0.1
bit_len = 16
tx_mod = np.empty(0)

# Modulation
for i in range(0, Nbits):
    for j in range(0, bit_len):
        tx_mod = np.append(tx_mod, (2 * tx_bin[i] - 1) * np.cos(2 * np.pi * fc * (i * bit_len + j)))

# VCO and Demodulation
in_phase = 1.0
quadrature = 0.0
fi = 0.125
v = 0
numtaps = 64
rx_mixed = np.empty(0)
b1 = np.flip(signal.firwin(numtaps, 0.1))

s_mixed = np.zeros(numtaps)
c_mixed = np.zeros(numtaps)
# c_lpf_output = np.zeros(Nbits*bit_len)
# s_lpf_output = np.zeros(Nbits*bit_len)
# c_lpf_output = np.zeros(numtaps)
# s_lpf_output = np.zeros(numtaps)
result = np.empty(0)
result_v = np.empty(0)


for i in range(0, Nbits):
    for j in range(0, bit_len):
        in_phase, quadrature, f0 = cordic_vco(in_phase, quadrature, fi, v)
        
        # in_phase = in_phase*tx_mod[i * bit_len + j]
        # quadrature = quadrature*tx_mod[i * bit_len + j]
        
        # Low-pass filter
        c_lpf_input = tx_mod[i*bit_len+j]*in_phase
        s_lpf_input = tx_mod[i*bit_len+j]*quadrature
        
        c_mixed[:] = np.append(c_mixed[1:], c_lpf_input)
        s_mixed[:] = np.append(s_mixed[1:], s_lpf_input)
        
        # c_lpf_output = np.append(c_lpf_output,np.sum(b1*c_mixed))
        # s_lpf_output = np.append(s_lpf_output,np.sum(b1*s_mixed))
        
        c_lpf_output = np.sum(b1*c_mixed)
        result = np.append(result, c_lpf_output)
        
        s_lpf_output = np.sum(b1*s_mixed)

        # Update frequency based on the Costas Loop
        v = c_lpf_output * s_lpf_output
        result_v =  np.append(result_v, v)
        
        # in_phase = signal.lfilter(b1, 1, in_phase)
        
        # v = in_phase*quadrature
        
        # rx_mixed = np.append(rx_mixed, tx_mod[i * bit_len + j] * in_phase)
print(result)
print(result.shape)

rx_bin = demodulation(result, bit_len, numtaps, fc, Nbits, id_num)

plt.plot(rx_bin)
# plt.plot(rx_mixed)
plt.show()

plt.figure()
plt.plot(result_v)