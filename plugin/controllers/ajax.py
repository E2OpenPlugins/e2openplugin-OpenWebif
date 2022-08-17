# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: AjaxController
##########################################################################
# Copyright (C) 2011 - 2020 E2OpenPlugins
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

from Tools.Directories import fileExists
from Components.config import config
from time import mktime, localtime
import os

from Plugins.Extensions.OpenWebif.controllers.models.services import getBouquets, getChannels, getAllServices, getSatellites, getProviders, getEventDesc, getChannelEpg, getSearchEpg, getCurrentFullInfo, getMultiEpg, getEvent
from Plugins.Extensions.OpenWebif.controllers.models.info import getInfo
from Plugins.Extensions.OpenWebif.controllers.models.movies import getMovieList, getMovieSearchList, getMovieInfo
from Plugins.Extensions.OpenWebif.controllers.models.timers import getTimers
from Plugins.Extensions.OpenWebif.controllers.models.config import getConfigs, getConfigsSections
from Plugins.Extensions.OpenWebif.controllers.models.stream import GetSession
from Plugins.Extensions.OpenWebif.controllers.base import BaseController
from Plugins.Extensions.OpenWebif.controllers.models.locations import getLocations
from Plugins.Extensions.OpenWebif.controllers.defaults import OPENWEBIFVER, getPublicPath, VIEWS_PATH, TRANSCODING, EXT_EVENT_INFO_SOURCE, HASAUTOTIMER, HASAUTOTIMERTEST, HASAUTOTIMERCHANGE, HASVPS, HASSERIES, ATSEARCHTYPES
from Plugins.Extensions.OpenWebif.controllers.utilities import getUrlArg, getEventInfoProvider

try:
	from boxbranding import getBoxType, getMachineName, getMachineBrand, getMachineBuild
except:  # nosec # noqa: E722
	from Plugins.Extensions.OpenWebif.controllers.models.owibranding import getBoxType, getMachineName, getMachineBrand, getMachineBuild  # noqa: F401


