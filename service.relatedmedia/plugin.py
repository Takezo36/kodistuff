# -*- coding: utf-8 -*-

# Copyright (C) 2018 - Benjamin Hebgen <mail>
# This program is Free Software see LICENSE file for details

import os
import sys
import xbmc
import xbmcvfs
import xbmcgui
import xbmcplugin
import xbmcaddon
import simplejson as json
import urllib
import re
try:
  from urllib.request import Request
  from urllib.request import urlopen
except:
  from urllib2 import Request
  from urllib2 import urlopen
from distutils.util import strtobool
try:
   import StorageServer
except:
   import storageserverdummy as StorageServer
 
CACHE_TIME = 999999
ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_USER_DATA_FOLDER = xbmc.translatePath("special://profile/addon_data/"+ADDON_ID)
PROVIDER_FILE = xbmc.translatePath("special://home")+ "addons" + os.sep + ADDON_ID + os.sep + "resources" + os.sep + "providers.json"
CACHE_ID = "plugin:program:relatedmedia:"
mediaInfoType2Provider = {}
player = xbmc.Player()
count = 0
with open(PROVIDER_FILE) as json_file:
  providersConfig = json.load(json_file)
def findInArray(key, contentList):
  findString = key.split(".*.", 1)[1]
  for entry in contentList:
    result = parseContent(entry, findString)
    if(len(result) > 0):
      return result
  return None
def parseResult(translate, content, array):
  xbmc.log("data yyyyyyyyyyyyyyyyyyyyyy " + str(content))
  if(not array):
    result = {}
    for key, value in translate.items():
      temp=content
      for index in value.split("."):
        xbmc.log("entry")
        xbmc.log(str(temp))
        xbmc.log("index")
        xbmc.log(index)
        if(index.isdigit()):
          temp = temp[int(index)]
        else:
          temp = temp[index]
      result[key] = temp
  else:
    result = []
    count = 0
    temp=content
    tempResult = {}
    for key, value in translate.items():
      splitted = value.split(".")
      for i in range(0, len(splitted)):
        index = splitted[i]
        if(index == "*"):
          count = 0
          for tempEntry in temp:
            if(len(result) <= count):
              tempResult = {}
              result.append(tempResult)
            else:
              tempResult = result[count]
            tempResult[key] = parseResult({key: ".".join(splitted[:i])}, tempEntry, False)
            count += 1
        else:
          if(index.isdigit()):
            temp = temp[int(index)]
          else:
            temp = temp[index]
  return result
def executeJson(command):
  xbmc.log("Command: " + command)
  temp = json.loads(xbmc.executeJSONRPC(command))
  if('result' in temp):
    return temp['result']
  return None
def passToSkin(listItems):
  global handle
  global params
  xbmc.log('passToSkin called')
  xbmc.log('handle ' + str(handle))
  for item in listItems:
    xbmc.log(str(item.getLabel()))
  result = xbmcplugin.addDirectoryItems(handle=handle,
                                     items=[(i.getProperty("path"), i, False) for i in listItems],
                                     totalItems=len(listItems))
  xbmc.log("adding dir was " + str(result))
  xbmcplugin.endOfDirectory(handle)
  #if('id' in params):
  #  windowId = 12901
  #  if('windowid' in params):
  #    windowId = int(Params['windowid'])
  #  xbmcgui.Window(windowId).getControl(int(params['id'])).setEnabled(True)

  xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=xbmcgui.ListItem())  
  return
def getDirectorFolder(director):
  command = '{"jsonrpc": "2.0","method": "Files.GetDirectory","params": {"directory": "videodb://movies/directors/"}, "id": 1}'
  jsonResult = executeJson(command)['files']
  for entry in jsonResult:
    if entry['label'] == director:
      return entry['file']
  
