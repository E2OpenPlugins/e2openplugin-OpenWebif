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
from models.movies import getMovieList
from models.timers import getTimers
from base import BaseController
from web import WebController
from ajax import AjaxController
from api import ApiController
from file import FileController
from mobile import MobileController

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
		self.putChild("images", static.File(getPublicPath() + "/images"))
		if piconpath:
			self.putChild("picon", static.File(piconpath))
		
		
	# this function will be called before a page is loaded
	def prePageLoad(self, request):
		# we set withMainTemplate here so it's a default for every page
		self.withMainTemplate = True
		
	# the "pages functions" must be called P_pagename
	# example http://boxip/index => P_index
	def P_index(self, request):
		if request.getHeader("User-Agent").find("iPhone") != -1 or request.getHeader("User-Agent").find("iPod") != -1:
			request.setHeader("Location", "/mobile/")
			request.setResponseCode(http.FOUND)
			return ""
		return {}
		
	def P_workinprogress(self, request):
		return {}
		
	def P_powerstate(self, request):
		return {}

	def P_message(self, request):
		return {}

	def P_movies(self, request):
		if "dirname" in request.args.keys():
			movies = getMovieList(request.args["dirname"][0])
		else:
			movies = getMovieList()
		return movies
	
	def P_radio(self, request):
		return {}

	def P_timers(self, request):
		return getTimers(self.session)
