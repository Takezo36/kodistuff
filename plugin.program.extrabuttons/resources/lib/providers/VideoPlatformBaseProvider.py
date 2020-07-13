#from youtube.youtube_requests import get_videos as getVideos
import xbmc
import xbmcgui
import xbmcaddon
import os
import _thread
from multiprocessing.connection import Client
from urllib.request import Request
from urllib.request import urlopen
import simplejson as json
#from resources.lib.Commons import getFolderList
class VideoPlatformBaseProvider:
  ADDON_MEDIA = xbmc.translatePath("special://home")+ "addons" + os.sep + "plugin.program.extrabuttons" + os.sep + "resources" + os.sep + "skins" + os.sep + "default" + os.sep + "media" + os.sep
  
  def getCommentsButton(self, logo):
    return {'label': 'Comments', 'path': 'provider='+self.providerName+'&action=show_comment&video_id='+self.videoId, 'logo': logo, 'isFolder': False, 'isPlayable':False, 'resolvedUrl':None}
  def getChatButton(self, logo):
    return {'label': 'Chat', 'path': 'provider='+self.providerName+'&action=show_chat&video_id='+self.videoId, 'logo': logo, 'isFolder': False, 'isPlayable':False, 'resolvedUrl':None}
  def getChannelButton(self, name, logo, path):
    return {'label': name, 'path': 'action=open&path=' + path, 'logo': logo, 'isFolder': True, 'isPlayable': False, 'resolvedUrl':None}
  def showChat(self, videoId):
    from resources.lib.dialogs.ChatDialog import ChatDialog
    chatDialog = ChatDialog("plugin-extrabuttons-chat.xml", xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), "default", "1080i", replyFunction=self.replyToChat, baseId=videoId)
    _thread.start_new_thread(self.getChatMessages, (chatDialog,))
    chatDialog.doModal()
  def showComments(self, comments):
    from resources.lib.dialogs.CommentsDialog import CommentsDialog
    commentsDialog = CommentsDialog("plugin-extrabuttons-comments.xml", xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), "default", "1080i", comments=comments, loadMoreFunction=self.loadMore, replyFunction=self.replyToComment, reloadFunction=self.reload)
    commentsDialog.doModal()
  def executeJson(self, command):
    xbmc.log("Command: " + command)
    temp = json.loads(xbmc.executeJSONRPC(command))
    if('result' in temp):
      return temp['result']
    return None

  def getPreloadData(self):
    return self.receiveData(0)
  def doGet(self, url, headers):
    req = Request(url, headers=headers)
    response = urlopen(req)
    result = response.read()
    return json.loads(result)
  def getStoredData(self):
    return self.receiveData(3)
  def storeData(self, data):
    self.sendData(2, data)
  def showRelated(self, videoId):
    relatedInfo = self.getRelatedVideos(videoId)#self.getPreloadData()
    from resources.lib.dialogs.RelatedMediaDialog import RelatedMediaDialog
    relatedMediaDialog = RelatedMediaDialog("plugin-extrabuttons-relatedmedia.xml", xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), "default", "1080i", content=relatedInfo, playFunction=self.play)
    relatedMediaDialog.doModal()
  def stopChat():
    self.stop = True
  def receiveData(self, command):
    port = 7777#sharedMem.buf[0]
    #shareMem.close()
    address = ('localhost', port)
    with Client(address) as conn:
      conn.send(command)
      data = conn.recv()
      conn.close()
    return data
  def sendData(self, command, data):
    port = 7777#sharedMem.buf[0]
    #shareMem.close()
    address = ('localhost', port)
    with Client(address) as conn:
      conn.send(command)
      conn.send(data)
      conn.close()
  def executeBuiltin(self, command):
    self.sendData(4, command)
  def playNow(self, url):
    self.sendData(5, url)    