def getSeasonForEpisode(mediaInfo):
  command = '{"jsonrpc": "2.0","method": "Player.GetActivePlayers", "id": 1}'
  #{"id":1,"jsonrpc":"2.0","result":[{"playerid":1,"playertype":"internal","type":"video"}]}
  jsonResult = executeJson(command)
  playerId = jsonResult[0]['playerid']  
  command = '{"jsonrpc": "2.0","method": "Player.GetItem","params": {"playerid": '+str(playerId)+', "properties":["tvshowid","season"]}, "id": 1}'
  jsonResult = executeJson(command)['item']
  xbmc.log(json.dumps(jsonResult))
  global params
  depth = params['depth']
  xbmc.log("depth" + depth)
  if(depth == "0"):
    return 'videodb://tvshows/titles/' +str(jsonResult['tvshowid'])+ '/'+str(jsonResult['season'])+ '/'    
  if(depth == "1"):
    return 'videodb://tvshows/titles/' +str(jsonResult['tvshowid'])+ '/'+str(jsonResult['season'] + 1)+ '/'
  if(depth == "2"):
    return 'videodb://tvshows/titles/' +str(jsonResult['tvshowid'])+ '/'+str(jsonResult['season'] - 1)+ '/'
def getSurroundingMovies(mediaInfo):
  command = '{"jsonrpc": "2.0","method": "Player.GetActivePlayers", "id": 1}'
  #{"id":1,"jsonrpc":"2.0","result":[{"playerid":1,"playertype":"internal","type":"video"}]}
  jsonResult = executeJson(command)
  playerId = jsonResult[0]['playerid']  
  command = '{"jsonrpc": "2.0","method": "Player.GetItem","params": {"playerid": '+str(playerId)+', "properties":["director","setid"]}, "id": 1}'
  jsonResult = executeJson(command)['item']
  if jsonResult['setid'] != 0:
    return 'videodb://movies/sets/'+str(jsonResult['setid'])
  return getDirectorFolder(jsonResult['director'][0])
def createListItemsFromDescriptor(listItemDescriptors):
  result = []
  for listItemDescriptor in listItemDescriptors:
    art = {}
    if("thumb" in listItemDescriptor):
      art['thumb'] = listItemDescriptor['thumb']
    elif("icon" in listItemDescriptor):
      art['icon'] = listItemDescriptor['icon']
    elif("poster" in listItemDescriptor):
      art['poster'] = listItemDescriptor['poster']
    result.append(createListItem(listItemDescriptors['label'], listItemDescriptors['path'], listItemDescriptors['thumb'], listItemDescriptors['label']))
  return result
def doGet(url, headers):
  req = Request(url, headers=headers)
  response = urlopen(req)
  result = response.read()
  xbmc.log(result)
  return json.loads(result)
