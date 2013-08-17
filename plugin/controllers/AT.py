##############################################################################
#                        2013 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from twisted.web import static, resource, http, server
import json

class ATController(resource.Resource):
	def __init__(self, session, path = ""):
		resource.Resource.__init__(self)
		self.session = session
		try:
			from Plugins.Extensions.AutoTimer.AutoTimerResource import AutoTimerDoParseResource, \
			AutoTimerListAutoTimerResource, AutoTimerAddOrEditAutoTimerResource, \
			AutoTimerRemoveAutoTimerResource, AutoTimerChangeSettingsResource, \
			AutoTimerSettingsResource, AutoTimerSimulateResource, API_VERSION
		except ImportError:
			print "AT plugin not found"
			return
		self.putChild('parse', AutoTimerDoParseResource())
		self.putChild('remove', AutoTimerRemoveAutoTimerResource())
		self.putChild('edit', AutoTimerAddOrEditAutoTimerResource())
		self.putChild('get', AutoTimerSettingsResource())
		self.putChild('set', AutoTimerChangeSettingsResource())
		self.putChild('simulate', AutoTimerSimulateResource())
		
	def render(self, request):
		data = []
		try:
			from Plugins.Extensions.AutoTimer.AutoTimerResource import API_VERSION
			data.append({"result": True,"AutoTimer-Plugin": API_VERSION})
		except ImportError:
			data.append({"result": False,"AutoTimer-Plugin": "Not Found"})
		request.setHeader("content-type", "text/plain")
		request.write(json.dumps(data))
		request.finish()
		return server.NOT_DONE_YET
