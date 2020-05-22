import xbmc
import os
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

from xbmcaddon import Addon
from Window import MyWindow
from threading import Lock

class Management:

  ADDON = Addon()
  ADDON_ID = ADDON.getAddonInfo('id')
  lock = Lock()
  PROVIDER_FILE = xbmc.translatePath("special://home")+ "addons" + os.sep + ADDON_ID + os.sep + "resources" + os.sep + "providers.json"
  with open(PROVIDER_FILE) as json_file:
    providersConfig = json.load(json_file)
  
  def __init__(self, *args, **kwargs):
    return

  def get_addon_info(self, key):
    return self.ADDON.getAddonInfo(key)


  def addon_id(self):
    return self.get_addon_info('id')


  def addon_path(self):
    return self.get_addon_info('path')
  def __init__(self):
    self.myWindow = MyWindow('script-relatedmedia-window.xml', self.addon_path(), 'default', '1080i')
  def set_last_file(self, filename):
    self.state.last_file = filename

  def get_last_file(self):
    return self.state.last_file


  def onPlayBackStarted(self, currentlyPlaying):  # pylint: disable=invalid-name
    #TODO: check to thread off here
    self.myWindow.reset()
    self.myWindow.setLoading()
    provider = self.getProvider(currentlyPlaying)
    self.myWindow.addItems(self.loadFolder(provider))
    self.myWindow.removeLoading()
  def show(self):
    self.myWindow().doModal()
    return

  def getProvider(self, currentlyPlaying):
    provider = {}
    if (currentlyPlaying['type'] == "video"):
      provider['type'] = "path"
      provider['path'] = [currentlyPlaying['folderpath']]
    elif (currentlyPlaying['type'] == "episode"):
      provider['type'] = "path"
      provider['path'] = [self.getSeasonForEpisode(mediaInfo)]
    elif (mediaInfo['type'] == "movie"):
      provider['type'] = "path"
      provider['path'] = [self.getSurroundingMovies(mediaInfo)]
    elif (mediaInfo['type'] == "plugin"):
      provider = self.findProviderForPlugin(mediaInfo)
    return provider

  def loadFolder(self, provider):
    if(provider['type'] == "path"):
      return getInternalRelated(provider)
    elif(provider['type'] == "items"):
      return provider['path']
  def findInArray(self, key, contentList):
    findString = key.split(".*.", 1)[1]
    for entry in contentList:
      result = parseContent(entry, findString)
      if(len(result) > 0):
        return result
    return None
  def parseResult(self, translate, content, array):
    xbmc.log("data yyyyyyyyyyyyyyyyyyyyyy " + str(content))
    if(not array):
      result = {}
      for key, value in translate.items():
        temp=content
        for index in value.split("."):
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
  def executeJson(self, command):
    xbmc.log("Command: " + command)
    temp = json.loads(xbmc.executeJSONRPC(command))
    if('result' in temp):
      return temp['result']
    return None
  def passToWindow(self, listItems):
    return
  def getDirectorFolder(self, director):
    command = '{"jsonrpc": "2.0","method": "Files.GetDirectory","params": {"directory": "videodb://movies/directors/"}, "id": 1}'
    jsonResult = executeJson(command)['files']
    for entry in jsonResult:
      if entry['label'] == director:
        return entry['file']
  def getSeasonForEpisode(self, mediaInfo):
    command = '{"jsonrpc": "2.0","method": "Player.GetActivePlayers", "id": 1}'
    #{"id":1,"jsonrpc":"2.0","result":[{"playerid":1,"playertype":"internal","type":"video"}]}
    jsonResult = executeJson(command)
    playerId = jsonResult[0]['playerid']  
    command = '{"jsonrpc": "2.0","method": "Player.GetItem","params": {"playerid": '+str(playerId)+', "properties":["tvshowid","season"]}, "id": 1}'
    jsonResult = executeJson(command)['item']
    xbmc.log(json.dumps(jsonResult))
    return 'videodb://tvshows/titles/' +str(jsonResult['tvshowid'])+ '/'+str(jsonResult['season'])+ '/'    
  def getSurroundingMovies(self, mediaInfo):
    command = '{"jsonrpc": "2.0","method": "Player.GetActivePlayers", "id": 1}'
    #{"id":1,"jsonrpc":"2.0","result":[{"playerid":1,"playertype":"internal","type":"video"}]}
    jsonResult = executeJson(command)
    playerId = jsonResult[0]['playerid']  
    command = '{"jsonrpc": "2.0","method": "Player.GetItem","params": {"playerid": '+str(playerId)+', "properties":["director","setid"]}, "id": 1}'
    jsonResult = executeJson(command)['item']
    if jsonResult['setid'] != 0:
      return 'videodb://movies/sets/'+str(jsonResult['setid'])
    return getDirectorFolder(jsonResult['director'][0])
  def createListItemsFromDescriptor(self, listItemDescriptors):
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
  def doGet(self, url, headers):
    req = Request(url, headers=headers)
    response = urlopen(req)
    result = response.read()
    xbmc.log(result)
    return json.loads(result)
  def findProviderForPlugin(self, mediaInfo):
    path = mediaInfo['pluginpath']
    providerResult = {}
    providerResult['type'] = None
    providerResult['path'] = []
    toSearch = self.providersConfig[0]
    xbmc.log("finding plugin")
    xbmc.log(str(providersConfig))
    for key, values in toSearch.items():
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