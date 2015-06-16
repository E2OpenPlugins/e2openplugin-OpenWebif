# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from enigma import eEPGCache, eServiceReference
from Components.UsageConfig import preferredTimerPath, preferredInstantRecordPath
from Components.config import config
from Components.TimerSanityCheck import TimerSanityCheck
from RecordTimer import RecordTimerEntry, RecordTimer, parseEvent, AFTEREVENT
from ServiceReference import ServiceReference
from time import time, strftime, localtime, mktime
from urllib import unquote
from info import GetWithAlternative
from Plugins.Extensions.OpenWebif.__init__ import _

def getTimers(session):
	rt = session.nav.RecordTimer
	timers = []
	for timer in rt.timer_list + rt.processed_timers:
		descriptionextended = "N/A"
		filename = None
		nextactivation = None
		if timer.eit and timer.service_ref:
			event = eEPGCache.getInstance().lookupEvent(['EX', (str(timer.service_ref) , 2, timer.eit)])
			if event and event[0][0]:
				descriptionextended = event[0][0]

		try:
			filename = timer.Filename
		except Exception, e:
			pass

		try:
			nextactivation = timer.next_activation
		except Exception, e:
			pass

		disabled = 0
		if timer.disabled:
			disabled  = 1

		justplay = 0
		if timer.justplay:
			justplay  = 1

		if timer.dirname:
			dirname = timer.dirname
		else:
			dirname = "None"

		dontSave = 0
		if timer.dontSave:
			dontSave  = 1

		toggledisabled = 1
		if timer.disabled:
				toggledisabled = 0

		toggledisabledimg = "off"
		if timer.disabled:
				toggledisabledimg = "on"

		asrefs = ""
		achannels = GetWithAlternative(str(timer.service_ref), False)
		if achannels:
			asrefs = achannels

		vpsplugin_enabled = False
		vpsplugin_overwrite = False
		vpsplugin_time = -1
		if hasattr(timer, "vpsplugin_enabled"):
			vpsplugin_enabled = True if timer.vpsplugin_enabled else False
		if hasattr(timer, "vpsplugin_overwrite"):
			vpsplugin_overwrite = True if timer.vpsplugin_overwrite else False
		if hasattr(timer, "vpsplugin_time"):
			vpsplugin_time = timer.vpsplugin_time
			if not vpsplugin_time:
				vpsplugin_time = -1

		always_zap = -1
		if hasattr(timer,"always_zap"):
			if timer.always_zap:
				always_zap = 1
			else:
				always_zap = 0

		timers.append({
			"serviceref": str(timer.service_ref),
			"servicename": timer.service_ref.getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', ''),
			"eit": timer.eit,
			"name": timer.name,
			"description": timer.description,
			"descriptionextended": descriptionextended,
			"disabled": disabled,
			"begin": timer.begin,
			"end": timer.end,
			"duration": timer.end - timer.begin,
			"startprepare": timer.start_prepare,
			"justplay": justplay,
			"afterevent": timer.afterEvent,
			"dirname": dirname,
			"tags": " ".join(timer.tags),
			"logentries": timer.log_entries,
			"backoff": timer.backoff,
			"firsttryprepare": timer.first_try_prepare,
			"state": timer.state,
			"repeated": timer.repeated,
			"dontsave": dontSave,
			"cancelled": timer.cancelled,
			"toggledisabled": toggledisabled,
			"toggledisabledimg" : toggledisabledimg,
			"filename": filename,
			"nextactivation": nextactivation,
			"realbegin":strftime("%d.%m.%Y %H:%M", (localtime(float(timer.begin)))),
			"realend":strftime("%d.%m.%Y %H:%M", (localtime(float(timer.end)))),
			"asrefs": asrefs,
			"vpsplugin_enabled":vpsplugin_enabled,
			"vpsplugin_overwrite":vpsplugin_overwrite,
			"vpsplugin_time":vpsplugin_time,
			"always_zap":always_zap
		})

	return {
		"result": True,
		"timers": timers
	}

