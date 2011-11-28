##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from models.info import getInfo, getCurrentTime , getStatusInfo, getFrontendStatus
from models.services import getCurrentService, getBouquets, getServices, getChannels, getSatellites, getBouquetEpg, getBouquetNowNextEpg, getSearchEpg, getChannelEpg, getNowNextEpg, getSearchSimilarEpg
from models.volume import getVolumeStatus, setVolumeUp, setVolumeDown, setVolumeMute, setVolume
from models.audiotrack import getAudioTracks, setAudioTrack
from models.control import zapService, remoteControl, setPowerState
from models.locations import getLocations, getCurrentLocation, addLocation, removeLocation
from models.timers import getTimers, addTimer, addTimerByEventId, editTimer, removeTimer, cleanupTimer, writeTimerList, recordNow
from models.message import sendMessage
from models.movies import getMovieList

from base import BaseController

class WebController(BaseController):
	def __init__(self, session, path = ""):
		BaseController.__init__(self, path)
		self.session = session
		
	def prePageLoad(self, request):
		request.setHeader("content-type", "text/xml")
		
	def testMandatoryArguments(self, request, keys):
		for key in keys:
			if key not in request.args.keys():
				return {
					"result": False,
					"message": "Missing mandatory parameter '%s'" % key
				}
		
			if len(request.args[key][0]) == 0:
				return {
					"result": False,
					"message": "The parameter '%s' can't be empty" % key
				}
		
		return None
		
	def P_about(self, request):
		return {
			"info": getInfo(),
			"service": getCurrentService(self.session)
		}

	def P_statusinfo(self, request):
		return getStatusInfo(self)

	def P_signal(self, request):
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
				res["message"] = "Wrong parameter format 'set=%s'. Use set=set15 " % request.args["set"][0]
				return rets
				
		res = getVolumeStatus()
		res["result"] = False
		res["message"] = "Unknown Volume command %s" % request.args["set"][0]
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
				"message": "The parameter 'command' must be a number"
			}
			
		type = ""
		rcu = ""
		if "type" in request.args.keys():
			type = request.args["type"][0]
			
		if "rcu" in request.args.keys():
			rcu = request.args["rcu"][0]
			
		return remoteControl(id, type, rcu)

	def P_powerstate(self, request):
		res = self.testMandatoryArguments(request, ["newstate"])
		if res:
			return {
				"result": False,
				"message": "Missing parameter 'newstate'"
			}

		return setPowerState(self.session, request.args["newstate"][0])

	def P_getlocations(self, request):
		return getLocations()
		
	def P_getcurrlocation(self, request):
		return getCurrentLocation()

	def P_getservices(self, request):
		if "sRef" in request.args.keys():
			sRef = request.args["sRef"][0]
		else:
			sRef = ""
		
		return getServices(sRef)

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
		
		return removeLocation(request.args["dirname"][0])

	def P_message(self, request):
		return sendMessage(self, request)

	def P_movielist(self, request):
		if "dirname" in request.args.keys():
			movies = getMovieList(request.args["dirname"][0])
		else:
			movies = getMovieList()
		return movies

	def P_timerlist(self, request):
		return getTimers(self.session)
		
	def P_timeradd(self, request):
		res = self.testMandatoryArguments(request, ["sRef", "begin", "end", "name", "description"])
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
			
		repeated = False
		if "repeated" in request.args.keys() and request.args["afterevent"][0] in ["1", "2", "3"]:
			repeated = request.args["repeated"][0] == "1"
			
		return addTimer(
			self.session,
			request.args["sRef"][0],
			request.args["begin"][0],
			request.args["end"][0],
			request.args["name"][0],
			request.args["description"][0],
			disabled,
			justplay,
			afterevent,
			dirname,
			tags,
			repeated
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
			
		return addTimerByEventId(
			self.session,
			eventid,
			request.args["sRef"][0],
			justplay,
			dirname,
			tags,
		)

	def P_timerchange(self, request):
		res = self.testMandatoryArguments(request, ["sRef", "begin", "end", "name", "description", "channelOld", "beginOld", "endOld"])
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
			
		repeated = False
		if "repeated" in request.args.keys() and request.args["afterevent"][0] in ["1", "2", "3"]:
			repeated = request.args["repeated"][0] == "1"
			
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
			
		return editTimer(
			self.session,
			request.args["sRef"][0],
			request.args["begin"][0],
			request.args["end"][0],
			request.args["name"][0],
			request.args["description"][0],
			disabled,
			justplay,
			afterevent,
			dirname,
			tags,
			repeated,
			request.args["channelOld"][0],
			beginOld,
			endOld
		)
		
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
		
	def P_recordnow(self, request):
		infinite = False
		if "undefinitely" in request.args.keys() or "infinite" in request.args.keys():
			infinite = True
		return recordNow(self.session, infinite)
		
	def P_currenttime(self, request):
		return getCurrentTime()
		
	def P_deviceinfo(self, request):
		return getInfo()
		
	def P_epgbouquet(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
			
		begintime = -1
		if "time" in request.args.keys():
			try:
				begintime = int(request.args["time"][0])
			except Exception, e:
				pass
		
		return getBouquetEpg(request.args["bRef"][0], begintime)
		
	def P_epgmulti(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
			
		begintime = -1
		if "time" in request.args.keys():
			try:
				begintime = int(request.args["time"][0])
			except Exception, e:
				pass
		
		endtime = -1
		if "endTime" in request.args.keys():
			try:
				endtime = int(request.args["endTime"][0])
			except Exception, e:
				pass
				
		return getBouquetEpg(request.args["bRef"][0], begintime, endtime)
		
	def P_epgnow(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
			
		return getBouquetNowNextEpg(request.args["bRef"][0], 0)
		
	def P_epgnext(self, request):
		res = self.testMandatoryArguments(request, ["bRef"])
		if res:
			return res
			
		return getBouquetNowNextEpg(request.args["bRef"][0], 1)
		
	def P_epgsearch(self, request):
		res = self.testMandatoryArguments(request, ["search"])
		if res:
			return res
			
		return getSearchEpg(request.args["search"][0])
		
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
			except Exception, e:
				pass
		
		endtime = -1
		if "endTime" in request.args.keys():
			try:
				endtime = int(request.args["endTime"][0])
			except Exception, e:
				pass
				
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
		except Exception, e:
			return {
				"result": False,
				"message": "The parameter 'eventid' must be a number"
			}
			
		return getSearchSimilarEpg(request.args["sRef"][0], eventid)
		
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
		return {
			"info": info,
			"now": now,
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
