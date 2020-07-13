import xbmc
import xbmcgui
import xbmcaddon
class CommentsDialog(xbmcgui.WindowXMLDialog):
  def __init__(self, *args, **kvargs):#xmlFilename="plugin-extrabuttons-comments.xml", scriptPath=xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), defaultSkin="default", defaultRes="1080i", comments=None, loadMoreFunction = None, replyFunction = None):
    if('replyFunction' in kvargs):
      self.setProperty('canReply', 'true')
      self.replyFunction = kvargs['replyFunction']
    self.loadMoreFunction = kvargs['loadMoreFunction']
    self.reloadFunction = kvargs['reloadFunction']
    self.count = 0
    self.CANCEL_ID = 5555
    self.RELOAD_ID = 6666
    self.REPLY_ID = 7777
    self.comments = kvargs['comments']
    self.currentPath = None
    xbmcgui.WindowXMLDialog.__init__(self, *args, **kvargs)
    
  def onInit(self):
    self.setContent()
  def setContent(self, parent='HOME'):
    self.currentParent = parent
    listItems = []
    count = 0
    if(parent != 'HOME'):
      li = xbmcgui.ListItem('..', '')
      li.setPath(path=parent)
      li.setProperty("index", str(self.count))
      count += 1
      listItems.append(li)
      comment = self.comments['comments'][parent]
      label = comment['author']
      label2 = comment['value']
      thumb = comment['thumb']
      li = xbmcgui.ListItem(label, label2)
      li.setPath(path=comment['id'])
      li.setProperty("index", str(count))
      li.setProperty("commentId", comment['id'])
      li.setProperty("date", comment['date'])
      if('replyCount' in comment):
        li.setProperty("replyCount", str(comment['replyCount']))
      #li.setProperty("canReply", str(comment['canReply']))
      li.setProperty("likeCount", str(comment['likeCount']))
      li.setProperty("liked", str(comment['liked']))
      li.setProperty("canLike", str(comment['canLike']))
      li.setArt({'thumb':thumb})
      listItems.append(li)
      count += 1
      hasMore = False
      if('children' in comment):
        comments = self.comments['comments'][parent]['children']['comments']
        hasMore = self.comments['comments'][parent]['children']['hasMore']
      else:
        comments = {}
      
    else:
      hasMore = self.comments['hasMore']
      comments = self.comments['comments']
    for key in sorted(comments.keys(), reverse=True, key=lambda x: (comments[x]['date'])):
      comment = comments[key]
      label = comment['author']
      label2 = comment['value']
      thumb = comment['thumb']
      li = xbmcgui.ListItem(label, label2)
      li.setPath(path=comment['id'])
      li.setProperty("index", str(count))
      li.setProperty("commentId", comment['id'])
      li.setProperty("date", comment['date'])
      if('replyCount' in comment):
        li.setProperty("replyCount", str(comment['replyCount']))
      #li.setProperty("canReply", str(comment['canReply']))
      li.setProperty("likeCount", str(comment['likeCount']))
      li.setProperty("liked", str(comment['liked']))
      li.setProperty("canLike", str(comment['canLike']))
      li.setArt({'thumb':thumb})
      listItems.append(li)
      count += 1
    if(hasMore):
      li = xbmcgui.ListItem('Load More', '')
      li.setPath(path=parent)
      li.setProperty("index", str(self.count))
      count += 1
      listItems.append(li)
    
    self.getControl(50111).addItems(listItems) 
  def onClick(self, controlId):
    if controlId == self.REPLY_ID:
      self.showReplyDialog()
    elif controlId == self.CANCEL_ID:
      self.close()
    elif controlId == self.RELOAD_ID:
      self.comments = self.reloadFunction(self.comments['id'])
      self.getControl(50111).reset()
      self.setContent('HOME')
    else:
      pos = self.getControl(50111).getSelectedPosition()
      if(self.currentParent != 'HOME'):
        if(pos == 0):
          self.getControl(50111).reset()
          self.setContent('HOME')
        elif(pos == self.getControl(50111).size() - 1 and self.getControl(50111).getSelectedItem().getLabel() == 'Load More'):
          self.comments = self.loadMoreFunction(self.currentParent, True)
          self.getControl(50111).reset()
          self.setContent(self.currentParent)
          self.getControl(50111).selectItem(pos)
        else:
          #do rating etc
          return
      else:
        if(pos == self.getControl(50111).size() - 1 and self.getControl(50111).getSelectedItem().getLabel() == 'Load More'):
          self.comments = self.loadMoreFunction(self.comments['id'], False)
          self.getControl(50111).reset()
          self.setContent(self.currentParent)
          self.getControl(50111).selectItem(pos)
        else:
          index = self.getControl(50111).getSelectedItem().getPath()      
          self.getControl(50111).reset()
          self.setContent(index)
  def getReplyId(self):
    if(self.currentPath == 'HOME'):
      return comments['id']
    else:
      return comments['comments'][self.currentParent]['id']
        
  def showReplyDialog(self):
    kb = xbmc.Keyboard()
    kb.doModal()
    if(kb.isConfirmed()):
      text = kb.getText()
      replyToReply = False
      if(self.currentParent == 'HOME'):
        replyId = self.comments['id']
      else:
        replyId = self.comments['comments'][self.currentParent]['id']
        replyToReply = True
      self.replyFunction(replyId, text, replyToReply)