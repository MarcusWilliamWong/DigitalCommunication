'''
Author       : Eureke
Date         : 2023-02-08 16:10:41
LastEditors  : Marcus Wong
LastEditTime : 2023-02-17 14:04:36
Description  : 
'''
import numpy as np
from matplotlib import pyplot as plt
from scipy import fft
from scipy import signal
from numpy import random

def bin_array(num, m):
    # Convert a positive integer num into an m-bit bit vector
    return np.array(list(np.binary_repr(num).zfill(m))).astype(bool)

id_num = 2635088
Nbits = 24
tx_bin = bin_array(id_num, Nbits)

# Show original signal
plt.figure()
plt.title('Original signal')
plt.plot(tx_bin)
plt.show()

s = tx_bin
# carrier wave ideal frequency
fi = 1/64
# samples per bit
bit_len = 128 # 64

withDiff = True
if (withDiff):
    #Differential Coding of tx_bin
    tx_diff = np.zeros(1, dtype='bool')
    for i in range(Nbits):
        tx_diff = np.append(tx_diff, tx_diff[i]^s[i])
    Nbits = Nbits+1
else:
    tx_diff = tx_bin

# low-pass filter
numtaps = 128 #64
b1 = np.flip(signal.firwin(numtaps, 0.005))    

# initialise
clock = np.array([1.0,0.0])
# carrier radom frequency
f_c =  fi*(1.+0.02*(random.rand()-0.5))
# carrier radom phase of carrier
p_c = 2*np.pi*random.rand()

# Modulation
s_mod = np.empty(0)
for t in range(0, bit_len*Nbits + numtaps//2):
    s_mod = np.append(s_mod, (2*tx_diff[(t//bit_len)%Nbits]-1)*np.cos(p_c+2*np.pi*f_c*t))

plt.figure()
plt.title('Modulated signal')
plt.plot(s_mod)
plt.show()

fout = np.array(f_c)
volt = 1.0
# volt changes
vout = np.array(volt)
# output of clock cos wave
cout = clock[0]
# output of reference clock
rout = np.cos(p_c)
# demod output
dout = np.empty(0)

def cordic(clock, fi, volt):
    alpha = 0.25
    f0 = fi*(1.+alpha*volt)
    w0 = 2*np.pi*f0
    c = np.cos(w0)
    s = np.sin(w0)
    clock = np.matmul(np.array([[c, -s], [s, c]]), clock)

    return clock, f0

mixed = np.zeros((2,numtaps))
for i in range(0, bit_len*Nbits + numtaps//2):
    # modulated signal mixed with clock
    mixed[0,:] = np.append(mixed[0,1:],clock[0]*s_mod[i])
    mixed[1,:] = np.append(mixed[1,1:],-clock[1]*s_mod[i])
    # lpf
    lpmixed = [np.sum(b1*mixed[j,:]) for j in range(2)]
    volt = lpmixed[0]*lpmixed[1]
    
    clock, f0 = cordic(clock, fi, volt)
    
    fout = np.append(fout, f0)
    vout = np.append(vout, volt)
    cout = np.append(cout, clock[0])
    rout = np.append(rout, np.cos(p_c+2*np.pi*f_c*i)) #Reference block
    dout = np.append(dout, lpmixed[0])

plt.figure()
plt.title('Voltage change')
plt.plot(vout)
plt.show()

plt.figure()
plt.title('Frequency change')
plt.axhline(f_c, color='r')
plt.plot(fout)
plt.show()

plt.figure()
plt.title('Clock output with reference carrier')
plt.plot(cout, color='b')
plt.plot(rout, color='r')
plt.show()

plt.figure()
plt.title('Output data before thresholding')
plt.plot(dout)
plt.show()

print(f_c)
print(fout[-1])
print(fout[-1] - f_c)

if (withDiff):
    # With differential coding
    rx_diff = np.empty(0)
    for i in range(Nbits):
        #select an appropriate sample point
        k = (2*i+1)*bit_len//2 +numtaps//2
        rx_diff= np.append(rx_diff, np.heaviside(dout[k],0))

    rx_bin = np.empty(0, dtype='bool')
    Nbits = Nbits-1
    for i in range(Nbits):
        rx_bin = np.append(rx_bin, rx_diff[i].astype(bool)^rx_diff[i+1].astype(bool))

    # print(rx_bin)
    plt.figure()
    plt.title('With differential encoding')
    plt.plot(rx_bin) 
    plt.show()
else:
    # Without differential coding
    rx_bin = np.empty(0, dtype='bool')
    for i in range(0,Nbits):
        t = (2*i+1)*bit_len//2 +numtaps//2
        rx_bin = np.append(rx_bin, np.heaviside(dout[t],0))

    if ((rx_bin != tx_bin).any()):
        plt.figure()
        plt.title('Without differential encoding but inverse phase')
        plt.plot(rx_bin, color='orange')
        plt.show()
    else:
        plt.figure()
        plt.title('Without differential encoding but the same')
        plt.plot(rx_bin)
        plt.show()