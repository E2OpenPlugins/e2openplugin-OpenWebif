##############################################################################
#                         <<< path.web >>>                                   
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

from Plugins.Extensions.OpenWebif.core.info import getInfo, getBasePath, getWebPublicPath, getWebTemplatesPath
from Plugins.Extensions.OpenWebif.core.services import getCurrentService, getBouquets, getChannels, getSatellites
from Plugins.Extensions.OpenWebif.core.volume import getVolumeStatus, setVolumeUp, setVolumeDown, setVolumeMute, setVolume
from dynamic import DynamicPath

class WebPath(DynamicPath):
	def __init__(self, session, path = ""):
		DynamicPath.__init__(self, path)
		self.session = session

	def getPath(self, file = ""):
		return getWebTemplatesPath() + "/web/" + file

	def getPage(self, path, request):
		request.setHeader("content-type", "text/xml")
		if path == "about":
			info = getInfo()
			service = getCurrentService(self.session)
			return self.loadTemplate(self.getPath(path + ".xml"), {"info": info, "service": service})
			
		elif path == "vol":
			if "set" not in request.args.keys() or request.args["set"][0] == "state":
				volume = getVolumeStatus()
			elif request.args["set"][0] == "up":
				volume = setVolumeUp()
			elif request.args["set"][0] == "down":
				volume = setVolumeDown()
			elif request.args["set"][0] == "mute":
				volume = setVolumeMute()
			elif request.args["set"][0][:3] == "set":
				try:
					value = int(request.args["set"][0][3:])
					volume = setVolume(value)
				except Exception, e:
					volume = getVolumeStatus()
					volume["result"] = False
					volume["message"] = "Wrong parameter format 'set=%s'. Use set=set15 " % request.args["set"][0]
			else:
				volume = getVolumeStatus()
				volume["result"] = False
				volume["message"] = "Unknown Volume command %s" % request.args["set"][0]
			return self.loadTemplate(self.getPath(path + ".xml"), volume)
			
		return None

	def getChild(self, path, request):
		return WebPath(self.session, path)
