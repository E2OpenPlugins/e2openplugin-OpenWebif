# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: SRController
##########################################################################
# Copyright (C) 2013 - 2018 betonme and E2OpenPlugins
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
##########################################################################

from twisted.web import resource, http


class SRController(resource.Resource):
	rootApi = None

	def __init__(self, session):
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
