'''
Author       : Eureke
Date         : 2023-02-13 10:28:40
LastEditors  : Marcus Wong
LastEditTime : 2023-02-22 23:04:42
Description  : 
'''
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import komm
from scipy import special
from ParityCheck import imgInfo, theoryBer


# compute ber in practice
practiceBer = lambda tx_bin, rx_bin : np.sum([pix[0] != pix[1] for pix in zip(tx_bin, rx_bin)]) / tx_bin.size


if __name__ == '__main__':
  # 注意当前打开的工作路径的相对路径，这里打开的文件夹是LAB，所以要加子文件夹路径 ./Lab3/
  is_plot = True # True
  # open image and binary information
  fp = "./Lab3/DC4_150x100.pgm"
  word_len = 8 # 256 bits per pixel
  img = imgInfo(fp, word_len)

  # save ber ,theoretical ber and snr
  ber_out = np.empty(0)
  theory_ber_out = np.empty(0)
  snr_out = np.empty(0)

  for i in np.arange(2., 12., 0.2):
    # BPSK modulation
    psk = komm.PSKModulation(4)
    # Additive white gaussian noise (AWGN) channel
    # snr -> signal-to-noise ratio
    # snr = np.array([10**(6./10.), 10**(5./10.), 10**(4./10.), 10**(3./10.), 10**(2./10.), 10**(1./10.)])
    awgn = komm.AWGNChannel(snr=10**(i/10.))
    tx_data = psk.modulate(img.imBin)
    # demodulation
    rx_data = awgn(tx_data)
    if (not is_plot):
      # is_plot = not is_plot
      plt.figure()
      plt.axes().set_aspect("equal")
      plt.title("Modulated signal with noise")
      plt.scatter(rx_data[:10000].real,rx_data[:10000].imag,s=1,marker=".")
      plt.show()
    rx_bin = psk.demodulate(rx_data)

    if (False):
      img.displayDemodImage(rx_bin.astype(np.bool_))

    snr = 10**(i/10.)
    ber = practiceBer(img.imBin, rx_bin)
    theory_ber = theoryBer(snr, img.word_len)

    snr_out = np.append(snr_out, snr)
    ber_out = np.append(ber_out, ber)
    theory_ber_out = np.append(theory_ber_out, theory_ber)

    print("snr :", snr)
    print('ber practice: {:.30}%'.format(ber * 100.0 ))
    print('ber real: {:.3}%'.format(theory_ber * 100.0 ))


  if (True):
    plt.figure()
    plt.title("QPSK Snr(dB) vs Ber without Parity Code")
    plt.scatter(snr_out, ber_out, color='r', label='Practical')
    plt.plot(snr_out, theory_ber_out, color='b', label='Theoretical')
    plt.yscale("log")
    plt.grid(True)
    plt.legend()
    plt.show()