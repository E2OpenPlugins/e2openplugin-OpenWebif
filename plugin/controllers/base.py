# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: BaseController
##########################################################################
# Copyright (C) 2011 - 2018 E2OpenPlugins
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

import os
import imp
import json

from twisted.web import server, http, resource
from twisted.web.resource import EncodingResourceWrapper
from twisted.web.server import GzipEncoderFactory

from i18n import _
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from Cheetah.Template import Template
from enigma import eEPGCache
from Components.config import config
from Components.Network import iNetwork

from models.info import getInfo
from models.config import getCollapsedMenus, getConfigsSections
from models.config import getShowName, getCustomName, getBoxName

from defaults import getPublicPath, getViewsPath

def new_getRequestHostname(self):
	host = self.getHeader(b'host')
	if host:
		if host[0] == '[':
			return host.split(']', 1)[0] + "]"
		return host.split(':', 1)[0].encode('ascii')
	return self.getHost().host.encode('ascii')


http.Request.getRequestHostname = new_getRequestHostname

REMOTE = ''

try:
	from boxbranding import getBoxType, getMachineName
except:  # noqa: E722
	from models.owibranding import getBoxType, getMachineName  # noqa: F401

try:
	from Components.RcModel import rc_model
	REMOTE = rc_model.getRcFolder() + "/remote"
except:  # noqa: E722
	from models.owibranding import rc_model
	REMOTE = rc_model().getRcFolder()


