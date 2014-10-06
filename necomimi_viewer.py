#!/usr/bin/env python
# coding:utf-8
#
# necomimi_viewer.py
#
# Author:   Hiromasa Ihara (miettal)
# URL:      http://miettal.com
# License:  MIT License
# Created:  2014-10-04
#

import sys
import os
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import thinkgear
import numpy as np

save_length_ms = 12000
view_length_ms = 10000
flash_rate = 1
sample_rate = 512

if os.uname()[0] == "Linux" :
  PORT = "/dev/ttyUSB0"
else :
  PORT = '/dev/tty.usbserial-AE01AQ3X'

data = []
data_lock = threading.Lock()

def save() :
  global data
  buf_size = int(save_length_ms/1000.0*sample_rate)
  for packets in thinkgear.ThinkGearProtocol(PORT).get_packets():
    for p in packets:
      if not isinstance(p, thinkgear.ThinkGearRawWaveData):
        continue 
      with data_lock :
        data.insert(0, p.value)
        if buf_size < len(data) : data.pop()

def update(i, sp1, sp2, sp3) :
  global data

  sp1.cla()
  sp2.cla()
  sp3.cla()

  with data_lock :
    sp1.plot(map(lambda x: x*(1.0/sample_rate), range(0, len(data))), data, 'r-')
    sp2.specgram(data, NFFT=sample_rate, Fs=sample_rate)
    sp3.psd(data[:sample_rate], NFFT=sample_rate, Fs=sample_rate)

  sp1.set_xlabel("time")
  sp1.set_ylabel("TGAM1 raw data")
  sp1.set_xlim([0, view_length_ms/1000.0])
  sp1.set_ylim([-2048, 2047])

  sp2.set_xlabel("time")
  sp2.set_ylabel("frequency")
  sp2.set_xlim([0, view_length_ms/1000.0])
  sp2.set_ylim([0, 20])

  sp3.set_xlim([0, 20])
  sp3.set_ylim([0, 60])
  sp3.set_xlabel("frequency")
  sp3.set_ylabel("psd")

if __name__ == '__main__':
  t=threading.Thread(target=save)
  t.daemon = True
  t.start()
  
  fig = plt.figure()
  sp1 = fig.add_subplot(311)
  sp2 = fig.add_subplot(312)
  sp3 = fig.add_subplot(313)

  ani = animation.FuncAnimation(fig, update, fargs=(sp1,sp2,sp3), interval=30)
  plt.show()
