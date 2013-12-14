# -*- coding: utf-8 -*-

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
from models.services import getBouquets, getChannels, getChannelEpg
from urllib import quote

class MobileController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session

	def P_index(self, request):
		return {}

	def P_control(self, request):
		return {}
		
	def P_screenshot(self, request):
		return {}

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
		return getChannels(idbouquet, stype)

	def P_channelinfo(self, request):
		channelinfo = {}
		channelepg = {}
		if "sref" in request.args.keys():
			sref=request.args["sref"][0]
			channelepg = getChannelEpg(sref)
			# Detect if sRef contains a stream
			if ("://" in sref):
				# Repair sRef (URL part gets unquoted somewhere in between but MUST NOT)
				sref = ":".join(sref.split(':')[:10]) + ":" + quote(":".join(sref.split(':')[10:-1])) + ":" + sref.split(':')[-1]
				# Get service name from last part of the sRef
				channelinfo['sname'] = sref.split(':')[-1]
				# Use quoted sref when stream has EPG
				if len(channelepg['events']) > 1:
					channelepg["events"][0]["sref"] = sref
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
			return { "channelinfo": channelepg["events"][0], "channelepg": channelepg["events"] }
		else:
			# Make sure at least some basic channel info gets returned when there is no EPG
			return { "channelinfo": channelinfo, "channelepg": None }

	def P_satfinder(self, request):
		return {}

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
