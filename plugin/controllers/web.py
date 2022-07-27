# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: WebController
##########################################################################
# Copyright (C) 2011 - 2022 E2OpenPlugins
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

from __future__ import absolute_import, division
from re import match
from six import ensure_str, ensure_binary
from Components.config import config as comp_config
from Screens.InfoBar import InfoBar

from .models.info import getInfo, getCurrentTime, getStatusInfo, getFrontendStatus, testPipStatus
from .models.services import getCurrentService, getBouquets, getServices, getSubServices, getSatellites, getBouquetEpg, getBouquetNowNextEpg, getMultiChannelNowNextEpg, getSearchEpg, getChannelEpg, getNowNextEpg, getSearchSimilarEpg, getAllServices, getPlayableServices, getPlayableService, getParentalControlList, getEvent, getServiceRef, getPicon
from .models.volume import getVolumeStatus, setVolumeUp, setVolumeDown, setVolumeMute, setVolume
from .models.audiotrack import getAudioTracks, setAudioTrack
from .models.control import zapService, remoteControl, setPowerState, getStandbyState
from .models.locations import getLocations, getCurrentLocation, addLocation, removeLocation
from .models.timers import getTimers, addTimer, addTimerByEventId, editTimer, removeTimer, toggleTimerStatus, cleanupTimer, writeTimerList, recordNow, tvbrowser, getSleepTimer, setSleepTimer, getPowerTimer, setPowerTimer, getVPSChannels
from .models.message import sendMessage, getMessageAnswer
from .models.movies import getMovieList, removeMovie, getMovieInfo, moveMovie, renameMovie, getAllMovies, getMovieDetails
from .models.config import getSettings, addCollapsedMenu, removeCollapsedMenu, saveConfig, getConfigs, getConfigsSections, getUtcOffset
from .models.stream import getStream, getTS, getStreamSubservices, GetSession
from .models.servicelist import reloadServicesLists
from .models.mediaplayer import mediaPlayerAdd, mediaPlayerRemove, mediaPlayerPlay, mediaPlayerCommand, mediaPlayerCurrent, mediaPlayerList, mediaPlayerLoad, mediaPlayerSave, mediaPlayerFindFile
from .models.plugins import reloadPlugins

from .i18n import _
from .base import BaseController
from .stream import StreamController
from .utilities import getUrlArg
from .defaults import PICON_PATH
from .epg import EPG


