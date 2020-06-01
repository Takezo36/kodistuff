from __future__ import absolute_import, division, unicode_literals
import xbmc
from xbmc import Monitor
from .Player import MyPlayer


class MyMonitor(Monitor):
  
  def __init__(self):
    self.player = MyPlayer()
    Monitor.__init__(self)

  def start(self):
    while not self.abortRequested():
      if self.waitForAbort(1):
        break
  def onNotification(self, sender, method, data):  # pylint: disable=invalid-name
    xbmc.log("NOTIFICATION ARRIVED LOOOOOOK")
    xbmc.log(str(sender))
    xbmc.log(str(method))
    xbmc.log(str(data))
    xbmc.log(xbmc.getInfoLabel('Container.FolderName'))
    xbmc.log("#########################################")
    ''' Notification event handler for accepting data from add-ons '''
    if not method.endswith('upnext_data'):  # Method looks like Other.upnext_data
      return
    data, encoding = decode_json(data)
    data.update(id='%s_play_action' % sender.replace('.SIGNAL', ''))
    self.api.addon_data_received(data, encoding=encoding)   