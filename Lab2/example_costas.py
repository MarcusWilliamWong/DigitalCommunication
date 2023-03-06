# -*- coding: utf-8 -*-
"""
Costas Loop
Created on Fri Nov  6 15:23:43 2020

@author: dch2y
"""

# import required libraries

import numpy as np
from numpy import random
from matplotlib import pyplot as plt
from scipy import signal
from PIL import Image

tx_im = Image.open("gulogo.pbm")
Nbits = tx_im.size[1]*tx_im.size[0]
tx_bin = np.array(tx_im)
plt.figure()
plt.imshow(tx_bin)
plt.show() 
tx_bin = np.ravel(tx_bin)
tx_diff = np.zeros(1, dtype='bool')
for i in range(Nbits):
    tx_diff = np.append(tx_diff, tx_diff[i]^tx_bin[i])
Nbits = Nbits+1

# import 24bit digital data
def bin_array(num, m):
    """Convert a positive integer num into an m-bit bit vector"""
    return np.array(list(np.binary_repr(num).zfill(m))).astype(np.bool)
id_num = 3141592
#Nbits = 24
prelude = np.array(np.random.randint(2, size=16), dtype="bool")
tx_diff = np.append(prelude, tx_diff)
#tx_bin = np.append(prelude, bin_array(id_num, Nbits))

# initialise

myclock = np.array([1.0,0.0])
bit_period = 16 #128
fc = 1/8 #1/32
fref = fc*(1.+0.02*(random.rand()-0.5))
pref = 2*np.pi*random.rand()
volt = 0.0
vout = np.array(volt)
cout = myclock[0]
rout = np.cos(pref)
dout0 = np.empty(0)

# low-pass filter
numtaps = 64 #128
b1 = np.flip(signal.firwin(numtaps, 0.1)) #0.005))

mixed = np.zeros((2,numtaps))
lpmixed = np.empty(2)

for i in range(0,bit_period*(prelude.size+Nbits)+numtaps//2):
    mixed[0,:] = np.append(mixed[0,1:],myclock[0]*(2*tx_diff[(i//bit_period)%(prelude.size+Nbits)]-1)*np.cos(pref+2*np.pi*fref*i))
    mixed[1,:] = np.append(mixed[1,1:],-myclock[1]*(2*tx_diff[(i//bit_period)%(prelude.size+Nbits)]-1)*np.cos(pref+2*np.pi*fref*i))

    lpmixed = [np.inner(b1,mixed[j,:]) for j in range(2)]
    volt = lpmixed[0]*lpmixed[1]

    c = np.cos(2*np.pi*fc*(1.+0.25*volt))
    s = np.sin(2*np.pi*fc*(1.+0.25*volt))
    myclock = np.matmul(np.array([[c, -s], [s, c]]),myclock)

    vout = np.append(vout,volt)
    cout = np.append(cout,myclock[0])
    rout = np.append(rout,np.cos(pref+2*np.pi*fref*i))
    dout0 = np.append(dout0,lpmixed[0])
    
plt.figure()
plt.plot(vout, color='b')
plt.show()
plt.figure()
plt.plot(cout, color='b')
plt.plot(rout, color='r')
plt.show()
plt.figure()
plt.plot(dout0, color='b')
plt.show()

rx_diff = np.uint8([np.heaviside(dout0[(2*i+1)*bit_period//2+numtaps//2],0) for i in range(prelude.size,Nbits+prelude.size)])
rx_bin = np.empty(0, dtype='bool')
Nbits = Nbits-1
for i in range(Nbits):
    rx_bin = np.append(rx_bin, rx_diff[i]^rx_diff[i+1]).astype(bool)

print((rx_bin ^ tx_bin).sum())
rx_bin = rx_bin.reshape(tx_im.size[1],tx_im.size[0])
plt.figure()
plt.imshow(rx_bin)
plt.show() 
