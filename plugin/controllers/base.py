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

from Tools.Directories import fileExists
try:
	from enigma import getBoxType, getMachineName
except:
	pass

from twisted.web import server, http, static, resource, error
from Cheetah.Template import Template

from models.info import getInfo, getBasePath, getPublicPath, getViewsPath
from models.config import getCollapsedMenus, getRemoteGrabScreenshot, getZapStream, getConfigsSections

import imp
import sys
import json

class BaseController(resource.Resource):
	isLeaf = False

	def __init__(self, path = ""):
		resource.Resource.__init__(self)

		self.path = path
		self.withMainTemplate = False
		self.isJson = False
		self.isCustom = False

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

	def render(self, request):
		# cache data
		withMainTemplate = self.withMainTemplate
		path = self.path
		isJson = self.isJson
		isCustom = self.isCustom

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
				if not self.suppresslog:
					print "[OpenWebif] page '%s' without content" % request.uri
				self.error404(request)
			elif self.isCustom:
				if not self.suppresslog:
					print "[OpenWebif] page '%s' ok (custom)" % request.uri
				request.write(data)
				request.finish()
			elif self.isJson:
				if not self.suppresslog:
					print "[OpenWebif] page '%s' ok (json)" % request.uri
				request.setHeader("content-type", "text/plain")
				request.write(json.dumps(data))
				request.finish()
			elif type(data) is str:
				if not self.suppresslog:
					print "[OpenWebif] page '%s' ok (simple string)" % request.uri
				request.setHeader("content-type", "text/plain")
				request.write(data)
				request.finish()
			else:
				print "[OpenWebif] page '%s' ok (cheetah template)" % request.uri
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

		return server.NOT_DONE_YET

	def prepareMainTemplate(self):
		# here will be generated the dictionary for the main template
		ret = getCollapsedMenus()
		ret['remotegrabscreenshot'] = getRemoteGrabScreenshot()['remotegrabscreenshot']
		ret['configsections'] = getConfigsSections()['sections']
		ret['zapstream'] = getZapStream()['zapstream']
		ret['box'] = "dmm"

		if fileExists("/proc/stb/info/hwmodel"):
			file = open("/proc/stb/info/hwmodel")
			model = file.read().strip().lower()
			file.close()
		elif fileExists("/proc/stb/info/boxtype"):
			file = open("/proc/stb/info/boxtype")
			model = file.read().strip().lower()
			file.close()
			if model == "gigablue":
				if fileExists("/proc/stb/info/gbmodel"):
					file = open("/proc/stb/info/gbmodel")
					model = file.read().strip().lower()
					file.close()
					if model == "quad":
						model = "gbquad"
				else:
					model = 'gb800solo'
		elif fileExists("/proc/stb/info/azmodel"):
			file = open("/proc/stb/info/model")
			model = file.read().strip().lower()
			file.close()
		elif fileExists("/proc/stb/info/vumodel"):
			file = open("/proc/stb/info/vumodel")
			model = file.read().strip().lower()
			file.close()
		else:
			file = open("/proc/stb/info/model")
			model = file.read().strip().lower()
			file.close()

		ret['box'] = model

		if ret["box"] == "tmtwinoe":
			ret["remote"] = "tm"
		elif ret["box"] == "tm2toe":
			ret["remote"] = "tm"
		elif ret["box"] == "tmsingle":
			ret["remote"] = "tm"
		elif ret["box"] == "tmnanooe":
			ret["remote"] = "tm"
		elif ret["box"] in ("ios100hd", "ios200hd", "ios300hd"):
			ret["remote"] = "iqon"
		elif ret["box"] in ("optimussos1", "optimussos2"):
			ret["remote"] = "optimuss"
		elif ret["box"] in ("solo", "duo", "uno", "solo2", "duo2"):
			ret["remote"] = "vu_normal"
		elif ret["box"] == "ultimo":
			ret["remote"] = "vu_ultimo"
		elif ret["box"] in ("et9x00", "et9000", "et9200", "et9500"):
			ret["remote"] = "et9x00"
		elif ret["box"] in ("et5x00", "et5000", "et6000"):
			ret["remote"] = "et5x00"
		elif ret["box"] in ("et4x00", "et4000"):
			ret["remote"] = "et4x00"
		elif ret["box"] == "et6500":
			ret["remote"] = "et6500"
		elif ret["box"] in ("gb800solo", "gb800se", "gb800ue", "gbquad", "gb800seplus", "gb800ueplus", "gbquadplus"):
			ret["remote"] = "gigablue"
		elif ret["box"] in ("me", "minime"):
			ret["remote"] = "me"
		elif ret["box"] in ("premium", "premium+"):
			ret["remote"] = "premium"
		elif ret["box"] in ("elite", "ultra"):
			ret["remote"] = "elite"
		elif ret["box"] in ("ini-1000de", "ini-9000de"):
			ret["remote"] = "xpeedlx"
		elif ret["box"] in ("ini-1000", "ini-1000ru", "ini-9000ru"):
			ret["remote"] = "ini-1000"
		elif ret["box"] in ("ini-1000sv", "ini-5000sv"):
			ret["remote"] = "miraclebox"
		elif ret["box"] == "ini-3000":
			ret["remote"] = "ini-3000"
		elif ret["box"] in ("ini-7012", "ini-7000", "ini-5000", "ini-5000ru"):
			ret["remote"] = "ini-7000"
		elif ret["box"] in ("xp1000", "xp1000s"):
			ret["remote"] = "xp1000"
		elif ret["box"] == "odinm9":
			ret["remote"] = "odinm9"
		elif getBoxType() == 'odinm6' or getMachineName() == 'AX-Odin':
			ret["remote"] = "starsatlx"
		elif ret["box"] == "odinm7":
			ret["remote"] = "odinm7"
		elif ret["box"] == "e3hd":
			ret["remote"] = "e3hd"
		elif ret["box"] in ("ebox5000", "ebox5100", "ebox7358"):
			ret["remote"] = "ebox5000"
		elif getBoxType() == 'ixusssone':
			ret["remote"] = "ixussone"
		elif getBoxType() == 'ixussduo':
			ret["remote"] = "ixussone"
		elif getBoxType() == 'ixusszero':
			ret["remote"] = "ixusszero"
		elif ret["box"] in ("spark", "spark7162"):
			ret["remote"] = "spark"
		else:
			ret["remote"] = "dmm"
		extras = []
		extras.append({ 'key': 'ajax/settings','description': 'Settings'})

