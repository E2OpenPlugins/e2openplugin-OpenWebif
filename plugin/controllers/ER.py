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

class ERController(resource.Resource):
	def __init__(self, session, path = ""):
		resource.Resource.__init__(self)
		self.session = session
		try:
			from Plugins.Extensions.EPGRefresh.EPGRefreshResource import EPGRefreshSettingsResource, \
			EPGRefreshChangeSettingsResource, \
			EPGRefreshListServicesResource, EPGRefreshAddRemoveServiceResource, \
			EPGRefreshStartRefreshResource, API_VERSION
		except ImportError:
			print "ER plugin not found"
			return
		self.putChild('get', EPGRefreshSettingsResource())
		self.putChild('set', EPGRefreshChangeSettingsResource())
		self.putChild('refresh', EPGRefreshStartRefreshResource())
		self.putChild('add', EPGRefreshAddRemoveServiceResource(EPGRefreshAddRemoveServiceResource.TYPE_ADD))
		self.putChild('del', EPGRefreshAddRemoveServiceResource(EPGRefreshAddRemoveServiceResource.TYPE_DEL))
		try:
			from Plugins.Extensions.EPGRefresh.EPGRefreshResource import EPGRefreshPreviewServicesResource
		except ImportError:
			pass
		else:
			self.putChild('preview', EPGRefreshPreviewServicesResource())

	def render(self, request):
		request.setResponseCode(http.OK)
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')
		try:
			from Plugins.Extensions.EPGRefresh.EPGRefresh import epgrefresh
			request.setHeader('Content-type', 'application/xhtml+xml')
			request.setHeader('charset', 'UTF-8')
			return ''.join(epgrefresh.buildConfiguration(webif = True))
		except ImportError:
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>EPG Refresh Plugin not found</e2statetext></e2simplexmlresult>'
