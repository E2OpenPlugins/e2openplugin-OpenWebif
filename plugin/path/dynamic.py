##############################################################################
#                         <<< path.dynamic >>>                               
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

from Plugins.Extensions.OpenWebif.core.info import getBasePath, getWebPublicPath, getWebTemplatesPath
	
class DynamicPath(resource.Resource):
	isLeaf = False
	
	def __init__(self, path = ""):
		resource.Resource.__init__(self)

		if path != "":
			self.isLeaf = True
		
		self.path = path

	def loadHtmlSource(self, file):
		out = ""
		if fileExists(file):
			try:
				f = open(file,'r')
				out = f.read()
				f.close()
			except Exception, e:
				print e
		return out

	def loadTemplate(self, template, searchList):
		htmlout = self.loadHtmlSource(template)
		return str(Template(htmlout, searchList=[searchList]))
		
	def render(self, request):
		path = self.path
		
		buff = self.getPage(path, request)
		if buff != None:
			request.setResponseCode(http.OK)
			request.write(str(buff))
			request.finish()
		elif fileExists(getWebPublicPath() + "/" + path):
			request.setResponseCode(http.OK)
			request.write(self.loadHtmlSource(getWebPublicPath() + "/" + path))
			request.finish()
		else:
			request.setResponseCode(http.NOT_FOUND)
			request.write("<html><head><title>Open Webif</title></head><body><h1>Error 404: Page not found</h1><br />The requested URL was not found on this server.</body></html>")
			request.finish()
			
		return server.NOT_DONE_YET