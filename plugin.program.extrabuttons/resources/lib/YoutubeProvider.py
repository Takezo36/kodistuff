#from youtube.youtube_requests import get_videos as getVideos
import xbmcaddon
import xbmcgui
import xbmc
import os
import urllib
from youtube_requests import get_videos as getVideos
from youtube_requests import get_channels as getChannels
from youtube_requests import v3_request as v3Request
#from youtube_requests import __get_core_components as getCoreComponents
import simplejson as json
try:
  from urllib.request import Request
  from urllib.request import urlopen
except:
  from urllib2 import Request
  from urllib2 import urlopen

class Provider:
  MEDIA_BASE = xbmc.translatePath("special://home")+ "addons" + os.sep + "plugin.video.youtube" + os.sep + "resources" + os.sep + "media" + os.sep 
  count = 0
  def __init__(self, match):
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
    return self.createListItem(channelName, 'plugin://plugin.video.youtube/channel/'+self.channelInfo[0]['id']+'/', channelLogo)
  def getUpVoteButton(self): 
    logo = self.MEDIA_BASE + 'likes.png'
    upVotes = self.videoInfo['items'][0]['statistics']['likeCount']
    return self.createListItem(upVotes, 'plugin://plugin.video.youtube/video/rate/?video_id='+self.videoInfo['items'][0]['id']+'refresh_container=0', logo)
  def getDownVoteButton(self):
    logo = self.MEDIA_BASE + 'dislikes.png'
    downVotes = self.videoInfo['items'][0]['statistics']['dislikeCount']
    return self.createListItem(downVotes, 'plugin://plugin.video.youtube/video/rate/?video_id='+self.videoInfo['items'][0]['id']+'refresh_container=0', logo)
  def getCommentsButton(self):
    logo = self.MEDIA_BASE + 'playlist.png'
    return self.createListItem('Comments', 'plugin://plugin.program.extrabuttons/?provider=plugin.video.youtube&action=show_comment&video_id='+self.videoInfo['items'][0]['id'], logo)
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
    xbmc.Dialog().textviewer('Comments', dialogText)
  def getTextForCommentsDialog(self, result):
    return str(result)
  def doAction(self, action, params):
    if('show_comments' == action):
      self.showComments(params['video_id'])
    elif('upvote' == action):
      return
    elif('downvote' == action):
      return
  def doGet(self, url, headers):
    req = Request(url, headers=headers)
    response = urlopen(req)
    result = response.read()
    return json.loads(result)
  def createListItem(self, label, path, thumb):
    li = xbmcgui.ListItem(label, offscreen=True)
    li.setArt({'thumb': thumb})
    li.setLabel(label)
    li.setProperty("isPlayable", "false")
    li.setProperty("index", str(self.count))
    li.setPath(path=path)
    li.setProperty('path', path)
    self.count += 1
    return li
