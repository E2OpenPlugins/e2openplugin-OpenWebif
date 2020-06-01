# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: MobileController
##########################################################################
# Copyright (C) 2011 - 2018 E2OpenPlugins
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

from base import BaseController
from models.movies import getMovieList
from models.timers import getTimers
from models.services import getBouquets, getChannels, getChannelEpg, getEvent, getPicon
from urllib import quote
from time import localtime, strftime

from defaults import TRANSCODING


class MobileController(BaseController):
	"""
	Mobile Web Controller
	"""
	def __init__(self, session, path=""):
		BaseController.__init__(self, path=path, session=session, isMobile=True)

	def NoDataRender(self):
		"""
		mobile requests with no extra data
		"""
		return ['index', 'control', 'screenshot', 'satfinder', 'about']

	def P_bouquets(self, request):
		stype = "tv"
		if "stype" in request.args.keys():
			stype = request.args["stype"][0]
		return getBouquets(stype)

	def P_channels(self, request):
		stype = "tv"
		idbouquet = "ALL"
		if "stype" in request.args.keys():
			stype = request.args["stype"][0]
		if "id" in request.args.keys():
			idbouquet = request.args["id"][0]
		channels = getChannels(idbouquet, stype)
		channels['transcoding'] = TRANSCODING
		return channels

	def P_channelinfo(self, request):
		channelinfo = {}
		channelepg = {}
		if "sref" in request.args.keys():
			sref = request.args["sref"][0]
			channelepg = getChannelEpg(sref)
			# Detect if sRef contains a stream
			if ("://" in sref):
				# Repair sRef (URL part gets unquoted somewhere in between but MUST NOT)
				sref = ":".join(sref.split(':')[:10]) + ":" + quote(":".join(sref.split(':')[10:-1])) + ":" + sref.split(':')[-1]
				# Get service name from last part of the sRef
				channelinfo['sname'] = sref.split(':')[-1]
				# Use quoted sref when stream has EPG
				if len(channelepg['events']) > 1:
					channelepg['events'][0]['sref'] = sref
			else:
				# todo: Get service name
				channelinfo['sname'] = ""
			# Assume some sane blank defaults
			channelinfo['sref'] = sref
			channelinfo['title'] = ""
			channelinfo['picon'] = ""
			channelinfo['shortdesc'] = ""
			channelinfo['longdesc'] = ""
			channelinfo['begin'] = 0
			channelinfo['end'] = 0

		# Got EPG information?
		if len(channelepg['events']) > 1:
			# Return the EPG
			return {"channelinfo": channelepg["events"][0], "channelepg": channelepg["events"]}
		else:
			# Make sure at least some basic channel info gets returned when there is no EPG
			return {"channelinfo": channelinfo, "channelepg": None}

	def P_eventview(self, request):
		event = {}
		event['sref'] = ""
		event['title'] = ""
		event['picon'] = ""
		event['shortdesc'] = ""
		event['longdesc'] = ""
		event['begin'] = 0
		event['end'] = 0
		event['duration'] = 0
		event['channel'] = ""

		if "eventid" in request.args.keys():
			eventid = request.args["eventid"][0]
		if "eventref" in request.args.keys():
			ref = request.args["eventref"][0]
		if ref and eventid:
			event = getEvent(ref, eventid)['event']
			event['id'] = eventid
			event['picon'] = getPicon(ref)
			event['end'] = event['begin'] + event['duration']
			event['duration'] = int(event['duration'] / 60)
			event['start'] = event['begin']
			event['begin'] = strftime("%H:%M", (localtime(event['begin'])))
			event['end'] = strftime("%H:%M", (localtime(event['end'])))

		return {"event": event}

	def P_timerlist(self, request):
		return getTimers(self.session)

	def P_movies(self, request):
		movies = getMovieList(request.args)
		movies['transcoding'] = TRANSCODING
		return movies

	def P_remote(self, request):
		try:
			from Components.RcModel import rc_model
			REMOTE = rc_model.getRcFolder() + "/remote"
		except:
			from models.owibranding import rc_model
			REMOTE = rc_model().getRcFolder()
		return { "remote": REMOTE }
