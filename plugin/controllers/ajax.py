##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Tools.Directories import fileExists
from Components.config import config

from models.services import getCurrentService, getBouquets, getChannels, getSatellites, getProviders, getEventDesc, getChannelEpg, getSearchEpg, getCurrentFullInfo
from models.info import getInfo, getPublicPath
from models.movies import getMovieList
from models.timers import getTimers
from models.config import getConfigs
from base import BaseController

class AjaxController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session
		
	def P_current(self, request):
		return getCurrentFullInfo(self.session)
		
	def P_bouquets(self, request):
		stype = "tv"
		if "stype" in request.args.keys():
			stype = request.args["stype"][0]
		bouq = getBouquets(stype)
		return { "bouquets": bouq['bouquets'], "stype": stype }
			
	def P_providers(self, request):
		stype = "tv"
		if "stype" in request.args.keys():
			stype = request.args["stype"][0]
		prov = getProviders(stype)
		return { "providers": prov['providers'], "stype": stype }
		
	def P_satellites(self, request):
		stype = "tv"
		if "stype" in request.args.keys():
			stype = request.args["stype"][0]
		sat = getSatellites(stype)
		return { "satellites": sat['satellites'], "stype": stype }

	
	def P_channels(self, request):
		stype = "tv"
		idbouquet = "ALL"
		if "stype" in request.args.keys():
			stype = request.args["stype"][0]
		if "id" in request.args.keys():
			idbouquet = request.args["id"][0]
		return getChannels(idbouquet, stype)
		

	def P_eventdescription(self, request):
		return getEventDesc(request.args["sref"][0], request.args["idev"][0])

	def P_about(self, request):
		return {}
	
	def P_boxinfo(self, request):
		info = getInfo()
		model = info["model"]
		if model == "et9000" or model == "et9200":
			model = "et9x00"
		elif model == "et5000" or model == "et6000":
			model = "et5x00"
		if fileExists(getPublicPath("/images/boxes/" + model + ".jpg")):
			info["boximage"] = model + ".jpg"
		else:
			info["boximage"] = "unknown.jpg"
		return info

	def P_epgpop(self, request):
		if "sref" in request.args.keys():
			return getChannelEpg(request.args["sref"][0])
		elif  "sstr" in request.args.keys():
			return getSearchEpg(request.args["sstr"][0])
		else: 
			return []
			
	def P_screenshot(self, request):
		box = {}
		box['brand'] = "dmm"
		if fileExists("/proc/stb/info/vumodel"):
			box['brand'] = "vuplus"
		return { "box": box }
		
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
		
	def P_workinprogress(self, request):
		return {}
	
	def P_radio(self, request):
		return {}

	def P_timers(self, request):
		return getTimers(self.session)
		
	def P_tv(self, request):
		return {}
		
	def P_config(self, request):
		section = "usage"
		if "section" in request.args.keys():
			section = request.args["section"][0]
			
		return getConfigs(section)