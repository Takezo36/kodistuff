# -*- coding: utf-8 -*-

# Copyright (C) 2018 - Benjamin Hebgen <mail>
# This program is Free Software see LICENSE file for details
import xbmc
from xbmc import Player
from .Commons import setupProviders
from .Commons import CACHE_ID
from .Commons import CACHE_TIME
import simplejson as json
import re
try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

class MyPlayer(Player):
  def __init__(self):
    Player.__init__(self)
    self.providers = setupProviders()
    self.cache = StorageServer.StorageServer(CACHE_ID, CACHE_TIME)
    
  def onPlayBackStarted(self):  # pylint: disable=invalid-name
    print('ddddddddddddddddddddddddddddddddd')
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
  def storeButtons(self, currentlyPlaying, provider):
    buttons = provider.getButtons()
    toStore = json.dumps(buttons)
    print('toStore: ' + toStore)
    print('cacheId: ' + self.cacheId)
    self.cache.set(self.cacheId, toStore)