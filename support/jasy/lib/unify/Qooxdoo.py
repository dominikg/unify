
import sys, re

from jasy.parser.Node import Node

class Patcher:
    __breakpatchmap = {}
    __requirepatchmap = {}

    def __init__(self, session):
      self.__session = session

      self.__assetRe = re.compile(r"#asset\(([^\)]+)\)")

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

    def patchClasses(self):
      """ Patches all classes that are defined in the patchmap """

      for project in self.__session.getProjects():
        for clazz in project.getClasses():
          clazzObj = project.getClassByName(clazz)
          self.__patchClass(clazzObj.getName(), clazzObj.getMeta())
          self.__treeWalker(clazzObj, [self.__detectAsset, self.__patchEnvironment])

      self.__session.clearCache()

    def __patchClass(self, className, meta):
      """ Patch meta data of classes with given Information """

      if className in self.__breakpatchmap:
        meta.breaks.update(self.__breakpatchmap[className])
      
      if className in self.__requirepatchmap:
        meta.requires.update(self.__requirepatchmap[className])

    def __treeWalker(self, clazz, modifiers, startNode=None):
      if startNode == None:
        startNode = clazz.getTree()
      for node in list(startNode):
        for modifier in modifiers:
          modifier(node, clazz)
        self.__treeWalker(clazz, modifiers, node)

    def __detectAsset(self, node, clazz):
      """ Update asset meta data with qooxdoo's own meta tags """
      if hasattr(node, "comments"):
        for comment in getattr(node, "comments"):
          clazz.getMeta().assets.update(self.__parseAsset(comment))

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


    def __patchEnvironment(self, node, clazz):
      """ Patch all classes to use Jasy Environment """

      if node.type == "call":
        identifier = self.__getCallName(node)

        if identifier == "qx.core.Environment.get":
          p1 = Node(None, "identifier")
          p1.value = "jasy"
          p2 = Node(None, "identifier")
          p2.value = "Env"
          p3 = Node(None, "identifier")
          p3.value = "get"
          jasyEnv = Node(None, "dot", [Node(None, "dot", [p1, p2]), p3])
          node.replace(node[0], jasyEnv)

        elif identifier == "qx.core.Environment.select":
          p1 = Node(None, "identifier")
          p1.value = "jasy"
          p2 = Node(None, "identifier")
          p2.value = "Env"
          p3 = Node(None, "identifier")
          p3.value = "select"
          jasyEnv = Node(None, "dot", [Node(None, "dot", [p1, p2]), p3])
          node.replace(node[0], jasyEnv)

        elif identifier == "qx.core.Environment.add":
          p1 = Node(None, "identifier")
          p1.value = "jasy"
          p2 = Node(None, "identifier")
          p2.value = "Env"
          p3 = Node(None, "identifier")
          p3.value = "define"
          jasyEnv = Node(None, "dot", [Node(None, "dot", [p1, p2]), p3])
          node.replace(node[0], jasyEnv)
        
