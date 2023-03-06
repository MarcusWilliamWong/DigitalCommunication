'''
Author       : Eureke
Date         : 2023-02-08 06:34:28
LastEditors  : Marcus Wong
LastEditTime : 2023-02-08 10:44:11
Description  : 
'''
import numpy as np
from numpy import random
from matplotlib import pyplot as plt
from scipy import signal
from PIL import Image

# tx_im = Image.open("gulogo.pbm")
# Npixels = tx_im.size[1]*tx_im.size[0]
# tx_bin = np.array(tx_im)
# plt.figure()
# plt.imshow(tx-bin)
# plt.show()

# 十进制数转换为固定位数的二进制
def bin_array(num, m):
  # Convert a positive integer num into an m-bit bit vector
  return np.array(list(np.binary_repr(num).zfill(m))).astype(np.bool)

# Decimal to binary
id_num = 2635088 # 2807941  # 2633609 # 
Nbits = 24
tx_bin = bin_array(id_num, Nbits)
print(tx_bin)
print(tx_bin.shape)

# Show original signal
is_show = True
if (is_show):
	plt.figure()
	plt.title('Original signal')
	plt.plot(tx_bin)
	plt.show()

for i in range(4):
	tx_bin = np.append(tx_bin, 0)

# 生成一个只有元素为0，1，大小为16的数组
# prelude = np.array(np.random.randint(2,size=16),dtype = "bool")
# tx_bin = np.append(prelude, tx_bin)
# tx_bin = np.append(prelude,np.ravel(tx_bin))

#import 24bit digital data
#id_num = 3141592
#tx_bin = np.array([id_num//(2**(23-i))%2 for i in range(0,24)],dtype = "u
# Npixels = tx_bin.size

#initialise
myclock = np.array([1.0, 0.0]) # VCO output?
bit_period = 128 # the number of sample pre bit? bit_len?
fc = 1/32 # 2^(-5) = 0.03125

# random phase and frequency
# 设定参考信号，与实际信号有1%的频率误差和一定的相位差
fref = fc*(1.+0.02*random.rand()-0.5)  
pref = 2*np.pi*random.rand() # [0, 2*pi)
alpha = 0.25
volt = 0.0
# 保存电压变化
vout = np.array(volt)
cout = myclock[0]
rout = np.cos(pref)
# 最终输出，也就是我们的解调信号
dout0 = np.empty(0)

# low pass filter
numtaps = 128 # 2^7
fir = np.flip(signal.firwin(numtaps,0.005)) # cutoff 0.005

# save data to do convolution
mixed = np.zeros((2, numtaps))
lpmixed = np.empty(2) # 两条分支经过lpf的计算结果

for i in range(0,bit_period*tx_bin.size+numtaps//2):
	# 上一个传输符号
	T_index = (i//bit_period)%tx_bin.size
	mixed[0,:] = np.append(mixed[0,1:], myclock[0]*(2*tx_bin[(i//bit_period)%tx_bin.size]-1)*np.cos(pref+2*np.pi*fref*i)) #不全
	mixed[1,:] = np.append(mixed[1,1:], -myclock[1]*(2*tx_bin[(i//bit_period)%tx_bin.size]-1)*np.cos(pref+2*np.pi*fref*i)) #不全

	# 做卷积，即滤波操作，两分支均存入lpmixed
	lpmixed = [np.sum(fir*mixed[j,:1]) for j in range(2)]
	volt = lpmixed[0]*lpmixed[1]
	
	# Cordic，更新当前输出
	w0 = 2*np.pi*fc*(1.+alpha*volt)
	c = np.cos(w0)
	s = np.sin(w0) 
	myclock = np.matmul(np.array([[c,-s],[s,c]]), myclock)

	vout = np.append(vout, volt)
	cout = np.append(cout, myclock[0])
	# 参考载波信号
	rout = np.append(rout, np.cos(pref+2*np.pi*fref*i))
	dout0 = np.append(dout0, lpmixed[0])

plt.figure()
plt.plot(vout,color = 'b')
plt.show()
plt.figure()
plt.plot(cout,color = 'b')
plt.plot(cout,color = 'r')
plt.show()
plt.figure()
plt.plot(dout0,color = 'b')
plt.show()

rx_bin = np.empty(0)
for i in range(0,Nbits):
    t = (2*i+1)*bit_period//2 +numtaps//2
    rx_bin= np.append(rx_bin, dout0[t] > 0.0) 
# print((rx_bin != tx_bin[prelude.size:]).sum())
# rx_bin = rx_bin.reshape(tx_im.size[1],tx_im.size[0])
# plt.figure()
# plt.imshow(rx_bin)
# plt.show()
if ((rx_bin[:24] == tx_bin[:24]).all()):
	print("Phase inverse")
	plt.figure()
	plt.title('Demodulated signal with inverse phase')
	plt.plot(rx_bin[:24], color = 'orange')
	plt.show()

if (is_show):
	plt.figure()
	plt.title('Demodulated signal')
	plt.plot(rx_bin[:24])
	plt.show()
