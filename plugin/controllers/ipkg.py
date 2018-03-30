# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from enigma import eConsoleAppContainer
from twisted.web import server, resource, http
# from os import path, popen, remove, stat

import os
import json

from base import BaseController
from Components.config import config

from Plugins.Extensions.OpenWebif.__init__ import _

PACKAGES = '/var/lib/opkg/lists'
INSTALLEDPACKAGES = '/var/lib/opkg/status'

class IpkgController(BaseController):

	def __init__(self, session, path = ""):
		BaseController.__init__(self, path=path, session=session)
		self.putChild('upload', IPKGUpload(self.session))

	def render(self, request):
		action =''
		package = ''
		self.request = request
		self.format = "html"
		self.container = None
		if "command" in request.args:
			action = request.args["command"][0]
		if "package" in request.args:
			package = request.args["package"][0]
		if "format" in request.args:
			self.format = request.args["format"][0]
		if action is not '':
			if action in ( "update", "upgrade" ):
				return self.CallOPKG(request,action)
			elif action in ( "info", "status", "install", "remove" ):
				return self.CallOPKGP(request,action,package)
			elif action in ( "listall", "list", "list_installed", "list_upgradable" ):
				return self.CallOPKList(request,action)
			elif action in ( "tmp" ):
				import glob
				tmpfiles = glob.glob('/tmp/*.ipk') # nosec
				ipks = []
				for tmpfile in tmpfiles:
					ipks.append({
						'path': tmpfile,
						'name' : (tmpfile.split('/')[-1]),
						'size' : os.stat(tmpfile).st_size,
						'date' : os.stat(tmpfile).st_mtime,
					})
				request.setHeader("content-type", "text/plain")
				request.write(json.dumps({'ipkfiles' : ipks}, encoding="ISO-8859-1"))
				request.finish()
				return server.NOT_DONE_YET
			else:
				return self.ShowError(request,"Unknown command: "+ action)
		else:
			return self.ShowHint(request)

		return self.ShowError(request,"Error")

	def enumFeeds(self):
		for fn in os.listdir('/etc/opkg'):
			if fn.endswith('-feed.conf'):
				file = open(os.path.join('/etc/opkg', fn))
				feedfile = file.readlines()
				file.close()
				try:
					for feed in feedfile:
						yield feed.split()[1]
				except IndexError:
					pass
				except IOError:
					pass

	def getPackages(self,action):
		map = {}
		for feed in self.enumFeeds():
			package = None
			try:
				for line in open(os.path.join(PACKAGES, feed), 'r'):
					if line.startswith('Package:'):
						package = line.split(":",1)[1].strip()
						version = ''
						description = ''
						continue
					if package is None:
						continue
					if line.startswith('Version:'):
						version = line.split(":",1)[1].strip()
					# TDOD : check description
					elif line.startswith('Description:'):
						description = line.split(":",1)[1].strip()
					elif description and line.startswith(' '):
						description += line[:-1]
					elif len(line) <= 1:
						d = description.split(' ',3)
						if len(d) > 3:
							if d[1] == 'version':
								description = d[3]
							if description.startswith('gitAUTOINC'):
								description = description.split(' ',1)[1]
						map.update( { package : [ version , description.strip(), "0" , "0"] } )		
						package = None
			except IOError:
				pass
	
		for line in open(INSTALLEDPACKAGES, 'r'):
			if line.startswith('Package:'):
				package = line.split(":",1)[1].strip()
				version = ''
				continue
			if package is None:
				continue
			if line.startswith('Version:'):
				version = line.split(":",1)[1].strip()
			elif len(line) <= 1:
				if map.has_key(package):
					if map[package][0] == version:
						map[package][2] = "1"
					else:
						nv = map[package][0]
						map[package][0] = version
						map[package][3] = nv
				package = None
	
		keys=map.keys()
		keys.sort()
		self.ResultString = ""
		if action == "listall":
			self.format = "json"
			ret = []
			for name in keys:
				ret.append({
					"name": name,
					"v": map[name][0],
					"d": map[name][1],
					"i": map[name][2],
					"u": map[name][3]
				})
			return ret
		elif action == "list":
			for name in keys:
				self.ResultString += name + " - " + map[name][0] + " - " + map[name][1] + "<br>"
		elif action == "list_installed":
			for name in keys:
				if map[name][2] == "1":
					self.ResultString += name + " - " + map[name][0] + "<br>"
		elif action == "list_upgradable":
			for name in keys:
				if len(map[name][3]) > 1:
					self.ResultString += name + " - " + map[name][3] + " - " + map[name][0] + "<br>"
		if self.format == "json":
			data = []
			# nresult = unicode(nresult, errors='ignore')
			data.append({"result": True,"packages": self.ResultString.split("<br>")})
			return data
		return self.ResultString

