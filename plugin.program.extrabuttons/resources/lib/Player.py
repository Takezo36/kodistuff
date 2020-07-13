# -*- coding: utf-8 -*-

# Copyright (C) 2018 - Benjamin Hebgen <mail>
# This program is Free Software see LICENSE file for details
import xbmc
from xbmc import Player
from .Commons import setupProviders
import re
import threading
import _thread
import random
from multiprocessing.connection import Listener
from multiprocessing.connection import Client

#from multiprocessing.shared_memory import SharedMemory


class MyPlayer(Player):
  def __init__(self):
    Player.__init__(self)
 #   self.sharedMem = SharedMemory('myfunkyname', True, 1)
    self.buttonLock = threading.Lock()
    self.preloadLock = threading.Lock()
    self.buttons = []
    self.preload = {}
    self.id2buttons = {}
    self.id2preload = {}
    _thread.start_new_thread(self.setupListener, ())
    self.providers = setupProviders()
    
  def onPlayBackStarted(self):  # pylint: disable=invalid-name
    self.tempStore = 'None'
    self.preloadLock.acquire()
    self.buttonLock.acquire()
    currentlyPlaying = self.getCurrentlyPlaying()
    provider = self.getProvider(currentlyPlaying)
    self.storePreload(currentlyPlaying, provider)
    self.preloadLock.release()
    self.storeButtons(currentlyPlaying, provider)
    self.buttonLock.release()
  def getCurrentlyPlaying(self):
    item = {}
    if(self.isPlayingVideo()):
      mediaType = self.getVideoInfoTag().getMediaType()
      if(("episode" == mediaType) or ("movie" == mediaType)):
        item['dbid'] = xbmc.getInfoLabel('VideoPlayer.DBID')
        if(item['dbid']):
          item['type'] = mediaType
        else:
          if(len(xbmc.getInfoLabel('Player.Filenameandpath')) > 9 and xbmc.getInfoLabel('Player.Filenameandpath')[:9] == "plugin://"):
            item['type'] = "plugin"
            item['pluginpath'] = xbmc.getInfoLabel('Player.Filenameandpath')
          else:
            item['type'] = "video"
            item['folderpath'] = xbmc.getInfoLabel('Player.Folderpath')
      else:
        if(len(xbmc.getInfoLabel('Player.Filenameandpath')) > 9 and xbmc.getInfoLabel('Player.Filenameandpath')[:9] == "plugin://"):
          item['type'] = "plugin"
          item['pluginpath'] = xbmc.getInfoLabel('Player.Filenameandpath')
        else:
          item['type'] = "video"
          item['folderpath'] = xbmc.getInfoLabel('Player.Folderpath')
    elif(self.isPlayingAudio()):
      item['type'] = "audio"
    else:
      item['type'] = "plugin"
      item['pluginpath'] = xbmc.getInfoLabel('Player.Filenameandpath')
    return item
  def stopThreads(self):
    self.stop = True
    port = 7777
    address = ('localhost', port)
    with Client(address) as conn:
      conn.send(-1)
      preload = conn.recv()
      conn.close()
  def getProvider(self, mediaInfo):
    if(mediaInfo['type']=='plugin'):
      for key,value in self.providers.items():
        match = re.search(key, mediaInfo['pluginpath'])
        if(match):
          return value.Provider(match, mediaInfo['pluginpath'])
    elif(mediaInfo['type']=='episode'):
      return TvShowProvider(mediaInfo['dbid'])
    elif(mediaInfo['type']=='movie'):
      return MovieProvider(mediaInfo['dbid'])
  def setupListener(self):
    listener = None
    self.stop = False
    port = 7777
    count = 0
    #while listener == None:
    #  if(count > 5):
    #    raise NameError#figure out a proper error...
      #port = random.randint(1025, 65535)
    #  listener = self.getListener(port)
    #  count += 1
    #self.publishPort(port)
    address = ('localhost', port)
    while not self.stop:
      with Listener(address) as listener:
        with listener.accept() as conn:
          value = conn.recv()
          if(value == 0):
            self.preloadLock.acquire()
            conn.send(self.preload)
            self.preloadLock.release()
          elif(value == 1):
            self.buttonLock.acquire()
            conn.send(self.buttons)
            self.buttonLock.release()
          elif(value == 2):
            self.tempStore = conn.recv()
          elif(value == 3):
            conn.send(self.tempStore)
          elif(value == 4):
            command = conn.recv()
            xbmc.executebuiltin(command)
          elif(value == 5):
            url = conn.recv()
            self.stop()
            self.play(url)
  def publishPort(self, port):
    #self.sharedMem.buf[0] = port
    #self.sharedMem.close()
    return    
  def getListener(self, port):
    address = ('localhost', port)
    try:
      with Listener(address) as listener:
        return listener
    except:
      return None
  
  def storePreload(self, currentlyPlaying, provider):
    contentId = provider.getId()
    if(contentId in self.id2preload):
      self.preload = self.id2preload[contentId]
    else:
      self.preload = provider.preload()
      self.id2preload[contentId] = self.preload
  def storeButtons(self, currentlyPlaying, provider):
    contentId = provider.getId()
    if(contentId in self.id2buttons):
      self.buttons = self.id2buttons[contentId]
    else:
      self.buttons = provider.getButtons()
      self.id2buttons[contentId] = self.buttons
    
    #toStore = json.dumps(buttons)
    print('toStore: ' + str(self.buttons))
    #print('cacheId: ' + self.cacheId)
    #self.cache.set(self.cacheId, toStore)
