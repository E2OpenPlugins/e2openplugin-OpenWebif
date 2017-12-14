# -*- coding: utf-8 -*-

##############################################################################
#                        2011-2017 E2OpenPlugins                             #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Plugins.Extensions.OpenWebif.__init__ import _

from Components.config import config

from models.info import getInfo, getCurrentTime , getStatusInfo, getFrontendStatus
from models.services import getCurrentService, getBouquets, getServices, getSubServices, getChannels, getSatellites, getBouquetEpg, getBouquetNowNextEpg, getServicesNowNextEpg, getSearchEpg, getChannelEpg, getNowNextEpg, getSearchSimilarEpg, getAllServices, getPlayableServices, getPlayableService, getParentalControlList, getEvent, loadEpg, saveEpg
from models.volume import getVolumeStatus, setVolumeUp, setVolumeDown, setVolumeMute, setVolume
from models.audiotrack import getAudioTracks, setAudioTrack
from models.control import zapService, remoteControl, setPowerState, getStandbyState
from models.locations import getLocations, getCurrentLocation, addLocation, removeLocation
from models.timers import getTimers, addTimer, addTimerByEventId, editTimer, removeTimer, toggleTimerStatus, cleanupTimer, writeTimerList, recordNow, tvbrowser, getSleepTimer, setSleepTimer, getPowerTimer, setPowerTimer, getVPSChannels
from models.message import sendMessage, getMessageAnswer
from models.movies import getMovieList, removeMovie, getMovieTags, moveMovie, renameMovie, getAllMovies
from models.config import getSettings, addCollapsedMenu, removeCollapsedMenu, setZapStream, saveConfig, getZapStream, setShowChPicon, getConfigs, getConfigsSections
from models.stream import getStream, getTS, getStreamSubservices, GetSession
from models.servicelist import reloadServicesLists
from models.mediaplayer import mediaPlayerAdd, mediaPlayerRemove, mediaPlayerPlay, mediaPlayerCommand, mediaPlayerCurrent, mediaPlayerList, mediaPlayerLoad, mediaPlayerSave, mediaPlayerFindFile
from models.plugins import reloadPlugins
from Screens.InfoBar import InfoBar

from fcntl import ioctl
from base import BaseController
from stream import StreamController
import re

def whoami(request):
	port = config.OpenWebif.port.value
	proto = 'http'
	if request.isSecure():
		port = config.OpenWebif.https_port.value
		proto = 'https'
	ourhost = request.getHeader('host')
	m = re.match('.+\:(\d+)$', ourhost)
	if m is not None:
		port = m.group(1)
	return {'proto':proto, 'port':port }

class WebController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path=path, session=session)
		self.putChild("stream", StreamController(session))

	def prePageLoad(self, request):
		request.setHeader("content-type", "text/xml")

	def testMandatoryArguments(self, request, keys):
		for key in keys:
			if key not in request.args.keys():
				return {
					"result": False,
					"message": _("Missing mandatory parameter '%s'") % key
				}

			if len(request.args[key][0]) == 0:
				return {
					"result": False,
					"message": _("The parameter '%s' can't be empty") % key
				}

		return None

	def P_tsstart(self, request):
		success = True
		try:
			InfoBar.instance.startTimeshift()
		except Exception, e:
			success = False
		return self.P_tstate(request,success)

