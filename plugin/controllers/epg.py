#!/usr/bin/python
# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: services
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

from time import time, localtime, gmtime, strftime
from datetime import datetime
from json import dumps

from enigma import eEPGCache, eServiceReference
from ServiceReference import ServiceReference
from Components.config import config
from .defaults import DEBUG_ENABLED

try:
	from Components.Converter.genre import getGenreStringLong
except ImportError:
	def getGenreStringLong(*args): return ""


CASE_SENSITIVE_QUERY = 0
CASE_INSENSITIVE_QUERY = 1
REGEX_QUERY =2
MAX_RESULTS = 128
MATCH_EVENT_ID = 2
PREVIOUS_EVENT = -1
NOW_EVENT = 0
NEXT_EVENT = +1
TIME_NOW = -1

#TODO: load configgy stuff once


def _debug(msg):
	if DEBUG_ENABLED:
		print(msg)


# #Tests (GMT+01:00 DST)
# timeNow = 1657925970   #              Fri, July 15, 2022 11:59:30 PM GMT+01:00 DST
# timestamp = 1657666800 #prev 00:00:00 Wed, July 13, 2022 12:00:00 AM GMT+01:00 DST
# timestamp = 1657753199 #prev 23:59:59 Wed, July 13, 2022 11:59:59 PM GMT+01:00 DST
# timestamp = 1657753200 #yest 00:00:00 Thu, July 14, 2022 12:00:00 AM GMT+01:00 DST
# timestamp = 1657839599 #yest 23:59:59 Thu, July 14, 2022 11:59:59 PM GMT+01:00 DST
# timestamp = 1657839600 #today00:00:00 Fri, July 15, 2022 12:00:00 AM GMT+01:00 DST
# timestamp = 1657925999 #today23:59:59 Fri, July 15, 2022 11:59:59 PM GMT+01:00 DST
# timestamp = 1657926000 #tomo 00:00:00 Sat, July 16, 2022 12:00:00 AM GMT+01:00 DST
# timestamp = 1658012399 #tomo 23:59:59 Sat, July 16, 2022 11:59:59 PM GMT+01:00 DST
# timestamp = 1658012400 #next 00:00:00 Sun, July 17, 2022 12:00:00 AM GMT+01:00 DST
# timestamp = 1658098799 #next 23:59:59 Sun, July 17, 2022 11:59:59 PM GMT+01:00 DST
#
# #Tests (GMT+02:00 DST)
# timeNow = 1657922370   #              Fri, July 15, 2022 11:59:30 PM GMT+02:00 DST
# timestamp = 1657663200 #prev 00:00:00 Wed, July 13, 2022 12:00:00 AM GMT+02:00 DST
# timestamp = 1657749599 #prev 23:59:59 Wed, July 13, 2022 11:59:59 PM GMT+02:00 DST
# timestamp = 1657749600 #yest 00:00:00 Thu, July 14, 2022 12:00:00 AM GMT+02:00 DST
# timestamp = 1657835999 #yest 23:59:59 Thu, July 14, 2022 11:59:59 PM GMT+02:00 DST
# timestamp = 1657836000 #today00:00:00 Fri, July 15, 2022 12:00:00 AM GMT+02:00 DST
# timestamp = 1657922399 #today23:59:59 Fri, July 15, 2022 11:59:59 PM GMT+02:00 DST
# timestamp = 1657922400 #tomo 00:00:00 Sat, July 16, 2022 12:00:00 AM GMT+02:00 DST
# timestamp = 1658008799 #tomo 23:59:59 Sat, July 16, 2022 11:59:59 PM GMT+02:00 DST
# timestamp = 1658008800 #next 00:00:00 Sun, July 17, 2022 12:00:00 AM GMT+02:00 DST
# timestamp = 1658095199 #next 23:59:59 Sun, July 17, 2022 11:59:59 PM GMT+02:00 DST


