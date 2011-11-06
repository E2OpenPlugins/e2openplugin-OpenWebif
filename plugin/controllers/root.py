##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Tools.Directories import fileExists

from models.info import getInfo, getBasePath, getPublicPath, getViewsPath
from base import BaseController
from web import WebController
from ajax import AjaxController

from twisted.web import static

class RootController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session
		
		self.putChild("web", WebController(session))
		self.putChild("ajax", AjaxController(session))
		self.putChild("js", static.File(getPublicPath() + "/js"))
		self.putChild("css", static.File(getPublicPath() + "/css"))
		self.putChild("images", static.File(getPublicPath() + "/images"))
		
	# this function will be called before a page is loaded
	def prePageLoad(self, request):
		# we set withMainTemplate here so it's a default for every page
		self.withMainTemplate = True
		
	# the "pages functions" must be called P_pagename
	# example http://boxip/index => P_index
	def P_index(self, request):
		return {}
		
	def P_about(self, request):
		return {}
		
	def P_boxinfo(self, request):
		info = getInfo()
		if fileExists(getPublicPath("/images/boxes/" + info["model"] + ".jpg")):
			info["boximage"] = info["model"] + ".jpg"
		else:
			info["boximage"] = "unknown.jpg"
		return info
		
	def P_workinprogress(self, request):
		return {}