def findProviderForPlugin(mediaInfo):
  path = mediaInfo['pluginpath']
  providerResult = {}
  providerResult['type'] = None
  providerResult['path'] = []
  global providersConfig
  global params
  toSearch = providersConfig[params['depth']]
  xbmc.log("finding plugin")
  xbmc.log(str(providersConfig))
  for key, values in toSearch.items():
    xbmc.log(path)
    xbmc.log(key)
    xbmc.log(str(values))
    match = re.search(key, path)
    if(match):
      xbmc.log("match")
      result = []
      for providers in values:
        for provider in providers:
          providerType = provider['type']
          if(providerType == 'plugin'):
            # is always last to be called
            providerResult['type'] = "path"            
            path = eval(provider['path'])
            providerResult['path'].append(path)
          elif(providerType == 'getlistitm'):
            # is always last to be called
            providerResult['type'] = "items"
            url = eval(provider['path'])
            headers = {}
            resultMapping = provider['result']
            if 'headers' in provider:   
              for headerName, headerValue in provider['headers'].items():
                headers[headerName] = eval(headerValue)
            rResult = doGet(url, headers)
            listItemDescriptors = parseResult(resultMapping, rResult, True)
            providerResult['path'].append(createListItemFromDescriptor(listItemDescriptors))
          elif(providerType == 'get'):
            url = eval(provider['path'])
            headers = {}
            resultMapping = provider['result']
            if 'headers' in provider:
              for headerName, headerValue in provider['headers'].items():
                headers[headerName] = eval(headerValue)
            xbmc.log("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
            xbmc.log(url)
            xbmc.log(str(headers))
            rResult = doGet(url, headers)
            xbmc.log(str(rResult))
            result.append(parseResult(resultMapping, rResult, False))
      return providerResult      
  xbmc.log("loop ended")
  providerResult['type'] = "items"
  providerResult['path'] = getLastDir()
  xbmc.log("last dir used " + str(providerResult))
  return providerResult
def getRelatedProvider(mediaInfo):
  provider = {}
  if (mediaInfo['type'] == "video"):
    provider['type'] = "path"
    provider['path'] = [mediaInfo['folderpath']]
  elif (mediaInfo['type'] == "episode"):
    provider['type'] = "path"
    provider['path'] = [getSeasonForEpisode(mediaInfo)]
  elif (mediaInfo['type'] == "movie"):
    provider['type'] = "path"
    provider['path'] = [getSurroundingMovies(mediaInfo)]
  elif (mediaInfo['type'] == "plugin"):
    provider = findProviderForPlugin(mediaInfo)
  return provider
def createListItem(name, art, path, label, focused = False):
  global count
  if(focused):
    xbmc.log(":::::::::::::::::::::::::::::::::")
  li = xbmcgui.ListItem(name)
  li.setArt(art)
  li.setLabel(label)
  li.setProperty("isPlayable", "false")
  li.setProperty("index", str(count))
  li.setPath(path=buildPath(art, path, label))
  li.setProperty('path', path)
  li.select(focused)
  count += 1
  return li
def buildPath(art, path, label):
  return "plugin://plugin.program.relatedmedia?play=1&art=" + urllib.quote(json.dumps(art)) + "&path=" + urllib.quote(path) + "&label=" + urllib.quote(label.encode('utf8'))
def getInternalRelated(provider):
  global params
  length = -1
  jsonResult = None
  if('length' in params):
    length = params['length']
  for path in provider['path']:
    command = '{"jsonrpc": "2.0","method": "Files.GetDirectory","params": {"directory": "'+path+'", "properties":["art"]'
    #if(length != -1):
    #  command += ',"limits": {"end":"' + str(length)+'"}'
    command += '}, "id": 1}'
  
    jsonResult = executeJson(command)
    if(jsonResult == None or not 'files' in jsonResult):
      continue
    break
  if(jsonResult == None or not 'files' in jsonResult):
    return None
  jsonResult = jsonResult['files']
  listItems = []
  for entry in jsonResult:
    listItems.append(createListItem(entry['label'], entry['art'], entry['file'], entry['label']))
  return listItems
def getRelatedItems(mediaInfo):
  provider = getRelatedProvider(mediaInfo)
  if(provider['type'] == "path"):
    return getInternalRelated(provider)
  elif(provider['type'] == "items"):
    return provider['path']
  
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

def getRecommendations():
  mediaInfo = getRunningmediaInfoInfo()
  listItems = getRelatedItems(mediaInfo)
  if(listItems):
    passToSkin(listItems)
def addToPlaylist(path, art, label):
  playList = xbmc.PlayList(1)
  pos = playList.getposition();
  pos += 1
  item = createListItem(label, path, art, label)
  playList.add(path, item, pos)
def playNext():
  xbmc.Player().playnext()
  window = xbmcgui.Window(12005)
  window.show()
  window.doModal()
def getLastDir():
  xbmc.log("IIIIIIIIII last dir called")
  cache = StorageServer.StorageServer(CACHE_ID, CACHE_TIME)
  myDir = json.loads(cache.get(cache.get("dir")))
  result = []
  current = xbmc.getInfoLabel('Player.Filenameandpath')
  for entry in myDir:
    result.append(createListItem(entry[0], entry[1], entry[2], entry[0], current==entry[2]))
  return result
def store():
  cache = StorageServer.StorageServer(CACHE_ID, CACHE_TIME)
  currentDir = xbmc.getInfoLabel('Container.FolderPath')
  if(not cache.get(currentDir)):
    lastDir = []
    try:
      for i in range(0, int(xbmc.getInfoLabel('Container.NumItems'))+1):
        art = {}
        iString = str(i)
        label = unicode(xbmc.getInfoLabel('Container.ListItem(' + iString + ').label'), 'utf-8', 'ignore')
        if label == "..":
          continue
        art['thumb'] = xbmc.getInfoLabel('Container.ListItem(' + iString + ').thumb')
        art['icon'] = xbmc.getInfoLabel('Container.ListItem(' + iString + ').icon')
        art['poster'] = xbmc.getInfoLabel('Container.ListItem(' + iString + ').poster')
        path =xbmc.getInfoLabel('Container.ListItem(' + iString + ').FileNameAndPath')
        lastDir.append([label, art, path])
      xbmc.log("LAAAAAAST DIR STORED " + str(lastDir))
      cache.set(currentDir, json.dumps(lastDir))
    except:
      return
  cache.set("dir", currentDir)
  
def getLogging():
  xbmc.log('LOOOK')
  xbmc.log(str(xbmcvfs.listdir("plugin://plugin.video.joyn/?block_id&channel_id&channel_path&client_data&compilation_id&fav_type&mode=channels&movie_id&season_id&stream_type=LIVE&title=Live%20TV&tv_show_id&video_id&viewtype")))
  xbmc.log('1')
  xbmc.log(xbmc.translatePath(xbmc.getInfoLabel('Player.Filenameandpath')))
  if(xbmc.Player().isPlayingVideo()):
    xbmc.log(xbmc.Player().getVideoInfoTag().getMediaType())
  xbmc.log('2')
  xbmc.log(xbmc.getInfoLabel('Container.FolderPath'))
  xbmc.log('3')
  xbmc.log(xbmc.getInfoLabel('Container.FolderName'))
  xbmc.log('4')
  xbmc.log(xbmc.getInfoLabel('Container.CurrentItem'))
  xbmc.log('5')
  xbmc.log(xbmc.getInfoLabel('Player.Filenameandpath'))
  xbmc.log('6')
  xbmc.log(xbmc.getInfoLabel('Player.Folderpath'))
  xbmc.log('7')
  xbmc.log(xbmc.getInfoLabel('Player.Filename'))
  xbmc.log('8')
  xbmc.log(xbmc.getInfoLabel('Player.Title'))
  xbmc.log('9')
  xbmc.log(xbmc.getInfoLabel('VideoPlayer.Title'))
  xbmc.log('10')
  xbmc.log(xbmc.getInfoLabel('VideoPlayer.DBID'))
  xbmc.log('window id')
  xbmc.log(str(xbmcgui.getCurrentWindowId()))
  xbmc.log(str(xbmcgui.getCurrentWindowDialogId()))
  xbmc.log('EEEEEND')
def parseArgs():
  global handle
  handle = int(sys.argv[1])
  params = {}
  args = sys.argv[2][1:]
  if args:
    for argPair in args.split("&"):
      xbmc.log(argPair)
      temp = argPair.split("=")
      xbmc.log(str(temp))
      
      params[temp[0]] = urllib.unquote(temp[1])
  return params
if (__name__ == "__main__"):
  params = parseArgs()
  xbmc.log("args")
  xbmc.log(str(sys.argv))
  xbmc.log("args")
  getLogging()
  if("store" in params):
    store()
  elif(xbmc.Player().isPlaying()):
    if("play" in params):
      addToPlaylist(params['path'], json.loads(params['art']), params['label'])
      if(params['play'] == "1"):
        playNext()
    else:
      getRecommendations()
  else:
    xbmc.log("not playing")
  xbmc.log('finished')

