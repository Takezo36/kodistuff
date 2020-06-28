import xbmc
import xbmcgui
import xbmcaddon
class PopUpDialog(xbmcgui.WindowXMLDialog):
  def __init__(self, *args, **kvargs):#xmlFilename="plugin-extrabuttons-comments.xml", scriptPath=xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), defaultSkin="default", defaultRes="1080i", comments=None, loadMoreFunction = None, replyFunction = None):
    self.buttons = kvargs['buttons']
    xbmcgui.WindowXMLDialog.__init__(self, *args, **kvargs)
  
  def onInit(self):
    listControl = self.getControl(50111)
    listControl.addItems(self.buttons)
    self.getControl(50111).selectItem(0)
      
  def onClick(self, controlId):
    xbmc.executebuiltin('RunScript(../../../plugin.py, ' + self.getControl(50111).getSelectedItem().getPath() + ')')
