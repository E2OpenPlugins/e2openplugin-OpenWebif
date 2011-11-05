##############################################################################
#                         <<< path.root >>>                                  
#                                                                            
#                        2011 E2OpenPlugins                                  
#                                                                            
#  This file is open source software; you can redistribute it and/or modify  
#     it under the terms of the GNU General Public License version 2 as      
#               published by the Free Software Foundation.                   
#                                                                            
##############################################################################

from Tools.Directories import fileExists

from twisted.web import server, http, static, resource, error
from Cheetah.Template import Template

from Plugins.Extensions.OpenWebif.core.info import getInfo, getBasePath, getWebPublicPath, getWebTemplatesPath
from dynamic import DynamicPath

class RootPath(DynamicPath):
	isLeaf = False
	
	def __init__(self, session, path = ""):
		DynamicPath.__init__(self, path)
		self.session = session
		
	def loadTemplateInsideBody(self, template, searchList):
		content = self.loadTemplate(template, searchList)
		return self.loadTemplate(getWebTemplatesPath() + "/body.html", {"content": content})
	
	def getPage(self, path, request):
		if path == "index.html":
			path = "tv.html"
			
		if path == "box_info.html":
			info = getInfo()
			if fileExists(getWebPublicPath("/images/boxes/" + info["model"] + ".jpg")):
				info["boximage"] = info["model"] + ".jpg"
			else:
				info["boximage"] = "unknown.jpg"
			return self.loadTemplateInsideBody(getWebTemplatesPath(path), info)

		elif path[-5:] == ".html" and fileExists(getWebPublicPath() + "/" + path):
			htmlout = self.loadHtmlSource(getWebPublicPath() + "/" + path)
			return self.loadTemplate(getWebTemplatesPath() + "/body.html", {"content": htmlout})

		return None
		
	def getChild(self, path, request):
		if path == "":
			path = "index.html"
			
		return RootPath(self.session, path)
		