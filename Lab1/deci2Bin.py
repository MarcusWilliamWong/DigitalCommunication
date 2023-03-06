'''
Author       : Eureke
Date         : 2023-01-24 10:39:31
LastEditors  : Marcus Wong
LastEditTime : 2023-01-24 10:54:39
Description  : 
'''
def deci2Bin(n):
  if n >= 2:
    deci2Bin(n // 2)
  print(n % 2, end='')
  return n % 2

deci2Bin(2635088)