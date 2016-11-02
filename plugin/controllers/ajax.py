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
from Components.config import config

from models.services import getCurrentService, getBouquets, getChannels, getSatellites, getProviders, getEventDesc, getChannelEpg, getSearchEpg, getCurrentFullInfo, getMultiEpg, getEvent
from models.info import getInfo, getPublicPath, getOpenWebifVer, getTranscodingSupport, getLanguage
from models.movies import getMovieList
from models.timers import getTimers
from models.config import getConfigs, getConfigsSections, getZapStream, getShowChPicon
from base import BaseController
from time import mktime, localtime
from models.locations import getLocations

try:
	from boxbranding import getBoxType, getMachineName, getMachineBrand, getMachineBuild
except:
	from models.owibranding import getBoxType, getMachineName, getMachineBrand, getMachineBuild

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
		channels = getChannels(idbouquet, stype)
		channels['transcoding'] = getTranscodingSupport()
		channels['type'] = stype
		channels['showchannelpicon'] = getShowChPicon()['showchannelpicon']
		return channels

	def P_eventdescription(self, request):
		return getEventDesc(request.args["sref"][0], request.args["idev"][0])

	def P_event(self, request):
		event = getEvent(request.args["sref"][0], request.args["idev"][0])
		event['event']['recording_margin_before'] = config.recording.margin_before.value
		event['event']['recording_margin_after'] = config.recording.margin_after.value
		at = False
		try:
			from Plugins.Extensions.AutoTimer.AutoTimer import AutoTimer
			at = True
		except ImportError:
			pass
		event['at'] = at
		event['transcoding'] = getTranscodingSupport()
		event['kinopoisk'] = getLanguage()
		return event

	def P_about(self, request):
		info = {}
		info["owiver"] = getOpenWebifVer()
		return { "info": info }
	
	def P_boxinfo(self, request):
		info = getInfo(self.session)
		type = getBoxType()

		if fileExists(getPublicPath("/images/boxes/"+type+".png")):
			info["boximage"] = type+".png"
		elif fileExists(getPublicPath("/images/boxes/"+type+".jpg")):
			info["boximage"] = type+".jpg"
		else:
			info["boximage"] = "unknown.png"
		return info

	def P_epgpop(self, request):
		events=[]
		timers=[]
		if "sref" in request.args.keys():
			ev = getChannelEpg(request.args["sref"][0])
			events = ev["events"]
		elif "sstr" in request.args.keys():
			ev = getSearchEpg(request.args["sstr"][0])
			events = ev["events"]
		at = False
		if len(events) > 0: 
			t = getTimers(self.session)
			timers = t["timers"]
			try:
				from Plugins.Extensions.AutoTimer.AutoTimer import AutoTimer
				at = True
			except ImportError:
				pass
		if config.OpenWebif.webcache.theme.value:
			theme = config.OpenWebif.webcache.theme.value
		else:
			theme = 'original'
		return { "theme":theme, "events": events , "timers" : timers , "at" : at, "kinopoisk": getLanguage()}

	def P_epgdialog(self, request):
		return self.P_epgpop(request)

	def P_screenshot(self, request):
		box = {}
		box['brand'] = "dmm"
		if getMachineBrand() == 'Vu+':
			box['brand'] = "vuplus"
		elif getMachineBrand() == 'GigaBlue':
			box['brand'] = "gigablue"
		elif getMachineBrand() == 'Edision':
			box['brand'] = "edision"
		elif getMachineBrand() == 'iQon':
			box['brand'] = "iqon"
		elif getMachineBrand() == 'Technomate':
			box['brand'] = "techomate"
		elif fileExists("/proc/stb/info/azmodel"):
			box['brand'] = "azbox"
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
		movies['transcoding'] = getTranscodingSupport()

		sorttype = config.OpenWebif.webcache.moviesort.value
		unsort = movies['movies']

		if sorttype == 'name':
			movies['movies'] = sorted(unsort, key=lambda k: k['eventname']) 
		elif sorttype == 'named':
			movies['movies'] = sorted(unsort, key=lambda k: k['eventname'],reverse=True) 
		elif sorttype == 'date':
			movies['movies'] = sorted(unsort, key=lambda k: k['recordingtime']) 
		elif sorttype == 'dated':
			movies['movies'] = sorted(unsort, key=lambda k: k['recordingtime'],reverse=True) 

		movies['sort'] = sorttype
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

	def P_settings(self, request):
		ret = {
			"result": True
		}
		ret['configsections'] = getConfigsSections()['sections']
		if config.OpenWebif.webcache.theme.value:
			ret['themes'] = config.OpenWebif.webcache.theme.choices
			ret['theme'] = config.OpenWebif.webcache.theme.value
		else:
			ret['themes'] = []
			ret['theme'] = 'original'
		ret['zapstream'] = getZapStream()['zapstream']
		ret['showchannelpicon'] = getShowChPicon()['showchannelpicon']
		return ret

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
				if day > 0:
					now = localtime()
					begintime = mktime( (now.tm_year, now.tm_mon, now.tm_mday+day, 0, 0, 0, -1, -1, -1) )
			except Exception, e:
				pass
		mode = 1
		if config.OpenWebif.webcache.mepgmode.value:
			try:
				mode = int(config.OpenWebif.webcache.mepgmode.value)
			except Exception, e:
				pass
		epg = getMultiEpg(self, bref, begintime, endtime, mode)
		epg['bouquets'] = bouq['bouquets']
		epg['bref'] = bref
		epg['day'] = day
		epg['mode'] = mode
		return epg

	def P_at(self, request):
		ret = {}
		ret['hasVPS'] = 0
		ret['hasSeriesPlugin'] = 0
		try:
			from Plugins.Extensions.AutoTimer.AutoTimer import typeMap
			ret['types'] = typeMap
		except ImportError:
			pass
		loc = getLocations()
		ret['locations'] = loc['locations']
				
		try:
			from Plugins.SystemPlugins.vps import Vps
			ret['hasVPS'] = 1
		except ImportError as ie:
			pass
		try:
			from Plugins.Extensions.SeriesPlugin.plugin import Plugins
			ret['hasSeriesPlugin'] = 1
		except ImportError as ie:
			pass
		return ret

	def P_bqe(self, request):
		ret = {}
		return ret

	def P_epgr(self, request):
		ret = {}
		return ret

