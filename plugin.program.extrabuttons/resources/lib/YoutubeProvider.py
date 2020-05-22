from youtube.youtube_requests import get_videos as getVideos

class YouTubeProvider:
  def __init__(self, match):
    self.videoId = match.group(1)
    return
  def getButtons(self)
    result = []
    print(str(getVideos(self.videoId)))