def addTimer(session, serviceref, begin, end, name, description, disabled, justplay, afterevent, dirname, tags, repeated, vpsinfo=None, logentries=None, eit=0, always_zap=-1):
	rt = session.nav.RecordTimer

	print "mao1", dirname

	if not dirname:
		dirname = preferredTimerPath()

	print "mao2", dirname

	try:
		timer = RecordTimerEntry(
			ServiceReference(serviceref),
			begin,
			end,
			name,
			description,
			eit,
			disabled,
			justplay,
			afterevent,
			dirname=dirname,
			tags=tags)

		timer.repeated = repeated

		if logentries:
			timer.log_entries = logentries

		conflicts = rt.record(timer)
		if conflicts:
			errors = []
			for conflict in conflicts:
				errors.append(conflict.name)

			return {
				"result": False,
				"message": _("Conflicting Timer(s) detected! %s") % " / ".join(errors)
			}
		#VPS
		if vpsinfo is not None:
			timer.vpsplugin_enabled = vpsinfo["vpsplugin_enabled"]
			timer.vpsplugin_overwrite = vpsinfo["vpsplugin_overwrite"]
			timer.vpsplugin_time = vpsinfo["vpsplugin_time"]

		if always_zap <> -1:
			if hasattr(timer,"always_zap"):
				timer.always_zap = always_zap == 1

	except Exception, e:
		print e
		return {
			"result": False,
			"message": _("Could not add timer '%s'!") % name
		}

	return {
		"result": True,
		"message": _("Timer '%s' added") % name
	}

def addTimerByEventId(session, eventid, serviceref, justplay, dirname, tags, vpsinfo, always_zap):
	event = eEPGCache.getInstance().lookupEventId(eServiceReference(serviceref), eventid)
	if event is None:
		return {
			"result": False,
			"message": _("EventId not found")
		}

	(begin, end, name, description, eit) = parseEvent(event)
	return addTimer(
		session,
		serviceref,
		begin,
		end,
		name,
		description,
		False,
		justplay,
		AFTEREVENT.AUTO,
		dirname,
		tags,
		False,
		vpsinfo,
		None,
		eit,
		always_zap
	)

# NEW editTimer function to prevent delete + add on change
# !!! This new function must be tested !!!! 
def editTimer(session, serviceref, begin, end, name, description, disabled, justplay, afterEvent, dirname, tags, repeated, channelOld, beginOld, endOld, vpsinfo, always_zap):
	# TODO: exception handling
	channelOld_str =  ':'.join(str(channelOld).split(':')[:11])
	rt = session.nav.RecordTimer
	for timer in rt.timer_list + rt.processed_timers:
		needed_ref = ':'.join(timer.service_ref.ref.toString().split(':')[:11]) == channelOld_str
		if needed_ref and int(timer.begin) == beginOld and int(timer.end) == endOld:
			timer.service_ref = ServiceReference(serviceref)
			# TODO: start end time check
			timer.begin = int(float(begin))
			timer.end = int(float(end))
			timer.name = name
			timer.description = description
			# TODO : EIT
			#timer.eit = eit
			timer.disabled = disabled
			timer.justplay = justplay
			timer.afterEvent = afterEvent
			timer.dirname = dirname
			timer.tags = tags
			timer.repeated = repeated
			timer.processRepeated()
			if vpsinfo is not None:
				timer.vpsplugin_enabled = vpsinfo["vpsplugin_enabled"]
				timer.vpsplugin_overwrite = vpsinfo["vpsplugin_overwrite"]
				timer.vpsplugin_time = vpsinfo["vpsplugin_time"]

			if always_zap <> -1:
				if hasattr(timer,"always_zap"):
					timer.always_zap = always_zap == 1

			# TODO: multi tuner test
			sanity = TimerSanityCheck(rt.timer_list, timer)
			conflicts = None
			if not sanity.check():
				conflicts = sanity.getSimulTimerList()
				if conflicts is not None:
					for conflict in conflicts:
						if conflict.setAutoincreaseEnd(entry):
							rt.timeChanged(conflict)
							if not sanity.check():
								conflicts = sanity.getSimulTimerList()
			if conflicts is None:
				rt.timeChanged(timer)
				return {
					"result": True,
					"message": _("Timer '%s' changed") % name
				}
			else:
				return {
					"result": False,
					"message": _("Timer '%s' not saved while Conflict") % name
				}

	return {
		"result": False,
		"message": _("Could not find timer '%s' with given start and end time!") % name
	}

