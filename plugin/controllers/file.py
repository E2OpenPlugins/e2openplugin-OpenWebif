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
from twisted.web import static, resource, http
from urllib import unquote, quote
from Components.config import config
from os import path as os_path, listdir
from Tools.Directories import fileExists
import glob

def new_getRequestHostname(self):
	host = self.getHeader(b'host')
	if host:
		if host[0]=='[':
			return host.split(']',1)[0] + "]"
		return host.split(':', 1)[0].encode('ascii')
	return self.getHost().host.encode('ascii')

http.Request.getRequestHostname = new_getRequestHostname

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
			filename = re.sub("^/+", "/", os.path.realpath(filename))

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
					if os_path.isdir(x):
						directories.append(x + '/')
						files.remove(x)
				data.append({"result": True,"dirs": directories,"files": files})
			else:
				data.append({"result": False,"message": "path %s not exits" % (path)})
			request.setHeader("content-type", "text/plain")
			return json.dumps(data)
