import xbmcgui
import xbmcaddon
class CommentsDialog(xbmcgui.WindowXMLDialog):
  def __init__(self, *args, **kvargs):#xmlFilename="plugin-extrabuttons-comments.xml", scriptPath=xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), defaultSkin="default", defaultRes="1080i", comments=None, loadMoreFunction = None, replyFunction = None):
    if('replyFunction' in kvargs):
      self.setProperty('canReply', 'true')
      self.replyFunction = kvargs['replyFunction']
    print("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
    count = 0
    self.CANCEL_ID = 5555
    self.REPLY_ID = 6666
    self.LOAD_MORE_ID = 7777
    self.comments = kvargs['comments']
    print(str(self.comments))
    self.currentPath = None
    xbmcgui.WindowXMLDialog.__init__(self, *args, **kvargs)
    self.setContent()
  def setContent(self, parent='loadmoreid=HOME'):
    comments = self.comments
    self.currentParent = parent
    listItems = []
    count = 0
    if(parent == 'loadmoreid=HOME'):
      li = xbmcgui.ListItem('..', '..')
      li.setPath(path=parent)
      li.setProperty("index", str(count))
      count += 1
      listItems.append(li)
    for comment in comments:
      print(str(comment))
      label = comment['author'] + ' - ' + comment['date']
      label2 = comment['value']
      thumb = comment['thumb']
      path = 'loadmoreid=' + comment['loadmoreid']
      li = xbmcgui.ListItem(label, label2)
      li.setPath(path=path)
      li.setProperty("index", str(count))
      li.setArt({'thumb':thumb})
      listItems.append(li)
      count += 1
    self.addItems(listItems) 
  def onClick(self, controlId):
    if controlId == self.REPLY_ID:
      self.showReplyDialog()
    elif controlId == self.CANCEL_ID:
      self.close()
    else:
      li = self.getListItem(self.getCurrentListPosition)
      path = li.getPath()
      self.clearList()
      self.setContent(self.loadMoreFunction(path),path)
  def getReplyId(self):
  #REDO
    if(self.currentPath):
      comments = self.comments
      for index in self.currentPath.split('/'):
        comments = comments[int(index)]
      return comments['replyId']
    return None
        
  def showReplyDialog(self):
    kb = xbmc.Keyboard()
    kb.doModal()
    if(kb.isConfirmed()):
      text = kb.getText()
      replyId = self.getReplyId()
      replyFunction(replyId, text)