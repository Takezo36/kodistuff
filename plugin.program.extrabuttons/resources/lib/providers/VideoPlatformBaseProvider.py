#from youtube.youtube_requests import get_videos as getVideos
import xbmc
import xbmcgui
import xbmcaddon
import os
import _thread
from multiprocessing.connection import Client
from urllib.request import Request
from urllib.request import urlopen

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
    commentsDialog = CommentsDialog("plugin-extrabuttons-comments.xml", xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), "default", "1080i", comments=comments, loadMoreFunction=self.loadMore, replyFunction=self.replyToComment)
    commentsDialog.doModal()
  def doAction(self, action, params):
    if('show_comment' == action):
      self.showComments(params['video_id'])
      return True
    if('show_chat' == action):
      self.showChat(params['video_id'])
      return True
    if('upvote' == action or 'downvote' == action):
      rate = self.rate(params['rate'], self.getRating(params['video_id']), params['video_id'])
      xbmcgui.Dialog().ok("Voted " + rate, "Voted " + rate)
      return True
    if('show_related' == action):
      self.showRelated(params['video_id'])
      return True
    return False
  def getPreloadData(self):
    port = 7777#sharedMem.buf[0]
    #shareMem.close()
    address = ('localhost', port)
    with Client(address) as conn:
      conn.send(0)
      preload = conn.recv()
      conn.close()
    return preload
  def doGet(self, url, headers):
    print('do get')
    print(str(headers))
    print(str(url))
    print('do get')
    req = Request(url, headers=headers)
    response = urlopen(req)
    result = response.read()
    return json.loads(result)
  def getStoredData(self):
    port = 7777#sharedMem.buf[0]
    #shareMem.close()
    address = ('localhost', port)
    with Client(address) as conn:
      conn.send(3)
      preload = conn.recv()
      conn.close()
    return preload
  def storeData(self, data):
    port = 7777#sharedMem.buf[0]
    #shareMem.close()
    address = ('localhost', port)
    with Client(address) as conn:
      conn.send(2)
      conn.send(data)
      conn.close()
  def showRelated(self, videoId):
    relatedInfo = self.getRelatedVideos(videoId)#self.getPreloadData()
    from resources.lib.dialogs.RelatedMediaDialog import RelatedMediaDialog
    relatedMediaDialog = RelatedMediaDialog("plugin-extrabuttons-relatedmedia.xml", xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), "default", "1080i", content=relatedInfo)
    relatedMediaDialog.doModal()
  