'''
Author       : Eureke
Date         : 2023-02-17 11:49:10
LastEditors  : Marcus Wong
LastEditTime : 2023-02-22 22:04:22
Description  : ParityCheck
'''
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import komm
from scipy import special

class imgInfo:
  def __init__(self, fp, word_len):
    self.imBin, self.imSize = self.openImagetoBin(fp)
    self.Npixels = self.imSize[1] * self.imSize[0]
    self.word_len = word_len

  # open image file
  def openImagetoBin(self, filePath):
    im = Image.open(filePath)
    if (True):
      plt.figure()
      plt.imshow(np.array(im),cmap="gray",vmin=0,vmax=255)
      plt.show()
    imBin = np.unpackbits(np.array(im))
    print('original shape: ', imBin.shape)
    return imBin, im.size

  # use parity code before transmission
  def createParityCode(self, parity_mode):
    '''
    parity: choose even(0) or odd(1)
    '''
    indices = np.arange(self.word_len - 1, self.imBin.size, self.word_len, dtype=int)
    # print(indices[10:])
    self.parityCode = np.copy(self.imBin).astype(np.bool_)
    if (not parity_mode):
    # even
      for i in indices:
        self.parityCode[i] = np.sum(self.imBin[i-7:i]) % 2
    else:
      # odd
      for i in indices:
        self.parityCode[i] = ~np.sum(self.imBin[i-7:i]) % 2
    self.parityCode = self.parityCode.astype(np.int32)
    return self.parityCode

  # show demodulated image 
  def displayDemodImage(self, rx_bin):
    # demod signal with noise
    rx_im = np.packbits(rx_bin).reshape(self.imSize[1], self.imSize[0])
    plt.figure()
    plt.imshow(np.array(rx_im),cmap="gray",vmin=0,vmax=255)
    plt.show()


class modConfig:
  def __init__(self, method, orders, snr, base_amplitudes, phase_offset):
    self.method = method
    self.orders = orders
    self.snr = snr
    self.base_amplitudes = base_amplitudes
    self.phase_offset = phase_offset
    self.modulation, self.awgn = self.set_modulation()

  # create komm's modulation object
  def set_modulation(self):
    if self.method == 'psk':
      modulation = komm.PSKModulation(self.orders, amplitude=self.base_amplitudes, phase_offset=self.phase_offset)
    elif self.method == 'qam':
      modulation = komm.QAModulation(self.orders, base_amplitudes=self.base_amplitudes, phase_offset=self.phase_offset)
    # Additive white gaussian noise(AWGN)
    awgn = komm.AWGNChannel(self.snr)
    return modulation, awgn

  # self-add snr
  def set_snr(self, new_snr):
    self.snr = new_snr
    self.modulation, self.awgn = self.set_modulation()


# simulate transmitter send single original word
tx_ori = lambda signal, word_len, start_index : signal[start_index: start_index + word_len]


# region parityCheck
'''
even_true
(not parity_mode) and (not (sum % 2)) => 1
odd_true
parity_mode and (sum % 2) => 1
equal to not (parity_mode ^ (sum % 2))

even false
(not parity_mode) and (sum % 2) => 0
odd_false
parity_mode and (not (sum % 2)) => 0
equal to parity_mode ^ (sum % 2)
'''
# endregion
doParityCheck = lambda rx_bin, parity_mode : not (parity_mode ^ (np.sum(rx_bin) % 2))


# simulate receiver demodluate signal
def rx_sim(s_mod, mod_config):
  rx_data = mod_config.awgn(s_mod)
  rx_bin = mod_config.modulation.demodulate(rx_data)
  # print(rx_bin)
  return rx_bin