def removeTimer(session, serviceref, begin, end):
	serviceref_str = ':'.join(str(serviceref).split(':')[:11])
	rt = session.nav.RecordTimer
	for timer in rt.timer_list + rt.processed_timers:
		needed_ref = ':'.join(timer.service_ref.ref.toString().split(':')[:11]) == serviceref_str
		if needed_ref and int(timer.begin) == begin and int(timer.end) == end:
			rt.removeEntry(timer)
			return {
				"result": True,
				"message": _("The timer '%s' has been deleted successfully") % timer.name
			}

	return {
		"result": False,
		"message": _("No matching Timer found")
	}

def toggleTimerStatus(session, serviceref, begin, end):
	serviceref = unquote(serviceref)
	serviceref_str = ':'.join(str(serviceref).split(':')[:11])
	rt = session.nav.RecordTimer
	for timer in rt.timer_list + rt.processed_timers:
		needed_ref = ':'.join(timer.service_ref.ref.toString().split(':')[:11]) == serviceref_str
		if needed_ref and int(timer.begin) == begin and int(timer.end) == end:
			if timer.disabled:
				timer.enable()
				effect = "enabled"
				sanity = TimerSanityCheck(rt.timer_list, timer)
				if not sanity.check():
					timer.disable()
					return {
						"result": False,
						"message": _("Timer '%s' not enabled while Conflict") % (timer.name)
					}
				elif sanity.doubleCheck():
					timer.disable()
					return {
						"result": False,
						"message": _("Timer '%s' already exists!") % (timer.name)
					}
			else:
				if timer.isRunning():
					return {
						"result": False,
						"message": _("The timer '%s' now recorded! Not disabled!") % (timer.name)
					}
				else:
					timer.disable()
					effect = "disabled"
			rt.timeChanged(timer)
			return {
				"result": True,
				"message": _("The timer '%s' has been %s successfully") % (timer.name, effect),
				"disabled": timer.disabled
			}

	return {
		"result": False,
		"message": _("No matching Timer found")
	}

def cleanupTimer(session):
	session.nav.RecordTimer.cleanup()
	return {
		"result": True,
		"message": _("List of Timers has been cleaned")
	}

def writeTimerList(session):
	session.nav.RecordTimer.saveTimer()
	return {
		"result": True,
		"message": _("TimerList has been saved")
	}

def recordNow(session, infinite):
	rt = session.nav.RecordTimer
	serviceref = session.nav.getCurrentlyPlayingServiceReference().toString()

	try:
		event = session.nav.getCurrentService().info().getEvent(0)
	except Exception:
		event = None

	if not event and not infinite:
		return {
			"result": False,
			"message": _("No event found! Not recording!")
		}

	if event:
		(begin, end, name, description, eit) = parseEvent(event)
		begin = time()
		msg = _("Instant record for current Event started")
	else:
		name = "instant record"
		description = ""
		eit = 0

	if infinite:
		begin = time()
		end = begin + 3600 * 10
		msg = _("Infinite Instant recording started")

	timer = RecordTimerEntry(
		ServiceReference(serviceref),
		begin,
		end,
		name,
		description, 
		eit,
		False,
		False,
		0,
		dirname=preferredInstantRecordPath()
	)
	timer.dontSave = True

	if rt.record(timer):
		return {
			"result": False,
			"message": _("Timer conflict detected! Not recording!")
		}
	nt = {
		"serviceref": str(timer.service_ref),
		"servicename": timer.service_ref.getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', ''),
		"eit": timer.eit,
		"name": timer.name,
		"begin": timer.begin,
		"end": timer.end,
		"duration": timer.end - timer.begin
	}

	return {
		"result": True,
		"message": msg,
		"newtimer": nt
	}


