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
#from multiprocessing.shared_memory import SharedMemory


class MyPlayer(Player):
  def __init__(self):
    Player.__init__(self)
 #   self.sharedMem = SharedMemory('myfunkyname', True, 1)
    self.lock = threading.Lock()
    self.buttons = []
    _thread.start_new_thread(self.setupListener, ())
    self.providers = setupProviders()
    
  def onPlayBackStarted(self):  # pylint: disable=invalid-name
    self.lock.acquire()
    currentlyPlaying = self.getCurrentlyPlaying()
    print('ddddddddddddddddddddddddddddddddd: ' + str(currentlyPlaying))
    self.cacheId = str(hash(frozenset(currentlyPlaying.items())))
    print('eeeeeeeeeeeeeeeeeeeeeeeeee: ' + str(self.cacheId))
    #test = self.cache.get(self.cacheId)
    #print('ssssssssssssssssssssssss: ' + str(test))  
    #if(not test):
    provider = self.getProvider(currentlyPlaying)
    print('fffffffffffffffffffffffff: ' + str(self.cacheId))
    self.storeButtons(currentlyPlaying, provider)
    self.lock.release()
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
  def getProvider(self, mediaInfo):
    print('mediainfo ' + str(mediaInfo))
    if(mediaInfo['type']=='plugin'):
      print('providers ' + str(self.providers))
      for key,value in self.providers.items():
        match = re.search(key, mediaInfo['pluginpath'])
        if(match):
          return value.Provider(match)
    elif(mediaInfo['type']=='episode'):
      return TvShowProvider(mediaInfo['dbid'])
    elif(mediaInfo['type']=='movie'):
      return MovieProvider(mediaInfo['dbid'])
  def setupListener(self):
    listener = None
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
    while not xbmc.Monitor().abortRequested():
      with Listener(address) as listener:
        with listener.accept() as conn:
          self.lock.acquire()
          conn.send(self.buttons)
          self.lock.release()
    #self.sharedMem.unlink()
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
  
  def storeButtons(self, currentlyPlaying, provider):
    self.buttons = provider.getButtons()
    #toStore = json.dumps(buttons)
    #print('toStore: ' + toStore)
    #print('cacheId: ' + self.cacheId)
    #self.cache.set(self.cacheId, toStore)
