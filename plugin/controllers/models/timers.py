# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: timers
##########################################################################
# Copyright (C) 2011 - 2020 E2OpenPlugins
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

from __future__ import print_function
import six
from enigma import eServiceReference
from Components.UsageConfig import preferredTimerPath, preferredInstantRecordPath
from Components.config import config
from Components.TimerSanityCheck import TimerSanityCheck
from RecordTimer import RecordTimerEntry, parseEvent
from ServiceReference import ServiceReference
from Screens.InfoBar import InfoBar
from time import time, strftime, localtime, mktime
from six.moves.urllib.parse import unquote
from Plugins.Extensions.OpenWebif.controllers.models.info import GetWithAlternative, getInfo
from Plugins.Extensions.OpenWebif.controllers.i18n import _
from Plugins.Extensions.OpenWebif.controllers.utilities import removeBad
from Plugins.Extensions.OpenWebif.controllers.epg import EPG


def adjustStartEndTimes(event, description=True):
	begin = event.start['timestamp']
	end = event.end['timestamp']
	begin -= config.recording.margin_before.value * 60
	end += config.recording.margin_after.value * 60
	return (begin, end)  # We should also report the margins!


def FuzzyTime(t, inPast=False):
	d = localtime(t)
	nt = time()
	n = localtime()
	dayOfWeek = (_("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat"), _("Sun"))

	if d[:3] == n[:3]:
		# same day
		date = _("Today")
	elif d[0] == n[0] and d[7] == n[7] - 1 and inPast:
		# won't work on New Year's day
		date = _("Yesterday")
	elif ((t - nt) < 7 * 86400) and (nt < t) and not inPast:
		# same week (must be future)
		date = dayOfWeek[d[6]]
	elif d[0] == n[0]:
		# same year
		if inPast:
			# I want the day in the movielist
			date = _("%s %02d.%02d.") % (dayOfWeek[d[6]], d[2], d[1])
		else:
			date = _("%02d.%02d.") % (d[2], d[1])
	else:
		date = _("%02d.%02d.%d") % (d[2], d[1], d[0])

	timeres = _("%02d:%02d") % (d[3], d[4])

	return date, timeres


def getTimers(session):
	rt = session.nav.RecordTimer
	epg = EPG()
	timers = []
	for timer in rt.timer_list + rt.processed_timers:
		if hasattr(timer, "wakeup_t"):
			energytimer = timer.wakeup_t or timer.standby_t or timer.shutdown_t or timer.fnc_t != "off" or 0
			if energytimer:
				continue

		descriptionextended = "N/A"
		filename = None
		nextactivation = None
		if timer.eit and timer.service_ref:
			descriptionextended = epg.getEventDescription(timer.service_ref, timer.eit)

		try:
			filename = timer.Filename
		except Exception:
			pass

		try:
			nextactivation = timer.next_activation
		except Exception:
			pass

		disabled = 0
		if timer.disabled:
			disabled = 1

		justplay = 0
		if timer.justplay:
			justplay = 1

		if hasattr(timer, "allow_duplicate"):
			allow_duplicate = timer.allow_duplicate and 1 or 0
		else:
			allow_duplicate = 1

		autoadjust = -1
		if hasattr(timer, "autoadjust"):
			autoadjust = timer.autoadjust and 1 or 0
		elif hasattr(config.recording, "adjust_time_to_event"):
			autoadjust = config.recording.adjust_time_to_event.value and 1 or 0

		if timer.dirname:
			dirname = timer.dirname
		else:
			dirname = "None"

		dontSave = 0
		if timer.dontSave:
			dontSave = 1

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
		if hasattr(timer, "always_zap"):
			if timer.always_zap:
				always_zap = 1
			else:
				always_zap = 0
		if hasattr(timer, "zapbeforerecord"):
			if timer.zapbeforerecord:
				always_zap = 1
			else:
				always_zap = 0

		pipzap = -1
		if hasattr(timer, "pipzap"):
			if timer.pipzap:
				pipzap = 1
			else:
				pipzap = 0

		isAutoTimer = -1
		if hasattr(timer, "isAutoTimer"):
			if timer.isAutoTimer:
				isAutoTimer = 1
			else:
				isAutoTimer = 0

		if six.PY2:
			descriptionextended = six.text_type(descriptionextended, 'utf_8', errors='ignore').encode('utf_8', 'ignore')

		recordingtype = "normal"

		if timer.record_ecm:
			recordingtype = "scrambled"
			if timer.descramble:
				recordingtype = "descrambled"

		ice_timer_id = -1
		if hasattr(timer, "ice_timer_id"):
			ice_timer_id = timer.ice_timer_id or -1

		# switch back to old way.
		#fuzzyBegin = ' '.join(str(i) for i in FuzzyTime(timer.begin, inPast = True)[1:])
		#fuzzyEnd = ""
		#if strftime("%Y%m%d", localtime(timer.begin)) == strftime("%Y%m%d", localtime(timer.end)):
		#	fuzzyEnd = FuzzyTime(timer.end)[1]
		#else:
		#	fuzzyEnd = ' '.join(str(i) for i in FuzzyTime(timer.end, inPast = True))

		fuzzyBegin = strftime(_("%d.%m.%Y %H:%M"), (localtime(float(timer.begin))))
		fuzzyEnd = strftime(_("%d.%m.%Y %H:%M"), (localtime(float(timer.end))))

		timers.append({
			"serviceref": str(timer.service_ref),
			"servicename": removeBad(timer.service_ref.getServiceName()),
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
			"toggledisabledimg": toggledisabledimg,
			"filename": filename,
			"nextactivation": nextactivation,
			"realbegin": fuzzyBegin,
			"realend": fuzzyEnd,
			"asrefs": asrefs,
			"vpsplugin_enabled": vpsplugin_enabled,
			"vpsplugin_overwrite": vpsplugin_overwrite,
			"vpsplugin_time": vpsplugin_time,
			"always_zap": always_zap,
			"pipzap": pipzap,
			"isAutoTimer": isAutoTimer,
			"allow_duplicate": allow_duplicate,
			"autoadjust": autoadjust,
			"recordingtype": recordingtype,
			"ice_timer_id": ice_timer_id
		})

	return {
		"result": True,
		"timers": timers
	}


