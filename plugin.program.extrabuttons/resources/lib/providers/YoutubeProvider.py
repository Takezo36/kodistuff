#from youtube.youtube_requests import get_videos as getVideos
import xbmc
import xbmcgui
import xbmcaddon
import os
import urllib
import simplejson as json
import _thread
import time
from youtube_requests import get_videos as getVideos
from youtube_requests import get_channels as getChannels
from youtube_requests import v3_request as v3Request
from youtube_requests import __get_core_components as getCoreComponents

class Provider:
  MEDIA_BASE = xbmc.translatePath("special://home")+ "addons" + os.sep + "plugin.video.youtube" + os.sep + "resources" + os.sep + "media" + os.sep 
  count = 0
  def __init__(self, match=None):
    if(match):
      videoId = match.group(1)
      parts = ['snippet,statistics,liveStreamingDetails']
      params = {'part': ''.join(parts), 'id': videoId}
      self.videoInfo = v3Request(method='GET', path='videos', params=params)
      self.channelInfo = getChannels(self.videoInfo['items'][0]['snippet']['channelId'])
    return
  def getButtons(self):
    result = []
    result.append(self.getChannelButton())
    result.append(self.getUpVoteButton())
    result.append(self.getDownVoteButton())
    if(self.videoInfo['items'][0]['snippet']['liveBroadcastContent'] == 'live'):
      result.append(self.getChatButton())
    else:
      result.append(self.getCommentsButton())
    #result.append(self.getRelatedVideos())
    return result
  def getChannelButton(self):
    channelLogo = self.channelInfo[0]['snippet']['thumbnails']['default']['url']
    channelName = self.channelInfo[0]['snippet']['title']
    return {'label': channelName, 'path': 'action=open&path=plugin://plugin.video.youtube/channel/'+self.channelInfo[0]['id']+'/', 'logo': channelLogo, 'isFolder': True, 'isPlayable': False, 'resolvedUrl':None}
  def getUpVoteButton(self): 
    logo = self.MEDIA_BASE + 'likes.png'
    try:
      upVotes = self.videoInfo['items'][0]['statistics']['likeCount']
    except:
      upVotes = '0'
    return {'label': upVotes, 'path': 'provider=plugin.video.youtube&action=upvote&rate=like&video_id='+self.videoInfo['items'][0]['id'], 'logo': logo, 'isFolder': True, 'isPlayable':False, 'resolvedUrl':None}
  def getDownVoteButton(self):
    logo = self.MEDIA_BASE + 'dislikes.png'
    try:
      downVotes = self.videoInfo['items'][0]['statistics']['dislikeCount']
    except:
      downVotes = '0'
    return {'label': downVotes, 'path': 'provider=plugin.video.youtube&action=downvote&rate=dislike&video_id='+self.videoInfo['items'][0]['id'], 'logo': logo, 'isFolder': True, 'isPlayable':False, 'resolvedUrl':None}
  def getCommentsButton(self):
    logo = self.MEDIA_BASE + 'playlist.png'
    return {'label': 'Comments', 'path': 'provider=plugin.video.youtube&action=show_comment&video_id='+self.videoInfo['items'][0]['id'], 'logo': logo, 'isFolder': False, 'isPlayable':False, 'resolvedUrl':None}
  def getChatButton(self):
    logo = self.MEDIA_BASE + 'playlist.png'
    return {'label': 'Chat', 'path': 'provider=plugin.video.youtube&action=show_chat&video_id='+self.videoInfo['items'][0]['id'], 'logo': logo, 'isFolder': False, 'isPlayable':False, 'resolvedUrl':None}
  def showChat(self, videoId):
    parts = ['snippet,statistics,liveStreamingDetails']
    params = {'part': ''.join(parts), 'id': videoId}
    self.videoInfo = v3Request(method='GET', path='videos', params=params)
    from resources.lib.ChatDialog import ChatDialog
    chatDialog = ChatDialog("plugin-extrabuttons-chat.xml", xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), "default", "1080i", replyFunction=self.replyToChat, baseId=videoId)
    _thread.start_new_thread(self.getChatMessages, (chatDialog,))
    chatDialog.doModal()
  def getChatMessages(self, chatDialog):
    try:
      chatId = self.videoInfo['items'][0]['liveStreamingDetails']['activeLiveChatId']
    except:
      xbmcgui.Dialog().ok("Failed to get live chat", "No live chat available")
    
    parts = ['snippet,authorDetails']
    params = {'part': ''.join(parts), 'liveChatId': chatId}

    messages = v3Request(method='GET', path='liveChat/messages', params=params)
    
    while not xbmc.Monitor().abortRequested():
      for item in messages['items']:
        msg = {}
        msg['author'] = item['authorDetails']['displayName']
        msg['date'] = item['snippet']['publishedAt']
        msg['value'] = item['snippet']['displayMessage']
        msg['thumb'] = item['authorDetails']['profileImageUrl']
        chatDialog.updateContent(msg)
      waitTime = messages['pollingIntervalMillis']
      time.sleep(waitTime/1000)
      params['pageToken'] = messages['nextPageToken']
      messages = v3Request(method='GET', path='liveChat/messages', params=params)
  def showComments(self, videoId, page=None):
    items = self.getComments(videoId, True)
    comments = []
    for item in items:
      comment = {}
      comment['author'] = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
      comment['date'] = item['snippet']['topLevelComment']['snippet']['publishedAt']
      comment['value'] = item['snippet']['topLevelComment']['snippet']['textOriginal']
      comment['thumb'] = item['snippet']['topLevelComment']['snippet']['authorProfileImageUrl']
      comment['loadmoreid'] = item['id']
      comment['replyId'] = item['id']
      comments.append(comment)
    from resources.lib.CommentsDialog import CommentsDialog
    commentsDialog = CommentsDialog("plugin-extrabuttons-comments.xml", xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), "default", "1080i", comments=comments, loadMoreFunction=self.getComments, replyFunction=self.replyToComment, baseId=videoId)
    commentsDialog.doModal()
  def getComments(self, videoId, isHome = False):
    if(isHome):
      params = {'part': 'snippet',
               'videoId': videoId,
               'order': 'relevance',
               'textFormat': 'plainText',
               'maxResults': '50'}
      path = 'commentThreads'
    else:
      params = {'part': 'snippet',
                'parentId': videoId,
                'textFormat': 'plainText',
                'maxResults': '50'}
      path = 'comments'
    provider, context, client = getCoreComponents()
    result = client.perform_v3_request(method='GET', path=path, params=params, no_login=True)
    return result['items']
  def replyToComment(self, commentId):
    return
  def replyToChat(self, chatId):
    return
  def doAction(self, action, params):
    if('show_comment' == action):
      self.showComments(params['video_id'])
    elif('show_chat' == action):
      self.showChat(params['video_id'])
    elif('upvote' == action or 'downvote' == action):
      rate = self.rate(params['rate'], self.getRating(params['video_id']), params['video_id'])
      xbmcgui.Dialog().ok("Voted " + rate, "Voted " + rate)
  def getRating(self, videoId):
    params = {'id': videoId}
    return v3Request(method='GET', path='videos/getRating', params=params)['items'][0]['rating']
  def rate(self, rate, currentRating, videoId):
    if(currentRating==rate):
      rate = 'none'
    xbmc.executebuiltin("RunPlugin(plugin://plugin.video.youtube/video/rate/?rating="+rate+"&video_id="+videoId+")")
    return rate