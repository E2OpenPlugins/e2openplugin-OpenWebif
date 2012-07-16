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
from os import path as os_path, listdir
from Tools.Directories import fileExists

import json

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
			#elif action == "download":
			elif action == "downloadx": ## stupid fix for security hole DDamir
				request.setHeader("Content-Disposition:", "attachment;filename=\"%s\"" % (filename.split('/')[-1]))
				rfile = static.File(filename, defaultType = "application/octet-stream")
				return rfile.render(request)
			else: 
				return "wrong action parameter"
		
		if "dir" in request.args:
			path = request.args["dir"][0]

			if "pattern" in request.args:
				pattern = request.args["pattern"][0]
			else:
				pattern = None
				
			directories = []
			files = []	
			if fileExists(path):
				try:
					files = listdir(path)
				except:
					files = []

				files.sort()
				tmpfiles = files[:]
				for x in tmpfiles:
					if os_path.isdir(path + x):
						directories.append(path + x + "/")
						files.remove(x)

				data = []
				data.append({"result": True,"dirs": directories,"files": files})

				request.setHeader("content-type", "text/plain")
				request.write(json.dumps(data))
				request.finish()
				return server.NOT_DONE_YET
			else:
				return "path %s not exits" % (path)
