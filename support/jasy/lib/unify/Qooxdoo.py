
import sys, re

from jasy.parser.Node import Node
from jasy.tokenizer.Comment import Comment

class Patcher:
    
    def __init__(self, session):
        self.__session = session
  
        self.__assetRe = re.compile(r"#asset\(([^\)]+)\)")
        
        self.__modifiers = [self.__detectAsset, self.__patchEnvironment]
  
        self.__breakpatchmap = {
          "qx.Bootstrap" : ["qx.data.IListData"],
          "qx.bom.Document" : ["qx.bom.Viewport"],
          "qx.bom.element.Overflow" : ["qx.bom.element.Style"],
          "qx.core.Assert" : ["qx.core.AssertionError", "qx.lang.Json", "qx.lang.String"],
          "qx.core.AssertionError" : ["qx.dev.StackTrace"],
          "qx.core.Object" : ["qx.event.type.Data"],
          "qx.core.ObjectRegistry" : ["qx.dev.Debug", "qx.dev.StackTrace"],
          "qx.data.MBinding" : ["qx.data.SingleValueBinding"],
          "qx.event.Manager" : ["qx.event.Pool"],
          "qx.event.Registration" : ["qx.event.Manager", "qx.event.type.Event", "qx.event.Pool", "qx.event.IEventDispatcher"],
          "qx.lang.Function" : ["qx.core.Object"],
          "qx.log.Logger" : ["qx.dev.StackTrace"],
          "qx.bom.client.Scroll" : ["qx.bom.element.Overflow", "qx.core.Environment"]
        }
  
        self.__requirepatchmap = {
          "qx.bom.Element" : ["qx.event.dispatch.Direct", "qx.event.dispatch.DomBubbling", "qx.event.handler.Keyboard", "qx.event.handler.Mouse", "qx.event.handler.DragDrop", "qx.event.handler.Element", "qx.event.handler.Appear", "qx.event.handler.Touch"],
          "qx.bom.Iframe" : ["qx.event.handler.Iframe"],
          "qx.bom.Input" : ["qx.event.handler.Input"],
          "qx.bom.Lifecycle" : ["qx.event.handler.Application"],
          "qx.core.Init" : ["qx.event.handler.Application", "qx.event.handler.Window", "qx.event.dispatch.Direct"],
          "qx.core.Object" : ["qx.event.handler.Object"],
          "qx.event.handler.DragDrop" : ["qx.event.handler.Mouse", "qx.event.handler.Capture", "qx.event.handler.Keyboard"],
          "qx.event.handler.Keyboard" : ["qx.event.handler.UserAction"],
          "qx.event.handler.Mouse" : ["qx.event.handler.UserAction"],
          "qx.event.handler.Touch" : ["qx.event.handler.UserAction", "qx.event.handler.Orientation"],
          "qx.ui.core.queue.Manager" : ["qx.event.handler.UserAction"],
          "qx.ui.root.Application" : ["qx.event.handler.Window"]
        }


    def treePatcher(self, tree, className):
        """ Patcher for tree of javascript """
        
        if tree.type == "script":
            self.__checkPatchmaps(tree, className)
        
        for node in list(tree):
            for modifier in self.__modifiers:
                modifier(node)
                
            self.treePatcher(node, className)


    def patchClasses(self):
      """ Patches all classes that are defined in the patchmap """
      return
      for project in self.__session.getProjects():
        for clazz in project.getClasses():
          clazzObj = project.getClassByName(clazz)
          #self.__patchClass(clazzObj.getName(), clazzObj.getMeta())


    def __checkPatchmaps(self, tree, className):
        commentString = ["/**"]
        modified = False
        
        if className in self.__breakpatchmap:
            modified = True
            for cls in self.__breakpatchmap[className]:
                commentString.append(" * @break {%s}" % cls)
      
        if className in self.__requirepatchmap:
            modified = True
            for cls in self.__requirepatchmap[className]:
                commentString.append(" * @require {%s}" % cls)
            
        if modified:
            commentString.append("*/")
            
            newComment = Comment("\n".join(commentString), "multi", None)
            
            try:
                comments = tree.comments
                comments.append(newComment)
            except AttributeError:
                comments = [newComment]
                
            tree.comments = comments
        

    def __patchClass(self, className, meta):
      """ Patch meta data of classes with given Information """

      if className in self.__breakpatchmap:
        meta.breaks.update(self.__breakpatchmap[className])
      
      if className in self.__requirepatchmap:
        meta.requires.update(self.__requirepatchmap[className])


    def __detectAsset(self, node):
        """ Update asset meta data with qooxdoo's own meta tags """
        if hasattr(node, "comments"):
            for comment in getattr(node, "comments"):
                assets = self.__parseAsset(comment)
                if len(assets) > 0:
                    tags = comment.getTags()
                    if tags == None:
                        tags = dict()
                        
                    tags["asset"] = assets
                    comment.setTags(tags)


    def __parseAsset(self, comment):
        return self.__assetRe.findall(comment.text)


    def __getCallName(self, node):
        if node.type == "call":
            return self.__getCallName(node[0])
  
        if node.type == "identifier":
            return node.value
  
        if node.type == "dot":
            return ".".join([self.__getCallName(node[0]), self.__getCallName(node[1])])
        
        return ""


    def __patchEnvironment(self, node):
        """ Patch all classes to use Jasy Environment """
  
        if node.type == "call":
            identifier = self.__getCallName(node)
  
            if identifier == "qx.core.Environment.get":
                p1 = Node(None, "identifier")
                p1.value = "jasy"
                p2 = Node(None, "identifier")
                p2.value = "Env"
                p3 = Node(None, "identifier")
                p3.value = "getValue"
                jasyEnv = Node(None, "dot", [Node(None, "dot", [p1, p2]), p3])
                node.replace(node[0], jasyEnv)
    
            #elif identifier == "qx.core.Environment.select":
            #  p1 = Node(None, "identifier")
            #  p1.value = "jasy"
            #  p2 = Node(None, "identifier")
            #  p2.value = "Env"
            #  p3 = Node(None, "identifier")
            #  p3.value = "select"
            #  jasyEnv = Node(None, "dot", [Node(None, "dot", [p1, p2]), p3])
            #  node.replace(node[0], jasyEnv)
    
            elif identifier == "qx.core.Environment.add":
                p1 = Node(None, "identifier")
                p1.value = "jasy"
                p2 = Node(None, "identifier")
                p2.value = "Env"
                p3 = Node(None, "identifier")
                p3.value = "define"
                jasyEnv = Node(None, "dot", [Node(None, "dot", [p1, p2]), p3])
                node.replace(node[0], jasyEnv)
          
