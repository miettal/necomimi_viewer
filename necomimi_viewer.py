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
import variogram
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
        print p
        continue
      with data_lock :
        data.insert(0, p.value)
        if buf_size < len(data) : data.pop()

def update(i, sp1, sp2, sp3, sp4) :
  global data

  sp1.cla()
  sp2.cla()
  sp3.cla()
  sp4.cla()

  with data_lock :
    sp1.plot(map(lambda x: x*(1.0/sample_rate), range(0, len(data))), data, 'r-')
    sp2.specgram(data, NFFT=sample_rate, Fs=sample_rate)
    sp3.psd(data[:sample_rate], NFFT=sample_rate, Fs=sample_rate)
    sp4.plot(map(lambda x: x*(1.0/sample_rate), range(0, len(data), sample_rate/32)),
      variogram.alpha(data, sample_rate, sample_rate, sample_rate/32), 'r-')

  sp1.set_xlabel("time")
  sp1.set_ylabel("TGAM1 raw data")
  sp1.set_xlim([0, view_length_ms/1000.0])
  sp1.set_ylim([-2048, 2047])

  sp2.set_xlabel("time")
  sp2.set_ylabel("frequency")
  sp2.set_xlim([0, view_length_ms/1000.0])
  sp2.set_ylim([0, 50])

  sp3.set_xlabel("frequency")
  sp3.set_ylabel("psd")
  sp3.set_xlim([0, 50])
  sp3.set_ylim([0, 60])

  sp4.set_ylabel("variogram")
  sp4.set_xlabel("time")
  sp4.set_xlim([0, view_length_ms/1000.0])
  sp4.set_ylim([0.6, 2.0])

if __name__ == '__main__':
  t=threading.Thread(target=save)
  t.daemon = True
  t.start()
  
  fig = plt.figure()
  sp1 = fig.add_subplot(411)
  sp2 = fig.add_subplot(412)
  sp3 = fig.add_subplot(413)
  sp4 = fig.add_subplot(414)

  ani = animation.FuncAnimation(fig, update, fargs=(sp1,sp2,sp3,sp4), interval=200)
  plt.show()
