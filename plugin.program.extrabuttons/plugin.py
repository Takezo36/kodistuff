# -*- coding: utf-8 -*-

# Copyright (C) 2018 - Benjamin Hebgen <mail>
# This program is Free Software see LICENSE file for details

import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import simplejson as json
from resources.lib.Commons import setupProviders
from resources.lib.Commons import createListItem
from resources.lib.Commons import CACHE_ID
from resources.lib.Commons import CACHE_TIME



from distutils.util import strtobool
try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

 


  
def getProviderForAction(provider):
  global providers
  print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
  print(str(providers))
  temp = 'plugin:\/\/' + provider.replace('.','\.')
  length = len(temp)
  print(temp)
  for key,value in providers.items():
    if(key[:length] == temp):
      return value.Provider()
def getRunningmediaInfoInfo():
  item = {}
  player = xbmc.Player()
  if(player.isPlayingVideo()):
    mediaType = xbmc.Player().getVideoInfoTag().getMediaType()
    if("episode" == mediaType or "movie" == mediaType):
      item['type'] = mediaType
      item['dbid'] = xbmc.getInfoLabel('VideoPlayer.DBID')
    else:
      if(len(xbmc.getInfoLabel('Player.Filenameandpath')) > 9 and xbmc.getInfoLabel('Player.Filenameandpath')[:9] == "plugin://"):
        item['type'] = "plugin"
        item['pluginpath'] = xbmc.getInfoLabel('Player.Filenameandpath')
      else:
        item['type'] = "video"
        item['folderpath'] = xbmc.getInfoLabel('Player.Folderpath')
  elif(player.isPlayingAudio()):
    item['type'] = "audio"
  else:
    item['type'] = "plugin"
    item['pluginpath'] = xbmc.getInfoLabel('Player.Filenameandpath')
  return item
def getListItems(buttons):
  count = 0
  result = []
  for button in buttons:
    result.append(createListItem(button['label'], button['path'], button['logo'], count, button['isFolder'], button['isPlayable'], button['resolvedUrl']))
    count += 1
  return result
def getButtons():
  print('5555555555555555555')
  currentlyPlaying = getRunningmediaInfoInfo()
  cache = StorageServer.StorageServer(CACHE_ID, CACHE_TIME)
  cacheId = str(hash(frozenset(currentlyPlaying.items())))
  jsonStr = None
  print('cacheId: ' + cacheId)
  jsonStr = cache.get(cacheId)
  print('jsonStr: ' + jsonStr)
  buttons = json.loads(jsonStr)
  passToSkin(getListItems(buttons))
def passToSkin(listItems):
  global handle
  global params
  print('Passing Listitemsssssssss')
  print(str(listItems))
  result = xbmcplugin.addDirectoryItems(handle=handle,
                                     items=[(i.getProperty("path"), i, False) for i in listItems],
                                     totalItems=len(listItems))
  xbmcplugin.endOfDirectory(handle)
  xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=xbmcgui.ListItem())  
  return

def parseArgs():
  global handle
  handle = int(sys.argv[1])
  params = {}
  args = sys.argv[2][1:]
  if args:
    for argPair in args.split("&"):
      temp = argPair.split("=")
      params[temp[0]] = urllib.unquote(temp[1])
  return params
if (__name__ == "__main__"):
  print('111111111111111111111')
  params = parseArgs()
  print('2222222222222222')
  providers = setupProviders()
  if('action' in params.keys()):
    print('33333333333333333')
    print(str(params))
    action = params['action']
    getProviderForAction(params['provider']).doAction(action, params)
  else:
    print('4444444444444444444444444')
    getButtons()
  xbmc.log('finished')

