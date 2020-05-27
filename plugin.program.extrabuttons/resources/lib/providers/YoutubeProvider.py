#from youtube.youtube_requests import get_videos as getVideos
import xbmc
import os
import urllib
from youtube_requests import get_videos as getVideos
from youtube_requests import get_channels as getChannels
from youtube_requests import v3_request as v3Request
#from youtube_requests import __get_core_components as getCoreComponents

class Provider:
  MEDIA_BASE = xbmc.translatePath("special://home")+ "addons" + os.sep + "plugin.video.youtube" + os.sep + "resources" + os.sep + "media" + os.sep 
  count = 0
  def __init__(self, match=None):
    if(match):
      videoId = match.group(1)
      parts = ['snippet,statistics']
      params = {'part': ''.join(parts), 'id': videoId}
      self.videoInfo = v3Request(method='GET', path='videos', params=params)
      self.channelInfo = getChannels(self.videoInfo['items'][0]['snippet']['channelId'])
    return
  def getButtons(self):
    result = []
    result.append(self.getChannelButton())
    result.append(self.getUpVoteButton())
    result.append(self.getDownVoteButton())
    result.append(self.getCommentsButton())
    #result.append(self.getRelatedVideos())
    return result
  def getChannelButton(self):
    channelLogo = self.channelInfo[0]['snippet']['thumbnails']['default']['url']
    channelName = self.channelInfo[0]['snippet']['title']
    return {'label': channelName, 'path': 'plugin://plugin.video.youtube/channel/'+self.channelInfo[0]['id']+'/', 'logo': channelLogo, 'isFolder': True, 'isPlayable': False, 'resolvedUrl':None}
  def getUpVoteButton(self): 
    logo = self.MEDIA_BASE + 'likes.png'
    upVotes = self.videoInfo['items'][0]['statistics']['likeCount']
    return {'label': upVotes, 'path': 'plugin://plugin.video.youtube/video/rate/?video_id='+self.videoInfo['items'][0]['id']+'refresh_container=0', 'logo': logo, 'isFolder': True, 'isPlayable':False, 'resolvedUrl':None}
  def getDownVoteButton(self):
    logo = self.MEDIA_BASE + 'dislikes.png'
    downVotes = self.videoInfo['items'][0]['statistics']['dislikeCount']
    return {'label': downVotes, 'path': 'plugin://plugin.video.youtube/video/rate/?video_id='+self.videoInfo['items'][0]['id']+'refresh_container=0', 'logo': logo, 'isFolder': True, 'isPlayable':False, 'resolvedUrl':None}
    
  def getCommentsButton(self):
    logo = self.MEDIA_BASE + 'playlist.png'
    return {'label': 'Comments', 'path': 'RunPlugin("plugin://plugin.program.extrabuttons/?provider=plugin.video.youtube&action=show_comment&video_id='+self.videoInfo['items'][0]['id']+'")', 'logo': logo, 'isFolder': False, 'isPlayable':None, 'resolvedUrl':None}
  def showComments(self, videoId, page=None):
    params = {'part': 'snippet',
             'videoId': videoId,
             'order': 'relevance',
             'textFormat': 'plainText',
             'maxResults': '50'}
    if page:
      params['pageToken'] = page
    result = v3Request(method='GET', path='commentThreads', params=params, no_login=True)
    diaogText = self.getTextForCommentsDialog(result)
    xbmc.Dialog().ok('Comments', dialogText)
  def getTextForCommentsDialog(self, result):
    return str(result)
  def doAction(self, action, params):
    print('doAction called 88888888888888888')
    print(str(action))
    print(str(params))
    if('show_comments' == action):
      self.showComments(params['video_id'])
    elif('upvote' == action):
      return
    elif('downvote' == action):
      return
