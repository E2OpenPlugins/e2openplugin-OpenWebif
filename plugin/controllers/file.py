##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
import os
from twisted.web import static, resource, http
from urllib import unquote, quote
from Components.config import config

class FileController(resource.Resource):

	def __init__(self, path = ""):
		resource.Resource.__init__(self)

	def render(self, request):
		action = "download"
		if "action" in request.args:
			action = request.args["action"][0]
			
		if "file" in request.args:
			filename = unquote(request.args["file"][0]).decode('utf-8', 'ignore').encode('utf-8')


			if not os.path.exists(filename):
				return "File '%s' not found" % (filename)

			name = "stream"
			if "name" in request.args:
				name = request.args["name"][0]
			if action == "stream":
				response = "#EXTM3U\n#EXTVLCOPT--http-reconnect=true\n#EXTINF:-1,%s\nhttp://%s:%s/file?action=download&file=%s" % (name, request.getRequestHostname(), config.OpenWebif.port.value, quote(filename))
				request.setHeader("Content-Disposition:", 'attachment;filename="%s.m3u"' % name)
				request.setHeader("Content-Type:", "audio/mpegurl")
				return response
			elif action == "delete":
				request.setResponseCode(http.OK)
				return "TODO: DELETE FILE: %s" % (filename)
			elif action == "download":
				request.setHeader("Content-Disposition:", "attachment;filename=\"%s\"" % (filename.split('/')[-1]))
				rfile = static.File(filename, defaultType = "application/octet-stream")
				return rfile.render(request)
		else:
			return "Missing file parameter"