def tvbrowser(session, request):
	if "name" in request.args:
		name = request.args['name'][0]
	else:
		name = "Unknown"

	if "description" in request.args:
		description = "".join(request.args['description'][0])
		description = description.replace("\n", " ")
	else:
		description = ""

	disabled = False
	if "disabled" in request.args:
		if (request.args['disabled'][0] == "1"):
			disabled = True

	justplay = False 
	if 'justplay' in request.args:
		if (request.args['justplay'][0] == "1"):
			justplay = True

	afterevent = 3
	if 'afterevent' in request.args:
		if (request.args['afterevent'][0] == "0") or (request.args['afterevent'][0] == "1") or (request.args['afterevent'][0] == "2"):
			afterevent = int(request.args['afterevent'][0])


	location = preferredTimerPath()
	if "dirname" in request.args:
		location = request.args['dirname'][0]

	if not location:
		location = "/hdd/movie/"

	begin = int(mktime((int(request.args['syear'][0]), int(request.args['smonth'][0]), int(request.args['sday'][0]), int(request.args['shour'][0]), int(request.args['smin'][0]), 0, 0, 0, -1)))
	end = int(mktime((int(request.args['syear'][0]), int(request.args['smonth'][0]), int(request.args['sday'][0]), int(request.args['ehour'][0]), int(request.args['emin'][0]), 0, 0, 0, -1)))	

	if end < begin:
		end += 86400

	repeated = int(request.args['repeated'][0])
	if repeated == 0:
		for element in ("mo", "tu", "we", "th", "fr", "sa", "su", "ms", "mf"):
			if element in request.args:
				number = request.args[element][0] or 0
				del request.args[element][0]
				repeated = repeated + int(number)
		if repeated > 127:
			repeated = 127
	repeated = repeated

	if request.args['sRef'][0] is None:
		return {
		 "result": False, 
		 "message": _("Missing requesteter: sRef") 
		}
	else:
		takeApart = unquote(request.args['sRef'][0]).decode('utf-8', 'ignore').encode('utf-8').split('|')
		sRef = takeApart[1]

	tags = []
	if 'tags' in request.args and request.args['tags'][0]:
		tags = unescape(request.args['tags'][0]).split(' ')

	if request.args['command'][0] == "add":
		del request.args['command'][0]
		return addTimer(session, sRef, begin, end, name, description, disabled, justplay, afterevent, location , tags , repeated)
	elif request.args['command'][0] == "del":
		del request.args['command'][0]
		return removeTimer(session, sRef, begin, end)
	elif request.args['command'][0] == "change":
		del request.args['command'][0]
		return editTimer(session, sRef, begin, end, name, description, disabled, justplay, afterevent, location, tags, repeated, begin, end, serviceref)
	else:
		return {
		 "result": False,
		 "message": _("Unknown command: '%s'") % request.args['command'][0]
		}

def getPowerTimer(session):
	
	try:
		from PowerTimer import TIMERTYPE ,AFTEREVENT

		timers = []
		timer_list  = session.nav.PowerTimer.timer_list
		processed_timers  = session.nav.PowerTimer.processed_timers

		for timer in timer_list + processed_timers:
			list = []
			for time, code, msg in timer.log_entries:
				list.append({
					"code": str(code),
					"time": str(time),
					"msg": str(msg)
					})
			timers.append({
			"timertype": str(timer.timerType),
			"timertypename": str({
				TIMERTYPE.WAKEUP: "wakeup",
				TIMERTYPE.WAKEUPTOSTANDBY: "wakeuptostandby",
				TIMERTYPE.AUTOSTANDBY: "autostandby",
				TIMERTYPE.AUTODEEPSTANDBY: "autodeepstandby",
				TIMERTYPE.STANDBY: "standby",
				TIMERTYPE.DEEPSTANDBY: "deepstandby",
				TIMERTYPE.REBOOT: "reboot",
				TIMERTYPE.RESTART: "restart"
				}[timer.timerType]),
			"begin": str(int(timer.begin)),
			"end": str(int(timer.end)),
			"repeated": str(int(timer.repeated)),
			"afterevent": str(timer.afterEvent),
			"aftereventname": str({
				AFTEREVENT.NONE: "nothing",
				AFTEREVENT.WAKEUPTOSTANDBY: "wakeuptostandby",
				AFTEREVENT.STANDBY: "standby",
				AFTEREVENT.DEEPSTANDBY: "deepstandby"
				}[timer.afterEvent]),
			"disabled": str(int(timer.disabled)),
			"autosleepinstandbyonly": str(timer.autosleepinstandbyonly),
			"autosleepdelay": str(timer.autosleepdelay),
			"autosleeprepeat": str(timer.autosleeprepeat),
			"logentries" : list
			})

		return {
			"result": True,
			"timers": timers
		}
	except Exception, e:
		print e
		return {
			"result": False,
			"message": _("PowerTimer feature not available")
		}

