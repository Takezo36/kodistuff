import xbmc
import xbmcgui
import xbmcaddon
class RelatedMediaDialog(xbmcgui.WindowXMLDialog):
  def __init__(self, *args, **kvargs):#xmlFilename="plugin-extrabuttons-comments.xml", scriptPath=xbmcaddon.Addon("plugin.program.extrabuttons").getAddonInfo('path'), defaultSkin="default", defaultRes="1080i", comments=None, loadMoreFunction = None, replyFunction = None):
    self.content = kvargs['content']
    self.playFunction = kvargs['playFunction']
    
    xbmcgui.WindowXMLDialog.__init__(self, *args, **kvargs)
    
  
  def onInit(self):
    controlId = 60111
    titleId = 6011
    entry = self.content
    line = entry['line']
    title = entry['title']
    titleControl = self.getControl(titleId)
    titleControl.setLabel(title)
    listItems = []
    count = 0
    for item in line:
      label = item['label']
      label2 = item['label2']
      thumb = item['thumb']
      path = item['path']
      li = xbmcgui.ListItem(label, label2, offscreen=True)
      li.setPath(path=path)
      li.setProperty("index", str(count))
      li.setArt({'thumb':thumb})
      listItems.append(li)
      count += 1
    listControl = self.getControl(controlId)
    listControl.addItems(listItems)
    self.getControl(60111).selectItem(0)
      
  def onClick(self, controlId):
    print('llllllllllllllllllllllllllllllllll')
    print(self.getControl(60111).getSelectedItem())
    print('llllllllllllllllllllllllllllllllll')
    listItem = self.getControl(60111).getSelectedItem()
    self.close()
    self.playFunction(listItem)
    