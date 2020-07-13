from __future__ import absolute_import, division, unicode_literals
import xbmc
from xbmc import Monitor
from .Player import MyPlayer
import simplejson as json


class MyMonitor(Monitor):
  
  def __init__(self):
    self.player = MyPlayer()
    Monitor.__init__(self)


  def start(self):
    self.waitForAbort()
    self.player.stopThreads()