# -*- coding: utf-8 -*-

##############################################################################
#                        2013 E2OpenPlugins                                  #
#                             by betonme                                     #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from twisted.web import static, resource, http, server

class SRController(resource.Resource):
	
	rootApi = None
	
	def __init__(self, session, path = ""):
		resource.Resource.__init__(self)
		self.session = session
		try:
			from Plugins.Extensions.serienrecorder.SerienRecorderResource import addWebInterfaceForOpenWebInterface
		except ImportError:
			print "SerienRecorder plugin not found"
			return
		
		(root, childs) = addWebInterfaceForOpenWebInterface()
		SRController.rootApi = root
		if childs:
			for name, api in childs:
				self.putChild(name, api)

	def render(self, request):
		if SRController.rootApi:
			return SRController.rootApi.render(request)
		else:
			request.setResponseCode(http.OK)
			request.setHeader('Content-type', 'application/xhtml+xml')
			request.setHeader('charset', 'UTF-8')
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>SerienRecorder Plugin not found</e2statetext></e2simplexmlresult>'