class BaseController(resource.Resource):
	"""
	Web Base Controller
	"""
	isLeaf = False

	def __init__(self, path="", **kwargs):
		"""

		Args:
			* path: Base path
			* session: (?) Session instance
			* withMainTemplate: (?)
			* isJson: responses shall be JSON encoded
			* isCustom: (?)
			* isGZ: responses shall be GZIP compressed
			* isMobile: (?) responses shall be optimised for mobile devices
		"""
		resource.Resource.__init__(self)

		self.path = path
		self.session = kwargs.get("session")
		self.withMainTemplate = kwargs.get("withMainTemplate", False)
		self.isJson = kwargs.get("isJson", False)
		self.isCustom = kwargs.get("isCustom", False)
		self.isGZ = kwargs.get("isGZ", False)
		self.isMobile = kwargs.get("isMobile", False)

	def error404(self, request):
		"""
		Perform HTTP Error 404

		Args:
			request (twisted.web.server.Request): HTTP request object

		"""
		request.setHeader("content-type", "text/html")
		request.setResponseCode(http.NOT_FOUND)
		request.write("<html><head><title>Open Webif</title></head><body><h1>Error 404: Page not found</h1><br />The requested URL was not found on this server.</body></html>")
		request.finish()

	def loadTemplate(self, path, module, args):
		if fileExists(getViewsPath(path + ".py")) or fileExists(getViewsPath(path + ".pyo")):
			if fileExists(getViewsPath(path + ".pyo")):
				template = imp.load_compiled(module, getViewsPath(path + ".pyo"))
			else:
				template = imp.load_source(module, getViewsPath(path + ".py"))
			mod = getattr(template, module, None)
			if callable(mod):
				return str(mod(searchList=args))
		elif fileExists(getViewsPath(path + ".tmpl")):
			return str(Template(file=getViewsPath(path + ".tmpl"), searchList=[args]))
		return None

	def putGZChild(self, path, child):
		child.isGZ = True
		self.putChild(path,EncodingResourceWrapper(child, [GzipEncoderFactory()]))

	def getChild(self, path, request):
		if self.isGZ:
			return EncodingResourceWrapper(self.__class__(self.session, path), [GzipEncoderFactory()])
		else:
			return self.__class__(self.session, path)

	def NoDataRender(self):
		return []

	def noData(self, request):
		return {}

	def render(self, request):
		# cache data
		withMainTemplate = self.withMainTemplate
		path = self.path
		isCustom = self.isCustom
		isMobile = self.isMobile

		if self.path == "":
			self.path = "index"
		elif self.path == "signal":
			self.path = "tunersignal"
			request.uri = request.uri.replace('signal', 'tunersignal')
			request.path = request.path.replace('signal', 'tunersignal')

		self.suppresslog = False
		self.path = self.path.replace(".", "")
		if request.path.startswith('/api/config'):
			func = getattr(self, "P_config", None)
		elif self.path in self.NoDataRender():
			func = getattr(self, "noData", None)
		else:
			func = getattr(self, "P_" + self.path, None)

		if callable(func):
			request.setResponseCode(http.OK)

			# call prePageLoad function if exist
			plfunc = getattr(self, "prePageLoad", None)
			if callable(plfunc):
				plfunc(request)

			data = func(request)
			if data is None:
				# if not self.suppresslog:
					# print "[OpenWebif] page '%s' without content" % request.uri
				self.error404(request)
			elif self.isCustom:
				# if not self.suppresslog:
					# print "[OpenWebif] page '%s' ok (custom)" % request.uri
				request.write(data)
				request.finish()
			elif self.isJson:
				request.setHeader("content-type", "application/json; charset=utf-8")
				try:
					return json.dumps(data, indent=1)
				except Exception as exc:
					request.setResponseCode(http.INTERNAL_SERVER_ERROR)
					return json.dumps({"result": False, "request": request.path, "exception": repr(exc)})
					pass
			elif type(data) is str:
				# if not self.suppresslog:
					# print "[OpenWebif] page '%s' ok (simple string)" % request.uri
				request.setHeader("content-type", "text/plain")
				request.write(data)
				request.finish()
			else:
				# print "[OpenWebif] page '%s' ok (cheetah template)" % request.uri
				module = request.path
				if module[-1] == "/":
					module += "index"
				elif module[-5:] != "index" and self.path == "index":
					module += "/index"
				module = module.strip("/")
				module = module.replace(".", "")
				out = self.loadTemplate(module, self.path, data)
				if out is None:
					print "[OpenWebif] ERROR! Template not found for page '%s'" % request.uri
					self.error404(request)
				else:
					if self.isMobile:
						head = self.loadTemplate('mobile/head', 'head', [])
						out = head + out
					elif self.withMainTemplate:
						args = self.prepareMainTemplate(request)
						args["content"] = out
						nout = self.loadTemplate("main", "main", args)
						if nout:
							out = nout
					elif self.isGZ:
						return out
					request.write(out)
					request.finish()

		else:
			print "[OpenWebif] page '%s' not found" % request.uri
			self.error404(request)

		# restore cached data
		self.withMainTemplate = withMainTemplate
		self.path = path
		self.isCustom = isCustom
		self.isMobile = isMobile

		return server.NOT_DONE_YET

	def oscamconfPath(self):
		# Find and parse running oscam
		opath = None
		owebif = False
		oport = None
		variant = "oscam"
		for file in ["/tmp/.ncam/ncam.version", "/tmp/.oscam/oscam.version"]:
			if fileExists(file):  # nosec
				if "ncam" in file:
					variant = "ncam"
				else:
					variant = "oscam"

				conffile = file.split('/')[-1].replace("version","conf")

				data = open(file, "r").readlines()  # nosec
				for i in data:
					if "configdir:" in i.lower():
						opath = i.split(":")[1].strip() + "/" + conffile
						if not fileExists(opath):
							opath = None
					elif "web interface support:" in i.lower():
						owebif = i.split(":")[1].strip()
						if owebif == "yes":
							owebif = True
					elif "webifport:" in i.lower():
						oport = i.split(":")[1].strip()
						if oport == "0":
							oport = None
					else:
						continue
		return owebif, oport, opath, variant

	def prepareMainTemplate(self, request):
		# here will be generated the dictionary for the main template
		ret = getCollapsedMenus()
		ret['configsections'] = getConfigsSections()['sections']
		ret['showname'] = getShowName()['showname']
		ret['customname'] = getCustomName()['customname']
		ret['boxname'] = getBoxName()['boxname']
		if not ret['boxname'] or not ret['customname']:
			ret['boxname'] = getInfo()['brand'] + " " + getInfo()['model']
		ret['box'] = getBoxType()
		ret["remote"] = REMOTE
		if hasattr(eEPGCache, 'FULL_DESCRIPTION_SEARCH'):
			ret['epgsearchcaps'] = True
		else:
			ret['epgsearchcaps'] = False
		extras = [{'key': 'ajax/settings', 'description': _("Settings")}]
		ifaces = iNetwork.getConfiguredAdapters()
		if len(ifaces):
			ip_list = iNetwork.getAdapterAttribute(ifaces[0], "ip")  # use only the first configured interface
			if ip_list:
				ip = "%d.%d.%d.%d" % (ip_list[0], ip_list[1], ip_list[2], ip_list[3])

				if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/LCD4linux/WebSite.pyo")):
					lcd4linux_key = "lcd4linux/config"
					if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/WebInterface/plugin.pyo")):
						try:
							lcd4linux_port = "http://" + ip + ":" + str(config.plugins.Webinterface.http.port.value) + "/"
							lcd4linux_key = lcd4linux_port + 'lcd4linux/config'
						except:  # noqa: E722
							lcd4linux_key = None
					if lcd4linux_key:
						extras.append({'key': lcd4linux_key, 'description': _("LCD4Linux Setup"), 'nw': '1'})

		oscamwebif, port, oscamconf, variant = self.oscamconfPath()

		# Assume http until we know better ...
		proto = "http"

		# config file exists
		if oscamwebif and oscamconf is not None:
			# oscam defaults to NOT to start the web interface unless a section for it exists, so reset port to None until we find one
			port = None
			data = open(oscamconf, "r").readlines()
			for i in data:
				if "httpport" in i.lower():
					port = i.split("=")[1].strip()
					if port[0] == '+':
						proto = "https"
						port = port[1:]

		if oscamwebif and port is not None:
			url = "%s://%s:%s" % (proto, request.getRequestHostname(), port)
			if variant == "oscam":
				extras.append({'key': url, 'description': _("OSCam Webinterface"), 'nw': '1'})
			elif variant == "ncam":
				extras.append({'key': url, 'description': _("NCam Webinterface"), 'nw': '1'})

		try:
			from Plugins.Extensions.AutoTimer.AutoTimer import AutoTimer  # noqa: F401
			extras.append({'key': 'ajax/at', 'description': _('AutoTimer')})
		except ImportError:
			pass

		if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/OpenWebif/controllers/views/ajax/bqe.tmpl")) or fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/OpenWebif/controllers/views/ajax/bqe.pyo")):
			extras.append({'key': 'ajax/bqe', 'description': _('BouquetEditor')})

		try:
			from Plugins.Extensions.EPGRefresh.EPGRefresh import epgrefresh  # noqa: F401
			extras.append({'key': 'ajax/epgr', 'description': _('EPGRefresh')})
		except ImportError:
			pass

		try:
			# this will currenly only works if NO Webiterface plugin installed
			# TODO: test if webinterface AND openwebif installed
			from Plugins.Extensions.WebInterface.WebChilds.Toplevel import loaded_plugins
			for plugins in loaded_plugins:
				if plugins[0] in ["fancontrol", "iptvplayer", "serienrecorderui"]:
					try:
						extras.append({'key': plugins[0], 'description': plugins[2], 'nw': '2'})
					except KeyError:
						pass
		except ImportError:
			pass

		if os.path.exists('/usr/bin/shellinaboxd') and (fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/OpenWebif/controllers/views/ajax/terminal.tmpl")) or fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/OpenWebif/controllers/views/ajax/terminal.pyo"))):
			extras.append({'key': 'ajax/terminal', 'description': _('Terminal')})

		ret['extras'] = extras
		theme = 'original'
		if config.OpenWebif.webcache.theme.value:
			theme = config.OpenWebif.webcache.theme.value
		if not os.path.exists(getPublicPath('themes')):
			if not (theme == 'original' or theme == 'clear'):
				theme = 'original'
				config.OpenWebif.webcache.theme.value = theme
				config.OpenWebif.webcache.theme.save()
		ret['theme'] = theme

		moviedb = config.OpenWebif.webcache.moviedb.value if config.OpenWebif.webcache.moviedb.value else 'IMDb'
		config.OpenWebif.webcache.moviedb.value = moviedb
		config.OpenWebif.webcache.moviedb.save()
		ret['moviedb'] = moviedb
		imagedistro = getInfo()['imagedistro']
		ret['vti'] = imagedistro in ("VTi-Team Image") and 1 or 0
		ret['webtv'] = os.path.exists(getPublicPath('webtv'))
		return ret
