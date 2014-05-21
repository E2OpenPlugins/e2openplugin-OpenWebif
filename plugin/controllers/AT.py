# -*- coding: utf-8 -*-

##############################################################################
#                        2013 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from twisted.web import static, resource, http, server

class ATController(resource.Resource):
	def __init__(self, session, path = ""):
		resource.Resource.__init__(self)
		self.session = session
		try:
			from Plugins.Extensions.AutoTimer.AutoTimerResource import AutoTimerDoParseResource, \
			AutoTimerAddOrEditAutoTimerResource, AutoTimerChangeSettingsResource, \
			AutoTimerRemoveAutoTimerResource, AutoTimerSettingsResource, \
			AutoTimerSimulateResource
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
		request.setResponseCode(http.OK)
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')
		try:
			from Plugins.Extensions.AutoTimer.plugin import autotimer
			try:
				if autotimer is not None:
					autotimer.readXml()
					return ''.join(autotimer.getXml())
			except Exception:
				pass
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>AutoTimer Config not found</e2statetext></e2simplexmlresult>'
		except ImportError:
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>AutoTimer Plugin not found</e2statetext></e2simplexmlresult>'
