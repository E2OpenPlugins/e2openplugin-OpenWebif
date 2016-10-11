# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Tools.Directories import fileExists
from models.info import getBasePath, getPublicPath, getViewsPath, getPiconPath
from models.grab import grabScreenshot
from base import BaseController
from web import WebController
from ajax import AjaxController
from api import ApiController
from file import FileController
from mobile import MobileController
from ipkg import IpkgController
from AT import ATController
from SR import SRController
from ER import ERController
from BQE import BQEController
from transcoding import TranscodingController
from wol import WOLSetupController, WOLClientController
from twisted.web import static, http

class RootController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session
		piconpath = getPiconPath()

		self.putChild("web", WebController(session))
		self.putChild("api", ApiController(session))
		self.putChild("ajax", AjaxController(session))
		self.putChild("file", FileController(session))
		self.putChild("grab", grabScreenshot(session))
		self.putChild("mobile", MobileController(session))
		self.putChild("js", static.File(getPublicPath() + "/js"))
		self.putChild("css", static.File(getPublicPath() + "/css"))
		self.putChild("static", static.File(getPublicPath() + "/static"))
		self.putChild("images", static.File(getPublicPath() + "/images"))
		self.putChild("ipkg", IpkgController(session))
		self.putChild("autotimer", ATController(session))
		self.putChild("serienrecorder", SRController(session))
		self.putChild("epgrefresh", ERController(session))
		self.putChild("bouqueteditor", BQEController(session))
		self.putChild("transcoding", TranscodingController(session))
		self.putChild("wol", WOLClientController(session))
		self.putChild("wolsetup", WOLSetupController(session))
		if piconpath:
			self.putChild("picon", static.File(piconpath))

	# this function will be called before a page is loaded
	def prePageLoad(self, request):
		# we set withMainTemplate here so it's a default for every page
		self.withMainTemplate = True

	# the "pages functions" must be called P_pagename
	# example http://boxip/index => P_index
	def P_index(self, request):
		mode = ''
		if "mode" in request.args.keys():
			mode = request.args["mode"][0]
		uagent = request.getHeader('User-Agent')
		if uagent and mode != 'fullpage':
			if uagent.lower().find("iphone") != -1 or uagent.lower().find("ipod") != -1 or uagent.lower().find("blackberry") != -1 or uagent.lower().find("android") != -1 or uagent.lower().find("mobile") != -1:
				request.setHeader("Location", "/mobile/")
				request.setResponseCode(http.FOUND)
				return ""
		return {}