def addTimer(session, serviceref, begin, end, name, description, disabled, justplay, afterevent, dirname, tags, repeated, recordingtype, vpsinfo=None, logentries=None, eit=0, always_zap=-1, pipzap=-1, allow_duplicate=1, autoadjust=-1):
	rt = session.nav.RecordTimer

	if not dirname:
		dirname = preferredTimerPath()

	#  IPTV Fix
	serviceref = serviceref.replace('%253a', '%3a')

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
			conflictinfo = []
			for conflict in conflicts:
				errors.append(conflict.name)
				conflictinfo.append({
					"serviceref": str(conflict.service_ref),
					"servicename": conflict.service_ref.getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', ''),
					"name": conflict.name,
					"begin": conflict.begin,
					"end": conflict.end,
					"realbegin": strftime(_("%d.%m.%Y %H:%M"), (localtime(float(conflict.begin)))),
					"realend": strftime(_("%d.%m.%Y %H:%M"), (localtime(float(conflict.end))))
				})

			return {
				"result": False,
				"message": _("Conflicting Timer(s) detected! %s") % " / ".join(errors),
				"conflicts": conflictinfo
			}
		# VPS
		if vpsinfo is not None:
			timer.vpsplugin_enabled = vpsinfo["vpsplugin_enabled"]
			timer.vpsplugin_overwrite = vpsinfo["vpsplugin_overwrite"]
			timer.vpsplugin_time = vpsinfo["vpsplugin_time"]

		if always_zap != -1:
			if hasattr(timer, "always_zap"):
				timer.always_zap = always_zap == 1
			if hasattr(timer, "zapbeforerecord"):
				timer.zapbeforerecord = always_zap == 1

		if hasattr(timer, "autoadjust"):
			if autoadjust == -1:
				autoadjust = config.recording.adjust_time_to_event.value and 1 or 0
			autoadjust = autoadjust

		if hasattr(timer, "allow_duplicate"):
			allow_duplicate = allow_duplicate

		if pipzap != -1:
			if hasattr(timer, "pipzap"):
				timer.pipzap = pipzap == 1

		if recordingtype:
			timer.descramble = {
				"normal": True,
				"descrambled": True,
				"scrambled": False,
				}[recordingtype]
			timer.record_ecm = {
				"normal": False,
				"descrambled": True,
				"scrambled": True,
				}[recordingtype]

	except Exception as e:
		print(str(e))
		return {
			"result": False,
			"message": _("Could not add timer '%s'!") % name
		}

	return {
		"result": True,
		"message": _("Timer '%s' added") % name
	}