TEXT_YESTERDAY = 'Yesterday %R'
TEXT_TODAY = 'Today %R'
TEXT_TOMORROW = 'Tomorrow %R'
#TODO: move to utilities
def getNaturalDayTime(timestamp, defaultFormat):
	timeNow = int(time())
	timeDiff = timestamp - timeNow
	deltaDays = timedelta(seconds=timeDiff).days
	if deltaDays >= -2 and deltaDays <= 2:
		dayDiff = localtime(timestamp)[2] - localtime(timeNow)[2]
		print('dayDiff: ' + str(dayDiff))
		if dayDiff == -1:
			text = strftime(TEXT_YESTERDAY, (localtime(timestamp)))
		elif dayDiff == 0:
			text = strftime(TEXT_TODAY, (localtime(timestamp)))
		elif dayDiff == 1:
			text = strftime(TEXT_TOMORROW, (localtime(timestamp)))
		else:
			text = strftime(defaultFormat, (localtime(timestamp)))
	else:
		text = strftime(defaultFormat, (localtime(timestamp)))
	return text


#TODO: move to utilities
def getCustomTimeFormats(timestamp):
	return {
		'timestamp': timestamp,
		'date': strftime(config.usage.date.displayday.value, (localtime(timestamp))),
		'time': strftime(config.usage.time.short.value, (localtime(timestamp))),
		'dateTime': strftime('%c', (localtime(timestamp))),
		'natural': getNaturalDayTime(timestamp, '%c'),
		'iso': datetime.fromtimestamp(timestamp).isoformat() if not None else ''
	}


#TODO: move to utilities
def getFuzzyHoursMinutes(timestamp=0):
	timeStruct = gmtime(timestamp)
	hours = timeStruct[3]
	mins = timeStruct[4]

	if hours > 1 and mins > 1:
		template = "%-Hhrs %-Mmins"
	elif hours > 1 and mins == 1:
		template = "%-Hhrs %-Mmin"
	elif hours > 1:
		template = "%-H hours"
	elif hours == 1 and mins > 1:
		template = "%-Hhr %-Mmins"
	elif hours == 1 and mins == 1:
		template = "%-Hhr %-Mmin"
	elif hours == 1:
		template = "%-H hour"
	elif mins > 1:
		template = "%-M mins"
	elif mins == 1:
		template = "%-M minute"
	else:
		template = ""
	formatted = strftime(template, timeStruct)  # if remaining is not None else None
	return formatted


#TODO: move to utilities
def convertGenre(val):
	if val is not None and len(val) > 0:
		val = val[0]
		if len(val) > 1:
			if val[0] > 0:
				genreId = val[0] * 16 + val[1]
				return str(getGenreStringLong(val[0], val[1])).strip(), genreId
	return "", 0


