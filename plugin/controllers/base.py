##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Tools.Directories import fileExists

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
		ret['vixconfigsections'] = getConfigsSections('/usr/lib/enigma2/python/Plugins/SystemPlugins/ViX/data/setup.xml')['sections']
		ret['zapstream'] = getZapStream()['zapstream']
		ret['box'] = "dmm"
		if open("/proc/stb/info/model",'r').read().strip() == "Gigablue":
			ret['box'] = "gigablue"
		if fileExists("/proc/stb/info/hwmodel"):
			ret['box'] = open("/proc/stb/info/hwmodel").read().strip().lower()
		elif fileExists("/proc/stb/info/vumodel"):
			ret['box'] = open("/proc/stb/info/vumodel").read().strip()
		elif fileExists("/proc/stb/info/azmodel"):
			ret['box'] = open("/proc/stb/info/model").read().strip()
		elif fileExists("/proc/stb/info/boxtype"):
			ret['box'] = open("/proc/stb/info/boxtype").read().strip()

		if ret["box"] == "twin":
			ret["remote"] = "tm_twin"
		elif ret["box"] == "duo" or ret["box"] == "solo" or ret["box"] == "uno":
			ret["remote"] = "vu_normal"
		elif ret["box"] == "ultimo":
			ret["remote"] = "vu_ultimo"
		elif ret["box"] == "et9x00" or ret["box"] == "et9000" or ret["box"] == "et9200":
			ret["remote"] = "et9x00"
		elif ret["box"] == "et5x00" or ret["box"] == "et5000" or ret["box"] == "et6000":
			ret["remote"] = "et5x00"
		elif ret["box"] == "gigablue":
			ret["remote"] = "gigablue"
		elif ret["box"] == "me" or ret["box"] == "minime":
			ret["remote"] = "me"
		elif ret["box"] == "premium" or ret["box"] == "premium+":
			ret["remote"] = "premium"
		elif ret["box"] == "elite" or ret["box"] == "ultra":
			ret["remote"] = "elite"
		else:
			ret["remote"] = "dmm"

		return ret