# TODO AutoTimer,Epgrefresh,BouquetEditor as Webinterface
		
#		try:
#			from Plugins.Extensions.AutoTimer.AutoTimer import AutoTimer
#			extras.append({ 'key': 'ajax/xxx','description': 'AutoTimer'})
#		except ImportError:
		
#		try:
#			from Plugins.Extensions.WebBouquetEditor.WebComponents.Sources.BouquetEditor import BouquetEditor
#			extras.append({ 'key': 'ajax/xxx','description': 'BouquetEditor'})
#		except ImportError:
		
#		try:
#			from Plugins.Extensions.EPGRefresh.EPGRefresh import epgrefresh
#			extras.append({ 'key': 'ajax/xxx','description': 'EPGRefresh'})
#		except ImportError:

		ret['extras'] = extras

#Translation
		tstrings = { 'movies': _("Movies"),
		'powercontrol': _("Power Control"),
		'grabscreenshot': _("Grab Screenshot"),
		'sendamessage': _("Send a Message"),
		'zapbeforestream': _("zap before Stream"),
		'search': _("Search"),
		'showfullremote': _("Show full remote"),
		'hidefullremote': _("Hide full remote"),
		'epgsearch': _("Epg Search"),
		'boxcontrol': _("Box Control"),
		'volumecontrol': _("Volume Control"),
		'shiftforlong': _("(shift + click for long pressure)")}
		ret['tstrings'] = tstrings
		return ret
