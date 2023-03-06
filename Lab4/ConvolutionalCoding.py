'''
Author       : Eureke
Date         : 2023-03-05 17:25:06
LastEditors  : Marcus Wong
LastEditTime : 2023-03-05 18:23:14
Description  : 
'''

import komm
code = komm.ConvolutionalCode(feedback_polynomials=[[0o7, 0o5]])
tblen = 18
encoder = komm.ConvolutionalStreamEncoder(code)
decoder = komm.ConvolutionalStreamDecoder(code, traceback_length=tblen, input_type="hard")