# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: IpkgController
##########################################################################
# Copyright (C) 2011 - 2020 E2OpenPlugins
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
##########################################################################

from enigma import eConsoleAppContainer
from twisted.web import server, resource, http

import os
import json
import six

from Components.config import config
from Plugins.Extensions.OpenWebif.controllers.base import BaseController
from Plugins.Extensions.OpenWebif.controllers.i18n import _
from Plugins.Extensions.OpenWebif.controllers.utilities import getUrlArg, PY3

PACKAGES = '/var/lib/opkg/lists'
INSTALLEDPACKAGES = '/var/lib/opkg/status'


class IpkgController(BaseController):
	def __init__(self, session, path=""):
		BaseController.__init__(self, path=path, session=session)
		self.putChild(b'upload', IPKGUpload(self.session))

	def render(self, request):
		self.request = request
		self.json = False
		self.container = None
		action = getUrlArg(request, "command", "")
		package = getUrlArg(request, "package", "")
		self.json = getUrlArg(request, "format") == "json"
		if action != '':
			if action in ("update", "upgrade"):
				return self.CallOPKG(request, action)
			elif action in ("info", "status", "install", "remove"):
				return self.CallOPKGP(request, action, package)
			elif action in ("listall", "list", "list_installed", "list_upgradable"):
				return self.CallOPKList(request, action)
			elif action in ("tmp"):
				import glob
				tmpfiles = glob.glob('/tmp/*.ipk')  # nosec
				ipks = []
				for tmpfile in tmpfiles:
					ipks.append({
						'path': tmpfile,
						'name': (tmpfile.split('/')[-1]),
						'size': os.stat(tmpfile).st_size,
						'date': os.stat(tmpfile).st_mtime,
					})
				request.setHeader("content-type", "text/plain")
				if PY3:
					request.write(json.dumps({'ipkfiles': ipks}).encode("ISO-8859-1"))
				else:
					request.write(json.dumps({'ipkfiles': ipks}, encoding="ISO-8859-1"))
				request.finish()
				return server.NOT_DONE_YET
			else:
				return self.ShowError(request, "Unknown command: " + action)
		else:
			return self.ShowHint(request)

		return self.ShowError(request, "Error")

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

	def getPackages(self, action):
		map = {}
		for feed in self.enumFeeds():
			package = None
			try:
				for line in open(os.path.join(PACKAGES, feed), 'r'):
					if line.startswith('Package:'):
						package = line.split(":", 1)[1].strip()
						version = ''
						description = ''
						continue
					if package is None:
						continue
					if line.startswith('Version:'):
						version = line.split(":", 1)[1].strip()
					# TDOD : check description
					elif line.startswith('Description:'):
						description = line.split(":", 1)[1].strip()
					elif description and line.startswith(' '):
						description += line[:-1]
					elif len(line) <= 1:
						d = description.split(' ', 3)
						if len(d) > 3:
							if d[1] == 'version':
								description = d[3]
							if description.startswith('gitAUTOINC'):
								description = description.split(' ', 1)[1]
						map.update({package: [version, description.strip(), "0", "0"]})
						package = None
			except IOError:
				pass

		for line in open(INSTALLEDPACKAGES, 'r'):
			if line.startswith('Package:'):
				package = line.split(":", 1)[1].strip()
				version = ''
				continue
			if package is None:
				continue
			if line.startswith('Version:'):
				version = line.split(":", 1)[1].strip()
			elif len(line) <= 1:
				if package in map:
					if map[package][0] == version:
						map[package][2] = "1"
					else:
						nv = map[package][0]
						map[package][0] = version
						map[package][3] = nv
				package = None

		keys = list(map.keys())
		keys.sort()
		self.ResultString = ""
		if action == "listall":
			self.json = True
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
		if self.json:
			data = []
			data.append({"result": True, "packages": self.ResultString.split("<br>")})
			return data
		return self.ResultString

