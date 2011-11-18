##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Tools.Directories import fileExists

from twisted.web import server, http, static, resource, error
from Cheetah.Template import Template

from models.info import getInfo, getBasePath, getPublicPath, getViewsPath

import imp
import sys
import json
	
class BaseController(resource.Resource):
	isLeaf = False
	
	def __init__(self, path = ""):
		resource.Resource.__init__(self)

		if path != "":
			self.isLeaf = True
		
		self.path = path
		self.withMainTemplate = False
		self.isJson = False
	
	def error404(self, request):
		request.setHeader("content-type", "text/html")
		request.setResponseCode(http.NOT_FOUND)
		request.write("<html><head><title>Open Webif</title></head><body><h1>Error 404: Page not found</h1><br />The requested URL was not found on this server.</body></html>")
		request.finish()
		
	def loadTemplate(self, path, module, args):
		if fileExists(getViewsPath(path + ".py")) or fileExists(getViewsPath(path + ".pyo")):
			if fileExists(getViewsPath(path + ".pyo")):
				template = imp.load_compiled(module, getViewsPath(path + ".pyo"))
			else:
				template = imp.load_source(module, getViewsPath(path + ".py"))
			mod = getattr(template, module, None)
			if callable(mod):
				return str(mod(searchList=args))
		elif fileExists(getViewsPath(path + ".tmpl")):
			return str(Template(file=getViewsPath(path + ".tmpl"), searchList=[args]))
		return None
		
	def getChild(self, path, request):
		if path == "":
			path = "index"
			
		return self.__class__(self.session, path)
		
	def render(self, request):
		# cache data
		withMainTemplate = self.withMainTemplate
		path = self.path
		isJson = self.isJson
		
		func = getattr(self, "P_" + self.path, None)
		if callable(func):
			# call prePageLoad function if exist
			plfunc = getattr(self, "prePageLoad", None)
			if callable(plfunc):
				plfunc(request)
				
			data = func(request)
			if data is None:
				self.error404(request)
			elif type(data) is str:
				request.setHeader("content-type", "text/plain")
				request.setResponseCode(http.OK)
				request.write(data)
				request.finish()
			elif self.isJson:
				request.setHeader("content-type", "text/plain")
				request.setResponseCode(http.OK)
				request.write(json.dumps(data))
				request.finish()
			else:
				module = request.path
				if module[-1] == "/":
					module = module + "index"
				module = module.strip("/")
				out = self.loadTemplate(module, self.path, data)
				if out is None:
					self.error404(request)
				else:
					if self.withMainTemplate:
						args = self.prepareMainTemplate()
						args["content"] = out
						nout = self.loadTemplate("main", "main", args)
						if nout:
							out = nout
					request.setResponseCode(http.OK)
					request.write(out)
					request.finish()
				
		else:
			self.error404(request)
		
		# restore cached data
		self.withMainTemplate = withMainTemplate
		self.path = path
		self.isJson = isJson
		
		return server.NOT_DONE_YET

	def prepareMainTemplate(self):
		# here will be generated the dictionary for the main template
		return {}
