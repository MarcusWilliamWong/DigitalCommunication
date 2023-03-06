'''
Author       : Eureke
Date         : 2023-02-17 16:37:45
LastEditors  : Marcus Wong
LastEditTime : 2023-02-25 12:54:31
Description  : 
'''
import komm
from matplotlib import pyplot as plt
import numpy as np
s = 1
for i in range(5):
  if s:
    s = 0
    i = i - 1
    # print(i)
  else:
    s = 1
    # print(i)

# for i in np.arange(5, 9, 0.5):
  # print(i)

# tx_bin = [0, 1, 1, 0]
# psk = komm.PSKModulation(4, phase_offset=np.pi/4)
# print(psk.constellation)
# plt.figure()
# plt.plot(numpy.real(psk.constellation), numpy.imag(psk.constellation))
# plt.show()
# tx_data = q.modulate(tx_bin)

from pymediainfo import MediaInfo
fp = 'D:/Documents/WeChat Files/wxid_39ljlvnv88eh12/FileStorage/Video/2023-02/6f44f5c9ba985d72946f00e545f8c4ae.mp4'
media_info = MediaInfo.parse(fp)
# print(media_info)
data = media_info.to_json()
print(data)