# TDOD: check encoding
	def CallOPKList(self, request, action):
		data = self.getPackages(action)
		if self.json:
			request.setHeader("content-type", "application/json; charset=utf-8")
			try:
				return six.ensure_binary(json.dumps(data, indent=1))
			except Exception as exc:
				request.setResponseCode(http.INTERNAL_SERVER_ERROR)
				return json.dumps(six.ensure_binary({"result": False, "request": request.path, "exception": repr(exc)}))
				pass
		else:
			request.setHeader("content-type", "text/plain")
			request.write(b"<html><body><br>" + six.ensure_binary(data) + b"</body></html>")
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
			nresult = ''
			for a in self.ResultString.split("\n"):
				# print "%s" % a
				if a.count(" - ") > 0:
					if nresult[:-1] == "\n":
						nresult += a
					else:
						nresult += "\n" + a
				else:
					nresult += a + "\n"
			nresult = nresult.replace("\n\n", "\n")
			nresult = nresult.replace("\n ", " ")
			if self.json:
				data = []
				nresult = six.text_type(nresult, errors='ignore')
				data.append({"result": True, "packages": nresult.split("\n")})
				self.request.setHeader("content-type", "text/plain")
				self.request.write(six.ensure_binary(json.dumps(data)))
				self.request.finish()
			else:
				nresult = six.ensure_binary(nresult)
				self.request.write(b"<html><body>\n")
				self.request.write(nresult.replace(b"\n", b"<br>\n"))
				self.request.write(b"</body></html>\n")
				self.request.finish()

	def Moredata(self, data):
		if data != self.olddata or self.olddata is None and self.IsAlive:
			self.ResultString += data

	def CallOPKGP(self, request, action, pack):
		if pack != '':
			return self.CallOPKG(request, action, [pack])
		else:
			return self.ShowError(request, "parameter: package is missing")

	def ShowError(self, request, text):
		request.setResponseCode(http.OK)
		request.write(six.ensure_binary(text))
		request.finish()
		return server.NOT_DONE_YET

	def ShowHint(self, request):
		html = "<html><body><h1>OpenWebif Interface for OPKG</h1>"
		html += "Usage : ?command=<cmd>&package=packagename<&format=format><br>"
		html += "Valid Commands:<br>list,listall,list_installed,list_upgradable<br>"
		html += "Valid Package Commands:<br>info,status,install,remove<br>"
		html += "Valid Formats:<br>json,html(default)<br>"
		html += "</body></html>"
		request.setResponseCode(http.OK)
		request.write(six.ensure_binary(html))
		request.finish()
		return server.NOT_DONE_YET


class IPKGUpload(resource.Resource):
	def __init__(self, session):
		resource.Resource.__init__(self)
		self.session = session

	def mbasename(self, fname):
		_fname = fname.split('/')
		_fname = _fname[len(_fname) - 1]
		_fname = _fname.split('\\')
		return _fname[len(_fname) - 1]

	def render_POST(self, request):
		request.setResponseCode(http.OK)
		request.setHeader('content-type', 'text/plain')
		request.setHeader('charset', 'UTF-8')
		content = request.args[b'rfile'][0]
		filename = self.mbasename(getUrlArg(request, "filename"))
		if not content or not config.OpenWebif.allow_upload_ipk.value:
			result = [False, _('Error upload File')]
		else:
			if not filename.endswith(".ipk"):
				result = [False, _('wrong filetype')]
			else:
				FN = "/tmp/" + filename  # nosec
				fileh = os.open(FN, os.O_WRONLY | os.O_CREAT)
				bytes = 0
				if fileh:
					bytes = os.write(fileh, content)
					os.close(fileh)
				if bytes <= 0:
					try:
						os.remove(FN)
					except OSError:
						pass
					result = [False, _('Error writing File')]
				else:
					result = [True, FN]
		return six.ensure_binary(json.dumps({"Result": result}))
