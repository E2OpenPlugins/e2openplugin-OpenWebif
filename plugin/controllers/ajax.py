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

from models.services import getCurrentService, getBouquets, getChannels, getSatellites, getProviders, getEventDesc, getChannelEpg, getSearchEpg, getCurrentFullInfo, getMultiEpg, getEvent
from models.info import getInfo, getPublicPath, getOpenWebifVer
from models.movies import getMovieList
from models.timers import getTimers
from models.config import getConfigs
from base import BaseController
from time import mktime, localtime

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

	def P_event(self, request):
		event = getEvent(request.args["sref"][0], request.args["idev"][0])
		event['event']['recording_margin_before'] = config.recording.margin_before.value
		event['event']['recording_margin_after'] = config.recording.margin_after.value
		return event

	def P_about(self, request):
		info = {}
		info["owiver"] = getOpenWebifVer()
		return { "info": info }
	
	def P_boxinfo(self, request):
		info = getInfo()
		model = info["model"]
		if model == "et9000" or model == "et9200":
			model = "et9x00"
		elif model == "et5000" or model == "et6000":
			model = "et5x00"
		elif model == "et4000" :
			model = "et4x00"
		elif model == "xp1000" :
			model = "xp1000"
		elif model == 'Premium Twin':
			model = "ini-5000sv"
		elif model == 'Premium Mini':
			model = "ini-1000sv"			
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
		elif fileExists("/proc/stb/info/azmodel"):
			box['brand'] = "azbox"
		elif fileExists("/proc/stb/info/gbmodel"):
			box['brand'] = "gigablue"
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
		
	def P_edittimer(self, request):
		return {}
		
	def P_tv(self, request):
		return {}
		
	def P_config(self, request):
		section = "usage"
		if "section" in request.args.keys():
			section = request.args["section"][0]
			
		return getConfigs(section)

	def P_multiepg(self, request):
		bouq = getBouquets("tv")
		if "bref" not in request.args.keys():
			bref = bouq['bouquets'][0][0]
		else:
			bref = request.args["bref"][0]

		endtime = 1440
				
		begintime = -1
		day = 0
		if "day" in request.args.keys():
			try:
				day = int(request.args["day"][0])
				now = localtime()
				begintime = mktime( (now.tm_year, now.tm_mon, now.tm_mday+day, 6, 0, 0, -1, -1, -1) )
			except Exception, e:
				pass
		
		epg = getMultiEpg(self, bref, begintime, endtime)
		epg['bouquets'] = bouq['bouquets']
		epg['bref'] = bref
		epg['day'] = day
		
		return epg
