##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from urllib import unquote

def getStream(session, request, m3ufile):
	if "ref" in request.args:
		sRef=unquote(request.args["ref"][0]).decode('utf-8', 'ignore').encode('utf-8')    
	else:
		sRef = ""
		
	if m3ufile == "streamcurrent.m3u":
		sRef = session.nav.getCurrentlyPlayingServiceReference().toString() 

	name = "stream"
	if "name" in request.args:
		name = request.args["name"][0]
	# #EXTINF:-1,%s\n  remove not compatiple with old api
	response = "#EXTM3U \n#EXTVLCOPT--http-reconnect=true \nhttp://%s:8001/%s\n" % (request.getRequestHostname(), sRef)
	request.setHeader("Content-Disposition:", 'attachment;filename="%s"' % m3ufile)
	request.setHeader('Content-Type', 'audio/mpegurl')
	return response

def getTS(self,request):
	if "file" in request.args:
		filename = unquote(request.args["file"][0]).decode('utf-8', 'ignore').encode('utf-8')
		if not os.path.exists(filename):
			return "File '%s' not found" % (filename)

		response = "#EXTM3U\n#EXTVLCOPT--http-reconnect=true\n#EXTINF:-1,%s\nhttp://%s:%s/file?action=download&file=%s" % (name, request.getRequestHostname(), config.OpenWebif.port.value, quote(filename))
		request.setHeader("Content-Disposition:", 'attachment;filename="ts.m3u"')
		request.setHeader("Content-Type:", "audio/mpegurl")

		return response
	else:
		return "Missing file parameter"
