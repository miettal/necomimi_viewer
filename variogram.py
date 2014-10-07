#!/usr/bin/env python
# coding:utf-8
#
# variogram.py
#
# Author:   Hiromasa Ihara (miettal)
# URL:      http://miettal.com
# License:  MIT License
# Created:  2014-10-06
#

import numpy as np

map_f = np.vectorize(lambda a, b : (a-b)**2)

def alpha(x, window_size, f, skip) :
  alpha_ = []
  x = np.array(x)
  for t in range(0, len(x), skip) :
    x_sliced = np.zeros((window_size+2,), dtype=np.int)
    x_sliced[:len(x[t:t+window_size])] = x[t:t+window_size]
    v1 = map_f(x_sliced[:-1], x_sliced[1:]).sum()/(len(x)-1)
    v2 = map_f(x_sliced[:-2], x_sliced[2:]).sum()/(len(x)-2)
    slope = ((np.log(v2)-np.log(v1))/(np.log(2.0)))
    alpha_.append(slope)

  return alpha_
