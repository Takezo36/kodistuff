# -*- coding: utf-8 -*-

# Copyright (C) 2018 - Benjamin Hebgen <mail>
# This program is Free Software see LICENSE file for details

import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import simplejson as json
import resources.lib.YoutubeProvider as YoutubeProvider
#import resources.lib.TwitchProvider as TwitchProvider
#import resources.lib.TvShowProvider as TvShowProvider
#import resources.lib.MovieProvider as MovieProvider

import re
import subprocess
import urllib


from distutils.util import strtobool
try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

 

ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_USER_DATA_FOLDER = xbmc.translatePath("special://profile/addon_data/"+ADDON_ID)
player = xbmc.Player()

def setupProviders():
  providers = {}
  #provders['plugin:\/\/plugin\.video\.twitch\/\?video_id=[v]*(\d+).*&mode=play.*'] = TwitchProvider
  providers['plugin:\/\/plugin\.video\.youtube\/play/\?video_id=(\w+)'] = YoutubeProvider
  return providers
  
def getProviderForAction(provider):
  temp = 'plugin://' + provider
  length = len(temp)
  for key,value in providers.items():
    if(key[:length] == temp):
      return value.Provider(match)
def getProvider(mediaInfo):
  print('mediainfo ' + str(mediaInfo))
  if(mediaInfo['type']=='plugin'):
    global providers
    print('providers ' + str(providers))
    for key,value in providers.items():
      match = re.search(key, mediaInfo['pluginpath'])
      if(match):
        return value.Provider(match)
  elif(mediaInfo['type']=='episode'):
    return TvShowProvider(mediaInfo['dbid'])
  elif(mediaInfo['type']=='movie'):
    return MovieProvider(mediaInfo['dbid'])
def getRunningmediaInfoInfo():
  item = {}
  global player
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

def getButtons():
  mediaInfo = getRunningmediaInfoInfo()
  provider = getProvider(mediaInfo)
  passToSkin(provider.getButtons())
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
  params = parseArgs()
  providers = setupProviders()
  if('action' in params.keys()):
    action = params['action']
    getProviderForAction(params['provider']).action(action, params)
  else:
    getButtons()
  xbmc.log('finished')

