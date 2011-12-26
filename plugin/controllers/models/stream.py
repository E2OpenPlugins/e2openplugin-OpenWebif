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
		sRef = session.nav.getCurrentlyPlayingServiceReference().toString()
	response = "#EXTM3U\nhttp://%s:8001/%s\n" % (request.getRequestHostname(),sRef)
	request.setHeader("Content-Disposition:", 'attachment;filename="%s"' % m3ufile)
	request.setHeader("Content-Type:", "audio/mpegurl")
	return response

