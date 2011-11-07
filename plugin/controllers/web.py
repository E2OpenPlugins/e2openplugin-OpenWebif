##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from models.info import getInfo
from models.services import getCurrentService, getBouquets, getChannels, getSatellites
from models.volume import getVolumeStatus, setVolumeUp, setVolumeDown, setVolumeMute, setVolume
from models.audiotrack import getAudioTracks, setAudioTrack
from base import BaseController

class WebController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session
		
	def prePageLoad(self, request):
		request.setHeader("content-type", "text/xml")
				
	def P_about(self, request):
		return {
			"info": getInfo(),
			"service": getCurrentService(self.session)
		}
	
	def P_vol(self, request):
		if "set" not in request.args.keys() or request.args["set"][0] == "state":
			volume = getVolumeStatus()
			volume["result"] = True
			volume["message"] = "Status"
		elif request.args["set"][0] == "up":
			volume = setVolumeUp()
			volume["result"] = True
			volume["message"] = "Volume changed"
		elif request.args["set"][0] == "down":
			volume = setVolumeDown()
			volume["result"] = True
			volume["message"] = "Volume changed"
		elif request.args["set"][0] == "mute":
			volume = setVolumeMute()
			volume["result"] = True
			volume["message"] = "Mute toggled"
		elif request.args["set"][0][:3] == "set":
			try:
				value = int(request.args["set"][0][3:])
				volume = setVolume(value)
				volume["result"] = True
				volume["message"] = "Volume set to %i" % int(request.args["set"][0][3:])
			except Exception, e:
				volume = getVolumeStatus()
				volume["result"] = False
				volume["message"] = "Wrong parameter format 'set=%s'. Use set=set15 " % request.args["set"][0]
		else:
			volume = getVolumeStatus()
			volume["result"] = False
			volume["message"] = "Unknown Volume command %s" % request.args["set"][0]
		return volume
		
	def P_getaudiotracks(self, request):
		return getAudioTracks(self.session)
	
	def P_selectaudiotrack(self, request):
		try:
			id = int(request.args["id"][0])
		except Exception, e:
			id = -1
			
		return setAudioTrack(self.session, id)