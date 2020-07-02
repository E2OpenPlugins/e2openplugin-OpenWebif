# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: StreamAdapter, StreamController
##########################################################################
# Copyright (C) 2011 - 2020 E2OpenPlugins
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

from twisted.web import resource, server
from Components.Converter.Streaming import Streaming
from Components.Sources.StreamService import StreamService
from Plugins.Extensions.OpenWebif.controllers.utilities import PY3

streamList = []
streamStates = []


class StreamAdapter:
	EV_BEGIN = 0
	EV_STOP = 1

	def __init__(self, session, request):
		self.nav = session.nav
		self.request = request
		self.mystream = StreamService(self.nav)
		if PY3:
			self.mystream.handleCommand(request.args[b"StreamService"][0].decode(encoding='utf-8', errors='strict'))
		else:
			self.mystream.handleCommand(request.args["StreamService"][0])
		self.mystream.execBegin()
		self.service = self.mystream.getService()
		self.nav.record_event.append(self.requestWrite)
		request.notifyFinish().addCallback(self.close, None)
		request.notifyFinish().addErrback(self.close, None)
		self.mystream.clientIP = request.getAllHeaders().get('x-forwarded-for', request.getClientIP())
		self.mystream.streamIndex = len(streamList) - 1
		self.mystream.request = request
		streamList.append(self.mystream)
		self.setStatus(StreamAdapter.EV_BEGIN)

	def setStatus(self, state):
		for x in streamStates:
			x(state, self.mystream)

	def close(self, nothandled1=None, nothandled2=None):
		self.mystream.execEnd()
		self.nav.record_event.remove(self.requestWrite)
		self.converter = None
		if self.mystream in streamList:
			streamList.remove(self.mystream)
		self.setStatus(StreamAdapter.EV_STOP)

	def requestWrite(self, notused1=None, notused2=None):
		converter_args = []
		self.converter = Streaming(converter_args)
		self.converter.source = self
		if PY3:
			self.request.write(self.converter.getText().decode(encoding='utf-8', errors='strict'))
		else:
			self.request.write(self.converter.getText())


class StreamController(resource.Resource):
	def __init__(self, session, path=""):
		resource.Resource.__init__(self)
		self.session = session

	def render(self, request):
		StreamAdapter(self.session, request)
		return server.NOT_DONE_YET