# stimulate transmit single img
def transmission(img, mod_config, parity_mode):
  # save checked demodulation signal
  rx_bin = np.empty(0)
  # arq counter
  arq_cnt = 0
  
  # simulate single step of transmission
  hasTransPixel = 0 # pixel number has been trasmitted
  while hasTransPixel < img.Npixels:
    # original signal per step
    tx_single = tx_ori(img.parityCode, img.word_len, hasTransPixel * img.word_len)
    # modulation, transmit single word
    s_mod = mod_config.modulation.modulate(tx_single)
    # receive and demodulate single word
    rx_single = rx_sim(s_mod, mod_config)

    # print('tx_single: ', tx_single)
    # print('tx_single size: ', tx_single.size)
    # print('s_mod: ', s_mod)
    # print('s_mod size: ', s_mod.size)
    # print('rx_single: ', rx_single)
    # print('rx_single size: ', rx_single.size)

    # judge transmission error
    if doParityCheck(rx_single, parity_mode): # no error
      hasTransPixel += 1
      rx_bin = np.append(rx_bin, rx_single)
      # print("pass")
    else: # error, repeat transmit
      arq_cnt += 1
      # print('error')
  # bit error ratio
  ber = arq_cnt / img.Npixels
  # print('arq counter: ', arq_cnt)
  # print('Npixels: ', Npixels)
  print('snr(dB): ', mod_config.snr)
  print('bit error ratio: {:.3}%'.format(ber * 100.0 ))
  if (False):
    img.displayDemodImage(rx_bin.astype(np.bool_))

  return ber, mod_config.snr

# compute theoretical ber using erfc function
theoryBer = lambda snr, word_len: 0.5 * special.erfc(np.sqrt(10**(snr/10.)/word_len))

def repeatTransmit(img, parity_mode, method, orders, snr_ctrl, base_amplitudes=1., phase_offset=0.):
  print("Start " + str(orders) + '-' + method + "modulation:")

  # create parity code
  img.createParityCode(parity_mode)
  # print("original bin: ", img.imBin[88:104])
  # print("parity code: ", img.parityCode[88:104])

  # initial modulation config
  # snr = 10**(6./10.) # dB(信噪比强度) = 10*lg(signal/noise) = 6 => signal/noise 约为 3-4倍
  mod_config = modConfig(method, orders, snr_ctrl[0], base_amplitudes, phase_offset)

  # save ber and snr of each trasmission single image 
  ber_out = np.empty(0)
  theory_ber_out = np.empty(0)
  snr_out = np.empty(0)
  for i in np.arange(snr_ctrl[0], snr_ctrl[1], snr_ctrl[2]):
    snr = 10**(i/10.)
    mod_config.set_snr(snr)
    ber, snr = transmission(img, mod_config, parity_mode)
    theory_ber = theoryBer(snr, img.word_len)
    
    ber_out = np.append(ber_out, ber)
    theory_ber_out = np.append(theory_ber_out, theory_ber)
    snr_out = np.append(snr_out, i)
  # print(ber_out)
  # print(theory_ber_out)
  # print(snr_out)

  if (True):
    plt.figure()
    plt.title(str(orders) + '-' + method.upper() + " Snr(dB) vs Ber")
    plt.scatter(snr_out, ber_out, color='r', label='Practical ber (ratio of ARQs to Npixels)')
    plt.plot(snr_out, theory_ber_out, color='b', label='Theoretical ber')
    plt.yscale("log")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == '__main__':
  # open image and binary information
  fp = './Lab3/DC4_150x100.pgm'
  # fp = './Lab3/DC4_640x480.pgm'
  word_len = 8 # 256 bits per pixel
  img = imgInfo(fp, word_len)
  # use parity mode even(0), odd(1)
  parity_mode = 0
  snr_ctrl = [2., 12., 0.2]
  # psk modulation
  repeatTransmit(img=img, parity_mode=parity_mode, method='psk', orders=2, snr_ctrl=snr_ctrl, base_amplitudes=1., phase_offset=0.)
  repeatTransmit(img=img, parity_mode=parity_mode, method='psk', orders=4, snr_ctrl=snr_ctrl, base_amplitudes=1., phase_offset=0.)
  repeatTransmit(img=img, parity_mode=parity_mode, method='psk', orders=16, snr_ctrl=snr_ctrl, base_amplitudes=1., phase_offset=0.)
  repeatTransmit(img=img, parity_mode=parity_mode, method='psk', orders=256, snr_ctrl=snr_ctrl, base_amplitudes=1., phase_offset=0.)

  # qam mudulation
  repeatTransmit(img=img, parity_mode=parity_mode, method='qam', orders=4, snr_ctrl=snr_ctrl, base_amplitudes=1., phase_offset=0.)
  repeatTransmit(img=img, parity_mode=parity_mode, method='qam', orders=16, snr_ctrl=snr_ctrl, base_amplitudes=1., phase_offset=0.)
  repeatTransmit(img=img, parity_mode=parity_mode, method='qam', orders=256, snr_ctrl=snr_ctrl, base_amplitudes=1., phase_offset=0.)