#	TODO: improve after action / save , save+record , nothing
#	config.timeshift.favoriteSaveAction .... 
	def P_tsstop(self, request):
		success = True
		oldcheck = False
		try:
			if config.usage.check_timeshift.value:
				oldcheck = config.usage.check_timeshift.value
				# don't ask but also don't save
				config.usage.check_timeshift.value = False
				config.usage.check_timeshift.save()
			InfoBar.instance.stopTimeshift()
		except Exception, e:
			success = False
		if config.usage.check_timeshift.value:
			config.usage.check_timeshift.value = oldcheck
			config.usage.check_timeshift.save()
		return self.P_tstate(request,success)

	def P_tsstate(self, request, success = True):
		return {
			"state" : success,
			"timeshiftEnabled": InfoBar.instance.timeshiftEnabled()
		}

	def P_about(self, request):
		return {
			"info": getInfo(self.session, need_fullinfo = True),
			"service": getCurrentService(self.session)
		}

	def P_statusinfo(self, request):
		# we don't need to fill logs with this api (it's called too many times)
		self.suppresslog = True
		return getStatusInfo(self)

	def P_tunersignal(self, request):
		return getFrontendStatus(self.session)

	def P_vol(self, request):
		if "set" not in request.args.keys() or request.args["set"][0] == "state":
			return getVolumeStatus()
		elif request.args["set"][0] == "up":
			return setVolumeUp()
		elif request.args["set"][0] == "down":
			return setVolumeDown()
		elif request.args["set"][0] == "mute":
			return setVolumeMute()
		elif request.args["set"][0][:3] == "set":
			try:
				return setVolume(int(request.args["set"][0][3:]))
			except Exception, e:
				res = getVolumeStatus()
				res["result"] = False
				res["message"] = _("Wrong parameter format 'set=%s'. Use set=set15 ") % request.args["set"][0]
				return res

		res = getVolumeStatus()
		res["result"] = False
		res["message"] = _("Unknown Volume command %s") % request.args["set"][0]
		return res

	def P_getaudiotracks(self, request):
		return getAudioTracks(self.session)

	def P_selectaudiotrack(self, request):
		try:
			id = int(request.args["id"][0])
		except Exception, e:
			id = -1

		return setAudioTrack(self.session, id)

	def P_zap(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res

		if "title" in request.args.keys():
			return zapService(self.session, request.args["sRef"][0], request.args["title"][0])

		return zapService(self.session, request.args["sRef"][0])

	def P_remotecontrol(self, request):
		res = self.testMandatoryArguments(request, ["command"])
		if res:
			return res

		id = -1
		try:
			id = int(request.args["command"][0])
		except Exception, e:
			return {
				"result": False,
				"message": _("The parameter 'command' must be a number")
			}

		type = ""
		rcu = ""
		if "type" in request.args.keys():
			type = request.args["type"][0]

		if "rcu" in request.args.keys():
			rcu = request.args["rcu"][0]

		return remoteControl(id, type, rcu)

	def P_powerstate(self, request):
		if "shift" in request.args.keys():
			self.P_set_powerup_without_waking_tv(request)
		if "newstate" in request.args.keys():
			return setPowerState(self.session, request.args["newstate"][0])
		return getStandbyState(self.session)

	def P_supports_powerup_without_waking_tv(self, request):
		try:
			#returns 'True' if the image supports the function "Power on without TV":
			f = open("/tmp/powerup_without_waking_tv.txt", "r") # nosec
			powerupWithoutWakingTv = f.read()
			f.close()
			if ((powerupWithoutWakingTv == 'True') or (powerupWithoutWakingTv == 'False')):
				return True
			else:
				return False
		except:
			return False

	def P_set_powerup_without_waking_tv(self, request):
		if self.P_supports_powerup_without_waking_tv(request):
			try:
				#write "True" to file so that the box will power on ONCE skipping the HDMI-CEC communication:
				f = open("/tmp/powerup_without_waking_tv.txt", "w") # nosec
				f.write('True')
				f.close()
				return True
			except:
				return False
		else:
			return False

	def P_getlocations(self, request):
		return getLocations()

	def P_getcurrlocation(self, request):
		return getCurrentLocation()

	def P_getallservices(self, request):
		self.isGZ=True
		type = "tv"
		if "type" in request.args.keys():
			type = "radio"
		bouquets = getAllServices(type)
		if "renameserviceforxmbc" in request.args.keys():
			for bouquet in bouquets["services"]:
				for service in bouquet["subservices"]:
					if not int(service["servicereference"].split(":")[1]) & 64:
						service["servicename"] = "%d - %s" % (service["pos"], service["servicename"])
			return bouquets
		return bouquets

	def P_getservices(self, request):
		if "sRef" in request.args.keys():
			sRef = request.args["sRef"][0]
		else:
			sRef = ""
		if "hidden" in request.args.keys():
			hidden = request.args["hidden"][0] == "1"
		else:
			hidden = False
		self.isGZ=True
		return getServices(sRef, True, hidden)

	def P_servicesm3u(self, request):
		if "bRef" in request.args.keys():
			bRef = request.args["bRef"][0]
		else:
			bRef = ""

		request.setHeader('Content-Type', 'application/x-mpegurl')
		services = getServices(bRef,False)
		if config.OpenWebif.auth_for_streaming.value:
			session = GetSession()
			if session.GetAuth(request) is not None:
				auth = ':'.join(session.GetAuth(request)) + "@"
			else:
				auth = '-sid:' + str(session.GetSID(request)) + "@"
		else:
			auth=''
		services["host"] = "%s:8001" % request.getRequestHostname()
		services["auth"] = auth
		return services

	def P_subservices(self, request):
		return getSubServices(self.session)

	def P_parentcontrollist(self, request):
		return getParentalControlList()

	def P_servicelistplayable(self, request):
		sRef = ""
		if "sRef" in request.args.keys():
			sRef = request.args["sRef"][0]

		sRefPlaying = ""
		if "sRefPlaying" in request.args.keys():
			sRefPlaying = request.args["sRefPlaying"][0]
		self.isGZ=True
		return getPlayableServices(sRef, sRefPlaying)

	def P_serviceplayable(self, request):
		sRef = ""
		if "sRef" in request.args.keys():
			sRef = request.args["sRef"][0]

		sRefPlaying = ""
		if "sRefPlaying" in request.args.keys():
			sRefPlaying = request.args["sRefPlaying"][0]

		return getPlayableService(sRef, sRefPlaying)

	def P_addlocation(self, request):
		res = self.testMandatoryArguments(request, ["dirname"])
		if res:
			return res

		create = False
		if "createFolder" in request.args.keys():
			create = request.args["createFolder"][0] == "1"

		return addLocation(request.args["dirname"][0], create)

	def P_removelocation(self, request):
		res = self.testMandatoryArguments(request, ["dirname"])
		if res:
			return res

		remove = False
		if "removeFolder" in request.args.keys():
			remove = request.args["removeFolder"][0] == "1"

		return removeLocation(request.args["dirname"][0],remove)

	def P_message(self, request):
		res = self.testMandatoryArguments(request, ["text", "type"])
		if res:
			return res

		try:
			ttype = int(request.args["type"][0])
		except ValueError:
			return {
				"result": False,
				"message": _("type %s is not a number") % request.args["type"][0]
			}

		timeout = -1
		if "timeout" in request.args.keys():
			try:
				timeout = int(request.args["timeout"][0])
			except ValueError:
				pass

		return sendMessage(self.session, request.args["text"][0], ttype, timeout)

	def P_messageanswer(self, request):
		return getMessageAnswer()

	def P_movielist(self, request):
		self.isGZ=True
		if self.isJson:
			request.setHeader("content-type", "application/json; charset=utf-8")
		return getMovieList(request.args)
	
	def P_fullmovielist(self, request):
		self.isGZ=True
		return getAllMovies()

	def P_movielisthtml(self, request):
		request.setHeader("content-type", "text/html")
		return getMovieList(request.args)

	def P_movielistm3u(self, request):
		request.setHeader('Content-Type', 'application/x-mpegurl')
		movielist = getMovieList(request.args)
		movielist["host"] = "%s://%s:%s" % (whoami(request)['proto'], request.getRequestHostname(), whoami(request)['port'])
		return movielist

	def P_movielistrss(self, request):
		movielist = getMovieList(request.args)
		movielist["host"] = "%s://%s:%s" % (whoami(request)['proto'], request.getRequestHostname(), whoami(request)['port'])
		return movielist

	def P_moviedelete(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		force = False
		if "force" in request.args.keys():
			force = True
		return removeMovie(self.session, request.args["sRef"][0], force)

	def P_moviemove(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		res = self.testMandatoryArguments(request, ["dirname"])
		if res:
			return res

		return moveMovie(self.session, request.args["sRef"][0],request.args["dirname"][0])

	def P_movierename(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		res = self.testMandatoryArguments(request, ["newname"])
		if res:
			return res

		return renameMovie(self.session, request.args["sRef"][0],request.args["newname"][0])

	def P_movietags(self, request):
		_add = None
		_del = None
		_sref = None
		if "add" in request.args.keys():
			_add = request.args["add"][0]
		if "del" in request.args.keys():
			_del = request.args["del"][0]
		if "sref" in request.args.keys():
			_sref = request.args["sref"][0]
		return getMovieTags(_sref,_add,_del)

	# a duplicate api ??
	def P_gettags(self, request):
		return getMovieTags()

# VPS Plugin
	def vpsparams(self, request):
		vpsplugin_enabled = None
		if "vpsplugin_enabled" in request.args:
			vpsplugin_enabled = True if request.args["vpsplugin_enabled"][0] == '1' else False
		vpsplugin_overwrite = None
		if "vpsplugin_overwrite" in request.args:
			vpsplugin_overwrite = True if request.args["vpsplugin_overwrite"][0] == '1' else False
		vpsplugin_time = None
		if "vpsplugin_time" in request.args:
			vpsplugin_time = int(float(request.args["vpsplugin_time"][0]))
			if vpsplugin_time == -1:
				vpsplugin_time = None
		# partnerbox:
		if "vps_pbox" in request.args:
			vpsplugin_enabled = None
			vpsplugin_overwrite = None
			mode = request.args["vps_pbox"][0]
			if "yes_safe" in mode:
				vpsplugin_enabled = True
			elif "yes" in mode:
				vpsplugin_enabled = True
				vpsplugin_overwrite = True
		return { 
			"vpsplugin_time":vpsplugin_time,
			"vpsplugin_overwrite":vpsplugin_overwrite,
			"vpsplugin_enabled":vpsplugin_enabled
			}

	def P_timerlist(self, request):
		ret = getTimers(self.session)
		ret["locations"] = config.movielist.videodirs.value
		self.isGZ=True
		return ret

	def P_timeradd(self, request):
		res = self.testMandatoryArguments(request, ["sRef", "begin", "end", "name"])
		if res:
			return res

		disabled = False
		if "disabled" in request.args.keys():
			disabled = request.args["disabled"][0] == "1"

		justplay = False
		if "justplay" in request.args.keys():
			justplay = request.args["justplay"][0] == "1"

		afterevent = 3
		if "afterevent" in request.args.keys() and request.args["afterevent"][0] in ["1", "2", "3"]:
			afterevent = int(request.args["afterevent"][0])

		dirname = None
		if "dirname" in request.args.keys() and len(request.args["dirname"][0]) > 0:
			dirname = request.args["dirname"][0]

		tags = []
		if "tags" in request.args.keys():
			tags = request.args["tags"][0].split(' ')

		repeated = 0
		if "repeated" in request.args.keys():
			repeated = int(request.args["repeated"][0])

		description = ""
		if "description" in request.args.keys():
			description = request.args["description"][0]

		eit = 0
		if "eit" in request.args.keys() and type(request.args["eit"][0]) is int:
			eventid = request.args["eit"][0]
		else:
			from enigma import eEPGCache, eServiceReference
			queryTime = int(request.args["begin"][0]) + (int(request.args["end"][0]) - int(request.args["begin"][0])) / 2
			event = eEPGCache.getInstance().lookupEventTime(eServiceReference(request.args["sRef"][0]), queryTime)
			eventid = event and event.getEventId()
		if eventid is not None:
			eit = int(eventid)

		always_zap = -1
		if "always_zap" in request.args.keys():
			always_zap = int(request.args["always_zap"][0])

		return addTimer(
			self.session,
			request.args["sRef"][0],
			request.args["begin"][0],
			request.args["end"][0],
			request.args["name"][0],
			description,
			disabled,
			justplay,
			afterevent,
			dirname,
			tags,
			repeated,
			self.vpsparams(request),
			None,
			eit,
			always_zap
		)

	def P_timeraddbyeventid(self, request):
		res = self.testMandatoryArguments(request, ["sRef", "eventid"])
		if res:
			return res

		justplay = False
		if "justplay" in request.args.keys():
			justplay = request.args["justplay"][0] == "1"

		dirname = None
		if "dirname" in request.args.keys() and len(request.args["dirname"][0]) > 0:
			dirname = request.args["dirname"][0]

		tags = []
		if "tags" in request.args.keys():
			tags = request.args["tags"][0].split(' ')

		try:
			eventid = int(request.args["eventid"][0])
		except Exception, e:
			return {
				"result": False,
				"message": "The parameter 'eventid' must be a number"
			}

		always_zap = -1
		if "always_zap" in request.args.keys():
			always_zap = int(request.args["always_zap"][0])

		return addTimerByEventId(
			self.session,
			eventid,
			request.args["sRef"][0],
			justplay,
			dirname,
			tags,
			self.vpsparams(request),
			always_zap
		)

	def P_timerchange(self, request):
		res = self.testMandatoryArguments(request, ["sRef", "begin", "end", "name", "channelOld", "beginOld", "endOld"])
		if res:
			return res

		disabled = False
		if "disabled" in request.args.keys():
			disabled = request.args["disabled"][0] == "1"

		justplay = False
		if "justplay" in request.args.keys():
			justplay = request.args["justplay"][0] == "1"

		afterevent = 3
		if "afterevent" in request.args.keys() and request.args["afterevent"][0] in ["0", "1", "2", "3"]:
			afterevent = int(request.args["afterevent"][0])

		dirname = None
		if "dirname" in request.args.keys() and len(request.args["dirname"][0]) > 0:
			dirname = request.args["dirname"][0]

		tags = []
		if "tags" in request.args.keys():
			tags = request.args["tags"][0].split(' ')

		repeated = 0
		if "repeated" in request.args.keys():
			repeated = int(request.args["repeated"][0])

		description = ""
		if "description" in request.args.keys():
			description = request.args["description"][0]

		try:
			beginOld = int(request.args["beginOld"][0])
		except Exception, e:
			return {
				"result": False,
				"message": "The parameter 'beginOld' must be a number"
			}

		try:
			endOld = int(request.args["endOld"][0])
		except Exception, e:
			return {
				"result": False,
				"message": "The parameter 'endOld' must be a number"
			}

		always_zap = -1
		if "always_zap" in request.args.keys():
			always_zap = int(request.args["always_zap"][0])

		return editTimer(
			self.session,
			request.args["sRef"][0],
			request.args["begin"][0],
			request.args["end"][0],
			request.args["name"][0],
			description,
			disabled,
			justplay,
			afterevent,
			dirname,
			tags,
			repeated,
			request.args["channelOld"][0],
			beginOld,
			endOld,
			self.vpsparams(request),
			always_zap
		)

	def P_timertogglestatus(self, request):
		res = self.testMandatoryArguments(request, ["sRef", "begin", "end"])
		if res:
			return res
		try:
			begin = int(request.args["begin"][0])
		except Exception, e:
			return {
				"result": False,
				"message": "The parameter 'begin' must be a number"
			}

		try:
			end = int(request.args["end"][0])
		except Exception, e:
			return {
				"result": False,
				"message": "The parameter 'end' must be a number"
			}

		return toggleTimerStatus(self.session, request.args["sRef"][0], begin, end)

	def P_timerdelete(self, request):
		res = self.testMandatoryArguments(request, ["sRef", "begin", "end"])
		if res:
			return res

		try:
			begin = int(request.args["begin"][0])
		except Exception, e:
			return {
				"result": False,
				"message": "The parameter 'begin' must be a number"
			}

		try:
			end = int(request.args["end"][0])
		except Exception, e:
			return {
				"result": False,
				"message": "The parameter 'end' must be a number"
			}

		return removeTimer(self.session, request.args["sRef"][0], begin, end)

	def P_timercleanup(self, request):
		return cleanupTimer(self.session)

	def P_timerlistwrite(self, request):
		return writeTimerList(self.session)

	def P_vpschannels(self, request):
		return getVPSChannels(self.session)

	def P_recordnow(self, request):
		infinite = False
		if "undefinitely" in request.args.keys() or "infinite" in request.args.keys():
			infinite = True
		return recordNow(self.session, infinite)

	def P_currenttime(self, request):
		return getCurrentTime()

	def P_deviceinfo(self, request):
		return getInfo(session=self.session, need_fullinfo=True)

	def P_getipv6(self, request):
		request.setHeader("content-type", "text/html")
		firstpublic = ''
		info = getInfo()['ifaces']
		for iface in info:
			public = iface['firstpublic']
			if public is not None:
				firstpublic = public
				break

		return {
			"firstpublic": firstpublic
		}

	def P_epgbouquet(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res

		begintime = -1
		if "time" in request.args.keys():
			try:
				begintime = int(request.args["time"][0])
			except ValueError:
				pass
		self.isGZ=True
		return getBouquetEpg(request.args["bRef"][0], begintime)

	def P_epgmulti(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res

		begintime = -1
		if "time" in request.args.keys():
			try:
				begintime = int(request.args["time"][0])
			except ValueError:
				pass

		endtime = -1
		if "endTime" in request.args.keys():
			try:
				endtime = int(request.args["endTime"][0])
			except ValueError:
				pass
		self.isGZ=True
		return getBouquetEpg(request.args["bRef"][0], begintime, endtime)

	def P_epgnow(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
		self.isGZ=True
		return getBouquetNowNextEpg(request.args["bRef"][0], 0)

	def P_epgnext(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
		self.isGZ=True
		return getBouquetNowNextEpg(request.args["bRef"][0], 1)

	def P_epgnownext(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
		self.isGZ=True
		info = getCurrentService(self.session)
		ret = getBouquetNowNextEpg(request.args["bRef"][0], -1)
		ret["info"]=info
		return ret

	def P_epgservicelistnownext(self, request):
		res = self.testMandatoryArguments(request, ["sList"])
		if res:
			return res
		self.isGZ=True
		ret = getServicesNowNextEpg(request.args["sList"][0])
		return ret

	def P_epgsearch(self, request):
		self.isGZ=True
		if "search" in request.args.keys():
			endtime = None
			if "endtime" in request.args.keys():
				try:
					endtime = int(request.args["endtime"][0])
				except ValueError:
					pass
			fulldesc=False
			if "full" in request.args.keys():
				fulldesc=True
			return getSearchEpg(request.args["search"][0], endtime,fulldesc)
		else:
			res = self.testMandatoryArguments(request, ["sref", "eventid"])
			if res:
				return res
			service_reference = request.args["sref"][0]
			item_id = 0
			try:
				item_id = int(request.args["eventid"][0])
			except ValueError:
				pass
			return getEvent(service_reference,item_id)

	def P_epgsearchrss(self, request):
		res = self.testMandatoryArguments(request, ["search"])
		if res:
			return res

		ret = getSearchEpg(request.args["search"][0])
		ret["title"] = "EPG Search '%s'" % request.args["search"][0]
		ret["generator"] = "OpenWebif"
		ret["description"] = "%d result for '%s'" % (len(ret["events"]), request.args["search"][0])
		return ret

	def P_epgservice(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res

		begintime = -1
		if "time" in request.args.keys():
			try:
				begintime = int(request.args["time"][0])
			except ValueError:
				pass

		endtime = -1
		if "endTime" in request.args.keys():
			try:
				endtime = int(request.args["endTime"][0])
			except ValueError:
				pass
		self.isGZ=True
		return getChannelEpg(request.args["sRef"][0], begintime, endtime)

	def P_epgservicenow(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		return getNowNextEpg(request.args["sRef"][0], 0)

	def P_epgservicenext(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		return getNowNextEpg(request.args["sRef"][0], 1)

	def P_epgsimilar(self, request):
		res = self.testMandatoryArguments(request, ["sRef", "eventid"])
		if res:
			return res

		try:
			eventid = int(request.args["eventid"][0])
		except ValueError:
			return {
				"result": False,
				"message": "The parameter 'eventid' must be a number"
			}

		return getSearchSimilarEpg(request.args["sRef"][0], eventid)

	def P_event(self, request):
		event = getEvent(request.args["sref"][0], request.args["idev"][0])
		event['event']['recording_margin_before'] = config.recording.margin_before.value
		event['event']['recording_margin_after'] = config.recording.margin_after.value
		return event
	
	def P_getcurrent(self, request):
		info = getCurrentService(self.session)
		now = getNowNextEpg(info["ref"], 0)
		if len(now["events"]) > 0:
			now = now["events"][0]
			now["provider"] = info["provider"]
		else:
			now = {
				"id": 0,
				"begin_timestamp": 0,
				"duration_sec": 0,
				"title": "",
				"shortdesc": "",
				"longdesc": "",
				"sref": "",
				"sname": "",
				"now_timestamp": 0,
				"remaining": 0,
				"provider": ""
			}
		next = getNowNextEpg(info["ref"], 1)
		if len(next["events"]) > 0:
			next = next["events"][0]
			next["provider"] = info["provider"]
		else:
			next = {
				"id": 0,
				"begin_timestamp": 0,
				"duration_sec": 0,
				"title": "",
				"shortdesc": "",
				"longdesc": "",
				"sref": "",
				"sname": "",
				"now_timestamp": 0,
				"remaining": 0,
				"provider": ""
			}
		# replace EPG NOW with Movie info
		mnow = now
		if mnow["sref"].startswith('1:0:0:0:0:0:0:0:0:0:/'):
			try:
				service = self.session.nav.getCurrentService()
				minfo = service and service.info()
				movie = minfo and minfo.getEvent(0)
				if movie and minfo:
					mnow["title"] = movie.getEventName()
					mnow["shortdesc"] = movie.getShortDescription()
					mnow["longdesc"] = movie.getExtendedDescription()
					mnow["begin_timestamp"] = movie.getBeginTime()
					mnow["duration_sec"] = movie.getDuration()
					mnow["remaining"] = movie.getDuration()
					mnow["id"] = movie.getEventId()
			except Exception, e:
				mnow = now
		elif mnow["sref"] == '':
			serviceref = self.session.nav.getCurrentlyPlayingServiceReference()
			if serviceref is not None:
				try:
					if serviceref.toString().startswith('4097:0:0:0:0:0:0:0:0:0:/'):
						from enigma import eServiceCenter
						serviceHandler = eServiceCenter.getInstance()
						sinfo = serviceHandler.info(serviceref)
						if sinfo:
							mnow["title"] = sinfo.getName(serviceref)
						servicepath = serviceref and serviceref.getPath()
						if servicepath and servicepath.startswith("/"):
							mnow["filename"] = servicepath
							mnow["sref"] = serviceref.toString()
				except Exception, e: # nosec
					pass
		return {
			"info": info,
			"now": mnow,
			"next": next
		}

	def P_getpid(self, request):
		request.setHeader("content-type", "text/html")
		info = getCurrentService(self.session)
		return {
			"ppid": "%x" % info["pmtpid"],
			"vpid": "%x" % info["vpid"],
			"apid": "%x" % info["apid"],
			"host": request.getRequestHostname()
		}

	def P_collapsemenu(self, request):
		res = self.testMandatoryArguments(request, ["name"])
		if res:
			return res
		return addCollapsedMenu(request.args["name"][0])

	def P_expandmenu(self, request):
		res = self.testMandatoryArguments(request, ["name"])
		if res:
			return res
		return removeCollapsedMenu(request.args["name"][0])

	def P_zapstream(self, request):
		res = self.testMandatoryArguments(request, ["checked"])
		if res:
			return res
		return setZapStream(request.args["checked"][0] == "true")

	def P_showchannelpicon(self, request):
		res = self.testMandatoryArguments(request, ["checked"])
		if res:
			return res
		return setShowChPicon(request.args["checked"][0] == "true")

	def P_streamm3u(self,request):
		self.isCustom = True
		if getZapStream()['zapstream']:
			if "ref" in request.args:
				zapService(self.session, request.args["ref"][0], request.args["name"][0], stream=True)
		return getStream(self.session,request,"stream.m3u")

	def P_tsm3u(self,request):
		self.isCustom = True
		return getTS(self.session,request)

	def P_videom3u(self,request):
		self.isCustom = True
		return getStream(self.session,request,"video.m3u")

	def P_streamcurrentm3u(self,request):
		self.isCustom = True
		return getStream(self.session,request,"streamcurrent.m3u")

	def P_streamsubservices(self, request):
		return getStreamSubservices(self.session,request)

	def P_servicelistreload(self, request):
		return reloadServicesLists(self.session,request)

	def P_tvbrowser(self, request):
		return tvbrowser(self.session, request)

	def P_saveconfig(self, request):
		if request.method == b'POST':
			res = self.testMandatoryArguments(request, ["key", "value"])
			if res:
				return res
			key = request.args["key"][0]
			value = request.args["value"][0]
			return saveConfig(key, value)
		return {"result": False}

	def P_mediaplayeradd(self, request):
		res = self.testMandatoryArguments(request, ["file"])
		if res:
			return res
		return mediaPlayerAdd(self.session, request.args["file"][0])

	def P_mediaplayerplay(self, request):
		res = self.testMandatoryArguments(request, ["file"])
		if res:
			return res
		root = ""
		if "root" in request.args.keys():
			root = request.args["root"][0]
		return mediaPlayerPlay(self.session, request.args["file"][0], root)

	def P_mediaplayercmd(self, request):
		res = self.testMandatoryArguments(request, ["command"])
		if res:
			return res
		return mediaPlayerCommand(self.session, request.args["command"][0])

	def P_mediaplayercurrent(self, request):
		return mediaPlayerCurrent(self.session)

	def P_mediaplayerfindfile(self, request):
		path = "/media/"
		if "path" in request.args.keys():
			path = request.args["path"][0]
		pattern = "*.*"
		if "pattern" in request.args.keys():
			pattern = request.args["pattern"][0]
		return mediaPlayerFindFile(self.session, path, pattern)

	def P_mediaplayerlist(self, request):
		path = ""
		if "path" in request.args.keys():
			path = request.args["path"][0]

		types = ""
		if "types" in request.args.keys():
			types = request.args["types"][0]

		return mediaPlayerList(self.session, path, types)

	def P_mediaplayerremove(self, request):
		res = self.testMandatoryArguments(request, ["file"])
		if res:
			return res
		return mediaPlayerRemove(self.session, request.args["file"][0])

	def P_mediaplayerload(self, request):
		res = self.testMandatoryArguments(request, ["filename"])
		if res:
			return res
		return mediaPlayerLoad(self.session, request.args["filename"][0])

	def P_mediaplayerwrite(self, request):
		res = self.testMandatoryArguments(request, ["filename"])
		if res:
			return res
		return mediaPlayerSave(self.session, request.args["filename"][0])

	def P_pluginlistread(self, request):
		return reloadPlugins()

	def P_restarttwisted(self, request):
		from ..httpserver import HttpdRestart
		HttpdRestart(self.session)
		return ""

	def P_powertimer(self, request):
		if len(request.args):
			res = self.testMandatoryArguments(request, ["start","end","timertype", "repeated", "afterevent", "disabled"])
			if res:
				return res
			return setPowerTimer(self.session, request)
		else:
			return getPowerTimer(self.session)

	def P_sleeptimer(self, request):
		cmd = "get"
		if "cmd" in request.args.keys():
			cmd = request.args["cmd"][0]

		if cmd == "get":
			return getSleepTimer(self.session)

		time = None
		if "time" in request.args.keys():
			ttime = request.args["time"][0]
			try:
				time = int(ttime)
				if time > 999:
					time = 999
				elif time < 0:
					time = 0
			except ValueError:
				pass

		action = "standby"
		if "action" in request.args.keys():
			action = request.args["action"][0]

		enabled = None
		if "enabled" in request.args.keys():
			if request.args["enabled"][0] == "True":
				enabled = True
			elif request.args["enabled"][0] == "False":
				enabled = False

		ret = getSleepTimer(self.session)

		if cmd != "set":
			ret["message"] = "ERROR: Obligatory parameter 'cmd' [get,set] has unspecified value '%s'" % cmd
			return ret

		if time == None and enabled == True:	# it's used only if the timer is enabled
			ret["message"] = "ERROR: Obligatory parameter 'time' [0-999] is missing"
			return ret

		if enabled == None:
			ret["message"] = "Obligatory parameter 'enabled' [True,False] is missing"
			return ret

		return setSleepTimer(self.session, time, action, enabled)

	def P_external(self, request):
		try:
			from Plugins.Extensions.WebInterface.WebChilds.Toplevel import loaded_plugins
			return {
				"plugins": loaded_plugins
			}
		except Exception, e:
			return {
				"plugins": []
			}

	def P_settings(self, request):
		return getSettings()

	def P_bouquets(self, request):
		stype = "tv"
		if "stype" in request.args.keys():
			stype = request.args["stype"][0]
		return getBouquets(stype)

	def P_epgmultigz(self, request):
		return self.P_epgmulti(request)

	def P_getsatellites(self, request):
		stype = "tv"
		if "stype" in request.args.keys():
			stype = request.args["stype"][0]
		return getSatellites(stype)

	def P_saveepg(self, request):
		return saveEpg()

	def P_loadepg(self, request):
		return loadEpg()

	def P_getsubtitles(self, request):
		service = self.session.nav.getCurrentService()
		ret = { "subtitlelist": [], "result": False }
		subtitle = service and service.subtitle()
		subtitlelist = subtitle and subtitle.getSubtitleList()
		if subtitlelist:
			for i in range(0, len(subtitlelist)):
				ret["result"] = True
				subt = subtitlelist[i]
				ret["subtitlelist"].append({
					"type": subt[0],
					"pid": subt[1],
					"page_nr": subt[2],
					"mag_nr": subt[3],
					"lang": subt[4]
				})
		return ret

	def P_settheme(self, request):
		if "theme" in request.args.keys():
			theme = request.args["theme"][0]
			config.OpenWebif.webcache.theme.value = theme
			config.OpenWebif.webcache.theme.save()
		return {}

	def P_setmoviesort(self, request):
		if "nsort" in request.args.keys():
			nsort = request.args["nsort"][0]
			config.OpenWebif.webcache.moviesort.value = nsort
			config.OpenWebif.webcache.moviesort.save()
		return {}

	def P_css(self, request):
		request.setHeader("content-type", "text/css")
		ret = {}
		theme = 'original'
		if config.OpenWebif.webcache.theme.value:
			theme = config.OpenWebif.webcache.theme.value
		ret['theme'] = theme
		return ret

	def P_setmepgmode(self, request):
		if "mode" in request.args.keys():
			try:
				config.OpenWebif.webcache.mepgmode.value = int(request.args["mode"][0])
				config.OpenWebif.webcache.mepgmode.save()
			except ValueError:
				pass
		return {}
	
	def P_config(self, request):
		
		def RepresentsInt(s):
			try: 
				int(s)
				return True
			except ValueError:
				return False
		
		setcs = getConfigsSections()
		if request.path == '/api/config':
			return setcs
		else:
			try:
				sect = request.path.split('/')
				if len(sect) == 4:
					cfgs = getConfigs(sect[3])
					resultcfgs = []
					for cfg in cfgs['configs']:
						min = -1
						kv=[]
						data = cfg['data']
						if data.has_key('choices'):
							for ch in data['choices']:
								if type(ch).__name__ == 'tuple' and len(ch)==2 and ch[0] == ch[1]:
									if RepresentsInt(ch[0]):
										kv.append(int(ch[0]))
									else:
										kv=[]
										break
								else:
									kv=[]
									break
						
						if len(kv) > 1:
							if kv[1] == (kv[0]+1):
								min = kv[0]
								max = kv[len(kv)-1]

						if min > -1:
							data['min'] = min
							data['max'] = max
							del data['choices']
							cfg['data'] = data
							resultcfgs.append(cfg)
						else:
							resultcfgs.append(cfg)
					return { 'configs' : resultcfgs }
			except Exception, e:
				#TODO show exception
				pass
		return {}

class ApiController(WebController):
	def __init__(self, session, path = ""):
		WebController.__init__(self, session, path)

	def prePageLoad(self, request):
		self.isJson = True

from Plugins.Extensions.OpenWebif.vtiaddon import expand_basecontroller
