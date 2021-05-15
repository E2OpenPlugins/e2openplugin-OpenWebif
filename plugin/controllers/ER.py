# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: ERController
##########################################################################
# Copyright (C) 2013 - 2020 jbleyel and E2OpenPlugins
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

from __future__ import print_function
from twisted.web import resource, http
import six


class ERController(resource.Resource):
	def __init__(self, session):
		resource.Resource.__init__(self)
		self.session = session

		try:
			from Plugins.Extensions.EPGRefresh.EPGRefreshResource import EPGRefreshSettingsResource, \
				EPGRefreshChangeSettingsResource, EPGRefreshAddRemoveServiceResource, \
				EPGRefreshStartRefreshResource
		except ImportError:
			#  print("EPG Refresh Plugin not found")
			return
		self.putChild(b'get', EPGRefreshSettingsResource())
		self.putChild(b'set', EPGRefreshChangeSettingsResource())
		self.putChild(b'refresh', EPGRefreshStartRefreshResource())
		self.putChild(b'add', EPGRefreshAddRemoveServiceResource(EPGRefreshAddRemoveServiceResource.TYPE_ADD))
		self.putChild(b'del', EPGRefreshAddRemoveServiceResource(EPGRefreshAddRemoveServiceResource.TYPE_DEL))
		try:
			from Plugins.Extensions.EPGRefresh.EPGRefreshResource import EPGRefreshPreviewServicesResource
		except ImportError:
			pass
		else:
			self.putChild(b'preview', EPGRefreshPreviewServicesResource())

	def render(self, request):
		request.setResponseCode(http.OK)
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')

		try:
			from Plugins.Extensions.EPGRefresh.EPGRefresh import epgrefresh
			return six.ensure_binary(''.join(epgrefresh.buildConfiguration(webif=True)))
		except ImportError:
			return b'<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>EPG Refresh Plugin not found</e2statetext></e2simplexmlresult>'