def addTimerByEventId(session, eventid, serviceref, justplay, dirname, tags, vpsinfo, always_zap, afterevent, pipzap, allow_duplicate, autoadjust, recordingtype):
	epg = EPG()
	event = epg.getEventById(serviceref, eventid)
	if event is None:
		return {
			"result": False,
			"message": _("EventId not found")
		}

	(begin, end) = adjustStartEndTimes(event)

	if justplay:
		begin += config.recording.margin_before.value * 60
		end = begin + 1

	return addTimer(
		session,
		serviceref,
		begin,
		end,
		event.title,
		event.description.replace("\n", " "), # Enigma2's InputBox and VirtualKeyBoard don't (yet?) have multi-line capability
		False,
		justplay,
		afterevent,
		dirname,
		tags,
		0,
		recordingtype,
		vpsinfo,
		None,
		event.eventId,
		always_zap,
		pipzap,
		allow_duplicate,
		autoadjust
	)


# NEW editTimer function to prevent delete + add on change
# !!! This new function must be tested !!!!
# TODO: exception handling
def editTimer(session, serviceref, begin, end, name, description, disabled, justplay, afterEvent, dirname, tags, repeated, channelOld, beginOld, endOld, recordingtype, vpsinfo, always_zap, pipzap, allow_duplicate, autoadjust):
	channelOld_str = ':'.join(str(channelOld).split(':')[:11])
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
			# timer.eit = eit
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

			if always_zap != -1:
				if hasattr(timer, "always_zap"):
					timer.always_zap = always_zap == 1
				if hasattr(timer, "zapbeforerecord"):
					timer.zapbeforerecord = always_zap == 1

			if pipzap != -1:
				if hasattr(timer, "pipzap"):
					timer.pipzap = pipzap == 1

			if hasattr(timer, "allow_duplicate"):
				timer.allow_duplicate = allow_duplicate

			if hasattr(timer, "autoadjust"):
				if autoadjust == -1:
					autoadjust = config.recording.adjust_time_to_event.value and 1 or 0
				timer.autoadjust = autoadjust

			if recordingtype:
				timer.descramble = {
					"normal": True,
					"descrambled": True,
					"scrambled": False,
					}[recordingtype]
				timer.record_ecm = {
					"normal": False,
					"descrambled": True,
					"scrambled": True,
					}[recordingtype]

			# TODO: multi tuner test
			sanity = TimerSanityCheck(rt.timer_list, timer)
			conflicts = None
			if not sanity.check():
				conflicts = sanity.getSimulTimerList()
				if conflicts is not None:
					for conflict in conflicts:
						if conflict.setAutoincreaseEnd(timer):
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
				errors = []
				conflictinfo = []
				for conflict in conflicts:
					errors.append(conflict.name)
					conflictinfo.append({
						"serviceref": str(conflict.service_ref),
						"servicename": removeBad(conflict.service_ref.getServiceName()),
						"name": conflict.name,
						"begin": conflict.begin,
						"end": conflict.end,
						"realbegin": strftime(_("%d.%m.%Y %H:%M"), (localtime(float(conflict.begin)))),
						"realend": strftime(_("%d.%m.%Y %H:%M"), (localtime(float(conflict.end))))
					})

				return {
					"result": False,
					"message": _("Timer '%s' not saved while Conflict") % name,
					"conflicts": conflictinfo
				}

	return {
		"result": False,
		"message": _("Could not find timer '%s' with given start and end time!") % name
	}


def removeTimer(session, serviceref, begin, end, eit):
	serviceref_str = ':'.join(str(serviceref).split(':')[:11])
	rt = session.nav.RecordTimer
	for timer in rt.timer_list + rt.processed_timers:
		needed_ref = ':'.join(timer.service_ref.ref.toString().split(':')[:11]) == serviceref_str
		if needed_ref and timer.eit and eit and timer.eit == eit:
			rt.removeEntry(timer)
			return {
				"result": True,
				"message": _("The timer '%s' has been deleted successfully") % timer.name
			}
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
		"servicename": removeBad(timer.service_ref.getServiceName()),
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
		tags = unquote(request.args['tags'][0]).split(' ')

	if request.args['command'][0] == "add":
		del request.args['command'][0]
		return addTimer(session, sRef, begin, end, name, description, disabled, justplay, afterevent, location, tags, repeated)
	elif request.args['command'][0] == "del":
		del request.args['command'][0]
		return removeTimer(session, sRef, begin, end, eit=None)
	elif request.args['command'][0] == "change":
		del request.args['command'][0]
		return editTimer(session, sRef, begin, end, name, description, disabled, justplay, afterevent, location, tags, repeated, begin, end, serviceref)
	else:
		return {
			"result": False,
			"message": _("Unknown command: '%s'") % request.args['command'][0]
		}


