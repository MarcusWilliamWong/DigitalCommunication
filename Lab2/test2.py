'''
Author       : Eureke
Date         : 2023-02-06 16:30:05
LastEditors  : Marcus Wong
LastEditTime : 2023-02-07 10:20:33
Description  : 
'''
import numpy as np
import matplotlib.pyplot as plt

# VCO模块，用于计算复数信号
def vco(fi, av, samples):
    N = len(samples)
    phase = 0
    freq = fi # 初始频率
    out = np.zeros(N, dtype=np.complex) # 输出数组
    for i in range(N):
        f0 = fi + av # 根据输入的电压计算频率
        cos_f0 = np.cos(f0)
        sin_f0 = np.sin(f0)
        x = samples[i] * np.exp(-1j*phase)
        real = np.real(x)
        imag = np.imag(x)
        error = real * imag # 计算误差
        freq += error
        phase += freq
        out[i] = x * np.exp(1j*phase)
    return out

# Costas环模块，用于计算相位锁定
def costas_loop(samples, alpha, beta):
    N = len(samples)
    phase = 0 # 初始相位
    freq = 0 # 初始频率
    out = np.zeros(N, dtype=np.complex)
    freq_log = []
    for i in range(N):
        out[i] = samples[i] * np.exp(-1j*phase)
        error = np.real(out[i]) * np.imag(out[i]) # 计算误差
        freq += (beta * error) # 根据误差调整频率
        freq_log.append(freq)
        phase += freq + (alpha * error) # 根据误差调整相位
        while phase >= 2*np.pi:
            phase -= 2*np.pi
        while phase < 0:
            phase += 2*np.pi
    return out, freq_log

# 组合模块，调用VCO和Costas环模块
def combined_loop(samples, fi, av, alpha, beta):
    vco_out = vco(fi, av, samples)
    costas_out, freq_log = costas_loop(vco_out, alpha, beta)
    return costas_out, freq_log


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

samples = BPSKmod(tx_bin, Nbits)
# 使用示例
# samples = np.array(s_mod) # 输入BPSK调制信号
fi =0.01 # 设定初始频率
av = 0.1 # 设定调频电压
alpha = 0.132 # 设定相位锁定系数
beta = 0.00932 # 设定频率锁定系数

costas_out, freq_log = combined_loop(samples, fi, av, alpha, beta)

plt.plot(freq_log)
plt.title("Frequency Lock")
plt.xlabel("Sample Index")
plt.ylabel("Frequency")
plt.show()

c_lpf_output = np.real(costas_out)
s_demod_bin = np.zeros(Nbits)
for i in range(Nbits):
    t = i*bit_len
    s_demod_bin[i] = np.heaviside(c_lpf_output[i], 0)
plt.figure()
plt.title('Cosine output')
plt.plot(s_demod_bin    )
plt.show()