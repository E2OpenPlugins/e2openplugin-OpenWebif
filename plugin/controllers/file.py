# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

import os
import re
import glob
from urllib import quote
import json

from twisted.web import static, resource, http

from Components.config import config
from Tools.Directories import fileExists
from utilities import lenient_force_utf_8, sanitise_filename_slashes


def new_getRequestHostname(self):
	host = self.getHeader(b'host')
	if host:
		if host[0]=='[':
			return host.split(']',1)[0] + "]"
		return host.split(':', 1)[0].encode('ascii')
	return self.getHost().host.encode('ascii')

http.Request.getRequestHostname = new_getRequestHostname


class FileController(resource.Resource):
	def render(self, request):
		action = "download"
		if "action" in request.args:
			action = request.args["action"][0]

		if "file" in request.args:
			filename = lenient_force_utf_8(request.args["file"][0])
			filename = sanitise_filename_slashes(os.path.realpath(filename))

			if not os.path.exists(filename):
				return "File '%s' not found" % (filename)

			if action == "stream":
				name = "stream"
				if "name" in request.args:
					name = request.args["name"][0]

				port = config.OpenWebif.port.value
				proto = 'http'
				if request.isSecure():
					port = config.OpenWebif.https_port.value
					proto = 'https'
				ourhost = request.getHeader('host')
				m = re.match('.+\:(\d+)$', ourhost)
				if m is not None:
					port = m.group(1)

				response = "#EXTM3U\n#EXTVLCOPT--http-reconnect=true\n#EXTINF:-1,%s\n%s://%s:%s/file?action=download&file=%s" % (name, proto, request.getRequestHostname(), port, quote(filename))
				request.setHeader("Content-Disposition", 'attachment;filename="%s.m3u"' % name)
				request.setHeader("Content-Type", "application/x-mpegurl")
				return response
			elif action == "delete":
				request.setResponseCode(http.OK)
				return "TODO: DELETE FILE: %s" % (filename)
			elif action == "download":
				request.setHeader("Content-Disposition", "attachment;filename=\"%s\"" % (filename.split('/')[-1]))
				rfile = static.File(filename, defaultType = "application/octet-stream")
				return rfile.render(request)
			else: 
				return "wrong action parameter"

		if "dir" in request.args:
			path = request.args["dir"][0]
			pattern = '*'
			data = []
			if "pattern" in request.args:
				pattern = request.args["pattern"][0]
			directories = []
			files = []
			if fileExists(path):
				try:
					files = glob.glob(path+'/'+pattern)
				except:
					files = []
				files.sort()
				tmpfiles = files[:]
				for x in tmpfiles:
					if os.path.isdir(x):
						directories.append(x + '/')
						files.remove(x)
				data.append({"result": True,"dirs": directories,"files": files})
			else:
				data.append({"result": False,"message": "path %s not exits" % (path)})
			request.setHeader("content-type", "application/json; charset=utf-8")
			return json.dumps(data, indent=2)
