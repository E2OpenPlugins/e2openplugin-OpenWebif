##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from base import BaseController
from models.movies import getMovieList
from models.timers import getTimers
from models.services import getBouquets, getChannels

class MobileController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session

	def P_index(self, request):
		return {}

	def P_powerstate(self, request):
		return {}
		
	def P_screenshot(self, request):
		return {}

	def P_bouquets(self, request):
		return getBouquets()

	def P_channels(self, request):
		if "id" in request.args.keys():
			channels = getChannels(request.args["id"][0])
		else:
			channels = getChannels()
		return channels
		
	def P_timerlist(self, request):
		return getTimers(self.session)
		
	def P_movies(self, request):
		if "dirname" in request.args.keys():
			movies = getMovieList(request.args["dirname"][0])
		else:
			movies = getMovieList()
		return movies
		
	def P_about(self, request):
		return {}