class Epg():
	NOW = 10
	NEXT = 11
	NOW_NEXT = 21

	def __init__(self):
		self._instance = eEPGCache.getInstance()


	def getEncoding(self):
		return config.OpenWebif.epg_encoding.value


	#TODO: make search type fully user-selectable
	def search(self, queryString, searchFullDescription=False):
		_debug("[[[   search(%s, %s)   ]]]" % (queryString, searchFullDescription))
		if not queryString:
			_debug("A required parameter 'queryString' is missing!")

		epgEncoding = self.getEncoding()

		if epgEncoding.lower() != 'utf-8':
			try:
				queryString = queryString.encode(epgEncoding)
			except UnicodeEncodeError:
				pass

		queryType = eEPGCache.PARTIAL_TITLE_SEARCH

		if searchFullDescription:
			if hasattr(eEPGCache, 'FULL_DESCRIPTION_SEARCH'):
				queryType = eEPGCache.FULL_DESCRIPTION_SEARCH
			elif hasattr(eEPGCache, 'PARTIAL_DESCRIPTION_SEARCH'):
				queryType = eEPGCache.PARTIAL_DESCRIPTION_SEARCH

		eventFields = 'IBDTSENRW'
		criteria = (eventFields, MAX_RESULTS, queryType, queryString, CASE_INSENSITIVE_QUERY)
		epgEvents = self._instance.search(criteria)

		_debug(epgEvents)
		return epgEvents


	def findSimilarEvents(self, sRef, eventId):
		_debug("[[[   findSimilarEvents(%s, %s)   ]]]" % (sRef, eventId))
		if not sRef or not eventId:
			_debug("A required parameter 'sRef' or eventId is missing!")
			# return None
		else:
			sRef = str(sRef)
			eventId = int(eventId)

		eventFields = 'IBDTSENRW'
		criteria = (eventFields, MAX_RESULTS, eEPGCache.SIMILAR_BROADCASTINGS_SEARCH, sRef, eventId)
		epgEvents = self._instance.search(criteria)

		_debug(epgEvents)
		return epgEvents


	def _transformEventData(self, eventFields, *args):
		_debug("[[[   _transformEventData(%s)   ]]]" % (eventFields))
		# _debug(*args)

		eventData = {}
		dateAndTime = {}
		service = {}
		startTimestamp = None
		currentTimestamp = None
		duration = 0
		shortDescription = None
		longDescription = None


		# TODO: skip processing if there isn't a valid event (id is None)

		for index, argValue in enumerate(args):
			key = eventFields[index]

			if key == 'I':
				eventData['eventId'] = argValue
			elif key == 'B':
				startTimestamp = argValue
				if startTimestamp is not None:
					startTimeFormats = getCustomTimeFormats(startTimestamp)
					dateAndTime['start'] = startTimeFormats['timestamp']
					dateAndTime['startDate'] = startTimeFormats['date']
					dateAndTime['startTime'] = startTimeFormats['time']
					dateAndTime['startDateTime'] = startTimeFormats['dateTime']
					dateAndTime['startFuzzy'] = startTimeFormats['fuzzy']
				else:
					dateAndTime['start'] = None
					dateAndTime['startDate'] = None
					dateAndTime['startTime'] = None
					dateAndTime['startDateTime'] = None
					dateAndTime['startFuzzy'] = None
			elif key == 'D':
				duration = argValue or 0
				dateAndTime['duration'] = duration
				dateAndTime['durationMinutes'] = int(duration / 60)
				dateAndTime['durationFuzzy'] = getFuzzyHoursMinutes(duration)
			elif key == 'T':
				eventData['title'] = (argValue or '').strip()
			elif key == 'S':
				if argValue is not None:
					shortDescription = argValue.strip()
					eventData['shortDescription'] = shortDescription
			elif key == 'E':
				if argValue is not None:
					longDescription = argValue.strip()
					eventData['longDescription'] = longDescription
			elif key == 'P':
				eventData['parentalRating'] = argValue
			elif key == 'W':
				eventData['genre'], eventData['genreId'] = convertGenre(argValue)
			elif key == 'C':
				currentTimestamp = argValue
				dateAndTime['current'] = currentTimestamp
			elif key == 'R':
				service['sRef'] = argValue
			elif key == 'n':
				service['nameShort'] = argValue
			elif key == 'N':
				service['name'] = argValue
			elif key == 'X':
				#ignored
				pass
			elif key == 'M':
				eventData['maxResults'] = argValue
			else:
				eventData[key] = argValue

		if startTimestamp and duration:
			endTimestamp = startTimestamp + duration
			endTimeFormats = getCustomTimeFormats(startTimestamp)
			dateAndTime['end'] = endTimeFormats['timestamp']
			dateAndTime['endDate'] = endTimeFormats['date']
			dateAndTime['endTime'] = endTimeFormats['time']
			dateAndTime['endDateTime'] = endTimeFormats['dateTime']
			dateAndTime['endFuzzy'] = endTimeFormats['fuzzy']
			if currentTimestamp:
				remaining = endTimestamp - currentTimestamp if currentTimestamp > startTimestamp else duration
				dateAndTime['remaining'] = remaining
				dateAndTime['remainingMinutes'] = int(remaining / 60)
				dateAndTime['remainingFormatted'] = getFuzzyHoursMinutes(remaining)
				progressPercent = int(((currentTimestamp - startTimestamp) / duration) * 100)
				progressPercent = progressPercent if progressPercent >= 0 else 0
				dateAndTime['progress'] = progressPercent
				dateAndTime['progressFormatted'] = '{0}%'.format(progressPercent)

		eventData['dateTime'] = dateAndTime
		eventData['service'] = service
		eventData['description'] = longDescription or shortDescription

		print(dumps(eventData, indent=2))
		# return args
		return eventData


	def _queryEPG(self, fields='', criteria=[]):
		if not fields or not criteria:
			_debug("A required parameter 'fields' or [criteria] is missing!")
			# return None

		def _callEventTransform(*args):
			return self._transformEventData(fields, *args)

		epgEvents = self._instance.lookupEvent(criteria, _callEventTransform)

		_debug(epgEvents)
		return epgEvents


	def _getChannelNowOrNext(self, sRef, nowOrNext):
		if not sRef:
			_debug("A required parameter 'sRef' is missing!")
			# return None
		else:
			sRef = str(sRef)

		epgEvent = self.getEventByTime(sRef, TIME_NOW, nowOrNext)
		evtupl = (
			epgEvent.getEventId(),
			epgEvent.getBeginTime(),
			epgEvent.getDuration(),
			localtime(), #int(time())
			epgEvent.getEventName(),
			epgEvent.getShortDescription(),
			epgEvent.getExtendedDescription(),
			sRef,
			ServiceReference(sRef).getServiceName(),
			epgEvent.getGenreDataList()
		)

		_debug(evtupl)
		return evtupl


	def _getBouquetNowOrNext(self, bqRef, nowOrNext):
		if not bqRef:
			_debug("A required parameter 'bqRef' is missing!")
			# return None

		fields = 'IBDCTSERNWX'
		criteria = []
		sRefs = bqRef

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, nowOrNext, TIME_NOW))

		epgEvents = self._queryEPG(fields, criteria)

		_debug(epgEvents)
		return epgEvents


	def getChannelEvents(self, sRef, startTime, endTime=None):
		_debug("[[[   getChannelEvents(%s, %s, %s)   ]]]" % (sRef, startTime, endTime))
		if not sRef:
			_debug("A required parameter 'sRef' is missing!")
			# return None
		else:
			sRef = str(sRef)

		fields = 'IBDTSENCW'
		criteria = []
		criteria.append((sRef, NOW_EVENT, startTime, endTime))
		epgEvents = self._queryEPG(fields, criteria)

		_debug(epgEvents)
		return epgEvents


	def getChannelNowEvent(self, sRef):
		_debug("[[[   getChannelNowEvent(%s)   ]]]" % (sRef))
		return _getChannelNowOrNext(sRef, NOW_EVENT)


	def getChannelNextEvent(self, sRef):
		_debug("[[[   getChannelNextEvent(%s)   ]]]" % (sRef))
		return _getChannelNowOrNext(sRef, NEXT_EVENT)


	def getMultiChannelEvents(self, sRefs, startTime, endTime=None, fields='IBTSRND'):
		_debug("[[[   getMultiChannelEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		if not sRefs:
			_debug("A required parameter [sRefs] is missing!")
			# return None

		criteria = []

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, NOW_EVENT, startTime, endTime))

		epgEvents = self._queryEPG(fields, criteria)

		_debug(epgEvents)
		return epgEvents


	def getMultiChannelNowNextEvents(self, sRefs, fields='IBDCTSERNX'):
		_debug("[[[   getMultiChannelNowNextEvents(%s)   ]]]" % (sRefs))
		if not sRefs:
			_debug("A required parameter [sRefs] is missing!")
			# return None

		criteria = []

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, NOW_EVENT, TIME_NOW))
			criteria.append((sRef, NEXT_EVENT, TIME_NOW))

		epgEvents = self._queryEPG(fields, criteria)

		_debug(epgEvents)
		return epgEvents


	def getBouquetEvents(self, sRefs, startTime, endTime=None):
		_debug("[[[   getBouquetEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		#TODO: accept only a bq ref and get list of srefs here
		return self.getMultiChannelEvents(sRefs, startTime, endTime, 'IBDCTSERNWX')


	def getBouquetNowEvents(self, bqRef):
		_debug("[[[   getBouquetNowEvents(%s)   ]]]" % (bqRef))
		return _getBouquetNowOrNext(sRefs, NOW_EVENT)


	def getBouquetNextEvents(self, bqRef):
		_debug("[[[   getBouquetNowEvents(%s)   ]]]" % (bqRef))
		return _getBouquetNowOrNext(sRefs, NEXT_EVENT)


	def getBouquetNowNextEvents(self, sRefs):
		_debug("[[[   getBouquetNowNextEvents(%s)   ]]]" % (sRefs))
		#TODO: accept only a bq ref and get list of srefs here
		return self.getMultiChannelNowNextEvents(sRefs, 'IBDCTSERNWX')


	def getCurrentEvent(self, sRef):
		_debug("[[[   getCurrentEvent(%s)   ]]]" % (sRef))
		if not sRef:
			_debug("A required parameter 'sRef' is missing!")
			# return None
		elif not isinstance(sRef, eServiceReference):
			sRef = eServiceReference(sRef)

		epgEvent = self._instance.lookupEventTime(sRef, TIME_NOW, 0)

		# from Components.Sources.EventInfo import EventInfo
		# evt = (EventInfo(self.session.nav, EventInfo.NOW).getEvent())
		# epgEvent = (
		# 	evt.getEventName(),           # [T]
		# 	evt.getEventID(),             # [I]
		# 	evt.getBeginTime(),           # [B]
		# 	evt.getDuration(),            # [D]
		# 	evt.getShortDescription(),    # [S]
		# 	evt.getExtendedDescription(), # [E]
		# 	evt.getParentalData(),        # [P]
		# 	evt.getGenreData()            # [W]
		#   # missing Service Reference     [R]
		#   # missing Service Name          [N]
		#   # missing Short Service Name    [n]
		# )

		_debug(epgEvent)
		return epgEvent


	def getEventById(self, sRef, eventId):
		_debug("[[[   getEventById(%s, %s)   ]]]" % (sRef, eventId))
		if not sRef or not eventId:
			_debug("A required parameter 'sRef' or eventId is missing!")
			# return None
		elif not isinstance(sRef, eServiceReference):
			sRef = eServiceReference(sRef)

		eventId = int(eventId)
		epgEvent = self._instance.lookupEventId(sRef, eventId)

		# _debug(dumps(epgEvent, indent = 2)) # Object of type eServiceEvent is not JSON serializable
		_debug(epgEvent and epgEvent.getEventName() or None)
		return epgEvent

		# epgEvent.getEventId(),
		# epgEvent.getBeginTime(),
		# epgEvent.getDuration(),
		# epgEvent.getEventName(),
		# epgEvent.getShortDescription(),
		# epgEvent.getExtendedDescription(),
		# ServiceReference(sRef).getServiceName(),
		# sRef,
		# epgEvent.getGenreDataList(), #TODO: genre stuff needs to be reworked

		# epgEvent.getParentalData(),
		# epgEvent.getSeriesCrid(),
		# epgEvent.getEpisodeCrid(),
		# epgEvent.getRunningStatus(),
		# epgEvent.getExtraEventData(),
		# epgEvent.getPdcPil()


	def getEventByTime(self, sRef, eventTime, direction=NOW_EVENT):
		_debug("[[[   getEventByTime(%s, %s)   ]]]" % (sRef, eventTime))
		if not sRef or not eventTime:
			_debug("A required parameter 'sRef' or eventTime is missing!")
			# return None
		elif not isinstance(sRef, eServiceReference):
			sRef = eServiceReference(sRef)

		epgEvent = self._instance.lookupEventTime(sRef, eventTime, direction)

		# Object of type eServiceEvent is not JSON serializable
		_debug(epgEvent)
		return epgEvent


	def getEvent(self, sRef, eventId):
		_debug("[[[   getEvent(%s, %s)   ]]]" % (sRef, eventId))
		if not sRef or not eventId:
			_debug("A required parameter 'sRef' or eventId is missing!")
			# return None
		else:
			sRef = str(sRef)
			eventId = int(eventId)

		epgEvent = self.getEventById(sRef, eventId)

		if epgEvent:
			print(epgEvent)
			genreData = epgEvent.getGenreDataList() #TODO: debug index out of range
			def getEndTime(): return epgEvent.getBeginTime() + epgEvent.getDuration()
			def getServiceReference(): return sRef
			def getServiceName(): return ServiceReference(sRef).getServiceName()
			def getGenre(): return "genreData[0]"
			def getGenreId(): return "genreData[1]"
			epgEvent.getEndTime = getEndTime
			epgEvent.getServiceReference = getServiceReference
			epgEvent.getServiceName = getServiceName
			epgEvent.getGenre = getGenre
			epgEvent.getGenreId = getGenreId

		_debug(epgEvent)
		return epgEvent


	def getEventDescription(self, sRef, eventId):
		_debug("[[[   getEventDescription(%s, %s)   ]]]" % (sRef, eventId))
		if not sRef or not eventId:
			_debug("A required parameter 'sRef' or eventId is missing!")
			return None
		else:
			sRef = str(sRef)
			eventId = int(eventId)

		description = None
		epgEvent = self.getEventById(sRef, eventId)

		if epgEvent:
			description = epgEvent.getExtendedDescription() or epgEvent.getShortDescription() or ""

		_debug(description)
		return description


	# /web/loadepg
	def load(self):
		self._instance.load()


	# /web/saveepg
	def save(self):
		self._instance.save()
