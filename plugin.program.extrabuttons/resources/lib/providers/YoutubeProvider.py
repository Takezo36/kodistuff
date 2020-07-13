#from youtube.youtube_requests import get_videos as getVideos
import xbmc
import xbmcgui
import xbmcaddon
import os
import urllib
import simplejson as json
import _thread
import time
from youtube_requests import get_related_videos as getRelatedVideos
from youtube_requests import get_videos as getVideos
from youtube_requests import get_channels as getChannels
from youtube_requests import v3_request as v3Request
from youtube_requests import __get_core_components as getCoreComponents
from multiprocessing.connection import Client
import resources.lib.providers.VideoPlatformBaseProvider as VideoPlatformBaseProvider

#from resources.lib.Commons import getFolderList
class Provider(VideoPlatformBaseProvider.VideoPlatformBaseProvider):
  MEDIA_BASE = xbmc.translatePath("special://home")+ "addons" + os.sep + "plugin.video.youtube" + os.sep + "resources" + os.sep + "media" + os.sep 
  ADDON_MEDIA = xbmc.translatePath("special://home")+ "addons" + os.sep + "plugin.program.extrabuttons" + os.sep + "resources" + os.sep + "skins" + os.sep + "default" + os.sep + "media" + os.sep
  count = 0
  def __init__(self, match=None, path=None):
    self.providerName = 'plugin.video.youtube'
    if(match):
      self.videoId = match.group(1)
    self.provider, self.context, self.client = getCoreComponents()
    return
  def getId(self):
    return self.videoId
  def getButtons(self):
    result = []
    result.append(self.getChannelButton())
    result.append(self.getRelatedVideosButton())
    result.append(self.getUpVoteButton())
    result.append(self.getDownVoteButton())
    if(self.videoInfo['items'][0]['snippet']['liveBroadcastContent'] == 'live'):
      result.append(self.getChatButton())
    else:
      result.append(self.getCommentsButton())
    return result
  def getChannelButton(self):
    logo = self.channelInfo[0]['snippet']['thumbnails']['default']['url']
    name = self.channelInfo[0]['snippet']['title']
    path = 'action=open&path=plugin://plugin.video.youtube/channel/'+self.channelInfo[0]['id']+'/'
    return super().getChannelButton(name, logo, path)
  def getUpVoteButton(self): 
    logo = self.MEDIA_BASE + 'likes.png'
    try:
      upVotes = self.videoInfo['items'][0]['statistics']['likeCount']
    except:
      upVotes = '0'
    return {'label': upVotes, 'path': 'provider=plugin.video.youtube&action=upvote&rate=like&video_id='+self.videoId, 'logo': logo, 'isFolder': True, 'isPlayable':False, 'resolvedUrl':None}
  def getRelatedVideosButton(self):
    logo = self.ADDON_MEDIA + 'relatedmedialogo.png'
    return {'label': 'show related', 'path': 'provider=plugin.video.youtube&action=show_related&rate=like&video_id='+self.videoId, 'logo': logo, 'isFolder': True, 'isPlayable':False, 'resolvedUrl':None}
  def getDownVoteButton(self):
    logo = self.MEDIA_BASE + 'dislikes.png'
    try:
      downVotes = self.videoInfo['items'][0]['statistics']['dislikeCount']
    except:
      downVotes = '0'
    return {'label': downVotes, 'path': 'provider=plugin.video.youtube&action=downvote&rate=dislike&video_id='+self.videoId, 'logo': logo, 'isFolder': True, 'isPlayable':False, 'resolvedUrl':None}
  def getCommentsButton(self):
    logo = self.MEDIA_BASE + 'playlist.png'
    return super().getCommentsButton(logo)
  def getChatButton(self):
    logo = self.MEDIA_BASE + 'playlist.png'
    return super().getChatButton(logo)
  def getChatMessages(self, chatDialog):
    self.videoInfo = self.getPreloadData()[0]
    try:
      self.chatId = self.videoInfo['items'][0]['liveStreamingDetails']['activeLiveChatId']
    except:
      xbmcgui.Dialog().ok("Failed to get live chat", "No live chat available")
    self.stop = False
    parts = ['snippet,authorDetails']
    params = {'part': ''.join(parts), 'liveChatId': self.chatId}

    messages = v3Request(method='GET', path='liveChat/messages', params=params)
    
    while not self.stop:
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
  def reload(self, videoId):
    return self.getComments(videoId, False, False, True)
  def loadMore(self, videoId, isReply = False):
    return self.getComments(videoId, isReply, True)
  def getComments(self, videoId, isReply = False, append=False, forceReload=False):
    if(forceReload):
      stored = 'None'
    else:
      stored = self.getStoredData()
    if(stored == 'None'):
      if(isReply):
        params = {'part': 'snippet',
                  'parentId': videoId,
                  'textFormat': 'plainText',
                  'maxResults': '100'}
        path = 'comments'
      else:
        params = {'part': 'snippet, replies',
                 'videoId': videoId,
                 'order': 'relevance',
                 'textFormat': 'plainText',
                 'maxResults': '100'}
        path = 'commentThreads'
      commentsRaw = self.client.perform_v3_request(method='GET', path=path, params=params, no_login=True)
      comments = self.parseComments(commentsRaw, videoId)
      stored = comments
      self.storeData(stored)
    if(append):
      if(isReply):
        params = {'part': 'snippet',
                  'parentId': videoId,
                  'textFormat': 'plainText',
                  'maxResults': '100'}
        path = 'comments'
      else:
        nextPageToken = stored['nextPageToken']
        params = {'part': 'snippet, replies',
                 'videoId': videoId,
                 'order': 'relevance',
                 'textFormat': 'plainText',
                 'maxResults': '100',
                 'nextPageToken': nextPageToken}
        path = 'commentThreads'
      commentsRaw = self.client.perform_v3_request(method='GET', path=path, params=params, no_login=True)
      comments = self.parseComments(commentsRaw, videoId, isReply)
      if(isReply):
        stored['comments'][videoId]['children']['comments'].update(comments['comments'])
        stored['comments'][videoId]['children']['hasMore'] = comments['hasMore']
      else:
        stored['nextPageToken'] = comments['nextPageToken']
        stored['hasMore'] = comments['hasMore']
        stored['comments'].update(comments['comments'])
      self.storeData(stored)
    return stored
  def parseComments(self, commentsRaw, parentId, isReply=False, replyCount=0):
    result = {}
    result['id'] = parentId
    result['hasMore'] = False
    print('%%%%%%%%%%%%%%%')
    print(commentsRaw)
    print('%%%%%%%%%%%%%%%')
    items = commentsRaw['items']
    if(isReply):
      if(len(items) < replyCount):
        result['hasMore'] = True
        result['nextPageToken'] = parentId
    else:
      if('nextPageToken' in  commentsRaw):
        result['hasMore'] = True
        result['nextPageToken'] = commentsRaw['nextPageToken']
    comments = {}
    for item in items:
      comment = {}
      if(isReply):
        snippet = item['snippet']
      else:
        snippet = item['snippet']['topLevelComment']['snippet']
        comment['replyCount'] = item['snippet']['totalReplyCount']
        comment['canReply'] = item['snippet']['canReply']
      comment['author'] = snippet['authorDisplayName']
      comment['date'] = snippet['publishedAt']
      comment['value'] = snippet['textOriginal']
      comment['thumb'] = snippet['authorProfileImageUrl']
      comment['likeCount'] = snippet['likeCount']
      comment['liked'] = snippet['viewerRating']
      comment['canLike'] = snippet['canRate']
      comment['id'] = item['id']
      comment['isReply'] = isReply
      if('replies' in item):
        comment['children'] = self.parseComments({'items': item['replies']['comments']}, item['id'], True, comment['replyCount'])
      comments[item['id']] = comment
    result['comments'] = comments
    return result
  def replyToComment(self, commentId, text, replyToComment):
    params = {'part':'snippet'}
    if(replyToComment):
      return
    else:
      data = {'snippet':{'videoId':commentId,'topLevelComment':{'snippet':{'textOriginal':text}}}}
      path = 'commentThreads'
    v3Request(method='POST', path=path, params=params, post_data=data)
    return
  def replyToChat(self, text):
    params = {'part':'snippet'}
    data= {'snippet':{'liveChatId': str(self.chatId),'type':'textMessageEvent','textMessageDetails':{'messageText':text}}}
    v3Request(method='POST', path='liveChat/messages', params=params, post_data=data)
    return
  def getRating(self, videoId):
    params = {'id': videoId}
    return v3Request(method='GET', path='videos/getRating', params=params)['items'][0]['rating']
  def rate(self, rate, currentRating, videoId):
    if(currentRating==rate):
      rate = 'none'
    params = {'id': videoId,
              'rating': rate}
    try:
      v3Request(method='POST', path='videos/rate', params=params)
    except json.errors.JSONDecodeError: #expected error bug in the youtube client
      return rate
    return rate
  def preload(self):
    parts = ['snippet,statistics,liveStreamingDetails']
    params = {'part': ''.join(parts), 'id': self.videoId}
    self.videoInfo = v3Request(method='GET', path='videos', params=params)
    #self.videoId = self.videoInfo['items'][0]['id']
    self.channelInfo = getChannels(self.videoInfo['items'][0]['snippet']['channelId'])
    return [self.videoInfo, self.channelInfo]#self.getRelatedVideos(self.videoId)
  def getRelatedVideos(self, videoId):
    relatedInfo = self.myGetRelatedVideos(videoId)
    listItems = []
    for item in relatedInfo:
      li = {}
      li['label'] = item['snippet']['title']
      li['label2'] =  item['snippet']['description']
      li['thumb'] = item['snippet']['thumbnails']['default']['url']
      li['path'] = 'plugin://plugin.video.youtube/?video_id=' + item['id']['videoId']
      listItems.append(li)
    result = {'title': 'Related Videos', 'line': listItems}
    return result
  def myGetRelatedVideos(self, videoId):
    params = {'relatedToVideoId': videoId,
              'part': 'snippet',
              'type': 'video',
              'maxResults': str(20)}
    return v3Request(method='GET', path='search', params=params)['items']
  #def rateCommentFunction(self, commentId, rating, isReply):
    
  def doAction(self, action, params):
    if('show_comment' == action):
      self.showComments(self.getComments(params['video_id']))
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
  def play(self, listItem):
    self.executeBuiltin('RunPlugin('+listItem.getPath()+')')