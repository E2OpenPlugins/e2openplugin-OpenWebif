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

from twisted.web import static, http, proxy
from twisted.web.resource import EncodingResourceWrapper
from twisted.web.server import GzipEncoderFactory

from models.info import getPublicPath, getPiconPath
from models.grab import grabScreenshot
from base import BaseController
from web import WebController
from ajax import AjaxController
from mobile import MobileController
from ipkg import IpkgController
from AT import ATController
from SR import SRController
from ER import ERController
from BQE import BQEController
from transcoding import TranscodingController
from wol import WOLSetupController, WOLClientController
import rest_fs_access
import rest_api_controller


class RootController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path=path, session=session)
		piconpath = getPiconPath()

		self.putChild("web", WebController(session))
		api_controller_instance = EncodingResourceWrapper(
			rest_api_controller.ApiController(session, resource_prefix='/api'),
			[GzipEncoderFactory()])
		self.putChild("api", api_controller_instance)
		self.putChild("ajax", AjaxController(session))

		encoder_factory = rest_fs_access.GzipEncodeByFileExtensionFactory(
			extensions=[
				'txt', 'json', 'html', 'xml', 'js', 'conf', 'cfg',
				'eit', 'sc', 'ap'
			])
		#: gzip compression enabled file controller
		wrapped_fs_controller = EncodingResourceWrapper(
			rest_fs_access.FileController(
				root='/',
				resource_prefix="/file",
				session=session),
			[encoder_factory]
		)
		self.putChild("file", wrapped_fs_controller)
		self.putChild("grab", grabScreenshot(session))
		if os.path.exists(getPublicPath('mobile')):
			self.putChild("mobile", MobileController(session))
			self.putChild("m", static.File(getPublicPath() + "/mobile"))
		self.putChild("js", static.File(getPublicPath() + "/js"))
		self.putChild("css", static.File(getPublicPath() + "/css"))
		self.putChild("static", static.File(getPublicPath() + "/static"))
		self.putChild("images", static.File(getPublicPath() + "/images"))
		self.putChild("fonts", static.File(getPublicPath() + "/fonts"))
		if os.path.exists(getPublicPath('themes')):
			self.putChild("themes", static.File(getPublicPath() + "/themes"))
		if os.path.exists(getPublicPath('webtv')):
			self.putChild("webtv", static.File(getPublicPath() + "/webtv"))
		if os.path.exists(getPublicPath('vxg')):
			self.putChild("vxg", static.File(getPublicPath() + "/vxg"))
		if os.path.exists('/usr/bin/shellinaboxd'):
			self.putChild("terminal", proxy.ReverseProxyResource('::1', 4200, '/'))
		self.putChild("ipkg", IpkgController(session))
		self.putChild("autotimer", ATController(session))
		self.putChild("serienrecorder", SRController(session))
		self.putChild("epgrefresh", ERController(session))
		self.putChild("bouqueteditor", BQEController(session))
		self.putChild("transcoding", TranscodingController())
		self.putChild("wol", WOLClientController())
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
		if uagent and mode != 'fullpage' and os.path.exists(getPublicPath('mobile')):
			if uagent.lower().find("iphone") != -1 or uagent.lower().find("ipod") != -1 or uagent.lower().find("blackberry") != -1 or uagent.lower().find("mobile") != -1:
				request.setHeader("Location", "/mobile/")
				request.setResponseCode(http.FOUND)
				return ""
		return {}
