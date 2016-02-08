# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from twisted.web import static, resource, http, server
from Components.Converter.Streaming import Streaming
from Components.Sources.StreamService import StreamService

streamList = []
streamStates = []

class StreamAdapter:
	EV_BEGIN = 0
	EV_STOP = 1

	def __init__(self, session, request):
		self.nav = session.nav
		self.request = request
		self.mystream = StreamService(self.nav)
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

	def close(self, nothandled1 = None, nothandled2 = None):
		self.mystream.execEnd()
		self.nav.record_event.remove(self.requestWrite)
		self.converter = None
		if self.mystream in streamList:
			streamList.remove(self.mystream)
		self.setStatus(StreamAdapter.EV_STOP)

	def requestWrite(self, notused1 = None, notused2 = None):
		converter_args = []
		self.converter = Streaming(converter_args)
		self.converter.source = self
		self.request.write(self.converter.getText())

class StreamController(resource.Resource):
	def __init__(self, session, path = ""):
		resource.Resource.__init__(self)
		self.session = session

	def render(self, request):
		StreamAdapter(self.session, request)
		return server.NOT_DONE_YET
