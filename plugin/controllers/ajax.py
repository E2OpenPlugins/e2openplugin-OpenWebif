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
try:
	from enigma import getBoxType, getMachineName
except:
	pass
	
from models.services import getCurrentService, getBouquets, getChannels, getSatellites, getProviders, getEventDesc, getChannelEpg, getSearchEpg, getCurrentFullInfo, getMultiEpg, getEvent
from models.info import getInfo, getPublicPath, getOpenWebifVer
from models.movies import getMovieList
from models.timers import getTimers
from models.config import getConfigs, getConfigsSections
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
		channels = getChannels(idbouquet, stype)
		info = getInfo()
		model = info["model"]
		channels['transcoding'] = False
		if model in ("solo2", "duo2", "Sezam Marvel", "Xpeed LX3"): 
			channels['transcoding'] = True
		return channels

	def P_eventdescription(self, request):
		return getEventDesc(request.args["sref"][0], request.args["idev"][0])

	def P_event(self, request):
		event = getEvent(request.args["sref"][0], request.args["idev"][0])
		event['event']['recording_margin_before'] = config.recording.margin_before.getValue()
		event['event']['recording_margin_after'] = config.recording.margin_after.getValue()
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
		elif model == "et4000":
			model = "et4x00"
		elif model == "xp1000":
			model = "xp1000"
		elif model == "xp1000s":
			model = "sf8"
		elif model == "odinm9":
			model = "odinm9"
		elif model == "odinm7":
			model = "odinm7"
		elif model == "e3hd":
			model = "e3hd"
		elif getBoxType() == 'odinm6':
			model = "starsatlx"
		elif getMachineName() == 'AX-Odin':
			model = "axodin"
		elif model == "MixOs F5":
			model = "ebox5000"
		elif model == "MixOs F5mini":
			model = "ebox5100"
		elif model == "MixOs F7":
			model = "ebox7358"
		elif model == "IOS-100HD":
			model = "ios100hd"
		elif model == "IOS-200HD":
			model = "ios200hd"
		elif model == "IOS-300HD":
			model = "ios300hd"
		elif model == "Optimuss-OS1":
			model = "optimussos1"
		elif model == "Optimuss-OS2":
			model = "optimussos2"
		elif model == "TM-TWIN-OE":
			model = "tmtwin"
		elif model == "TM-2T-OE":
			model = "tm2t"
		elif model == "TM-SINGLE":
			model = "tmsingle"
		elif model == "TM-NANO-OE":
			model = "tmnano"
		elif getBoxType() == 'ixusssone':
			model = "ixussone"
		elif getBoxType() == 'ixussduo':
			model = "ixussduo"
		elif getBoxType() == 'ixusszero':
			model = "ixusszero"
		elif model == 'Premium Twin':
			model = "ini-5000sv"
		elif model == 'Premium Mini':
			model = "ini-1000sv"
		elif model == 'Xpeed LX':
			if fileExists("/proc/stb/fp/version"):
				file = open("/proc/stb/fp/version")
				version = file.read().strip().lower()
				file.close()
			if version.startswith('2'):
				model = "xpeedlx2"
			else:
				model = "xpeedlx1"
		elif model == 'Xpeed LX3':
			model = "xpeedlx3"
		elif model == 'Sezam 1000-HD':
			model = "sezam-1000"
		elif model == 'Sezam 5000-HD':
			model = "sezam-5000"
		elif model == 'Sezam 1000-HD':
			model = "sezam-9000"
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
		elif fileExists("/proc/stb/info/hwmodel"):
			if getBoxType().startswith('opti'):
				box['brand'] = "edision"
			elif getBoxType().startswith('iqon'):
				box['brand'] = "iqon"
			else:
				box['brand'] = "technomate"
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
		info = getInfo()
		model = info["model"]
		movies['transcoding'] = False
		if model in ("solo2", "duo2", "Sezam Marvel", "Xpeed LX3", "gbquad", "gbquadplus"):
			movies['transcoding'] = True
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
				now = localtime()
				begintime = mktime( (now.tm_year, now.tm_mon, now.tm_mday+day, 6, 0, 0, -1, -1, -1) )
			except Exception, e:
				pass
		
		epg = getMultiEpg(self, bref, begintime, endtime)
		epg['bouquets'] = bouq['bouquets']
		epg['bref'] = bref
		epg['day'] = day
		
		return epg
	def P_multiepg2(self, request):
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
