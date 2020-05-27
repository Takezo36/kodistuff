import simplejson as json
import providers.YoutubeProvider as YoutubeProvider
import xbmcgui
#import resources.lib.TwitchProvider as TwitchProvider
#import resources.lib.TvShowProvider as TvShowProvider
#import resources.lib.MovieProvider as MovieProvider

try:
  from urllib.request import Request
  from urllib.request import urlopen
except:
  from urllib2 import Request
  from urllib2 import urlopen

CACHE_ID = "akshd@#asukd!@#"
CACHE_TIME = 999999999
def setupProviders():
  providers = {}
  #provders['plugin:\/\/plugin\.video\.twitch\/\?video_id=[v]*(\d+).*&mode=play.*'] = TwitchProvider
  providers['plugin:\/\/plugin\.video\.youtube\/play/\?video_id=(\w+)'] = YoutubeProvider
  return providers
def doGet(url, headers):
  req = Request(url, headers=headers)
  response = urlopen(req)
  result = response.read()
  return json.loads(result)
def createListItem(label, path, thumb, count, isFolder=None, isPlayable=None, resolvedUrl=None):
#- If a ListItem opens a lower lever list, it must have isFolder=True.
#- If a ListItem calls a playback function that ends with setResolvedUrl, it must have setProperty('isPlayable', 'true') and IsFolder=False.
#- If a ListItem does any other task except for mentioned above, is must have isFolder=False (and only this).
  li = xbmcgui.ListItem(label, offscreen=True)
  li.setArt({'thumb': thumb})
  li.setLabel(label)
  li.setProperty("index", str(count))
  li.setPath(path=path)
  li.setProperty('path', path)
  if(isFolder!=None):
    li.setIsFolder(isFolder)
  if(isPlayable!=None):
    if(isPlayable):
      li.setProperty("isPlayable", "true")
    else:
      li.setProperty("isPlayable", "false")
  #if(resolvedUrl!=None):
    
  return li
