from xbmc import Player
from xbmcgui import WindowXMLDialog
from platform import machine

class MyWindow(WindowXMLDialog):
  items = None
  OS_MACHINE = machine()
  
  def __init__(self, *args, **kwargs):
    if self.OS_MACHINE[0:5] == 'armv7':
      WindowXMLDialog.__init__(self)
    else:
      WindowXMLDialog.__init__(self, *args, **kwargs)

  def setLoading(self):
    return
  def addItems(self, items):
    return
  def reset(self):
    return
  def removeLoading(self):
    return
    
  def onInit(self):  # pylint: disable=invalid-name
    return

  def set_info(self):
    episode_info = '%(season)sx%(episode)s.' % self.item
    if self.item.get('rating') is None:
      rating = ''
    else:
      rating = str(round(float(self.item.get('rating')), 1))

    if self.item is not None:
      art = self.item.get('art')
      self.setProperty('fanart', art.get('tvshow.fanart', ''))
      self.setProperty('landscape', art.get('tvshow.landscape', ''))
      self.setProperty('clearart', art.get('tvshow.clearart', ''))
      self.setProperty('clearlogo', art.get('tvshow.clearlogo', ''))
      self.setProperty('poster', art.get('tvshow.poster', ''))
      self.setProperty('thumb', art.get('thumb', ''))
      self.setProperty('plot', self.item.get('plot', ''))
      self.setProperty('tvshowtitle', self.item.get('showtitle', ''))
      self.setProperty('title', self.item.get('title', ''))
      self.setProperty('season', str(self.item.get('season', '')))
      self.setProperty('episode', str(self.item.get('episode', '')))
      self.setProperty('seasonepisode', episode_info)
      self.setProperty('year', str(self.item.get('firstaired', '')))
      self.setProperty('rating', rating)
      self.setProperty('playcount', str(self.item.get('playcount', 0)))
      self.setProperty('runtime', str(self.item.get('runtime', '')))

  def prepare_progress_control(self):
    try:
      self.progress_control = self.getControl(3014)
    except RuntimeError:  # Occurs when skin does not include progress control
      pass
    else:
      self.progress_control.setPercent(self.current_progress_percent)  # pylint: disable=no-member,useless-suppression

  def set_item(self, item):
    self.item = item

  def set_progress_step_size(self, progress_step_size):
    self.progress_step_size = progress_step_size

  def update_progress_control(self, remaining=None, runtime=None):
    self.current_progress_percent = self.current_progress_percent - self.progress_step_size
    try:
      self.progress_control = self.getControl(3014)
    except RuntimeError:  # Occurs when skin does not include progress control
      pass
    else:
      self.progress_control.setPercent(self.current_progress_percent)  # pylint: disable=no-member,useless-suppression

    if remaining:
      self.setProperty('remaining', from_unicode('%02d' % remaining))
    if runtime:
      self.setProperty('endtime', from_unicode(localize_time(datetime.now() + timedelta(seconds=runtime))))

  def set_cancel(self, cancel):
    self.cancel = cancel

  def is_cancel(self):
    return self.cancel

  def set_watch_now(self, watchnow):
    self.watchnow = watchnow

  def is_watch_now(self):
    return self.watchnow

  def onFocus(self, controlId):  # pylint: disable=invalid-name
    pass

  def doAction(self):  # pylint: disable=invalid-name
    pass

  def closeDialog(self):  # pylint: disable=invalid-name
    self.close()

  def onClick(self, controlId):  # pylint: disable=invalid-name
    if controlId == 3012:  # Watch now
      self.set_watch_now(True)
      self.close()
    elif controlId == 3013:  # Close / Stop
      self.set_cancel(True)
      if bool(get_setting('stopAfterClose') == 'true'):
        Player().stop()
      self.close()

  def onAction(self, action):  # pylint: disable=invalid-name
    if action == ACTION_PLAYER_STOP:
      self.close()
    elif action == ACTION_NAV_BACK:
      self.set_cancel(True)
      self.close()
