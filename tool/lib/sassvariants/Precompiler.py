#
# SASS Precompiler
#

import re, os, base64

class Precompiler():
  def __init__(self, paths):
    self.__paths = paths
    self.__content = []

  def run(self, filename):
    with open(filename, encoding="utf-8") as input_file:
      self.__input_file = input_file
      self.__input_path = os.path.abspath(os.path.dirname(filename))
      self.__paths = [self.__input_path] + self.__paths
      self.__content = input_file.read().splitlines()
      self.__token_detector("@import",self.__token_import)
      self.__function_detector("inline_image",self.__function_inline_image)
      self.__input_file = None

  def get_content(self):
    return "\n".join(self.__content)

  def write_to_file(self, filename):
    with open(filename, mode="w", encoding="utf-8") as output_file:
      output_file.write(self.get_content())

  def __token_detector(self, token, handler):
    out_content = []
    for line in self.__content:
      matcher = re.match("^(\s*)(.*)$", line)
      if matcher != None:
        indents = len(matcher.group(1))
        command = matcher.group(2)

        if command[:len(token)] == token:
          out_content.append(handler(command))
        else:
          out_content.append(line)

      else:
        out_content.append(line)
    self.__content = out_content

  def __function_detector(self, function, handler):
    out_content = []
    for line in self.__content:
      matcher = re.match("^((\s*)(?:.*)):(?:\s*)(\S*)(?:\s*)$", line)
      if matcher != None:
        prefix = matcher.group(1)
        indents = len(matcher.group(2))
        command = matcher.group(3)
        
        if command[:len(function)] == function:
          out_content.append(handler(prefix,command))
        else:
          out_content.append(line)
      else:
        out_content.append(line)
    self.__content = out_content

  def __path_finder(self, url, paths):
    for path in paths:
      for pathpart in ["","framework/source/resource/unify/mobile"]:
        fname = os.path.join(path, pathpart, url)
        if os.path.isfile(fname):
          return path
    return None

  def __function_inline_image(self, prefix, command):
    matcher = re.match("^inline_image\((.*)\)(\s*)$", command)
    parameter = matcher.group(1)
    urlmatcher = re.match(".*[\"'](.+)[\"'].*", parameter)
    if urlmatcher != None:
      url = urlmatcher.group(1)
      path = self.__path_finder(url, self.__paths)
      if path:
        print ("Found image :", path)
        mime = ""
        ext = url[-4:1000]
        if (ext == ".png"):
          mime = "image/png"
        elif (ext == ".jpg"):
          mime = "image/jpeg"
        elif (ext == "jpeg"):
          mime = "image/jpeg"
        elif (ext == ".gif"):
          mime = "image/gif"
        return prefix + ": url(data:" + mime + ";base64," + self.__import_image(os.path.join(path, url)) + ")"
      else:
        print ("File not found : ", url)
    else:
      print ("Variable detected : " , parameter)
    return prefix + ":inline_image(\"" + self.__input_path + "\"," + matcher.group(1) + ")"

  def __import_image(self, filename):
    b64img = base64.encodebytes(open(filename, mode="rb").read()).decode("utf-8")
    b64img = "".join(b64img.splitlines())
    return b64img

  def __import_file(self, filename):
    new_pre = Precompiler(self.__paths)
    new_pre.run(filename)
    return new_pre.get_content()

  def __token_import(self, command):
    command = command[8:]
    input_file = self.__input_file
    inputdir = os.path.dirname(input_file.name)
    testdir = os.path.abspath(os.path.join(inputdir, command))
    if os.path.exists(testdir):
      return self.__import_file(testdir)
    for path in self.__paths:
      testdir = os.path.abspath(os.path.join(path, command))
      if os.path.exists(testdir):
        return self.__import_file(testdir)
    print("File not found for @import : ", command)
    return "// ---- NOT IMPORT: " + command