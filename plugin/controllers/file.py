##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from os import path as os_path
from twisted.web import static, resource, http
from urllib import unquote, quote
from Components.config import config
from Components.Network import iNetwork

class FileController(resource.Resource):

	def __init__(self, path = ""):
		resource.Resource.__init__(self)

	def formatIp(self, ip):
		if len(ip) != 4:
			return None
		return "%d.%d.%d.%d" % (ip[0], ip[1], ip[2], ip[3])

	def render(self, request):
		action = "download"
		if "action" in request.args:
			action = request.args["action"][0]
			
		if "file" in request.args:
			filename = unquote(request.args["file"][0]).decode('utf-8', 'ignore').encode('utf-8')

			if action != "streamts":
				if not os_path.exists(filename):
					request.setResponseCode(http.OK)
					request.write("File '%s' not found" % (filename))
					request.finish()

			if action == "stream":
				request.setHeader("content-disposition", "inline;filename=\"stream.m3u\"")
				request.setHeader("content-type", "audio/mpegurl")
				request.write("#EXTM3U\n")
				request.write("http://%s:%s/file?action=download&file=%s" % (request.getRequestHostname(), config.OpenWebif.port.value, quote(filename)))
				request.finish()
			elif action == "streamts":
				request.setHeader("content-disposition", "inline;filename=\"stream.m3u\"")
				request.setHeader("content-type", "audio/mpegurl")
				request.write("#EXTM3U\n")
				request.write("http://%s:8001/%s\n" % (request.getRequestHostname(), filename))
				request.finish()
			elif action == "delete":
				request.setResponseCode(http.OK)
				request.write("TODO: DELETE FILE: %s" % (filename))
				request.finish()
			elif action == "download":
				request.setHeader("content-disposition", "attachment;filename=\"%s\"" % (filename.split('/')[-1]))
				rfile = static.File(filename, defaultType = "application/octet-stream")
				return rfile.render(request)
		else:
			request.setResponseCode(http.OK)
			request.write("Missing file parameter")
			request.finish()