def setPowerTimer(session, request):

	timertype = 0
	if "timertype" in request.args.keys() and request.args["afterevent"][0] in ["0", "1", "2", "3","4","5","6","7"]:
		cmd = int(request.args["timertype"][0])
	begin = int(time() + 60)
	if "begin" in request.args.keys():
		begin = int(request.args["begin"][0])
	end = int(time() + 120)
	if "end" in request.args.keys():
		end = int(request.args["end"][0])
	disabled = 0
	if "disabled" in request.args.keys():
		disabled = long(request.args["disabled"][0])
	repeated = False
	if "repeated" in request.args.keys():
		repeated = request.args["repeated"][0] == "1"
	afterevent = 0
	if "afterevent" in request.args.keys() and request.args["afterevent"][0] in ["0", "1", "2", "3"]:
		afterevent = int(request.args["afterevent"][0])
	autosleepinstandbyonly = "no"
	if "autosleepinstandbyonly" in request.args.keys():
		autosleepinstandbyonly = request.args["autosleepinstandbyonly"][0]
	autosleepdelay = "0"
	if "autosleepdelay" in request.args.keys():
		autosleepdelay = request.args["autosleepdelay"][0]
	autosleeprepeat = "once"
	if "autosleeprepeat" in request.args.keys():
		autosleeprepeat = request.args["autosleeprepeat"][0]


	# find
	entry = None
	timers = []
	timer_list  = session.nav.PowerTimer.timer_list
	processed_timers  = session.nav.PowerTimer.processed_timers
	for timer in timer_list + processed_timers:
		if timer.timerType == timertype:
			if timer.begin == begin:
				if timer.end == end:
					entry = timer

	# create new Timer
	if entry == None:
		entry = PowerTimerEntry(begin, end, disabled, afterevent, timertype)
		entry.repeated = int(repeated)
		entry.autosleepinstandbyonly = autosleepinstandbyonly
		entry.autosleepdelay = int(autosleepdelay)
		entry.autosleeprepeat = autosleeprepeat
		print "[PowerTimer]",str(entry)
#	timers = []
#	timer_list  = session.nav.PowerTimer.timer_list
#	processed_timers  = session.nav.PowerTimer.processed_timers

	#change
#	pos = 0
#	for timer in timer_list + processed_timers:
#		pos+=1
#		if id == str(pos):

	return {
		"result": True,
		"message": "TODO"
	}


def getSleepTimer(session):
	if hasattr(session.nav, "SleepTimer"):
		try:
			return {
				"enabled": session.nav.SleepTimer.isActive(),
				"minutes": session.nav.SleepTimer.getCurrentSleepTime(),
				"action": config.SleepTimer.action.value,
				"message": _("Sleeptimer is enabled") if session.nav.SleepTimer.isActive() else _("Sleeptimer is disabled")
			}
		except Exception, e:
			return {
				"result": False,
				"message": _("SleepTimer error")
			}
	else:
		# use powertimer , this works only if there is one of the standby OR deepstandby entries
		# todo : do not use repeated entries
		try:
			timer_list = session.nav.PowerTimer.timer_list
			for timer in timer_list:
				timertype = str(timer.timerType)
				if timertype in ["2","3"]:
					action = "standby"
					if timertype == "3":
						action="shutdown"
					minutes = str(timer.autosleepdelay)
					enabled = True
					if int(timer.disabled) == 1:
						enabled = False
					return {
						"enabled": enabled,
						"minutes": minutes,
						"action": action,
						"message": _("Sleeptimer is enabled") if enabled else _("Sleeptimer is disabled")
					}
					break
		except Exception, e:
			return {
				"result": False,
				"message": _("SleepTimer error")
			}

