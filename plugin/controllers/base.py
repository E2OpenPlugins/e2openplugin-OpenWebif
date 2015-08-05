# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Plugins.Extensions.OpenWebif.__init__ import _

from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from twisted.web import server, http, static, resource, error
from Cheetah.Template import Template

from models.info import getInfo, getBasePath, getPublicPath, getViewsPath
from models.config import getCollapsedMenus, getRemoteGrabScreenshot, getZapStream, getEPGSearchType, getConfigsSections, getShowName, getCustomName, getBoxName

import imp
import sys
import json
import gzip
import cStringIO

from enigma import eEPGCache

try:
	from boxbranding import getBoxType, getMachineName
except:
	from models.owibranding import getBoxType, getMachineName

remote=''
try:
	from Components.RcModel import rc_model
	remote = rc_model.getRcFolder() + "/remote"
except:
	from models.owibranding import rc_model
	remote = rc_model().getRcFolder()

class BaseController(resource.Resource):
	isLeaf = False

	def __init__(self, path = ""):
		resource.Resource.__init__(self)

		self.path = path
		self.withMainTemplate = False
		self.isJson = False
		self.isCustom = False
		self.isGZ = False

	def error404(self, request):
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

	def getChild(self, path, request):
		return self.__class__(self.session, path)

	def compressBuf(self, buf):
		zbuf = cStringIO.StringIO()
		zfile = gzip.GzipFile(mode = 'wb',  fileobj = zbuf, compresslevel = 6)
		zfile.write(buf)
		zfile.close()
		return zbuf.getvalue()

	def render(self, request):
		# cache data
		withMainTemplate = self.withMainTemplate
		path = self.path
		isJson = self.isJson
		isCustom = self.isCustom
		isGZ = self.isGZ

		if self.path == "":
			self.path = "index"

		self.suppresslog = False
		self.path = self.path.replace(".", "")
		func = getattr(self, "P_" + self.path, None)
		if callable(func):
			request.setResponseCode(http.OK)

			# call prePageLoad function if exist
			plfunc = getattr(self, "prePageLoad", None)
			if callable(plfunc):
				plfunc(request)

			data = func(request)
			if data is None:
#				if not self.suppresslog:
#					print "[OpenWebif] page '%s' without content" % request.uri
				self.error404(request)
			elif self.isCustom:
#				if not self.suppresslog:
#					print "[OpenWebif] page '%s' ok (custom)" % request.uri
				request.write(data)
				request.finish()
			elif self.isJson:
#				if not self.suppresslog:
#					print "[OpenWebif] page '%s' ok (json)" % request.uri
				supported=[]
				if self.isGZ:
					acceptHeaders = request.requestHeaders.getRawHeaders('Accept-Encoding', [])
					supported = ','.join(acceptHeaders).split(',')
				if 'gzip' in supported:
					encoding = request.responseHeaders.getRawHeaders('Content-Encoding')
					if encoding:
						encoding = '%s,gzip' % ','.join(encoding)
					else:
						encoding = 'gzip'
					request.responseHeaders.setRawHeaders('Content-Encoding',[encoding])
					compstr = self.compressBuf(json.dumps(data))
					request.setHeader('Content-Length', '%d' % len(compstr))
					request.write(compstr)
				else:
					request.setHeader("content-type", "text/plain")
					request.write(json.dumps(data))
				request.finish()
			elif type(data) is str:
#				if not self.suppresslog:
#					print "[OpenWebif] page '%s' ok (simple string)" % request.uri
				request.setHeader("content-type", "text/plain")
				request.write(data)
				request.finish()
			else:
#				print "[OpenWebif] page '%s' ok (cheetah template)" % request.uri
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
					if self.withMainTemplate:
						args = self.prepareMainTemplate()
						args["content"] = out
						nout = self.loadTemplate("main", "main", args)
						if nout:
							out = nout