def whoami(request):
	port = comp_config.OpenWebif.port.value
	proto = 'http'
	if request.isSecure():
		port = comp_config.OpenWebif.https_port.value
		proto = 'https'
	ourhost = request.getHeader('host')
	m = match('.+\:(\d+)$', ourhost)
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
		self.putChild(b"stream", StreamController(session))

	def prePageLoad(self, request):
		request.setHeader("content-type", "text/xml")

	def testMandatoryArguments(self, request, keys):
		for key in keys:
			k = ensure_binary(key)
			if k not in list(request.args.keys()):
				return {
					"result": False,
					"message": _("Missing mandatory parameter '%s'") % key
				}

			if len(request.args[k][0]) == 0:
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
		except Exception:  # nosec # noqa: E722
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
		except Exception:  # nosec # noqa: E722
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
		set = getUrlArg(request, "set")
		if set == None or set == "state":
			return getVolumeStatus()
		elif set == "up":
			return setVolumeUp()
		elif set == "down":
			return setVolumeDown()
		elif set == "mute":
			return setVolumeMute()
		elif set[:3] == "set":
			try:
				return setVolume(int(set[3:]))
			except Exception:  # nosec # noqa: E722
				res = getVolumeStatus()
				res["result"] = False
				res["message"] = _("Wrong parameter format 'set=%s'. Use set=set15 ") % set
				return res

		res = getVolumeStatus()
		res["result"] = False
		res["message"] = _("Unknown Volume command %s") % set
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
			id = int(request.args[b"id"][0])
		except Exception:  # nosec # noqa: E722
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

		title = getUrlArg(request, "title", "")
		sRef = getUrlArg(request, "sRef")
		return zapService(self.session, sRef, title)

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

		text = getUrlArg(request, "text", "")
		if text:
			return remoteControl(0, "text", text)  # text input do not need type and command

		res = self.testMandatoryArguments(request, ["command"])
		if res:
			return res

		id = -1
		try:
			id = int(request.args[b"command"][0])
		except Exception:  # nosec # noqa: E722
			return {
				"result": False,
				"message": _("The parameter 'command' must be a number")
			}

		type = getUrlArg(request, "type", "")
		rcu = getUrlArg(request, "rcu", "")

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
		if b"shift" in list(request.args.keys()):
			self.P_set_powerup_without_waking_tv(request)
		newstate = getUrlArg(request, "newstate")
		if newstate != None:
			return setPowerState(self.session, newstate)
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
		except:  # nosec # noqa: E722
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
			except:  # nosec # noqa: E722
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
		if b"type" in list(request.args.keys()):
			type = "radio"

		noiptv = True if getUrlArg(request, "noiptv", "0") in ("1", "true") else False

		nolastscanned = True if getUrlArg(request, "nolastscanned", "0") in ("1", "true") else False

		removeNameFromsref = True if getUrlArg(request, "removenamefromsref", "0") in ("1", "true") else False

		showAll = False if getUrlArg(request, "showall", "1") in ("0", "false") else True

		showProviders = True if getUrlArg(request, "showproviders", "0") in ("1", "true") else False

		bouquets = getAllServices(type=type, noiptv=noiptv, nolastscanned=nolastscanned, removeNameFromsref=removeNameFromsref, showAll=showAll, showProviders=showProviders)
		if b"renameserviceforxmbc" in list(request.args.keys()):
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
		sRef = getUrlArg(request, "sRef", "")
		hidden = True if getUrlArg(request, "hidden", "0") in ("1", "true") else False
		showProviders = True if getUrlArg(request, "showproviders", "0") in ("1", "true") else False
		# FALLBACK for old 3rd party tools
		if getUrlArg(request, "provider") == "1":
			showProviders = True
		picon = True if getUrlArg(request, "picon", "0") in ("1", "true") else False
		removeNameFromsref = True if getUrlArg(request, "removenamefromsref", "0") in ("1", "true") else False
		return getServices(sRef=sRef, showAll=True, showHidden=hidden, showProviders=showProviders, picon=picon, removeNameFromsref=removeNameFromsref)

	def P_servicesxspf(self, request):
		"""
		Request handler for the `servicesxspf` endpoint.
		Retrieve list of bouquets(?) in XSPF format.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers

		.. http:get:: /web/services.xspf

			:query string bRef: bouquet reference
		"""
		bRef = getUrlArg(request, "bRef", "")
		request.setHeader('Content-Type', 'application/xspf+xml')
		bouquetName = getUrlArg(request, "bName")
		if bouquetName != None:
			bouquetName = bouquetName.replace(",", "_").replace(";", "_")
			request.setHeader('Content-Disposition', 'inline; filename=%s.%s;' % (bouquetName, 'xspf'))
		services = getServices(bRef, False)
		if comp_config.OpenWebif.auth_for_streaming.value:
			session = GetSession()
			if session.GetAuth(request) is not None:
				auth = ':'.join(session.GetAuth(request)) + "@"
			else:
				auth = '-sid:' + str(session.GetSID(request)) + "@"
		else:
			auth = ''
		portNumber = comp_config.OpenWebif.streamport.value
		services["host"] = "%s:%s" % (request.getRequestHostname(), portNumber)
		services["auth"] = auth
		services["bname"] = bouquetName
		return services

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
		bRef = getUrlArg(request, "bRef", "")
		request.setHeader('Content-Type', 'application/x-mpegurl')
		bouquetName = getUrlArg(request, "bName")
		if bouquetName != None:
			bouquetName = bouquetName.replace(",", "_").replace(";", "_")
			request.setHeader('Content-Disposition', 'inline; filename=%s.%s;' % (bouquetName, 'm3u8'))
		services = getServices(bRef, False)
		if comp_config.OpenWebif.auth_for_streaming.value:
			session = GetSession()
			if session.GetAuth(request) is not None:
				auth = ':'.join(session.GetAuth(request)) + "@"
			else:
				auth = '-sid:' + str(session.GetSID(request)) + "@"
		else:
			auth = ''
		portNumber = comp_config.OpenWebif.streamport.value
		services["host"] = "%s:%s" % (request.getRequestHostname(), portNumber)
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
		sRef = getUrlArg(request, "sRef", "")
		sRefPlaying = getUrlArg(request, "sRefPlaying", "")
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
		sRef = getUrlArg(request, "sRef", "")
		sRefPlaying = getUrlArg(request, "sRefPlaying", "")
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

		dirname = getUrlArg(request, "dirname")
		create = getUrlArg(request, "createFolder") == "1"
		return addLocation(dirname, create)

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

		dirname = getUrlArg(request, "dirname")
		remove = getUrlArg(request, "removeFolder") == "1"
		return removeLocation(dirname, remove)

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
			ttype = int(request.args[b"type"][0])
		except ValueError:
			return {
				"result": False,
				"message": _("type %s is not a number") % request.args[b"type"][0]
			}

		timeout = -1
		if b"timeout" in list(request.args.keys()):
			try:
				timeout = int(request.args[b"timeout"][0])
			except ValueError:
				pass

		text = getUrlArg(request, "text")
		return sendMessage(self.session, text, ttype, timeout)

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
		sRef = getUrlArg(request, "sRef")
		force = getUrlArg(request, "force") != None
		return removeMovie(self.session, sRef, force)

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

		sRef = getUrlArg(request, "sRef")
		dirname = getUrlArg(request, "dirname")
		return moveMovie(self.session, sRef, dirname)

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
		sRef = getUrlArg(request, "sRef")
		newname = getUrlArg(request, "newname")
		return renameMovie(self.session, sRef, newname)

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
		_add = getUrlArg(request, "add")
		_del = getUrlArg(request, "del")
		_sRef = getUrlArg(request, "sRef")
		if _sRef == None:
			_sRef = getUrlArg(request, "sref")
		return getMovieInfo(_sRef, _add, _del)

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
		_sRef = getUrlArg(request, "sRef")
		if _sRef == None:
			_sRef = getUrlArg(request, "sref")
		if _sRef != None:
			_addtag = getUrlArg(request, "addtag")
			_deltag = getUrlArg(request, "deltag")
			_title = getUrlArg(request, "title")
			_cuts = getUrlArg(request, "cuts")
			_desc = getUrlArg(request, "desc")
			return getMovieInfo(_sRef, _addtag, _deltag, _title, _cuts, _desc, True)
		else:
			return getMovieInfo()

	def P_moviedetails(self, request):
		"""
		Request handler for the `movie` endpoint.

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		_sRef = getUrlArg(request, "sRef")
		if _sRef == None:
			_sRef = getUrlArg(request, "sref")
		if _sRef != None:
			return getMovieDetails(_sRef)
		else:
			return {
				"result": False
			}

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
		vpsplugin_enabled = getUrlArg(request, "vpsplugin_enabled") == "1"
		vpsplugin_overwrite = getUrlArg(request, "vpsplugin_overwrite") == "1"
		vpsplugin_time = None
		if b"vpsplugin_time" in request.args:
			vpsplugin_time = int(float(request.args[b"vpsplugin_time"][0]))
			if vpsplugin_time == -1:
				vpsplugin_time = None
		# partnerbox:
		vps_pbox = getUrlArg(request, "vps_pbox")
		if vps_pbox != None:
			vpsplugin_enabled = None
			vpsplugin_overwrite = None
			if "yes_safe" in vps_pbox:
				vpsplugin_enabled = True
			elif "yes" in vps_pbox:
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

	def _AddEditTimer(self, request, mode):

		disabled = getUrlArg(request, "disabled") == "1"
		justplay = getUrlArg(request, "justplay") == "1"
		afterevent = getUrlArg(request, "afterevent", "3")
		if afterevent in ["0", "1", "2", "3"]:
			afterevent = int(afterevent)
		else:
			afterevent = 3

		dirname = getUrlArg(request, "dirname")
		if dirname != None and len(dirname) == 0:
			dirname = None

		tags = []
		_tags = getUrlArg(request, "tags")
		if _tags != None:
			tags = _tags.split(' ')

		repeated = int(getUrlArg(request, "repeated", "0"))

		description = getUrlArg(request, "description", "")

		sRef = getUrlArg(request, "sRef")

		eit = 0
		if mode == 1:
			try:
				eventid = int(request.args[b"eventid"][0])
			except Exception:  # nosec # noqa: E722
				return {
					"result": False,
					"message": "The parameter 'eventid' must be a number"
				}
		elif b"eit" in list(request.args.keys()) and isinstance(request.args[b"eit"][0], int):
			eit = int(request.args[b"eit"][0])
		else:
			# TODO : move this code to timers.py
			queryTime = int(request.args[b"begin"][0]) + (int(request.args[b"end"][0]) - int(request.args[b"begin"][0])) // 2
			epg = EPG()
			event = epg.getEventByTime(sRef, queryTime)
			eventid = event and event.getEventId()
			if eventid is not None:
				eit = int(eventid)

		always_zap = int(getUrlArg(request, "always_zap", "-1"))
		pipzap = int(getUrlArg(request, "pipzap", "-1"))
		allow_duplicate = getUrlArg(request, "allow_duplicate") == "1"
		_autoadjust = getUrlArg(request, "autoadjust")
		autoadjust = -1
		if _autoadjust != None:
			autoadjust = _autoadjust == "1"

		recordingtype = getUrlArg(request, "recordingtype")
		if recordingtype:
			if recordingtype not in ("normal", "descrambled", "scrambled"):
				recordingtype = None

		# TODO: merge function addTimer+editTimer+addTimerByEventId in timers.py
		if mode == 1:
			return addTimerByEventId(
				self.session,
				eventid,
				sRef,
				justplay,
				dirname,
				tags,
				self.vpsparams(request),
				always_zap,
				afterevent,
				pipzap,
				allow_duplicate,
				autoadjust,
				recordingtype
			)
		elif mode == 2:
			try:
				beginOld = int(request.args[b"beginOld"][0])
			except Exception:  # nosec # noqa: E722
				return {
					"result": False,
					"message": "The parameter 'beginOld' must be a number"
				}

			try:
				endOld = int(request.args[b"endOld"][0])
			except Exception:  # nosec # noqa: E722
				return {
					"result": False,
					"message": "The parameter 'endOld' must be a number"
				}
			return editTimer(
				self.session,
				sRef,
				getUrlArg(request, "begin"),
				getUrlArg(request, "end"),
				getUrlArg(request, "name"),
				description,
				disabled,
				justplay,
				afterevent,
				dirname,
				tags,
				repeated,
				getUrlArg(request, "channelOld"),
				beginOld,
				endOld,
				recordingtype,
				self.vpsparams(request),
				always_zap,
				pipzap,
				allow_duplicate,
				autoadjust
			)
		else:
			return addTimer(
				self.session,
				sRef,
				getUrlArg(request, "begin"),
				getUrlArg(request, "end"),
				getUrlArg(request, "name"),
				description,
				disabled,
				justplay,
				afterevent,
				dirname,
				tags,
				repeated,
				recordingtype,
				self.vpsparams(request),
				None,
				eit,
				always_zap,
				pipzap,
				allow_duplicate,
				autoadjust
			)

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

		return self._AddEditTimer(request, 0)

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

		return self._AddEditTimer(request, 1)

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

		return self._AddEditTimer(request, 2)

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
			begin = int(request.args[b"begin"][0])
		except Exception:  # nosec # noqa: E722
			return {
				"result": False,
				"message": "The parameter 'begin' must be a number"
			}

		try:
			end = int(request.args[b"end"][0])
		except Exception:  # nosec # noqa: E722
			return {
				"result": False,
				"message": "The parameter 'end' must be a number"
			}

		return toggleTimerStatus(self.session, getUrlArg(request, "sRef"), begin, end)

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
			begin = int(request.args[b"begin"][0])
		except Exception:  # nosec # noqa: E722
			return {
				"result": False,
				"message": "The parameter 'begin' must be a number"
			}

		try:
			end = int(request.args[b"end"][0])
		except Exception:  # nosec # noqa: E722
			return {
				"result": False,
				"message": "The parameter 'end' must be a number"
			}

		try:
			eit = int(request.args[b"eit"][0])
		except Exception:  # nosec # noqa: E722
			eit = None

		return removeTimer(self.session, getUrlArg(request, "sRef"), begin, end, eit)

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
		if b"undefinitely" in list(request.args.keys()) or b"infinite" in list(request.args.keys()):
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

	# http://enigma2/api/epgbouquet?bRef=1%3A7%3A1%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A%20FROM%20BOUQUET%20%22userbouquet.favourites.tv%22%20ORDER%20BY%20bouquet
	# http://enigma2/web/epgbouquet?bRef=1%3A7%3A1%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A%20FROM%20BOUQUET%20%22userbouquet.favourites.tv%22%20ORDER%20BY%20bouquet
	# TODO: this is _woefully_ inefficient
	def P_epgbouquet(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res

		begintime = -1
		if b"time" in list(request.args.keys()):
			try:
				begintime = int(request.args[b"time"][0])
			except ValueError:
				pass

		# TODO: test -1 actually works
		endtime = -1
		if b"endTime" in list(request.args.keys()):
			try:
				endtime = int(request.args[b"endTime"][0])
			except ValueError:
				pass

		return getBouquetEpg(getUrlArg(request, "bRef"), begintime, endtime, self.isJson)

	# http://enigma2/api/epgmulti?bRef=1%3A7%3A1%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A%20FROM%20BOUQUET%20"userbouquet.favourites.tv"%20ORDER%20BY%20bouquet
	# http://enigma2/web/epgmulti?bRef=1%3A7%3A1%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A%20FROM%20BOUQUET%20"userbouquet.favourites.tv"%20ORDER%20BY%20bouquet
	# TODO: check if originally dupe of `P_epgbouquet`
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
		if b"time" in list(request.args.keys()):
			try:
				begintime = int(request.args[b"time"][0])
			except ValueError:
				pass

		# TODO: test -1 actually works
		endtime = -1
		if b"endTime" in list(request.args.keys()):
			try:
				endtime = int(request.args[b"endTime"][0])
			except ValueError:
				pass
		return getBouquetEpg(getUrlArg(request, "bRef"), begintime, endtime, self.isJson)

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
		bRef = getUrlArg(request, "bRef")
		ret["services"] = getServices(bRef, True, False)["services"]
		ret["lang"] = getUrlArg(request, "lang")
		ret["offset"] = getUtcOffset()
		return ret

	# http://enigma2/api/epgnow?bRef=1%3A7%3A1%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A%20FROM%20BOUQUET%20"userbouquet.favourites.tv"%20ORDER%20BY%20bouquet
	# http://enigma2/web/epgnow?bRef=1%3A7%3A1%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A%20FROM%20BOUQUET%20"userbouquet.favourites.tv"%20ORDER%20BY%20bouquet
	def P_epgnow(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
		bqRef = getUrlArg(request, "bRef")

		return getBouquetNowNextEpg(bqRef, Epg.NOW, self.isJson)

	# http://enigma2/api/epgnext?bRef=1%3A7%3A1%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A%20FROM%20BOUQUET%20"userbouquet.favourites.tv"%20ORDER%20BY%20bouquet
	# http://enigma2/web/epgnext?bRef=1%3A7%3A1%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A%20FROM%20BOUQUET%20"userbouquet.favourites.tv"%20ORDER%20BY%20bouquet
	def P_epgnext(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
		bqRef = getUrlArg(request, "bRef")

		# from Components.Sources.EventInfo import EventInfo
		# print(EventInfo(self.session.nav, EventInfo.NEXT).getEvent().getBeginTime())
		return getBouquetNowNextEpg(bqRef, Epg.NEXT, self.isJson)

	# http://enigma2/api/epgnownext?bRef=1%3A7%3A1%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A%20FROM%20BOUQUET%20"userbouquet.favourites.tv"%20ORDER%20BY%20bouquet
	# http://enigma2/web/epgnownext?bRef=1%3A7%3A1%3A0%3A0%3A0%3A0%3A0%3A0%3A0%3A%20FROM%20BOUQUET%20"userbouquet.favourites.tv"%20ORDER%20BY%20bouquet
	# TODO: fix missing now or next
	def P_epgnownext(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
		bqRef = getUrlArg(request, "bRef")
		ret = getBouquetNowNextEpg(bqRef, Epg.NOW_NEXT, self.isJson)
		info = getCurrentService(self.session)
		ret["info"] = info
		return ret

	def P_epgmultichannelnownext(self, request):
		res = self.testMandatoryArguments(request, ["sRefs"])
		if res:
			return res

		sRefs = getUrlArg(request, "sRefs").split(",")
		ret = getMultiChannelNowNextEpg(sRefs, self.isJson)

		return str(ret)  # fixed Jun'22 (seems to have been broken for quite a while)

	# http://enigma2/api/epgsearch?search=test
	# http://enigma2/web/epgsearch?search=test
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
		search = getUrlArg(request, "search")
		if search != None:
			endtime = None
			if b"endtime" in list(request.args.keys()):
				try:
					endtime = int(request.args[b"endtime"][0])
				except ValueError:
					pass
			fulldesc = False
			if b"full" in list(request.args.keys()):
				fulldesc = True
			return getSearchEpg(search, endtime, fulldesc, False, self.isJson)
		else:
			res = self.testMandatoryArguments(request, ["eventid"])
			if res:
				return res
			sRef = getUrlArg(request, "sRef")
			if sRef == None:
				sRef = getUrlArg(request, "sref")
			if sRef == None:
				return {
					"result": False,
					"message": _("The parameter '%s' can't be empty") % "sRef,sref"
				}
			item_id = 0
			try:
				item_id = int(request.args[b"eventid"][0])
			except ValueError:
				pass
			return getEvent(sRef, item_id, self.isJson)

	# http://enigma2/api/epgsearchrss?search=test
	# http://enigma2/web/epgsearchrss?search=test
	def P_epgsearchrss(self, request):
		res = self.testMandatoryArguments(request, ["search"])
		if res:
			return res

		search = getUrlArg(request, "search")
		ret = getSearchEpg(search)
		ret["title"] = "EPG Search '%s'" % search
		ret["generator"] = "OpenWebif"
		ret["description"] = "%d result for '%s'" % (len(ret["events"]), search)
		return ret

	# http://enigma2/api/epgservice?sRef=1%3A0%3A19%3A1B1F%3A802%3A2%3A11A0000%3A0%3A0%3A0%3A
	# http://enigma2/web/epgservice?sRef=1%3A0%3A19%3A1B1F%3A802%3A2%3A11A0000%3A0%3A0%3A0%3A
	def P_epgservice(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res

		begintime = -1
		if b"time" in list(request.args.keys()):
			try:
				begintime = int(request.args[b"time"][0])
			except ValueError:
				pass

		endtime = -1
		if b"endTime" in list(request.args.keys()):
			try:
				endtime = int(request.args[b"endTime"][0])
			except ValueError:
				pass
		return getChannelEpg(getUrlArg(request, "sRef"), begintime, endtime, self.isJson)

	# http://enigma2/api/epgservicenow?sRef=1%3A0%3A19%3A1B1F%3A802%3A2%3A11A0000%3A0%3A0%3A0%3A
	# http://enigma2/web/epgservicenow?sRef=1%3A0%3A19%3A1B1F%3A802%3A2%3A11A0000%3A0%3A0%3A0%3A
	def P_epgservicenow(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		return getNowNextEpg(getUrlArg(request, "sRef"), Epg.NOW, self.isJson)

	# http://enigma2/api/epgservicenext?sRef=1%3A0%3A19%3A1B1F%3A802%3A2%3A11A0000%3A0%3A0%3A0%3A
	# http://enigma2/web/epgservicenext?sRef=1%3A0%3A19%3A1B1F%3A802%3A2%3A11A0000%3A0%3A0%3A0%3A
	def P_epgservicenext(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		return getNowNextEpg(getUrlArg(request, "sRef"), Epg.NEXT, self.isJson)

	# http://enigma2/api/epgsimilar?sRef=1%3A0%3A19%3A1B1F%3A802%3A2%3A11A0000%3A0%3A0%3A0%3A&eventid=32645
	# http://enigma2/web/epgsimilar?sRef=1%3A0%3A19%3A1B1F%3A802%3A2%3A11A0000%3A0%3A0%3A0%3A&eventid=32645
	def P_epgsimilar(self, request):
		res = self.testMandatoryArguments(request, ["sRef", "eventid"])
		if res:
			return res

		try:
			eventid = int(request.args[b"eventid"][0])
		except ValueError:
			return {
				"result": False,
				"message": "The parameter 'eventid' must be a number"
			}
		return getSearchSimilarEpg(getUrlArg(request, "sRef"), eventid, self.isJson)

	# http://enigma2/api/event?idev=32695&sref=1%3A0%3A19%3A1B1F%3A802%3A2%3A11A0000%3A0%3A0%3A0%3A
	# (/web/event returns a 404 in both `classic` and `modern` interfaces
	def P_event(self, request):
		sRef = getUrlArg(request, "sRef")
		if sRef == None:
			sRef = getUrlArg(request, "sref")

		event = getEvent(sRef, request.args[b"idev"][0], self.isJson)

		if event is not None:
			# TODO: this shouldn't really be part of an event's data
			event['event']['recording_margin_before'] = comp_config.recording.margin_before.value
			event['event']['recording_margin_after'] = comp_config.recording.margin_after.value
			return event
		else:
			return None

	# http://enigma2/api/getcurrent
	# http://enigma2/web/getcurrent
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
		now = getNowNextEpg(info["ref"], Epg.NOW, self.isJson)
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
		next = getNowNextEpg(info["ref"], Epg.NEXT, self.isJson)
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
			except Exception:  # nosec # noqa: E722
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
		return addCollapsedMenu(getUrlArg(request, "name"))

	def P_expandmenu(self, request):
		res = self.testMandatoryArguments(request, ["name"])
		if res:
			return res
		return removeCollapsedMenu(getUrlArg(request, "name"))

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
			ref = getUrlArg(request, "ref")
			if ref != None:
				name = getUrlArg(request, "name", "")
				zapService(self.session, ref, name, stream=True)
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
		mode = getUrlArg(request, "mode")
		return reloadServicesLists(self.session, mode)

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
			value = getUrlArg(request, "value")
			if value != None:
				key = getUrlArg(request, "key")
				return saveConfig(key, value)
		return {"result": False}

	def P_mediaplayeradd(self, request):
		res = self.testMandatoryArguments(request, ["file"])
		if res:
			return res
		return mediaPlayerAdd(self.session, getUrlArg(request, "file"))

	def P_mediaplayerplay(self, request):
		res = self.testMandatoryArguments(request, ["file"])
		if res:
			return res

		root = getUrlArg(request, "root", "")
		return mediaPlayerPlay(self.session, getUrlArg(request, "file"), root)

	def P_mediaplayercmd(self, request):
		res = self.testMandatoryArguments(request, ["command"])
		if res:
			return res
		return mediaPlayerCommand(self.session, getUrlArg(request, "command"))

	def P_mediaplayercurrent(self, request):
		return mediaPlayerCurrent(self.session)

	def P_mediaplayerfindfile(self, request):
		path = getUrlArg(request, "path", "/media/")
		pattern = getUrlArg(request, "pattern", "*.*")
		return mediaPlayerFindFile(self.session, path, pattern)

	def P_mediaplayerlist(self, request):
		path = getUrlArg(request, "path", "")
		types = getUrlArg(request, "types", "")
		return mediaPlayerList(self.session, path, types)

	def P_mediaplayerremove(self, request):
		res = self.testMandatoryArguments(request, ["file"])
		if res:
			return res
		return mediaPlayerRemove(self.session, getUrlArg(request, "file"))

	def P_mediaplayerload(self, request):
		res = self.testMandatoryArguments(request, ["filename"])
		if res:
			return res
		return mediaPlayerLoad(self.session, getUrlArg(request, "filename"))

	def P_mediaplayerwrite(self, request):
		res = self.testMandatoryArguments(request, ["filename"])
		if res:
			return res
		return mediaPlayerSave(self.session, getUrlArg(request, "filename"))

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
		from Plugins.Extensions.OpenWebif.httpserver import HttpdRestart
		HttpdRestart(self.session)
		return ""

	def P_powertimer(self, request):
		if len(request.args):
			res = self.testMandatoryArguments(request, ["start", "end", "timertype", "repeated", "afterevent", "disabled"])
			if res:
				return res
			return setPowerTimer(self.session, request)
		else:
			return getPowerTimer(self.session, request)

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
		cmd = getUrlArg(request, "cmd", "get")
		if cmd == "get":
			return getSleepTimer(self.session)

		time = getUrlArg(request, "time")
		if time != None:
			try:
				time = int(time)
				if time > 999:
					time = 999
				elif time < 0:
					time = 0
			except ValueError:
				pass

		action = getUrlArg(request, "action", "standby")
		enabled = getUrlArg(request, "enabled")
		if enabled != None:
			if enabled == "True" or enabled == "true":
				enabled = True
			elif enabled == "False" or enabled == "false":
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
			result = []
			for p in loaded_plugins:
				result.append((p[0], '', p[2], p[3]))
			return {
				"plugins": result
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
		stype = getUrlArg(request, "stype", "tv")
		return getBouquets(stype)

	def P_epgmultigz(self, request):
		return self.P_epgmulti(request)

	def P_getsatellites(self, request):
		stype = getUrlArg(request, "stype", "tv")
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
		EPG().save()

		return {
			"result": True,
			"message": "EPG data saved"
		}

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
		EPG().load()

		return {
			"result": True,
			"message": "EPG data loaded"
		}

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
			for i in list(range(0, len(subtitlelist))):
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
		nsort = getUrlArg(request, "nsort")
		if nsort != None:
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
		smallremote = comp_config.OpenWebif.webcache.smallremote.value if comp_config.OpenWebif.webcache.smallremote.value else 'new'
		ret['smallremote'] = smallremote
		return ret

	def P_config(self, request):

		def RepresentsInt(s):
			try:
				int(s)
				return True
			except ValueError:
				return False

		setcs = getConfigsSections()
		if request.path == b'/api/config':
			return setcs
		else:
			try:
				rp = ensure_str(request.path)
				sect = rp.split('/')
				if len(sect) == 4:
					cfgs = getConfigs(sect[3])
					resultcfgs = []
					for cfg in cfgs['configs']:
						min = -1
						kv = []
						data = cfg['data']
						if 'choices' in data:
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
		if b"responsivedesign" in list(request.args.keys()):
			val = (getUrlArg(request, "responsivedesign") == 'true')
			comp_config.OpenWebif.responsive_enabled.value = val
			comp_config.OpenWebif.responsive_enabled.save()
		elif b"moviedb" in list(request.args.keys()):
			try:
				comp_config.OpenWebif.webcache.moviedb.value = getUrlArg(request, "moviedb")
				comp_config.OpenWebif.webcache.moviedb.save()
			except Exception:
				pass
		elif b"showpicons" in list(request.args.keys()):
			val = (getUrlArg(request, "showpicons") == 'true')
			comp_config.OpenWebif.webcache.showpicons.value = val
			comp_config.OpenWebif.webcache.showpicons.save()
		elif b"showchanneldetails" in list(request.args.keys()):
			val = (getUrlArg(request, "showchanneldetails") == 'true')
			comp_config.OpenWebif.webcache.showchanneldetails.value = val
			comp_config.OpenWebif.webcache.showchanneldetails.save()
		elif b"showiptvchannelsinselection" in list(request.args.keys()):
			val = (getUrlArg(request, "showiptvchannelsinselection") == 'true')
			comp_config.OpenWebif.webcache.showiptvchannelsinselection.value = val
			comp_config.OpenWebif.webcache.showiptvchannelsinselection.save()
		elif b"screenshotchannelname" in list(request.args.keys()):
			val = (getUrlArg(request, "screenshotchannelname") == 'true')
			comp_config.OpenWebif.webcache.screenshotchannelname.value = val
			comp_config.OpenWebif.webcache.screenshotchannelname.save()
		elif b"showallpackages" in list(request.args.keys()):
			val = (getUrlArg(request, "showallpackages") == 'true')
			comp_config.OpenWebif.webcache.showallpackages.value = val
			comp_config.OpenWebif.webcache.showallpackages.save()
		elif b"zapstream" in list(request.args.keys()):
			val = (getUrlArg(request, "zapstream") == 'true')
			comp_config.OpenWebif.webcache.zapstream.value = val
			comp_config.OpenWebif.webcache.zapstream.save()
		elif b"smallremote" in list(request.args.keys()):
			try:
				comp_config.OpenWebif.webcache.smallremote.value = getUrlArg(request, "smallremote")
				comp_config.OpenWebif.webcache.smallremote.save()
			except Exception:
				pass
		elif b"theme" in list(request.args.keys()):
			try:
				comp_config.OpenWebif.webcache.theme.value = getUrlArg(request, "theme")
				comp_config.OpenWebif.webcache.theme.save()
			except Exception:
				pass
		elif b"mepgmode" in list(request.args.keys()):
			try:
				comp_config.OpenWebif.webcache.mepgmode.value = int(request.args[b"mepgmode"][0])
				comp_config.OpenWebif.webcache.mepgmode.save()
			except ValueError:
				pass
		elif b"screenshot_high_resolution" in list(request.args.keys()):
			val = (getUrlArg(request, "screenshot_high_resolution") == 'true')
			comp_config.OpenWebif.webcache.screenshot_high_resolution.value = val
			comp_config.OpenWebif.webcache.screenshot_high_resolution.save()
		elif b"screenshot_refresh_auto" in list(request.args.keys()):
			val = (getUrlArg(request, "screenshot_refresh_auto") == 'true')
			comp_config.OpenWebif.webcache.screenshot_refresh_auto.value = val
			comp_config.OpenWebif.webcache.screenshot_refresh_auto.save()
		elif b"screenshot_refresh_time" in list(request.args.keys()):
			try:
				comp_config.OpenWebif.webcache.screenshot_refresh_time.value = int(request.args[b"screenshot_refresh_time"][0])
				comp_config.OpenWebif.webcache.screenshot_refresh_time.save()
			except ValueError:
				pass
		else:
			return {"result": False}
		return {"result": True}

	def P_getserviceref(self, request):
		"""
		Get the serviceref from name.


		.. http:get:: /api/getserviceref

			:query string name: service name to find
			:query string searchinBouquetsOnly: must be 'true'
			:query string bRef: define only one single bouquet where to find

		Args:
			request (twisted.web.server.Request): HTTP request object
		Returns:
			HTTP response with headers
		"""
		res = self.testMandatoryArguments(request, ["name"])
		if res:
			return res
		name = getUrlArg(request, "name")
		bRef = getUrlArg(request, "bRef")
		searchinBouquetsOnly = (getUrlArg(request, "searchinBouquetsOnly") == 'true')
		return getServiceRef(name, searchinBouquetsOnly, bRef)

	def P_getpicon(self, request):
		res = self.testMandatoryArguments(request, ["sRef"])
		if res:
			return res
		path = getUrlArg(request, "path")
		sRef = getUrlArg(request, "sRef")
		json = getUrlArg(request, "json")
		pp = getPicon(sRef, path, False)
		if pp is not None:
			if path is None:
				path = PICON_PATH
			link = pp
			pp = pp.replace("/picon/", path)
		if json == 'true':
			if pp:
				return {"result": True, "path": pp, "link": link}
			else:
				return {"result": False}
		else:
			self.isImage = True
			return pp


class ApiController(WebController):
	def __init__(self, session, path=""):
		WebController.__init__(self, session, path)

	def prePageLoad(self, request):
		self.isJson = True


from Plugins.Extensions.OpenWebif.vtiaddon import expand_basecontroller  # noqa: F401
