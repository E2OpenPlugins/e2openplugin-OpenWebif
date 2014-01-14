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
from RecordTimer import RecordTimerEntry, RecordTimer, parseEvent, AFTEREVENT
from ServiceReference import ServiceReference
from time import time, strftime, localtime, mktime
from urllib import unquote
from info import GetWithAlternative

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
			vpsplugin_enabled = True
		if hasattr(timer, "vpsplugin_overwrite"):
			vpsplugin_overwrite = True
		if hasattr(timer, "vpsplugin_time"):
			vpsplugin_time = timer.vpsplugin_time
			if not vpsplugin_time:
				vpsplugin_time = -1

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
			"vpsplugin_time":vpsplugin_time
		})
		
	return {
		"result": True,
		"timers": timers
	}

def addTimer(session, serviceref, begin, end, name, description, disabled, justplay, afterevent, dirname, tags, repeated, vpsinfo=None, logentries=None, eit=0):
	serviceref = unquote(serviceref)
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
				"message": "Conflicting Timer(s) detected! %s" % " / ".join(errors)
			}
	except Exception, e:
		print e
		return {
			"result": False,
			"message": "Could not add timer '%s'!" % name
		}
		
	return {
		"result": True,
		"message": "Timer '%s' added" % name
	}

def addTimerByEventId(session, eventid, serviceref, justplay, dirname, tags, vpsinfo):
	serviceref = unquote(serviceref)
	event = eEPGCache.getInstance().lookupEventId(eServiceReference(serviceref), eventid)
	if event is None:
		return {
			"result": False,
			"message": "EventId not found"
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
		eit
	)
	
def editTimer(session, serviceref, begin, end, name, description, disabled, justplay, afterevent, dirname, tags, repeated, channelOld, beginOld, endOld, vpsinfo):
	rt = session.nav.RecordTimer
	for timer in rt.timer_list + rt.processed_timers:
		if str(timer.service_ref) == channelOld and int(timer.begin) == beginOld and int(timer.end) == endOld:
			rt.removeEntry(timer)
			res = addTimer(
				session,
				serviceref,
				begin,
				end,
				name,
				description,
				disabled,
				justplay,
				afterevent,
				dirname,
				tags,
				repeated,
				vpsinfo,
				timer.log_entries
			)
			if not res["result"]:
				rt.record(timer)
			return res
			
	return {
		"result": False,
		"message": "Could not find timer '%s' with given start and end time!" % name
	}

def removeTimer(session, serviceref, begin, end):
	serviceref = unquote(serviceref)
	rt = session.nav.RecordTimer
	for timer in rt.timer_list + rt.processed_timers:
		if str(timer.service_ref) == serviceref and int(timer.begin) == begin and int(timer.end) == end:
			rt.removeEntry(timer)
			return {
				"result": True,
				"message": "The timer '%s' has been deleted successfully" % timer.name
			}
			
	return {
		"result": False,
		"message": "No matching Timer found"
	}
	
def toggleTimerStatus(session, serviceref, begin, end):
	serviceref = unquote(serviceref)
	rt = session.nav.RecordTimer
	for timer in rt.timer_list + rt.processed_timers:
		if str(timer.service_ref) == serviceref and int(timer.begin) == begin and int(timer.end) == end:
			if timer.disabled:
				timer.enable()
				effect = "enabled"
			else:
				timer.disable()
				effect = "disabled"
			return {
				"result": True,
				"message": "The timer '%s' has been %s successfully" % (timer.name, effect),
				"disabled": timer.disabled
			}
			
	return {
		"result": False,
		"message": "No matching Timer found"
	}
	
def cleanupTimer(session):
	session.nav.RecordTimer.cleanup()

	return {
		"result": True,
		"message": "List of Timers has been cleaned"
	}

def writeTimerList(session):
	session.nav.RecordTimer.saveTimer()
	return {
		"result": True,
		"message": "TimerList has been saved"
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
			"message": "No event found! Not recording!"
		}
		
	if event:
		(begin, end, name, description, eit) = parseEvent(event)
		begin = time()
		msg = "Instant record for current Event started"
	else:
		name = "instant record"
		description = ""
		eit = 0
		
	if infinite:
		begin = time()
		end = begin + 3600 * 10
		msg = "Infinite Instant recording started"
		
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
			"message": "Timer conflict detected! Not recording!"
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
		 "message": "Missing requesteter: sRef" 
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
		 "message": "Unknown command: '%s'" % request.args['command'][0]
		}

def getSleepTimer(session):
	return {
		"enabled": session.nav.SleepTimer.isActive(),
		"minutes": session.nav.SleepTimer.getCurrentSleepTime(),
		"action": config.SleepTimer.action.value,
		"message": "Sleeptimer is enabled" if session.nav.SleepTimer.isActive() else "Sleeptimer is disabled"
	}
	
def setSleepTimer(session, time, action, enabled):
	ret = getSleepTimer(session)
	from Screens.Standby import inStandby
	if inStandby is not None:
		ret["message"] = "ERROR: Cannot set SleepTimer while device is in Standby-Mode"
		return ret
		
	if enabled == False:
		session.nav.SleepTimer.clear()
		ret = getSleepTimer(session)
		ret["message"] = "Sleeptimer has been disabled"
		return ret
		
	if action not in ["shutdown", "standby"]:
		action = "standby"
		
	config.SleepTimer.action.value = action
	config.SleepTimer.action.save()
	session.nav.SleepTimer.setSleepTime(time)
	
	ret = getSleepTimer(session)
	ret["message"] = "Sleeptimer set to %d minutes" % time
	return ret
	
