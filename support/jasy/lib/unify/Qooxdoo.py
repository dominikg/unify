
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
            self.treePatcher(node, className)
            
            for modifier in self.__modifiers:
                modifier(node)


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


    def __getCallName(self, node, initNodeType = "call"):
        if node.type == initNodeType and len(node) > 0:
            return self.__getCallName(node[0])
 
        if node.type == "identifier":
            return node.value
  
        if node.type == "dot":
            return ".".join([self.__getCallName(node[0], initNodeType), self.__getCallName(node[1], initNodeType)])
            
        return ""


    def __getFirstByType(self, node, type):
        children = list(node)
        
        for child in children:
            if child.type == type:
                return child
            
        return None
    
    
    def __getAllByType(self, node, type):
        children = list(node)
        ret = []
        
        for child in children:
            if child.type == type:
                ret.append(child)
            
        return ret
    
    
    def __createValueNode(self, type, value):
        node = Node(None, type)
        node.value = value
        
        return node
    
    
    def __createCall(self, fntname, arguments):
        fnt = str(fntname).split(".")
        
        fntNode = None
        if len(fnt) > 1:
            i1 = self.__createValueNode("identifier", fnt.pop(0))
            i2 = self.__createValueNode("identifier", fnt.pop(0))
            fntNode = Node(None, "dot", [i1, i2])
            
            for fntpart in fnt:
                fntNode = Node(None, "dot", [fntNode, self.__createValueNode("identifier", fntpart)])
        else:
            fntNode = self.__createValueNode("identifier", fnt.pop(0))
        
        argsNode = Node(None, "list")
        for argument in arguments:
            argsNode.append(self.__createValueNode("string", argument))
        
        call = Node(None, "call", [fntNode, argsNode])

        return call
    
    
    def __createHook(self, queryFnt, queryValue, resultValue, thenPart, elsePart):
        condition = Node(None, "eq", [
            self.__createCall(queryFnt, [queryValue]),
            self.__createValueNode("string", resultValue)
        ])
        hook = Node(None, "hook")
        hook.append(condition, "condition")
        hook.append(elsePart, "elsePart")
        hook.append(thenPart, "thenPart")
        
        return hook
    

    def __dispatchSelect(self, node):
        obj = self.__getFirstByType(node, "list")
        
        query = self.__getFirstByType(obj, "string").value
        resultObjects = self.__getAllByType(self.__getFirstByType(obj, "object_init"), "property_init")
        
        hookList = {}
        default = None
        
        for resultObject in resultObjects:
            identifier = list(resultObject)[0].value
            result = list(resultObject)[1]
            if identifier == "default":
                default = result
            else:
                hookList[identifier] = result
                
        newNode = default if default != None else Node(None, "null")
        for key, value in hookList.items():
            newNode = self.__createHook("jasy.Env.get", query, key, value, newNode)
        
        parent = node.parent
        parent.replace(node, newNode)


    def __patchEnvironment(self, node):
        """ Patch all classes to use Jasy Environment """
  
        if node.type == "call":
            identifier = self.__getCallName(node)
  
            if identifier == "qx.core.Environment.get":
                p1 = self.__createValueNode("identifier", "jasy")
                p2 = self.__createValueNode("identifier", "Env")
                p3 = self.__createValueNode("identifier", "getValue")
                jasyEnv = Node(None, "dot", [Node(None, "dot", [p1, p2]), p3])
                node.replace(node[0], jasyEnv)
    
            elif identifier == "qx.core.Environment.select":
                self.__dispatchSelect(node)
    
            elif identifier == "qx.core.Environment.add":
                p1 = self.__createValueNode("identifier", "jasy")
                p2 = self.__createValueNode("identifier", "Env")
                p3 = self.__createValueNode("identifier", "define")
                jasyEnv = Node(None, "dot", [Node(None, "dot", [p1, p2]), p3])
                node.replace(node[0], jasyEnv)
                
        elif node.type == "declaration":
            # Replace =qx.core.Environment;
            identifier = self.__getCallName(node, node.type)
            
            if identifier == "qx.core.Environment":
                p1 = self.__createValueNode("identifier", "jasy")
                p2 = self.__createValueNode("identifier", "Env")
                jasyEnv = Node(None, "dot", [p1, p2])
                node.replace(node[0], jasyEnv)
                
        elif node.type == "and":
            # Replace qx.core&&qx.core.Environment
            identifier1 = self.__getCallName(node[0], node.type)
            identifier2 = self.__getCallName(node[1], node.type)
            
            p1 = self.__createValueNode("identifier", "jasy")
            p2 = self.__createValueNode("identifier", "Env")
            jasyEnv = Node(None, "dot", [p1, p2])
            
            if identifier1 == "qx.core.Environment":
                node.replace(node[0], jasyEnv)
            elif identifier2 == "qx.core.Environment":
                node.replace(node[1], jasyEnv)