def getPowerTimer(session, request):

	try:
		from PowerTimer import TIMERTYPE, AFTEREVENT
		logs = False
		if "logs" in list(request.args.keys()):
			logs = True

		timers = []
		timer_list = session.nav.PowerTimer.timer_list
		processed_timers = session.nav.PowerTimer.processed_timers

		pos = 0
		for timer in timer_list + processed_timers:
			list = []
			pos += 1
			if logs:
				for _time, code, msg in timer.log_entries:
					list.append({
						"code": str(code),
						"time": str(_time),
						"msg": str(msg)
					})
			timers.append({
				"id": str(pos),
				"timertype": str(timer.timerType),
				"timertypename": str({
					TIMERTYPE.NONE: "nothing",
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
					AFTEREVENT.WAKEUP: "wakeup",
					AFTEREVENT.WAKEUPTOSTANDBY: "wakeuptostandby",
					AFTEREVENT.STANDBY: "standby",
					AFTEREVENT.DEEPSTANDBY: "deepstandby"
				}[timer.afterEvent]),
				"disabled": str(int(timer.disabled)),
				"autosleepinstandbyonly": str(timer.autosleepinstandbyonly),
				"autosleepdelay": str(timer.autosleepdelay),
				"autosleeprepeat": str(timer.autosleeprepeat),
				"logentries": list
			})

		return {
			"result": True,
			"timers": timers
		}
	except Exception as e:
		print(str(e))
		return {
			"result": False,
			"message": _("PowerTimer feature not available")
		}