class AjaxController(BaseController):
	"""
	Ajax Web Controller
	"""

	def __init__(self, session, path=""):
		BaseController.__init__(self, path=path, session=session)

	def NoDataRender(self):
		"""
		ajax requests with no extra data
		"""
		return ['powerstate', 'message', 'myepg', 'radio', 'terminal', 'bqe', 'tv', 'satfinder']

	def P_edittimer(self, request):
		pipzap = getInfo()['timerpipzap']
		autoadjust = getInfo()['timerautoadjust']
		return {"autoadjust": autoadjust, "pipzap": pipzap}

	def P_current(self, request):
		return getCurrentFullInfo(self.session)

	def P_bouquets(self, request):
		stype = getUrlArg(request, "stype", "tv")
		bouq = getBouquets(stype)
		return {"bouquets": bouq['bouquets'], "stype": stype}

	def P_providers(self, request):
		stype = getUrlArg(request, "stype", "tv")
		prov = getProviders(stype)
		return {"providers": prov['providers'], "stype": stype}

	def P_satellites(self, request):
		stype = getUrlArg(request, "stype", "tv")
		sat = getSatellites(stype)
		return {"satellites": sat['satellites'], "stype": stype}

	# http://enigma2/ajax/channels?id=1%3A7%3A1%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3AFROM%20BOUQUET%20%22userbouquet.favourites.tv%22%20ORDER%20BY%20bouquet&stype=tv
	def P_channels(self, request):
		stype = getUrlArg(request, "stype", "tv")
		idbouquet = getUrlArg(request, "id", "ALL")
		channels = getChannels(idbouquet, stype)
		channels['transcoding'] = TRANSCODING
		channels['type'] = stype
		channels['showpicons'] = config.OpenWebif.webcache.showpicons.value
		channels['showpiconbackground'] = config.OpenWebif.responsive_show_picon_background.value
		channels['shownownextcolumns'] = config.OpenWebif.responsive_nownext_columns_enabled.value
		return channels

	# http://enigma2/ajax/eventdescription?idev=479&sref=1%3A0%3A19%3A1B1F%3A802%3A2%3A11A0000%3A0%3A0%3A0%3A
	def P_eventdescription(self, request):
		return getEventDesc(getUrlArg(request, "sref"), getUrlArg(request, "idev"))

	# http://enigma2/ajax/event?idev=479&sref=1%3A0%3A19%3A1B1F%3A802%3A2%3A11A0000%3A0%3A0%3A0%3A
	def P_event(self, request):
		event = getEvent(getUrlArg(request, "sref"), getUrlArg(request, "idev"))
		if event:
			# TODO: this shouldn't really be part of an event's data
			event['event']['recording_margin_before'] = config.recording.margin_before.value
			event['event']['recording_margin_after'] = config.recording.margin_after.value
			event['at'] = HASAUTOTIMER
			event['transcoding'] = TRANSCODING
			event['moviedb'] = config.OpenWebif.webcache.moviedb.value if config.OpenWebif.webcache.moviedb.value else EXT_EVENT_INFO_SOURCE
			event['extEventInfoProvider'] = extEventInfoProvider = getEventInfoProvider(event['moviedb'])
		return event

	def P_about(self, request):
		info = {}
		info["owiver"] = OPENWEBIFVER
		return {"info": info}

	def P_boxinfo(self, request):
		info = getInfo(self.session, need_fullinfo=True)
		type = getBoxType()

		if fileExists(getPublicPath("/images/boxes/" + type + ".png")):
			info["boximage"] = type + ".png"
		elif fileExists(getPublicPath("/images/boxes/" + type + ".jpg")):
			info["boximage"] = type + ".jpg"
		else:
			info["boximage"] = "unknown.png"
		return info

	# http://enigma2/ajax/epgpop?sstr=test&bouquetsonly=1
	def P_epgpop(self, request):
		events = []
		timers = []
		sref = getUrlArg(request, "sref")
		sstr = getUrlArg(request, "sstr")
		if sref != None:
			ev = getChannelEpg(sref)
			events = ev["events"]
		elif sstr != None:
			fulldesc = False
			if getUrlArg(request, "full") != None:
				fulldesc = True
			bouquetsonly = False
			if getUrlArg(request, "bouquetsonly") != None:
				bouquetsonly = True
			ev = getSearchEpg(sstr, None, fulldesc, bouquetsonly)
			events = sorted(ev["events"], key=lambda ev: ev['begin_timestamp'])
		at = False
		if len(events) > 0:
			t = getTimers(self.session)
			timers = t["timers"]
			at = HASAUTOTIMER
		if config.OpenWebif.webcache.theme.value:
			theme = config.OpenWebif.webcache.theme.value
		else:
			theme = 'original'
		moviedb = config.OpenWebif.webcache.moviedb.value if config.OpenWebif.webcache.moviedb.value else EXT_EVENT_INFO_SOURCE
		extEventInfoProvider = getEventInfoProvider(moviedb)

		return {"theme": theme, "events": events, "timers": timers, "at": at, "moviedb": moviedb, "extEventInfoProvider": extEventInfoProvider}

	# http://enigma2/ajax/epgdialog?sstr=test&bouquetsonly=1
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

		return {"box": box,
				"high_resolution": config.OpenWebif.webcache.screenshot_high_resolution.value,
				"refresh_auto": config.OpenWebif.webcache.screenshot_refresh_auto.value,
				"refresh_time": config.OpenWebif.webcache.screenshot_refresh_time.value
				}

	def P_movies(self, request):
		movies = getMovieList(request.args)
		movies['transcoding'] = TRANSCODING

		sorttype = config.OpenWebif.webcache.moviesort.value
		unsort = movies['movies']

		if sorttype == 'name':
			movies['movies'] = sorted(unsort, key=lambda k: k['eventname'])
		elif sorttype == 'named':
			movies['movies'] = sorted(unsort, key=lambda k: k['eventname'], reverse=True)
		elif sorttype == 'date':
			movies['movies'] = sorted(unsort, key=lambda k: k['recordingtime'])
		elif sorttype == 'dated':
			movies['movies'] = sorted(unsort, key=lambda k: k['recordingtime'], reverse=True)

		movies['sort'] = sorttype
		return movies

	def P_moviesearch(self, request):
		movies = getMovieSearchList(request.args)
		movies['transcoding'] = TRANSCODING

		sorttype = config.OpenWebif.webcache.moviesort.value
		unsort = movies['movies']

		if sorttype == 'name':
			movies['movies'] = sorted(unsort, key=lambda k: k['eventname'])
		elif sorttype == 'named':
			movies['movies'] = sorted(unsort, key=lambda k: k['eventname'], reverse=True)
		elif sorttype == 'date':
			movies['movies'] = sorted(unsort, key=lambda k: k['recordingtime'])
		elif sorttype == 'dated':
			movies['movies'] = sorted(unsort, key=lambda k: k['recordingtime'], reverse=True)

		movies['sort'] = sorttype
		return movies

	def P_timers(self, request):

		timers = getTimers(self.session)
		unsort = timers['timers']

		sorttype = getUrlArg(request, "sort")
		if sorttype == None:
			return timers

		if sorttype == 'name':
			timers['timers'] = sorted(unsort, key=lambda k: k['name'])
		elif sorttype == 'named':
			timers['timers'] = sorted(unsort, key=lambda k: k['name'], reverse=True)
		elif sorttype == 'date':
			timers['timers'] = sorted(unsort, key=lambda k: k['begin'])
		else:
			timers['timers'] = sorted(unsort, key=lambda k: k['begin'], reverse=True)
			sorttype = 'dated'

		timers['sort'] = sorttype
		return timers

	# http://enigma2/ajax/tvradio
	# (`classic` interface only)
	def P_tvradio(self, request):
		epgmode = getUrlArg(request, "epgmode", "tv")
		if epgmode not in ["tv", "radio"]:
			epgmode = "tv"
		return {"epgmode": epgmode}

	def P_config(self, request):
		section = getUrlArg(request, "section", "usage")
		return getConfigs(section)

	def P_settings(self, request):
		ret = {
			"result": True
		}
		ret['configsections'] = getConfigsSections()['sections']
		if config.OpenWebif.webcache.theme.value:
			if os.path.exists(getPublicPath('themes')):
				ret['themes'] = config.OpenWebif.webcache.theme.choices
			else:
				ret['themes'] = ['original', 'clear']
			ret['theme'] = config.OpenWebif.webcache.theme.value
		else:
			ret['themes'] = []
			ret['theme'] = 'original'
		if config.OpenWebif.webcache.moviedb.value:
			ret['moviedbs'] = config.OpenWebif.webcache.moviedb.choices
			ret['moviedb'] = config.OpenWebif.webcache.moviedb.value
		else:
			ret['moviedbs'] = []
			ret['moviedb'] = EXT_EVENT_INFO_SOURCE
		ret['zapstream'] = config.OpenWebif.webcache.zapstream.value
		ret['showpicons'] = config.OpenWebif.webcache.showpicons.value
		ret['showchanneldetails'] = config.OpenWebif.webcache.showchanneldetails.value
		ret['showiptvchannelsinselection'] = config.OpenWebif.webcache.showiptvchannelsinselection.value
		ret['screenshotchannelname'] = config.OpenWebif.webcache.screenshotchannelname.value
		ret['showallpackages'] = config.OpenWebif.webcache.showallpackages.value
		ret['allowipkupload'] = config.OpenWebif.allow_upload_ipk.value
		ret['smallremotes'] = [(x, _('%s Style') % x.capitalize()) for x in config.OpenWebif.webcache.smallremote.choices]
		ret['smallremote'] = config.OpenWebif.webcache.smallremote.value
		loc = getLocations()
		ret['locations'] = loc['locations']
		if os.path.exists(VIEWS_PATH + "/responsive"):
			ret['responsivedesign'] = config.OpenWebif.responsive_enabled.value
		return ret

	# http://enigma2/ajax/multiepg
	def P_multiepg(self, request):
		epgmode = getUrlArg(request, "epgmode", "tv")
		if epgmode not in ["tv", "radio"]:
			epgmode = "tv"

		bouq = getBouquets(epgmode)
		bref = getUrlArg(request, "bref")
		if bref == None:
			bref = bouq['bouquets'][0][0]
		endtime = 1440
		begintime = -1
		day = 0
		week = 0
		wadd = 0
		_week = getUrlArg(request, "week")
		if _week != None:
			try:
				week = int(_week)
				wadd = week * 7
			except ValueError:
				pass
		_day = getUrlArg(request, "day")
		if _day != None:
			try:
				day = int(_day)
				if day > 0 or wadd > 0:
					now = localtime()
					begintime = int(mktime((now.tm_year, now.tm_mon, now.tm_mday + day + wadd, 0, 0, 0, -1, -1, -1)))
			except ValueError:
				pass
		mode = 1
		if config.OpenWebif.webcache.mepgmode.value:
			try:
				mode = int(config.OpenWebif.webcache.mepgmode.value)
			except ValueError:
				pass
		epg = getMultiEpg(self, bref, begintime, endtime, mode)
		epg['bouquets'] = bouq['bouquets']
		epg['bref'] = bref
		epg['day'] = day
		epg['week'] = week
		epg['mode'] = mode
		epg['epgmode'] = epgmode
		return epg

	def P_epgr(self, request):
		ret = {}
		ret['showiptvchannelsinselection'] = config.OpenWebif.webcache.showiptvchannelsinselection.value
		return ret

	def P_at(self, request):
		ret = {}
		ret['hasVPS'] = 1 if HASVPS else 0
		ret['hasSeriesPlugin'] = 1 if HASSERIES else 0
		ret['test'] = 1 if HASAUTOTIMERTEST else 0
		ret['hasChange'] = 1 if HASAUTOTIMERCHANGE else 0
		ret['autoadjust'] = getInfo()['timerautoadjust']
		ret['searchTypes'] = ATSEARCHTYPES

		if config.OpenWebif.autotimer_regex_searchtype.value:
			ret['searchTypes']['regex'] = 0

		loc = getLocations()
		ret['locations'] = loc['locations']
		ret['showiptvchannelsinselection'] = config.OpenWebif.webcache.showiptvchannelsinselection.value
		return ret

	def P_webtv(self, request):
		streaming_port = int(config.OpenWebif.streamport.value)
		if config.OpenWebif.auth_for_streaming.value:
			session = GetSession()
			if session.GetAuth(request) is not None:
				auth = ':'.join(session.GetAuth(request)) + "@"
			else:
				auth = '-sid:' + str(session.GetSID(request)) + "@"
		else:
			auth = ''
		vxgenabled = False
		if fileExists(getPublicPath("/vxg/media_player.pexe")):
			vxgenabled = True
		transcoding = TRANSCODING
		transcoder_port = 0
		if transcoding:
			try:
				transcoder_port = int(config.plugins.transcodingsetup.port.value)
				if getMachineBuild() in ('inihdp', 'hd2400', 'et10000', 'et13000', 'sf5008', 'ew7356', 'formuler1tc', 'tiviaraplus', '8100s'):
					transcoder_port = int(config.OpenWebif.streamport.value)
			except Exception:
				transcoder_port = 0
		return {"transcoder_port": transcoder_port, "vxgenabled": vxgenabled, "auth": auth, "streaming_port": streaming_port}

	def P_editmovie(self, request):
		sref = getUrlArg(request, "sRef")
		title = ""
		description = ""
		tags = ""
		resulttext = ""
		result = False
		if sref:
			mi = getMovieInfo(sref, NewFormat=True)
			result = mi["result"]
			if result:
				title = mi["title"]
				if title:
					description = mi["description"]
					tags = mi["tags"]
				else:
					result = False
					resulttext = "meta file not found"
			else:
				resulttext = mi["resulttext"]
		return {"title": title, "description": description, "sref": sref, "result": result, "tags": tags, "resulttext": resulttext}

	def P_epgplayground(self, request):
		TV = 'tv'
		RADIO = 'radio'

		ret = {
			'tvBouquets': getBouquets(TV),
			'tvChannels': getAllServices(TV),
			'radioBouquets': getBouquets(RADIO),
			'radioChannels': getAllServices(RADIO),
		}
		return {'data': ret}
