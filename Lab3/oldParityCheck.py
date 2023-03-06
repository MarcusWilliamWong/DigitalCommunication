'''
Author       : Eureke
Date         : 2023-02-17 11:49:10
LastEditors  : Marcus Wong
LastEditTime : 2023-02-20 14:36:52
Description  : ParityCheck
'''
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import komm
from scipy import special

# open image file
def openImagetoBin(filePath):
  tx_im = Image.open(filePath)
  Npixels = tx_im.size[1]*tx_im.size[0]
  plt.figure()
  plt.imshow(np.array(tx_im),cmap="gray",vmin=0,vmax=255)
  plt.show()
  tx_bin = np.unpackbits(np.array(tx_im))
  print('original shape: ', tx_bin.shape)
  # print(tx_bin[:10])

  return tx_bin, tx_im.size

# use parity code before transmission
def createParityCode(tx_bin, word_len, parityMode):
  '''
  parity: choose even(0) or odd(1)
  '''
  indices = np.arange(word_len - 1, tx_bin.shape[0], word_len, dtype=int)
  # print(indices[10:])
  parityCode = np.copy(tx_bin).astype(np.bool_)
  if (not parityMode):
    # even
    for i in indices:
      parityCode[i] = np.sum(tx_bin[i-7:i]) % 2
  else:
    # odd
    for i in indices:
      parityCode[i] = ~np.sum(tx_bin[i-7:i]) % 2

  return parityCode.astype(np.int32)

# even_true
# (not parityMode) and (not (sum % 2)) => 1
# odd_true
# parityMode and (sum % 2) => 1
# equal to not (parityMode ^ (sum % 2))

# even false
# (not parityMode) and (sum % 2) => 0
# odd_false
# parityMode and (not (sum % 2)) => 0
# equal to parityMode ^ (sum % 2)
parityCheck = lambda rx_bin, parityMode : not (parityMode ^ (np.sum(rx_bin) % 2))

# use specific modulation
def modulate(tx_bin, method, order, snr, base_amplitudes=1.0, phase_offset = 0.):
  if method == 'psk':
    modulation = komm.PSKModulation(orders, amplitude = base_amplitudes, phase_offset=phase_offset)
  elif method == 'am':
    modulation = komm.QAModulation(orders, base_amplitudes=base_amplitudes, phase_offset=phase_offset)
  
  # Additive white gaussian noise(AWGN)
  awgn = komm.AWGNChannel(snr)

  return modulation, awgn

# simulate transmitter single word
tx_ori = lambda s_mod, word_len, start_index : s_mod[start_index: start_index + word_len]

def rx_sim(tx_data, modulation, awgn):
  rx_data = awgn(tx_data)
  rx_bin = modulation.demodulate(rx_data)
  # print(rx_bin)

  return rx_bin

def displayDemodImage(rx_bin, imageSize):
  # demod signal with noise
  rx_im = np.packbits(rx_bin).reshape(imageSize[1], imageSize[0])
  plt.figure()
  plt.imshow(np.array(rx_im),cmap="gray",vmin=0,vmax=255)
  plt.show()


if __name__ == '__main__':
  # open image and binary information
  fp = "./Lab3/DC4_150x100.pgm"
  tx_bin, imSize = openImagetoBin(fp)
  Npixels = imSize[1] * imSize[0]
  word_len = 8

  # use even parity mode
  pm = 0
  tx_parityCode = createParityCode(tx_bin, word_len, pm)
  # print(tx_bin[88:104])
  # print(tx_parityCode[88:104])

  # modulation
  method = 'psk'
  # BPSK
  orders = 2
  # QPSK
  orders = 4
  orders = 16

  # method = 'am'
  # orders = 2
  
  base_amplitudes = 1.0
  phase_offset = 0 #np.pi / 4
  snr = 10**(6./10.) # dB(信噪比强度) = 10*lg(signal/noise) = 6 => signal/noise 约为 3-4倍
  modulation, awgn = modulate(tx_parityCode, method, orders, snr, base_amplitudes=base_amplitudes, phase_offset=phase_offset)

  # simulate single step of transmission
  n = 0 # pixel number has been trasmitted
  start_index = lambda n : n * word_len
  arq_cnt = 0
  # save demodulation signal
  rx_bin = np.empty(0)
  while n < Npixels:
    # original signal per step
    tx_per_step = tx_ori(tx_parityCode, word_len, start_index(n))
    # modulation, transmit single word
    s_mod = modulation.modulate(tx_per_step)
    
    # receive single word
    rx_per_step = rx_sim(s_mod, modulation, awgn)
    
    # print('tx_per_step: ', tx_per_step)
    # print('size: ', tx_per_step.size)
    # print('s_mod: ', s_mod)
    # print('size: ', s_mod.size)
    # print('rx_per_step: ', rx_per_step)
    # print('size: ', rx_per_step.size)
    # judge transmission error
    if parityCheck(rx_per_step, pm): # no error
      n += 1
      rx_bin = np.append(rx_bin, rx_per_step)
      print("pass")
    else: # error, repeat transmit
      arq_cnt += 1
      print('error')
  
  # error per pixel
  epp = arq_cnt * 100.0 / Npixels
  print('arq_cnt: ', arq_cnt)
  print('Npixels: ', Npixels)
  print('error per pixel: {:.3}%'.format(epp))

  displayDemodImage(rx_bin.astype(np.bool_), imSize)