def setPowerTimer(session, request):
	id = 0
	if "id" in list(request.args.keys()):
		id = int(request.args["id"][0])
	timertype = 0
	if "timertype" in list(request.args.keys()) and request.args["timertype"][0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8"]:
		timertype = int(request.args["timertype"][0])
	begin = int(time() + 60)
	if "begin" in list(request.args.keys()):
		begin = int(request.args["begin"][0])
	end = int(time() + 120)
	if "end" in list(request.args.keys()):
		end = int(request.args["end"][0])
	disabled = 0
	if "disabled" in list(request.args.keys()):
		disabled = int(request.args["disabled"][0])
	repeated = False
	if "repeated" in list(request.args.keys()):
		repeated = request.args["repeated"][0] == "1"
	afterevent = 0
	if "afterevent" in list(request.args.keys()) and request.args["afterevent"][0] in ["0", "1", "2", "3", "4"]:
		afterevent = int(request.args["afterevent"][0])
	autosleepinstandbyonly = "no"
	if "autosleepinstandbyonly" in list(request.args.keys()):
		autosleepinstandbyonly = request.args["autosleepinstandbyonly"][0]
	autosleepdelay = "0"
	if "autosleepdelay" in list(request.args.keys()):
		autosleepdelay = int(request.args["autosleepdelay"][0])
	autosleeprepeat = "once"
	if "autosleeprepeat" in list(request.args.keys()):
		autosleeprepeat = request.args["autosleeprepeat"][0]

	# find
	entry = None
	pos = 0
	if id > 0:
		timer_list = session.nav.PowerTimer.timer_list
		processed_timers = session.nav.PowerTimer.processed_timers
		for timer in timer_list + processed_timers:
			pos += 1
			if pos == 1:
				entry = timer

	# create new Timer
	if entry is None:
		from PowerTimer import PowerTimerEntry
		entry = PowerTimerEntry(begin, end, disabled, afterevent, timertype)
	else:
		entry.begin = begin
		entry.end = end
		entry.timertype = timertype
		entry.afterevent = afterevent
		entry.disabled = disabled

	#  TODO: repeated
	entry.repeated = int(repeated)
	entry.autosleepinstandbyonly = autosleepinstandbyonly
	entry.autosleepdelay = autosleepdelay
	entry.autosleeprepeat = autosleeprepeat

	#  TODO: Test !!!

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
		except Exception:
			return {
				"result": False,
				"message": _("SleepTimer error")
			}
	elif InfoBar.instance is not None and hasattr(InfoBar.instance, 'sleepTimer'):
		try:
			# TODO test OpenPLI and similar
			active = InfoBar.instance.sleepTimer.isActive()
			if hasattr(config.usage, 'sleepTimer'):
				time = config.usage.sleepTimer.value
			if hasattr(config.usage, 'sleep_timer'):
				time = config.usage.sleep_timer.value
			action = "shutdown"
			if hasattr(config.usage, 'sleepTimerAction'):
				action = config.usage.sleepTimerAction.value
			if hasattr(config.usage, 'sleep_timer_action'):
				action = config.usage.sleep_timer_action.value
			if action == "deepstandby":
				action = "shutdown"

			if time != None and int(time) > 0:
				try:
					time = int(int(time) / 60)
				except:
					time = 60
			remaining = 0
			if active:
				remaining = int(InfoBar.instance.sleepTimerState())
			return {
				"enabled": active,
				"minutes": time,
				"action": action,
				"remaining": remaining,
				"message": _("Sleeptimer is enabled") if active else _("Sleeptimer is disabled")
			}
		except Exception as e:
			print(e)
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
				if timertype in ["2", "3"]:
					action = "standby"
					if timertype == "3":
						action = "shutdown"
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
		except Exception:
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
			if enabled is False:
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
		except Exception:
			return {
				"result": False,
				"message": _("SleepTimer error")
			}
	elif InfoBar.instance is not None and hasattr(InfoBar.instance, 'sleepTimer'):
		try:
			if time == None:
				time = 60
			# TODO test OpenPLI and similar
			info = getInfo()
			cfgaction = None
			if hasattr(config.usage, 'sleepTimerAction'):
				cfgaction = config.usage.sleepTimerAction
			if hasattr(config.usage, 'sleep_timer_action'):
				cfgaction = config.usage.sleep_timer_action
			if cfgaction:
				if action == "shutdown":
					cfgaction.value = "deepstandby"
				else:
					cfgaction.value = action
				cfgaction.save()
			active = enabled
			time = int(time)
			cfgtimer = None
			if hasattr(config.usage, 'sleepTimer'):
				cfgtimer = config.usage.sleepTimer
				if cfgtimer.value == '0':
					if info["imagedistro"] in ('openatv'):
						for val in range(15, 241, 15):
							if time == val:
								break
							if time < val:
								time = int(abs(val / 60))
								break
			elif hasattr(config.usage, 'sleep_timer'):
				cfgtimer = config.usage.sleep_timer
				if cfgtimer.value == '0':
					# find the closest value
					if info["imagedistro"] in ('openatv'):
						times = time * 60
						for val in list(range(900, 14401, 900)):
							if times == val:
								break
							if times < val:
								time = int(abs(val / 60))
								break
			if cfgtimer:
				if active:
					cfgtimer.value = str(time * 60)
				else:
					cfgtimer.value = '0'
				cfgtimer.save()
				if enabled:
					InfoBar.instance.setSleepTimer(time * 60, False)
				else:
					InfoBar.instance.setSleepTimer(0, False)
			return {
				"enabled": active,
				"minutes": time,
				"action": action,
				"message": _("Sleeptimer is enabled") if active else _("Sleeptimer is disabled")
			}
		except Exception as e:
			print(e)
			return {
				"result": False,
				"message": _("SleepTimer error")
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
					if enabled:
						timer.disabled = False
						timer.autosleepdelay = int(time)
						timer.begin = begin
						timer.end = end
					else:
						timer.disabled = True
					done = True
					break
				if timertype == "3" and action == "shutdown":
					if enabled:
						timer.disabled = False
						timer.autosleepdelay = int(time)
						timer.begin = begin
						timer.end = end
					else:
						timer.disabled = True
					done = True
					break
				if timertype == "3" and action == "standby":
					if enabled:
						timer.disabled = False
						timer.autosleepdelay = int(time)
						timer.timerType = 2
						timer.begin = begin
						timer.end = end
					else:
						timer.disabled = True
					done = True
					break
				if timertype == "2" and action == "shutdown":
					if enabled:
						timer.disabled = False
						timer.autosleepdelay = int(time)
						timer.timerType = 3
						timer.begin = begin
						timer.end = end
					else:
						timer.disabled = True
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
				from PowerTimer import PowerTimerEntry
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
		except Exception:
			return {
				"result": False,
				"message": _("SleepTimer error")
			}


def getVPSChannels(session):
	vpsfile = "/etc/enigma2/vps.xml"
	from Tools.Directories import fileExists
	if fileExists(vpsfile):
		try:
			import xml.etree.cElementTree  # nosec
			vpsfile = open(vpsfile, 'r')
			vpsdom = xml.etree.cElementTree.parse(vpsfile)  # nosec
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
		except Exception:
			return {
				"result": False,
				"message": _("Error parsing vps.xml")
			}

	return {
		"result": False,
		"message": _("VPS plugin not found")
	}
