##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Tools.Directories import fileExists

from models.services import getCurrentService, getBouquets, getChannels, getSatellites, getProviders, getEventDesc, getChannelEpg, getSearchEpg
from models.info import getInfo, getPublicPath
from base import BaseController

class AjaxController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session
		
	def P_current(self, request):
		return getCurrentService(self.session)
		
	def P_bouquets(self, request):
		return getBouquets()
		
	def P_providers(self, request):
		return getProviders()
		
	def P_satellites(self, request):
		return getSatellites()
	
		
	def P_channels(self, request):
		if "id" in request.args.keys():
			channels = getChannels(request.args["id"][0])
		else:
			channels = getChannels()
		return channels
		
	def P_eventdescription(self, request):
		return getEventDesc(request.args["sref"][0], request.args["idev"][0])
		
		
	def P_about(self, request):
		return {}
	
	def P_boxinfo(self, request):
		info = getInfo()
		if fileExists(getPublicPath("/images/boxes/" + info["model"] + ".jpg")):
			info["boximage"] = info["model"] + ".jpg"
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
			

