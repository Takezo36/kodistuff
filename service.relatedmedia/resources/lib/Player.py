from xbmc import Player
from Management import Management
class MyPlayer(Player):
  def __init__(self):
    self.management = Management()
    Player.__init__(self)
    
  def onPlayBackStarted(self):  # pylint: disable=invalid-name
    currentlyPlaying = self.getCurrentlyPlaying()
    self.management.onPlayBackStarted(currentlyPlaying)

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
  