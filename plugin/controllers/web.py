# -*- coding: utf-8 -*-

##############################################################################
#                        2011-2017 E2OpenPlugins                             #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Components.config import config as comp_config
from models.info import getInfo, getCurrentTime, getStatusInfo, getFrontendStatus, testPipStatus
from models.services import getCurrentService, getBouquets, getServices, getSubServices, getSatellites, getBouquetEpg, getBouquetNowNextEpg, getServicesNowNextEpg, getSearchEpg, getChannelEpg, getNowNextEpg, getSearchSimilarEpg, getAllServices, getPlayableServices, getPlayableService, getParentalControlList, getEvent, loadEpg, saveEpg
from models.volume import getVolumeStatus, setVolumeUp, setVolumeDown, setVolumeMute, setVolume
from models.audiotrack import getAudioTracks, setAudioTrack
from models.control import zapService, remoteControl, setPowerState, getStandbyState
from models.locations import getLocations, getCurrentLocation, addLocation, removeLocation
from models.timers import getTimers, addTimer, addTimerByEventId, editTimer, removeTimer, toggleTimerStatus, cleanupTimer, writeTimerList, recordNow, tvbrowser, getSleepTimer, setSleepTimer, getPowerTimer, setPowerTimer, getVPSChannels
from models.message import sendMessage, getMessageAnswer
from models.movies import getMovieList, removeMovie, getMovieInfo, moveMovie, renameMovie, getAllMovies
from models.config import getSettings, addCollapsedMenu, removeCollapsedMenu, saveConfig, getConfigs, getConfigsSections, getUtcOffset
from models.stream import getStream, getTS, getStreamSubservices, GetSession
from models.servicelist import reloadServicesLists
from models.mediaplayer import mediaPlayerAdd, mediaPlayerRemove, mediaPlayerPlay, mediaPlayerCommand, mediaPlayerCurrent, mediaPlayerList, mediaPlayerLoad, mediaPlayerSave, mediaPlayerFindFile
from models.plugins import reloadPlugins
from Screens.InfoBar import InfoBar

from i18n import _
from base import BaseController
from stream import StreamController
import re


def whoami(request):
	port = comp_config.OpenWebif.port.value
	proto = 'http'
	if request.isSecure():
		port = comp_config.OpenWebif.https_port.value
		proto = 'https'
	ourhost = request.getHeader('host')
	m = re.match('.+\:(\d+)$', ourhost)
	if m is not None:
		port = m.group(1)
	return {'proto': proto, 'port': port}


