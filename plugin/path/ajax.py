##############################################################################
#                         <<< path.ajax >>>                                  
#                                                                            
#                        2011 E2OpenPlugins                                  
#                                                                            
#  This file is open source software; you can redistribute it and/or modify  
#     it under the terms of the GNU General Public License version 2 as      
#               published by the Free Software Foundation.                   
#                                                                            
##############################################################################

from twisted.web import server, http, static, resource, error
from Cheetah.Template import Template

from Plugins.Extensions.OpenWebif.core.info import getBasePath, getWebPublicPath, getWebTemplatesPath
from Plugins.Extensions.OpenWebif.core.services import getCurrentService, getBouquets, getChannels, getSatellites
from dynamic import DynamicPath

class AjaxPath(DynamicPath):
	def __init__(self, session, path = ""):
		DynamicPath.__init__(self, path)
		self.session = session

	def getPath(self, file = ""):
		return getWebTemplatesPath() + "/ajax/" + file

	def getPage(self, path, request):
		if path == "current.html":
			service = getCurrentService(self.session)
			return self.loadTemplate(self.getPath(path), service)
			
		elif path == "bouquets.html":
			bouquets = getBouquets();
			return self.loadTemplate(self.getPath(path), bouquets)

		elif path == "bouquets_chan.html":
			bouquets = getBouquets();
			return self.loadTemplate(self.getPath(path), bouquets)

		elif path == "providers.html" or path == "providers_chan.html" or path == "satellites_chan.html" or path == "all.html":
			if "id" in request.args.keys():
				channels = getChannels(request.args["id"][0])
			else:
				channels = getChannels()
				return self.loadTemplate(self.getPath(path), channels)

		elif path == "satellites.html":
			satellites = getSatellites()
			return self.loadTemplate(self.getPath(path), satellites)
			
		return None

	def getChild(self, path, request):
		return AjaxPath(self.session, path)
		