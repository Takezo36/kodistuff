# -*- coding: utf-8 -*-

# Copyright (C) 2018 - Benjamin Hebgen <mail>
# This program is Free Software see LICENSE file for details
import urllib.parse

def parseArgs():
  global handle
  params = {}
  try:
    handle = int(sys.argv[1])
    args = sys.argv[2][1:]
  except:
    args = sys.argv[1]
  if args:
    for argPair in args.split("&"):
      temp = argPair.split("=")
      params[temp[0]] = urllib.parse.unquote(temp[1])
  return params

import os
import sys
params = parseArgs()
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
sys.argv = ['']
from resources.lib.Commons import setupProviders
from resources.lib.Commons import createListItem
from multiprocessing.connection import Client
#from multiprocessing.shared_memory import SharedMemory


  
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
def getButtonsForSkin():
  listItems = getButtonListItems()
  passToSkin(listItems)
def getButtonListItems():
  print('5555555555555555555')
  currentlyPlaying = getRunningmediaInfoInfo()
  #sharedMem = SharedMemory('myfunkyname', False, 1)
  port = 7777#sharedMem.buf[0]
  #shareMem.close()
  address = ('localhost', port)
  with Client(address) as conn:
    conn.send(1)
    buttons = conn.recv()
    conn.close()
  return getListItems(buttons)
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

def showPopUpDialog():
  from resources.lib.dialogs.PopUpDialog import PopUpDialog
  buttons = getButtonListItems()
  popUpDialog = PopUpDialog("plugin-extrabuttons-popup.xml", xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), "default", "1080i", buttons=buttons)
  popUpDialog.doModal()

if (__name__ == "__main__"):
  print('111111111111111111111')
  print('2222222222222222')
  providers = setupProviders()
  if('action' in params.keys()):
    print('33333333333333333')
    print(str(params))
    action = params['action']
    if(action == 'buttons'):
      getButtonsForSkin()
    elif(action == 'open'):
      xbmcgui.Window(12901).close()
      cmd = 'ActivateWindow(videos, ' + params['path'] + ')'
      print(cmd)
      xbmc.executebuiltin(cmd)
    else:
      getProviderForAction(params['provider']).doAction(action, params)
  else:
    showPopUpDialog()
  xbmc.log('finished')

