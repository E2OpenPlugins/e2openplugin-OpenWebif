# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: ATController
##########################################################################
# Copyright (C) 2013 - 2018 jbleyel and E2OpenPlugins
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

class ATController(resource.Resource):
	def __init__(self, session):
		resource.Resource.__init__(self)
		self.session = session

		try:
			from Plugins.Extensions.AutoTimer.AutoTimerResource import AutoTimerDoParseResource, \
			AutoTimerAddOrEditAutoTimerResource, AutoTimerChangeSettingsResource, \
			AutoTimerRemoveAutoTimerResource, AutoTimerSettingsResource, \
			AutoTimerSimulateResource
		except ImportError:
			# print "AT plugin not found"
			return
		self.putChild('parse', AutoTimerDoParseResource())
		self.putChild('remove', AutoTimerRemoveAutoTimerResource())
		self.putChild('edit', AutoTimerAddOrEditAutoTimerResource())
		self.putChild('get', AutoTimerSettingsResource())
		self.putChild('set', AutoTimerChangeSettingsResource())
		self.putChild('simulate', AutoTimerSimulateResource())
		try:
			from Plugins.Extensions.AutoTimer.AutoTimerResource import AutoTimerTestResource
			self.putChild('test', AutoTimerTestResource())
		except ImportError:
			# this is not an error
			pass

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
				return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>AutoTimer Config not found</e2statetext></e2simplexmlresult>'
		except ImportError:
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>AutoTimer Plugin not found</e2statetext></e2simplexmlresult>'