# TDOD: check encoding
	def CallOPKList(self, request, action):
		data = self.getPackages(action)
		acceptHeaders = request.requestHeaders.getRawHeaders('Accept-Encoding', [])
		supported = ','.join(acceptHeaders).split(',')
		if 'gzip' in supported:
			encoding = request.responseHeaders.getRawHeaders('Content-Encoding')
			if encoding:
				encoding = '%s,gzip' % ','.join(encoding)
			else:
				encoding = 'gzip'
			request.responseHeaders.setRawHeaders('Content-Encoding',[encoding])
			if self.format == "json":
				compstr = self.compressBuf(json.dumps(data, encoding="ISO-8859-1"))
			else:
				compstr = self.compressBuf("<html><body><br>" + data + "</body></html>")
			request.setHeader('Content-Length', '%d' % len(compstr))
			request.write(compstr)
		else:
			request.setHeader("content-type", "text/plain")
			if self.format == "json":
				request.write(json.dumps(data, encoding="ISO-8859-1"))
			else:
				request.write("<html><body><br>" + data + "</body></html>")
		request.finish()
		return server.NOT_DONE_YET

	def CallOPKG(self, request, action, parms=[]):
		cmd = ["/usr/bin/opkg", "ipkg", action] + parms
		request.setResponseCode(http.OK)
		self.ResultString = ''
		if hasattr(self.request, 'notifyFinish'):
			self.request.notifyFinish().addErrback(self.connectionError)
		self.container = eConsoleAppContainer()
		self.container.dataAvail.append(self.Moredata)
		self.container.appClosed.append(self.NoMoredata)
		self.IsAlive = True
		self.olddata = None
		self.container.execute(*cmd)
		return server.NOT_DONE_YET

	def connectionError(self, err):
		self.IsAlive = False

	def NoMoredata(self, data):
		if self.IsAlive:
			nresult=''
			for a in self.ResultString.split("\n"):
				# print "%s" % a
				if a.count(" - ") > 0:
					if nresult[:-1] == "\n":
						nresult+=a
					else:
						nresult+="\n" + a
				else:
					nresult+=a + "\n"
			nresult = nresult.replace("\n\n","\n")
			nresult = nresult.replace("\n "," ")
			if self.format == "json":
				data = []
				nresult=unicode(nresult, errors='ignore')
				data.append({"result": True,"packages": nresult.split("\n")})
				self.request.setHeader("content-type", "text/plain")
				self.request.write(json.dumps(data))
				self.request.finish()
			else:
				self.request.write("<html><body>\n")
				self.request.write(nresult.replace("\n", "<br>\n"))
				self.request.write("</body></html>\n")
				self.request.finish()

	def Moredata(self, data):
		if data != self.olddata or self.olddata is None and self.IsAlive:
			self.ResultString += data

	def CallOPKGP(self, request,action,pack):
		if pack is not '':
			return self.CallOPKG(request,action, [pack])
		else:
			return self.ShowError(request, "parameter: package is missing")

	def ShowError(self, request,text):
		request.setResponseCode(http.OK)
		request.write(text)
		request.finish()
		return server.NOT_DONE_YET

	def ShowHint(self, request):
		html = "<html><body><h1>OpenWebif Interface for OPKG</h1>"
		html += "Usage : ?command=<cmd>&package=packagename<&format=json><br>"
		html += "Valid Commands:<br>list,listall,list_installed,list_upgradable<br>"
		html += "Valid Package Commands:<br>info,status,install,remove<br>"
		html += "Valid Formats:<br>json,html(default)<br>"
		html += "</body></html>"
		request.setResponseCode(http.OK)
		request.write(html)
		request.finish()
		return server.NOT_DONE_YET


class IPKGUpload(resource.Resource):
	def __init__(self, session):
		resource.Resource.__init__(self)
		self.session = session

	def mbasename(self, fname):
		l = fname.split('/')
		win = l[len(l)-1]
		l2 = win.split('\\')
		return l2[len(l2)-1]

	def render_POST(self, request):
		request.setResponseCode(http.OK)
		request.setHeader('content-type', 'text/plain')
		request.setHeader('charset', 'UTF-8')
		content = request.args['rfile'][0]
		filename = self.mbasename(request.args['filename'][0])
		if not content or not config.OpenWebif.allow_upload_ipk.value:
			result = [False,_('Error upload File')]
		else:
			if not filename.endswith(".ipk"):
				result = [False,_('wrong filetype')]
			else:
				FN = "/tmp/" + filename # nosec
				fileh = os.open(FN, os.O_WRONLY|os.O_CREAT )
				bytes = 0
				if fileh:
					bytes = os.write(fileh, content)
					os.close(fileh)
				if bytes <= 0:
					try:
						os.remove(FN)
					except OSError, oe:
						pass
					result = [False,_('Error writing File')]
				else:
					result = [True,FN]
		return json.dumps({"Result": result })