class WebController(BaseController):
	"""
	HTTP Web Controller

	Fork of *Enigma2 WebInterface API* as described in e.g.
	https://dream.reichholf.net/e2web/.
	"""
	def __init__(self, session, path=""):
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
		"""
		Request handler for the `tsstart` endpoint.
		Start timeshift (?).

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		success = True
		try:
			InfoBar.instance.startTimeshift()
		except Exception:  # noqa: E722
			success = False
		return self.P_tstate(request, success)

	def P_tsstop(self, request):
		"""
		Request handler for the `tsstop` endpoint.
		Stop timeshift (?).

		.. note::

			Not available in *Enigma2 WebInterface API*.

		*TODO: improve after action / save , save+record , nothing
		config.timeshift.favoriteSaveAction ....*

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		success = True
		oldcheck = False
		try:
			if comp_config.usage.check_timeshift.value:
				oldcheck = comp_config.usage.check_timeshift.value
				# don't ask but also don't save
				comp_config.usage.check_timeshift.value = False
				comp_config.usage.check_timeshift.save()
			InfoBar.instance.stopTimeshift()
		except Exception:  # noqa: E722
			success = False
		if comp_config.usage.check_timeshift.value:
			comp_config.usage.check_timeshift.value = oldcheck
			comp_config.usage.check_timeshift.save()
		return self.P_tstate(request, success)

	def P_tsstate(self, request, success=True):
		"""
		Request handler for the `tsstate` endpoint.
		Retrieve timeshift status(?).

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return {
			"state": success,
			"timeshiftEnabled": InfoBar.instance.timeshiftEnabled()
		}

	def P_about(self, request):
		"""
		Request handler for the `about` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#about

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return {
			"info": getInfo(self.session, need_fullinfo=True),
			"service": getCurrentService(self.session)
		}

	def P_statusinfo(self, request):
		# we don't need to fill logs with this api (it's called too many times)
		self.suppresslog = True
		return getStatusInfo(self)

	def P_pipinfo(self, request):
		return testPipStatus(self)

	def P_tunersignal(self, request):
		"""
		Request handler for the `tunersignal` endpoint.
		Get tuner signal status(?)

		.. seealso::

			Probably https://dream.reichholf.net/e2web/#signal

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/signal
		"""
		return getFrontendStatus(self.session)

	def P_vol(self, request):
		"""
		Request handler for the `vol` endpoint.
		Get/Set current volume setting.

		.. seealso::

			https://dream.reichholf.net/e2web/#vol

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
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
			except Exception:  # noqa: E722
				res = getVolumeStatus()
				res["result"] = False
				res["message"] = _("Wrong parameter format 'set=%s'. Use set=set15 ") % request.args["set"][0]
				return res

		res = getVolumeStatus()
		res["result"] = False
		res["message"] = _("Unknown Volume command %s") % request.args["set"][0]
		return res

	def P_getaudiotracks(self, request):
		"""
		Request handler for the `/getaudiotracks` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#getaudiotracks

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return getAudioTracks(self.session)

	def P_selectaudiotrack(self, request):
		"""
		Request handler for the `/selectaudiotrack` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#selectaudiotrack

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/signal

			:query int id: audio track ID
		"""
		try:
			id = int(request.args["id"][0])
		except Exception:  # noqa: E722
			id = -1

		return setAudioTrack(self.session, id)

	def P_zap(self, request):
		"""
		Request handler for the `/zap` endpoint.
		Zap to requested service_reference.

		.. seealso::

			https://dream.reichholf.net/e2web/#zap

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/zap

			:query string sRef: service reference
			:query string title: service title
		"""
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res

		if "title" in request.args.keys():
			return zapService(self.session, request.args["sRef"][0], request.args["title"][0])

		return zapService(self.session, request.args["sRef"][0])

	def P_remotecontrol(self, request):
		"""
		Request handler for the `remotecontrol` endpoint.
		Send remote control codes.

		.. seealso::

			https://dream.reichholf.net/e2web/#remotecontrol

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		res = self.testMandatoryArguments(request, ["command"])
		if res:
			return res

		id = -1
		try:
			id = int(request.args["command"][0])
		except Exception:  # noqa: E722
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
		"""
		Request handler for the `powerstate` endpoint.
		Get/set power state of enigma2 device.

		.. seealso::

			https://dream.reichholf.net/e2web/#powerstate

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		if "shift" in request.args.keys():
			self.P_set_powerup_without_waking_tv(request)
		if "newstate" in request.args.keys():
			return setPowerState(self.session, request.args["newstate"][0])
		return getStandbyState(self.session)

	def P_supports_powerup_without_waking_tv(self, request):
		"""
		Request handler for the `supports_powerup_without_waking_tv` endpoint.
		Check if 'powerup without waking TV' is available.

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		try:
			# returns 'True' if the image supports the function "Power on without TV":
			f = open("/tmp/powerup_without_waking_tv.txt", "r")  # nosec
			powerupWithoutWakingTv = f.read()
			f.close()
			if ((powerupWithoutWakingTv == 'True') or (powerupWithoutWakingTv == 'False')):
				return True
			else:
				return False
		except:  # noqa: E722
			return False

	def P_set_powerup_without_waking_tv(self, request):
		"""
		Request handler for the `set_powerup_without_waking_tv` endpoint.
		Mark 'powerup without waking TV' being available.

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		if self.P_supports_powerup_without_waking_tv(request):
			try:
				# write "True" to file so that the box will power on ONCE skipping the HDMI-CEC communication:
				f = open("/tmp/powerup_without_waking_tv.txt", "w")  # nosec
				f.write('True')
				f.close()
				return True
			except:  # noqa: E722
				return False
		else:
			return False

	def P_getlocations(self, request):
		"""
		Request handler for the `getlocations` endpoint.
		Retrieve paths where video files are stored.

		.. seealso::

			https://dream.reichholf.net/e2web/#getlocations

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return getLocations()

	def P_getcurrlocation(self, request):
		"""
		Request handler for the `getcurrlocation` endpoint.
		Get currently selected path where video files are to be stored.

		.. seealso::

			https://dream.reichholf.net/e2web/#getcurrlocation

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return getCurrentLocation()

	def P_getallservices(self, request):
		"""
		Request handler for the `getallservices` endpoint.
		Retrieve list of services in bouquets.

		.. seealso::

			https://dream.reichholf.net/e2web/#getallservices

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
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
		"""
		Request handler for the `getservices` endpoint.
		Retrieve list of bouquets.

		.. seealso::

			https://dream.reichholf.net/e2web/#getservices

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		if "sRef" in request.args.keys():
			sRef = request.args["sRef"][0]
		else:
			sRef = ""
		if "hidden" in request.args.keys():
			hidden = request.args["hidden"][0] == "1"
		else:
			hidden = False
		if "provider" in request.args.keys():
			provider = request.args["provider"][0] == "1"
		else:
			provider = False
		if "picon" in request.args.keys():
			picon = request.args["picon"][0] == "1"
		else:
			picon = False
		return getServices(sRef=sRef, showAll=True, showHidden=hidden, provider=provider, picon=picon)

	def P_servicesm3u(self, request):
		"""
		Request handler for the `servicesm3u` endpoint.
		Retrieve list of bouquets(?) in M3U format.

		.. seealso::

			https://dream.reichholf.net/e2web/#services.m3u

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/services.m3u

			:query string bRef: bouquet reference
		"""
		if "bRef" in request.args.keys():
			bRef = request.args["bRef"][0]
		else:
			bRef = ""

		request.setHeader('Content-Type', 'application/x-mpegurl')
		if "bName" in request.args.keys():
			bname = request.args["bName"][0]
			bname = bname.replace(",","_").replace(";","_")
			request.setHeader('Content-Disposition', 'inline; filename=%s.%s;' % (bname, 'm3u8'))
		services = getServices(bRef, False)
		if comp_config.OpenWebif.auth_for_streaming.value:
			session = GetSession()
			if session.GetAuth(request) is not None:
				auth = ':'.join(session.GetAuth(request)) + "@"
			else:
				auth = '-sid:' + str(session.GetSID(request)) + "@"
		else:
			auth = ''
		services["host"] = "%s:8001" % request.getRequestHostname()
		services["auth"] = auth
		return services

	def P_subservices(self, request):
		"""
		Request handler for the `subservices` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#subservices

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return getSubServices(self.session)

	def P_parentcontrollist(self, request):
		"""
		Request handler for the `parentcontrollist` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#parentcontrollist

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return getParentalControlList()

	def P_servicelistplayable(self, request):
		"""
		Request handler for the `servicelistplayable` endpoint.
		Retrieve list of 'playable' bouquets.

		.. seealso::

			https://dream.reichholf.net/e2web/#servicelistplayable

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		sRef = ""
		if "sRef" in request.args.keys():
			sRef = request.args["sRef"][0]

		sRefPlaying = ""
		if "sRefPlaying" in request.args.keys():
			sRefPlaying = request.args["sRefPlaying"][0]
		return getPlayableServices(sRef, sRefPlaying)

	def P_serviceplayable(self, request):
		"""
		Request handler for the `serviceplayable` endpoint.
		Check if referenced service is 'playable'.

		.. seealso::

			https://dream.reichholf.net/e2web/#serviceplayable

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		sRef = ""
		if "sRef" in request.args.keys():
			sRef = request.args["sRef"][0]

		sRefPlaying = ""
		if "sRefPlaying" in request.args.keys():
			sRefPlaying = request.args["sRefPlaying"][0]

		return getPlayableService(sRef, sRefPlaying)

	def P_addlocation(self, request):
		"""
		Request handler for the `addlocation` endpoint.
		Add a path to the list of paths where video files are stored.

		.. seealso::

			https://dream.reichholf.net/e2web/#addlocation

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		res = self.testMandatoryArguments(request, ["dirname"])
		if res:
			return res

		create = False
		if "createFolder" in request.args.keys():
			create = request.args["createFolder"][0] == "1"

		return addLocation(request.args["dirname"][0], create)

	def P_removelocation(self, request):
		"""
		Request handler for the `removelocation` endpoint.
		Remove a path from the list of paths where video files are stored.

		.. seealso::

			https://dream.reichholf.net/e2web/#removelocation

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		res = self.testMandatoryArguments(request, ["dirname"])
		if res:
			return res

		remove = False
		if "removeFolder" in request.args.keys():
			remove = request.args["removeFolder"][0] == "1"

		return removeLocation(request.args["dirname"][0], remove)

	def P_message(self, request):
		"""
		Request handler for the `message` endpoint.
		Display a message on the screen attached to enigma2 device.

		.. seealso::

			https://dream.reichholf.net/e2web/#message

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
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
		"""
		Request handler for the `messageanswer` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#messageanswer

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return getMessageAnswer()

	def P_movielist(self, request):
		"""
		Request handler for the `movielist` endpoint.
		Retrieve list of movie items. (alternative implementation)

		.. seealso::

			https://dream.reichholf.net/e2web/#movielist

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return getMovieList(request.args)

	def P_fullmovielist(self, request):
		return getAllMovies()

	def P_movielisthtml(self, request):
		"""
		Request handler for the `movielisthtml` endpoint.
		Retrieve list of movie items in HTML format.

		.. seealso::

			https://dream.reichholf.net/e2web/#movielist.html

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		request.setHeader("content-type", "text/html")
		return getMovieList(request.args)

	def P_movielistm3u(self, request):
		"""
		Request handler for the `movielistm3u` endpoint.
		Retrieve list of movie items in M3U format.

		.. seealso::

			https://dream.reichholf.net/e2web/#movielist.m3u

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		request.setHeader('Content-Type', 'application/x-mpegurl')
		movielist = getMovieList(request.args)
		movielist["host"] = "%s://%s:%s" % (whoami(request)['proto'], request.getRequestHostname(), whoami(request)['port'])
		return movielist

	def P_movielistrss(self, request):
		"""
		Request handler for the `movielistrss` endpoint.
		Retrieve list of movie items in RSS format.

		.. seealso::
			https://dream.reichholf.net/e2web/#movielist.rss

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		movielist = getMovieList(request.args)
		movielist["host"] = "%s://%s:%s" % (whoami(request)['proto'], request.getRequestHostname(), whoami(request)['port'])
		return movielist

	def P_moviedelete(self, request):
		"""
		Request handler for the `moviedelete` endpoint.
		Delete movie file.

		.. seealso::
			https://dream.reichholf.net/e2web/#moviedelete

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		force = False
		if "force" in request.args.keys():
			force = True
		return removeMovie(self.session, request.args["sRef"][0], force)

	def P_moviemove(self, request):
		"""
		Request handler for the `moviemove` endpoint.
		Move movie file.

		.. seealso::
			https://dream.reichholf.net/e2web/#moviemove

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		res = self.testMandatoryArguments(request, ["dirname"])
		if res:
			return res

		return moveMovie(self.session, request.args["sRef"][0], request.args["dirname"][0])

	def P_movierename(self, request):
		"""
		Request handler for the `movierename` endpoint.
		Rename movie file.

		.. seealso::
			https://dream.reichholf.net/e2web/#movierename

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		res = self.testMandatoryArguments(request, ["newname"])
		if res:
			return res

		return renameMovie(self.session, request.args["sRef"][0], request.args["newname"][0])

	# DEPRECATED use movieinfo
	def P_movietags(self, request):
		"""
		Request handler for the `movietags` endpoint.
		Add/Remove tags to movie file.

		.. seealso::
			https://dream.reichholf.net/e2web/#movietags

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		_add = None
		_del = None
		_sref = None
		if "add" in request.args.keys():
			_add = request.args["add"][0]
		if "del" in request.args.keys():
			_del = request.args["del"][0]
		if "sref" in request.args.keys():
			_sref = request.args["sref"][0]
		return getMovieInfo(_sref, _add, _del)

	def P_movieinfo(self, request):
		"""
		Request handler for the `movie` endpoint.
		Add/Remove tags to movie file. Multiple tags needs to separate by ,
		Remame title of movie.
		Get/set movie cuts.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		if "sref" in request.args.keys():
			_sref = request.args["sref"][0]
			_addtag = None
			_deltag = None
			_title = None
			_cuts = None
			if "addtag" in request.args.keys():
				_addtag = request.args["addtag"][0]
			if "deltag" in request.args.keys():
				_deltag = request.args["deltag"][0]
			if "title" in request.args.keys():
				_title = request.args["title"][0]
			if "cuts" in request.args.keys():
				_cuts = request.args["cuts"][0]
			return getMovieInfo(_sref, _addtag, _deltag, _title, _cuts, True)
		else:
			return getMovieInfo()

	# a duplicate api ??
	def P_gettags(self, request):
		"""
		Request handler for the `gettags` endpoint.
		Get tags of movie file (?).

		.. seealso::
			https://dream.reichholf.net/e2web/#gettags

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return getMovieInfo()

