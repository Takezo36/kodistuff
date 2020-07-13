import xbmc
import xbmcgui
import xbmcaddon
class ChatDialog(xbmcgui.WindowXMLDialog):
  def __init__(self, *args, **kvargs):#xmlFilename="plugin-extrabuttons-comments.xml", scriptPath=xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), defaultSkin="default", defaultRes="1080i", comments=None, loadMoreFunction = None, replyFunction = None):
    if('replyFunction' in kvargs):
      self.setProperty('canReply', 'true')
      self.replyFunction = kvargs['replyFunction']
    self.stopChat = None
    if('stopChat' in kvargs):
      self.stopChat = kvargs['stopChat']
    self.count = 0
    self.CANCEL_ID = 5555
    self.REPLY_ID = 7777
    xbmcgui.WindowXMLDialog.__init__(self, *args, **kvargs)
  def updateContent(self, comment):
    label = comment['author'] + ' - ' + comment['date']
    label2 = comment['value']
    thumb = comment['thumb']
    path = '/dummy/'
    li = xbmcgui.ListItem(label, label2)
    li.setPath(path=path)
    li.setProperty("index", str(self.count))
    li.setArt({'thumb':thumb})
    self.getControl(50111).addItem(li)
    self.getControl(50111).selectItem(self.count)
    self.count += 1
  def onClick(self, controlId):
    if controlId == self.REPLY_ID:
      self.showReplyDialog()
    elif controlId == self.CANCEL_ID:
      if(self.stopChat != None):
        self.stopChat()
      self.close()
  def showReplyDialog(self):
    kb = xbmc.Keyboard()
    kb.doModal()
    if(kb.isConfirmed()):
      text = kb.getText()
      self.replyFunction(text)