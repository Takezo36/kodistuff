import resources.lib.providers.VideoPlatformBaseProvider as VideoPlatformBaseProvider
import xbmcaddon
class Provider(VideoPlatformBaseProvider.VideoPlatformBaseProvider):
  TWITCH_TOKEN_URL = 'https://twitchapps.com/tmi'
  BASE_URL = 'https://api.twitch.tv/helix/'
# "plugin:\\/\\/plugin\\.video\\.twitch\\/\\?video_id=[v]*(\\d+).*&mode=play.*": [
#			[{
#					"type": "get",
#					"path": "'https://api.twitch.tv/helix/videos?id=' + match.group(1)",
#					"headers": {
#						"Client-ID": ""
#					},
#					"result": {
#						"a": "data.0.user_id",
#						"b": "data.0.type"
#					}
#				},
#				{
#					"type": "plugin",
#					"path": "'plugin://plugin.video.twitch/?broadcast_type=' + result[0]['b'] + '&channel_id='+result[0]['a']+'&game=None&mode=channel_video_list'"
#				}
#		]
##		],
#		"plugin:\\/\\/plugin\\.video\\.twitch\\/\\?channel_id=(\\d+).*&mode=play.*": [
#			[{
#				"type": "plugin",
#
#				"path": "'plugin://plugin.video.twitch/?broadcast_type=archive&channel_id='+match.group(1)+'&game=None&mode=channel_video_list'"
#			}],
#			[{
#				"type": "plugin",
#				"path": "'plugin://plugin.video.twitch/?broadcast_type=upload&channel_id='+match.group(1)+'&game=None&mode=channel_video_list'"
#			}]
#		]
  def __init__(self, match=None, path=None):
    self.headers = {}
    self.headers['ClientID'] = xbmcaddon.Addon("plugin.video.twitch").getSettingString("private_oauth_clientid")
    if(match):
      self.providerName = 'plugin.video.twitch'
      self.idType = match.group(1)
      self.videoId = match.group(2)
      self.videoInfo = self.getVideoInfo()
      self.channelInfo = self.getChannelInfo()
  def getChannelInfo(self):
    return
  def getVideoInfo(self):
    url = self.BASE_URL + 'videos?id='+self.videoId
    return self.doGet(url, self.headers)  
  def getButtons(self):
    result = []
    result.append(self.getTwitchChannelButton())
    result.append(self.getChatButton(''))
    return result
  def getChatMessages(self, chatDialog):
    import socket
    address = 'irc.chat.twitch.tv'
    port = 6667
    IRC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IRC.connect((address, port))
    IRC.send('PASS ' + self.token + '\n')
    IRC.send('NICK MusaTakezo\n')
    print(str(IRC.recv()))
    IRC.send('JOIN #' + self.videoInfo['data'][0]['user_name'])
    while not xbmc.Monitor().abortRequested():
      line = str(IRC.recv())
      msg = {}
      msg['author'] = 'jemand'
      msg['date'] = 'jetzt'
      msg['value'] = line
      msg['thumb'] = ''
      chatDialog.updateContent(msg)
  def getTwitchChannelButton(self):
    path = 'plugin://plugin.video.twitch/?&channel_id='+self.videoInfo['data'][0]['user_id'] #+'&game=None&mode=channel_video_list'
    logo = self.channelInfo['profile_image_url']
    name = self.channelInfo['display_name']
    return self.getChannelButton(name, logo, path)
  