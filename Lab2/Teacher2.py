import numpy as np
from numpy import random
from matplotlib import pyplot as plt 
from scipy import signal
from PIL import Image

def bin_array(num, m):
    """Convert a positive integer num into an m-bit bit vector"""
    return np.array(list(np.binary_repr(num).zfill(m))).astype(np.bool_)

# import 24 bit digital data
id_num = 2635088
Nbits = 24
tx_bin = bin_array(id_num, Nbits)

plt.figure()
plt.title('Original signal')
plt.plot(tx_bin)
plt.show()

# initialise
myclock = np.array([1.0,0.0])
bit_period = 128
fc = 1/32
fref = fc*(1.+0.02*(random.rand()-0.5))
pref = 2*np.pi*random.rand( )
volt = 0.0
vout = np.array(volt)
cout = myclock[0]
rout = np.cos(pref)
dout0 = np.empty(0)

# low-pass filter
numtaps = 128
b1 = np.flip(signal.firwin(numtaps,0.005))
mixed = np.zeros((2,numtaps))
lpmixed = np.empty(2)
for i in range(0,bit_period*Nbits+numtaps//2):
    mixed[0,:] = np.append(mixed[0,1:],myclock[0]*(2*tx_bin[(i//bit_period)%Nbits]-1)*np.cos(pref+2*np.pi*fref*i))
    mixed[1,:] = np.append(mixed[1,1:],-myclock[1]*(2*tx_bin[(i//bit_period)%Nbits]-1)*np.cos(pref+2*np.pi*fref*i))

    lpmixed = [np.sum(b1*mixed[j,:]) for j in range(2)]
    volt = lpmixed[0]*lpmixed[1]
    c = np.cos(2*np.pi*fc*(1.+0.25*volt))
    s = np.sin(2*np.pi*fc*(1.+0.25*volt))
    myclock = np.matmul(np.array([[c,-s],[s,c]]),myclock)
    vout = np.append(vout,volt)
    cout = np.append(cout,myclock[0])
    rout = np.append(rout,np.cos(pref+2*np.pi*fref*i))
    dout0 = np.append(dout0,lpmixed[0])

plt.figure()
plt.axhline(fc)
plt.plot(vout, color='b')
plt.show()

plt.figure()
plt.plot(cout,color='b')
plt.plot(rout, color='r')
plt.show()

plt.figure()
plt.plot(dout0,color='b')
plt.show()  

# Demod
rx_bin = np.empty(0)
for i in range(0,Nbits):
    t = (2*i+1)*bit_period//2 +numtaps//2
    rx_bin = np.append(rx_bin, np.heaviside(dout[t],0))
    # rx_bin= np.append(rx_bin, dout0[t] > 0.0) 

# 同相或反相
if ((rx_bin[:24] != tx_bin[:24]).any()):
	print("Phase inverse")
	plt.figure()
	plt.title('Demodulated signal with inverse phase')
	plt.plot(rx_bin[:24], color = 'orange')
	plt.show()
else:
    # print(rx_bin)
    plt.figure()
    plt.plot(rx_bin)
    plt.show()































