# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: RootController
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

from twisted.web import static, http, proxy
from Components.config import config

from models.info import getPublicPath, getPiconPath, getBasePath
from models.grab import grabScreenshot
from base import BaseController
from web import WebController, ApiController
from ajax import AjaxController
from mobile import MobileController
from ipkg import IpkgController
from AT import ATController
from SR import SRController
from ER import ERController
from BQE import BQEController
from transcoding import TranscodingController
from wol import WOLSetupController, WOLClientController
from file import FileController
from NET import NetController


class RootController(BaseController):
	def __init__(self, session, path=""):
		BaseController.__init__(self, path=path, session=session)
		piconpath = getPiconPath()

		self.putChild("web", WebController(session))
		self.putChild("api", ApiController(session))
		self.putChild("ajax", AjaxController(session))
		self.putChild("file", FileController())
		self.putChild("grab", grabScreenshot(session))
		if os.path.exists(getPublicPath('mobile')):
			self.putChild("mobile", MobileController(session))
			self.putChild("m", static.File(getPublicPath() + "/mobile"))
		for static_val in ('js', 'css', 'static', 'images', 'fonts'):
			self.putChild(static_val, static.File(getPublicPath() + '/' + static_val))
		for static_val in ('themes', 'webtv', 'vxg'):
			if os.path.exists(getPublicPath(static_val)):
				self.putChild(static_val, static.File(getPublicPath() + '/' + static_val))

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
		self.putChild("net", NetController(session))

	# this function will be called before a page is loaded
	def prePageLoad(self, request):
		# we set withMainTemplate here so it's a default for every page
		self.withMainTemplate = True

	# the "pages functions" must be called P_pagename
	# example http://boxip/index => P_index
	def P_index(self, request):
		if config.OpenWebif.responsive_enabled.value and os.path.exists(getBasePath() + "/controllers/views/responsive"):
			return {}
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