# VPS Plugin
	def vpsparams(self, request):
		"""
		VPS related helper function(?)

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
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
			"vpsplugin_time": vpsplugin_time,
			"vpsplugin_overwrite": vpsplugin_overwrite,
			"vpsplugin_enabled": vpsplugin_enabled
		}

	def P_vpschannels(self, request):
		"""
		Request handler for the `vpschannels` endpoint.

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return getVPSChannels(self.session)

	def P_timerlist(self, request):
		"""
		Request handler for the `timerlist` endpoint.
		Retrieve list of timers.

		.. seealso::

			https://dream.reichholf.net/e2web/#timerlist

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		ret = getTimers(self.session)
		ret["locations"] = comp_config.movielist.videodirs.value
		return ret

	def P_timeradd(self, request):
		"""
		Request handler for the `timeradd` endpoint.
		Add timer

		.. seealso::

			https://dream.reichholf.net/e2web/#timeradd

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
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
		"""
		Request handler for the `timeraddbyeventid` endpoint.
		Add timer by event ID

		.. seealso::

			https://dream.reichholf.net/e2web/#timeraddbyeventid

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/timeraddbyeventid
			:query string sRef: service reference
			:query int eventid: Event ID
			:query int justplay: *Just Play* indicator
			:query string dirname: target path(?)
			:query string tags: tags to add(?)
			:query int always_zap: always zap first(?)
			:query int afterevent: afterevent state
		"""
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
		except Exception:  # noqa: E722
			return {
				"result": False,
				"message": "The parameter 'eventid' must be a number"
			}

		always_zap = -1
		if "always_zap" in request.args.keys():
			always_zap = int(request.args["always_zap"][0])

		afterevent = 3
		if "afterevent" in request.args.keys() and request.args["afterevent"][0] in ["0", "1", "2", "3"]:
			afterevent = int(request.args["afterevent"][0])

		return addTimerByEventId(
			self.session,
			eventid,
			request.args["sRef"][0],
			justplay,
			dirname,
			tags,
			self.vpsparams(request),
			always_zap,
			afterevent
		)

	def P_timerchange(self, request):
		"""
		Request handler for the `timerchange` endpoint.
		Change timer

		.. seealso::

			https://dream.reichholf.net/e2web/#timerchange

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/timerchange

			:query string sRef: service reference
			:query int begin: begin timestamp
			:query int end: end timestamp
			:query string name: name
			:query string description: description
			:query string channelOld: old channel(?)
			:query int beginOld: old begin timestamp(?)
			:query int endOld: old end timestamp(?)
			:query int justplay: *Just Play* indicator
			:query string dirname: target path(?)
			:query string tags: tags to add(?)
			:query int always_zap: always zap first(?)
			:query int disabled: disabled state
			:query int afterevent: afterevent state
		"""
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
		except Exception:  # noqa: E722
			return {
				"result": False,
				"message": "The parameter 'beginOld' must be a number"
			}

		try:
			endOld = int(request.args["endOld"][0])
		except Exception:  # noqa: E722
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
		"""
		Request handler for the `timertogglestatus` endpoint.

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		res = self.testMandatoryArguments(request, ["sRef", "begin", "end"])
		if res:
			return res
		try:
			begin = int(request.args["begin"][0])
		except Exception:  # noqa: E722
			return {
				"result": False,
				"message": "The parameter 'begin' must be a number"
			}

		try:
			end = int(request.args["end"][0])
		except Exception:  # noqa: E722
			return {
				"result": False,
				"message": "The parameter 'end' must be a number"
			}

		return toggleTimerStatus(self.session, request.args["sRef"][0], begin, end)

	def P_timerdelete(self, request):
		"""
		Request handler for the `timerdelete` endpoint.
		Delete timer

		.. seealso::

			https://dream.reichholf.net/e2web/#timerdelete

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		res = self.testMandatoryArguments(request, ["sRef", "begin", "end"])
		if res:
			return res

		try:
			begin = int(request.args["begin"][0])
		except Exception:  # noqa: E722
			return {
				"result": False,
				"message": "The parameter 'begin' must be a number"
			}

		try:
			end = int(request.args["end"][0])
		except Exception:  # noqa: E722
			return {
				"result": False,
				"message": "The parameter 'end' must be a number"
			}

		return removeTimer(self.session, request.args["sRef"][0], begin, end)

	def P_timercleanup(self, request):
		"""
		Request handler for the `timercleanup` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#timercleanup

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return cleanupTimer(self.session)

	def P_timerlistwrite(self, request):
		"""
		Request handler for the `timerlistwrite` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#timerlistwrite

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return writeTimerList(self.session)

	def P_recordnow(self, request):
		"""
		Request handler for the `recordnow` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#recordnow

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		infinite = False
		if "undefinitely" in request.args.keys() or "infinite" in request.args.keys():
			infinite = True
		return recordNow(self.session, infinite)

	def P_currenttime(self, request):
		"""
		Request handler for the `currenttime` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#currenttime

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return getCurrentTime()

	def P_deviceinfo(self, request):
		"""
		Request handler for the `deviceinfo` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#deviceinfo

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
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
		return getBouquetEpg(request.args["bRef"][0], begintime, None, self.isJson)

	def P_epgmulti(self, request):
		"""
		Request handler for the `epgmulti` endpoint.

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
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
		return getBouquetEpg(request.args["bRef"][0], begintime, endtime, self.isJson)
	
	def P_epgxmltv(self, request):
		"""
		Request handler for the `epgxmltv` endpoint.
	
		.. note::
	
			Not available in *Enigma2 WebInterface API*.
	
		Args:
			request (twisted.web.server.Request): HTTP request object
			bRef: mandatory, method uses epgmulti
			lang: mandatory, needed for xmltv and Enigma2 has no parameter for epg language			
		Returns:
			HTTP response with headers
		"""
		res = self.testMandatoryArguments(request, ["bRef", "lang"])
		if res:
			return res
		ret = self.P_epgmulti(request)
		bRef = request.args["bRef"][0]
		ret["services"] = getServices(bRef, True, False)["services"]
		ret["lang"] = request.args["lang"][0]
		ret["offset"] = getUtcOffset()
		return ret

	def P_epgnow(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
		return getBouquetNowNextEpg(request.args["bRef"][0], 0, self.isJson)

	def P_epgnext(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
		return getBouquetNowNextEpg(request.args["bRef"][0], 1, self.isJson)

	def P_epgnownext(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
		info = getCurrentService(self.session)
		ret = getBouquetNowNextEpg(request.args["bRef"][0], -1, self.isJson)
		ret["info"] = info
		return ret

	def P_epgservicelistnownext(self, request):
		res = self.testMandatoryArguments(request, ["sList"])
		if res:
			return res
		ret = getServicesNowNextEpg(request.args["sList"][0], self.isJson)
		return ret

	def P_epgsearch(self, request):
		"""
		EPG event search and lookup handler.

		.. note::

			One may use
			:py:func:`controllers.events.EventsController.search` for
			searching events.

		.. seealso::

			https://dream.reichholf.net/e2web/#epgsearch

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		if "search" in request.args.keys():
			endtime = None
			if "endtime" in request.args.keys():
				try:
					endtime = int(request.args["endtime"][0])
				except ValueError:
					pass
			fulldesc = False
			if "full" in request.args.keys():
				fulldesc = True
			return getSearchEpg(request.args["search"][0], endtime, fulldesc, False, self.isJson)
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
			return getEvent(service_reference, item_id, self.isJson)

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
		return getChannelEpg(request.args["sRef"][0], begintime, endtime, self.isJson)

	def P_epgservicenow(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		return getNowNextEpg(request.args["sRef"][0], 0, self.isJson)

	def P_epgservicenext(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		return getNowNextEpg(request.args["sRef"][0], 1, self.isJson)

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

		return getSearchSimilarEpg(request.args["sRef"][0], eventid, self.isJson)

	def P_event(self, request):
		event = getEvent(request.args["sref"][0], request.args["idev"][0], self.isJson)
		event['event']['recording_margin_before'] = comp_config.recording.margin_before.value
		event['event']['recording_margin_after'] = comp_config.recording.margin_after.value
		return event

	def P_getcurrent(self, request):
		"""
		Request handler for the `getcurrent` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#getcurrent

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers


		.. http:get:: /web/getcurrent

		"""
		info = getCurrentService(self.session)
		now = getNowNextEpg(info["ref"], 0, self.isJson)
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
				"provider": "",
				"genre": "",
				"genreid": 0
			}
		next = getNowNextEpg(info["ref"], 1, self.isJson)
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
				"provider": "",
				"genre": "",
				"genreid": 0
			}
		# replace EPG NOW with Movie info
		mnow = now
		if mnow["sref"].startswith('1:0:0:0:0:0:0:0:0:0:/') or mnow["sref"].startswith('4097:0:0:0:0:0:0:0:0:0:/'):
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
			except Exception:  # noqa: E722
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
				except Exception:  # nosec
					pass
		return {
			"info": info,
			"now": mnow,
			"next": next
		}

	def P_getpid(self, request):
		"""
		Request handler for the `getpid` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#getpid

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
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

	def P_streamm3u(self, request):
		"""
		Request handler for the `streamm3u` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#stream.m3u

		.. note::

			Parameters Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/stream.m3u

			:query string ref: service reference
			:query string name: service name
		"""
		self.isCustom = True
		if comp_config.OpenWebif.webcache.zapstream.value:
			if "ref" in request.args:
				name = ""
				if "name" in request.args:
					name = request.args["name"][0]
				zapService(self.session, request.args["ref"][0], name, stream=True)
		return getStream(self.session, request, "stream.m3u")

	def P_tsm3u(self, request):
		"""
		Request handler for the `tsm3u` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#ts.m3u

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/ts.m3u

		"""
		self.isCustom = True
		return getTS(self.session, request)

	def P_videom3u(self, request):
		self.isCustom = True
		return getStream(self.session, request, "video.m3u")

	def P_streamcurrentm3u(self, request):
		"""
		Request handler for the `streamcurrentm3u` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#streamcurrent.m3u

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/streamcurrent.m3u

		"""
		self.isCustom = True
		return getStream(self.session, request, "streamcurrent.m3u")

	def P_streamsubservices(self, request):
		"""
		Request handler for the `streamsubservices` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#streamsubservices

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/streamsubservices

			:query string sRef: service reference
		"""
		return getStreamSubservices(self.session, request)

	def P_servicelistreload(self, request):
		"""
		Reload service lists, transponders, parental control black-/white lists
		or/and lamedb.

		.. seealso::

			https://dream.reichholf.net/e2web/#servicelistreload

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return reloadServicesLists(self.session, request)

	def P_tvbrowser(self, request):
		"""
		Request handler for the `tvbrowser` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#tvbrowser

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return tvbrowser(self.session, request)

	def P_saveconfig(self, request):
		"""
		Request handler for the `saveconfig` endpoint.

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:post:: /web/saveconfig

			:query string key: configuration key
			:query string value: configuration value
		"""
		if request.method == b'POST':
			res = self.testMandatoryArguments(request, ["key"])
			if res:
				return res
			if "value" in request.args.keys():
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
		"""
		Request handler for the `pluginlistread` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#pluginlistread

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return reloadPlugins()

	def P_restarttwisted(self, request):
		"""
		Request handler for the `restarttwisted` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#restarttwisted

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		from ..httpserver import HttpdRestart
		HttpdRestart(self.session)
		return ""

	def P_powertimer(self, request):
		if len(request.args):
			res = self.testMandatoryArguments(request, ["start", "end", "timertype", "repeated", "afterevent", "disabled"])
			if res:
				return res
			return setPowerTimer(self.session, request)
		else:
			return getPowerTimer(self.session)

	def P_sleeptimer(self, request):
		"""
		Request handler for the `sleeptimer` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#sleeptimer

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/sleeptimer

			:query string cmd: command (*get* or *set*)
			:query int time: time in minutes (*0* -- *999*)
			:query string action: action (*standby* or *shutdown*)
			:query string enabled: enabled (*True* or *False*)
			:query string confirmed: confirmed (supported?)
		"""
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

		if time is None and enabled is True:  # it's used only if the timer is enabled
			ret["message"] = "ERROR: Obligatory parameter 'time' [0-999] is missing"
			return ret

		if enabled is None:
			ret["message"] = "Obligatory parameter 'enabled' [True,False] is missing"
			return ret

		return setSleepTimer(self.session, time, action, enabled)

	def P_external(self, request):
		"""
		Request handler for the `external` endpoint.

		.. seealso::

			https://dream.reichholf.net/e2web/#external

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		try:
			from Plugins.Extensions.WebInterface.WebChilds.Toplevel import loaded_plugins
			return {
				"plugins": loaded_plugins
			}
		except Exception:
			return {
				"plugins": []
			}

	def P_settings(self, request):
		"""
		Request handler for the `settings` endpoint.
		Retrieve list of key/kalue pairs of device configuration.

		.. seealso::

			https://dream.reichholf.net/e2web/#settings

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return getSettings()

	def P_bouquets(self, request):
		"""
		Request handler for the `boquets` endpoint.
		Get list of tuples (bouquet reference, bouquet name) for available
		bouquets.

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
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
		"""
		Request handler for the `saveepg` endpoint.

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return saveEpg()

	def P_loadepg(self, request):
		"""
		Request handler for the `loadepg` endpoint.

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		return loadEpg()

	def P_getsubtitles(self, request):
		"""
		Request handler for the `getsubtitles` endpoint.

		.. note::

			Not available in *Enigma2 WebInterface API*.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		service = self.session.nav.getCurrentService()
		ret = {"subtitlelist": [], "result": False}
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

	def P_setmoviesort(self, request):
		if "nsort" in request.args.keys():
			nsort = request.args["nsort"][0]
			comp_config.OpenWebif.webcache.moviesort.value = nsort
			comp_config.OpenWebif.webcache.moviesort.save()
		return {}

	def P_css(self, request):
		request.setHeader("content-type", "text/css")
		ret = {}
		theme = 'original'
		if comp_config.OpenWebif.webcache.theme.value:
			theme = comp_config.OpenWebif.webcache.theme.value
		ret['theme'] = theme
		moviedb = comp_config.OpenWebif.webcache.moviedb.value if comp_config.OpenWebif.webcache.moviedb.value else 'IMDb'
		ret['moviedb'] = moviedb
		ret['showchanneldetails'] = comp_config.OpenWebif.webcache.showchanneldetails.value
		return ret

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
						kv = []
						data = cfg['data']
						if data.has_key('choices'):
							for ch in data['choices']:
								if type(ch).__name__ == 'tuple' and len(ch) == 2 and ch[0] == ch[1]:
									if RepresentsInt(ch[0]):
										kv.append(int(ch[0]))
									else:
										kv = []
										break
								else:
									kv = []
									break

						if len(kv) > 1:
							if kv[1] == (kv[0] + 1):
								min = kv[0]
								max = kv[len(kv) - 1]

						if min > -1:
							data['min'] = min
							data['max'] = max
							del data['choices']
							cfg['data'] = data
							resultcfgs.append(cfg)
						else:
							resultcfgs.append(cfg)
					return {'configs': resultcfgs}
			except Exception:
				# TODO show exception
				pass
		return {}

	def P_setwebconfig(self, request):
		if "responsivedesign" in request.args.keys():
			val = (request.args["responsivedesign"][0] == 'true')
			comp_config.OpenWebif.responsive_enabled.value = val
			comp_config.OpenWebif.responsive_enabled.save()
		elif "moviedb" in request.args.keys():
			try:
				comp_config.OpenWebif.webcache.moviedb.value = request.args["moviedb"][0]
				comp_config.OpenWebif.webcache.moviedb.save()
			except Exception:
				pass
		elif "showchannelpicon" in request.args.keys():
			val = (request.args["showchannelpicon"][0] == 'true')
			comp_config.OpenWebif.webcache.showchannelpicon.value = val
			comp_config.OpenWebif.webcache.showchannelpicon.save()
		elif "showchanneldetails" in request.args.keys():
			val = (request.args["showchanneldetails"][0] == 'true')
			comp_config.OpenWebif.webcache.showchanneldetails.value = val
			comp_config.OpenWebif.webcache.showchanneldetails.save()
		elif "zapstream" in request.args.keys():
			val = (request.args["zapstream"][0] == 'true')
			comp_config.OpenWebif.webcache.zapstream.value = val
			comp_config.OpenWebif.webcache.zapstream.save()
		elif "theme" in request.args.keys():
			try:
				comp_config.OpenWebif.webcache.theme.value = request.args["theme"][0]
				comp_config.OpenWebif.webcache.theme.save()
			except Exception:
				pass
		elif "mepgmode" in request.args.keys():
			try:
				comp_config.OpenWebif.webcache.mepgmode.value = int(request.args["mepgmode"][0])
				comp_config.OpenWebif.webcache.mepgmode.save()
			except ValueError:
				pass
		else:
			return {"result": False}
		return {"result": True}


class ApiController(WebController):
	def __init__(self, session, path=""):
		WebController.__init__(self, session, path)

	def prePageLoad(self, request):
		self.isJson = True


from Plugins.Extensions.OpenWebif.vtiaddon import expand_basecontroller  # noqa: F401
