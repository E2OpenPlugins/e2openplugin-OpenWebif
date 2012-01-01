##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from enigma import eServiceReference
from urllib import unquote, quote
import os
from Components.config import config

def getStream(self, request, m3ufile):

	if "ref" in request.args:
		sRef=unquote(request.args["ref"][0]).decode('utf-8', 'ignore').encode('utf-8')
	else:
		sRef = ""
	
	if m3ufile == "streamcurrent.m3u":
		sRef = self.session.nav.getCurrentlyPlayingServiceReference().toString() 

	name = "stream"
	if "name" in request.args:
		name = request.args["name"][0]
	# #EXTINF:-1,%s\n  remove not compatiple with old api
	response = "#EXTM3U \n#EXTVLCOPT--http-reconnect=true \nhttp://%s:8001/%s\n" % (request.getRequestHostname(), sRef)
	request.setHeader('Content-Type', 'application/text')
	return response

def getTS(self,request):
	if "file" in request.args:
		filename = unquote(request.args["file"][0]).decode('utf-8', 'ignore').encode('utf-8')
		if not os.path.exists(filename):
			return "File '%s' not found" % (filename)
		response = "#EXTM3U\n#EXTVLCOPT--http-reconnect=true \nhttp://%s:%s/file?file=%s\n" % (request.getRequestHostname(), config.OpenWebif.port.value, quote(filename))
		request.setHeader('Content-Type', 'application/text')
		return response
	else:
		return "Missing file parameter"

streamstack = []

class StreamProxyHelper(object):
	def __init__(self, session, request):
		self.session = session
		self.request = request
		
		streamstack.append(self)
		self.request.notifyFinish().addCallback(self.close, None)
		self.request.notifyFinish().addErrback(self.close, None)
		
		if "StreamService" not in request.args:
			self.request.write("=NO STREAM\n")
			return
		
		self.service = session.nav.recordService(eServiceReference(request.args["StreamService"][0]))
		session.nav.record_event.append(self.recordEvent)
		if self.service is not None:
			self.service.prepareStreaming()
			self.service.start()
		
	def close(self, nothandled1=None, nothandled2=None):
		if self in streamstack:
			streamstack.remove(self)
		
	def recordEvent(self, service, event):
		if service is self.service:
			return
			
		streaming = service.stream()
		s = streaming and streaming.getStreamingData()

		if s is None:
			err = service.getError()
			if err:
				self.request.write("-SERVICE ERROR:%d\n" % err)
				return
			else:
				self.request.write("=NO STREAM\n")
				return

		demux = s["demux"]
		pids = ','.join(["%x:%s" % (x[0], x[1]) for x in s["pids"]])

		self.request.write("+%d:%s\n" % (demux, pids))
