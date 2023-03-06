'''
Author       : Eureke
Date         : 2023-03-05 09:22:37
LastEditors  : Marcus Wong
LastEditTime : 2023-03-05 22:37:48
Description  : 
'''
import komm
import numpy as np
# Length = 2^miu - 1
# 
code = komm.BCHCode(mu=3, tau=1)
# n, k = code.length, code.dimension
print(code.length, code.dimension)
print(code.generator_polynomial)
print(code.generator_matrix)

message = np.array([1, 0, 0, 1])
recvword = code.encode(message)
print(recvword)

message_decoded = code.decode(recvword)
print(message_decoded)

print(np.dot(message, code.generator_matrix) % 2)