def setSleepTimer(session, time, action, enabled):
	if action not in ["shutdown", "standby"]:
		action = "standby"

	if hasattr(session.nav, "SleepTimer"):
		try:
			ret = getSleepTimer(session)
			from Screens.Standby import inStandby
			if inStandby is not None:
				ret["message"] = _("ERROR: Cannot set SleepTimer while device is in Standby-Mode")
				return ret
			if enabled == False:
				session.nav.SleepTimer.clear()
				ret = getSleepTimer(session)
				ret["message"] = _("Sleeptimer has been disabled")
				return ret
			config.SleepTimer.action.value = action
			config.SleepTimer.action.save()
			session.nav.SleepTimer.setSleepTime(time)
			ret = getSleepTimer(session)
			ret["message"] = _("Sleeptimer set to %d minutes") % time
			return ret
		except Exception, e:
			return {
				"result": False,
				"message": _("SleepTimer Error")
			}
	else:
		# use powertimer
		# todo activate powertimer
		try:
			done = False
			timer_list = session.nav.PowerTimer.timer_list
			begin = int(time() + 60)
			end = int(time() + 120)
			for timer in timer_list:
				timertype = str(timer.timerType)
				if timertype == "2" and action == "standby":
					if enabled == False:
						timer.disabled = True
					else:
						timer.disabled = False
						timer.autosleepdelay = int(time)
						timer.begin = begin
						timer.end = end
					done = True
					break
				if timertype == "3" and action == "shutdown":
					if enabled == False:
						timer.disabled = True
					else:
						timer.disabled = False
						timer.autosleepdelay = int(time)
						timer.begin = begin
						timer.end = end
					done = True
					break
				if timertype == "3" and action == "standby":
					if enabled == False:
						timer.disabled = True
					else:
						timer.disabled = False
						timer.autosleepdelay = int(time)
						timer.timerType=2
						timer.begin = begin
						timer.end = end
					done = True
					break
				if timertype == "2" and action == "shutdown":
					if enabled == False:
						timer.disabled = True
					else:
						timer.disabled = False
						timer.autosleepdelay = int(time)
						timer.timerType=3
						timer.begin = begin
						timer.end = end
					done = True
					break
			
			if done:
				return {
					"result": True,
					"message": _("Sleeptimer set to %d minutes") % time if enabled else _("Sleeptimer has been disabled")
				}
			if enabled:
				begin = int(time() + 60)
				end = int(time() + 120)
				timertype = 2
				if action == "shutdown":
					timertype = 3
				entry = PowerTimerEntry(begin, end, False, 0, timertype)
				entry.repeated = 0
				entry.autosleepdelay = time
				return {
					"result": True,
					"message": _("Sleeptimer set to %d minutes") % time
				}
			else:
				return {
					"result": True,
					"message": _("Sleeptimer has been disabled")
				}
		except Exception, e:
			return {
				"result": False,
				"message": _("SleepTimer Error")
			}

def getVPSChannels(session):
	vpsfile="/etc/enigma2/vps.xml"
	from Tools.Directories import fileExists
	if fileExists(vpsfile):
		try:
			import xml.etree.cElementTree
			vpsfile = file(vpsfile, 'r')
			vpsdom = xml.etree.cElementTree.parse(vpsfile)
			vpsfile.close()
			xmldata = vpsdom.getroot()
			channels = []
			for ch in xmldata.findall("channel"):
				channels.append({
					"serviceref": ch.attrib["serviceref"],
					"has_pdc": ch.attrib["has_pdc"],
					"last_check": ch.attrib["last_check"],
					"default_vps": ch.attrib["default_vps"]
				})
			return {
				"result": True,
				"channels": channels
			}
		except Exception, e:
			return {
				"result": False,
				"message": _("Error parsing vps.xml")
			}
			
	return {
			"result": False,
			"message": _("VPS plugin not found")
	}
	
	