# prepare gzip for all templates
# TODO: speed check with or without gzip on lower speed boxes
#					supported=[]
#					acceptHeaders = request.requestHeaders.getRawHeaders('Accept-Encoding', [])
#					supported = ','.join(acceptHeaders).split(',')
#					if 'gzip' in supported:
#						encoding = request.responseHeaders.getRawHeaders('Content-Encoding')
#						if encoding:
#							encoding = '%s,gzip' % ','.join(encoding)
#						else:
#							encoding = 'gzip'
#						request.responseHeaders.setRawHeaders('Content-Encoding',[encoding])
#						compstr = self.compressBuf(out)
#						request.setHeader('Content-Length', '%d' % len(compstr))
#						request.write(compstr)
#					else:
					request.write(out)
					request.finish()

		else:
			print "[OpenWebif] page '%s' not found" % request.uri
			self.error404(request)

		# restore cached data
		self.withMainTemplate = withMainTemplate
		self.path = path
		self.isJson = isJson
		self.isCustom = isCustom
		self.isGZ = isGZ

		return server.NOT_DONE_YET

	def prepareMainTemplate(self):
		# here will be generated the dictionary for the main template
		ret = getCollapsedMenus()
		ret['remotegrabscreenshot'] = getRemoteGrabScreenshot()['remotegrabscreenshot']
		ret['configsections'] = getConfigsSections()['sections']
		ret['zapstream'] = getZapStream()['zapstream']
		ret['showname'] = getShowName()['showname']
		ret['customname'] = getCustomName()['customname']
		ret['boxname'] = getBoxName()['boxname']
		if not ret['boxname'] or not ret['customname']:
			ret['boxname'] = getInfo()['brand']+" "+getInfo()['model']
		ret['box'] = getBoxType()
		ret["remote"] = remote
		from Components.config import config
		if hasattr(eEPGCache, 'FULL_DESCRIPTION_SEARCH'):
			ret['epgsearchcaps'] = True
		else:
			ret['epgsearchcaps'] = False
			if config.OpenWebif.webcache.epg_desc_search.value:
				config.OpenWebif.webcache.epg_desc_search.value = False
				config.OpenWebif.webcache.epg_desc_search.save()
		ret['epgsearchtype'] = getEPGSearchType()['epgsearchtype']
		extras = []
		extras.append({ 'key': 'ajax/settings','description': _("Settings")})
		if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/LCD4linux/WebSite.pyo")):
			lcd4linux_key = "lcd4linux/config"
			if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/WebInterface/plugin.pyo")):
				from Components.Network import iNetwork
				ifaces = iNetwork.getConfiguredAdapters()
				if len(ifaces):
					ip_list = iNetwork.getAdapterAttribute(ifaces[0], "ip") # use only the first configured interface
					ip = "%d.%d.%d.%d" % (ip_list[0], ip_list[1], ip_list[2], ip_list[3])
				try:
					lcd4linux_port = "http://" + ip + ":" + str(config.plugins.Webinterface.http.port.value) + "/"
					lcd4linux_key = lcd4linux_port + 'lcd4linux/config'
				except KeyError:
					lcd4linux_key = None
			if lcd4linux_key:
				extras.append({ 'key': lcd4linux_key, 'description': _("LCD4Linux Setup")})
		
		try:
			from Plugins.Extensions.AutoTimer.AutoTimer import AutoTimer
			extras.append({ 'key': 'ajax/at','description': _('AutoTimer')})
		except ImportError:
			pass
		if fileExists(resolveFilename(SCOPE_PLUGINS, "Extensions/OpenWebif/controllers/views/ajax/bqe.tmpl")):
			extras.append({ 'key': 'ajax/bqe','description': _('BouquetEditor')})
		
		try:
			from Plugins.Extensions.EPGRefresh.EPGRefresh import epgrefresh
			extras.append({ 'key': 'ajax/epgr','description': _('EPGRefresh')})
		except ImportError:
			pass
		ret['extras'] = extras

		return ret
