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

from time import localtime, strftime, gmtime
import json

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


def debug(msg):
	if DEBUG_ENABLED:
		print(msg)


#TODO: move to utilities
def getCustomTimeFormats(timestamp):
	return {
		'timestamp': timestamp,
		'date': strftime(config.usage.date.displayday.value, (localtime(timestamp))),
		'time': strftime(config.usage.time.short.value, (localtime(timestamp))),
		'dateTime': strftime('%c', (localtime(timestamp))),
		'fuzzy': 'fuzzyTimestamp'
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

# openatv_enigma2/lib/dvb/epgcache.cpp
#
# // here we get a python tuple
# // the first entry in the tuple is a python string to specify the format of the returned tuples (in a list)
# //   I = Event Id
# //   B = Event Begin Time
# //   D = Event Duration
# //   T = Event Title
# //   S = Event Short Description
# //   P = Event Parental Rating
# //   W = Event Content Description
# //   E = Event Extended Description
# //   R = Service Reference
# //   N = Service Name
# //   n = Short Service Name
# //  the second tuple entry is the MAX matches value
# //  the third tuple entry is the type of query
# //     0 = search for similar broadcastings (SIMILAR_BROADCASTINGS_SEARCH)
# //     1 = search events with exactly title name (EXACT_TITLE_SEARCH)
# //     2 = search events with text in title name (PARTIAL_TITLE_SEARCH)
# //     3 = search events starting with title name (START_TITLE_SEARCH)
# //     4 = search events ending with title name (END_TITLE_SEARCH)
# //     5 = search events with text in description (PARTIAL_DESCRIPTION_SEARCH)
# //  when type is 0 (SIMILAR_BROADCASTINGS_SEARCH)
# //   the fourth is the servicereference string
# //   the fifth is the eventid
# //  when type > 0 (*_TITLE_SEARCH)
# //   the fourth is the search text
# //   the fifth is
# //     0 = case sensitive (CASE_CHECK)
# //     1 = case insensitive (NO_CASE_CHECK)
# //     2 = regex search (REGEX_CHECK)

	def search(self, queryString, searchFullDescription=False):
		debug("[[[   search(%s, %s)   ]]]" % (queryString, searchFullDescription))
		if not queryString:
			debug("A required parameter 'queryString' is missing!")

		queryType = eEPGCache.PARTIAL_TITLE_SEARCH
		epgEncoding = config.OpenWebif.epg_encoding.value

		if epgEncoding.lower() != 'utf-8':
			try:
				queryString = queryString.encode(epgEncoding)
			except UnicodeEncodeError:
				pass

		if searchFullDescription:
			if hasattr(eEPGCache, 'FULL_DESCRIPTION_SEARCH'):
				queryType = eEPGCache.FULL_DESCRIPTION_SEARCH
			elif hasattr(eEPGCache, 'PARTIAL_DESCRIPTION_SEARCH'):
				queryType = eEPGCache.PARTIAL_DESCRIPTION_SEARCH

		criteria = ('IBDTSENRW', MAX_RESULTS, queryType, queryString, CASE_INSENSITIVE_QUERY)
		epgEvents = self._instance.search(criteria)

		debug(epgEvents)
		return epgEvents


	def findSimilarEvents(self, sRef, eventId):
		debug("[[[   findSimilarEvents(%s, %s)   ]]]" % (sRef, eventId))
		if not sRef or not eventId:
			debug("A required parameter 'sRef' or eventId is missing!")
			# return None
		else:
			sRef = str(sRef)
			eventId = int(eventId)

		eventFields = 'IBDTSENRW'
		criteria = (eventFields, MAX_RESULTS, eEPGCache.SIMILAR_BROADCASTINGS_SEARCH, sRef, eventId)
		epgEvents = self._instance.search(criteria)

		debug(epgEvents)
		return epgEvents


	def _transformEventData(self, eventFields, *args):
		debug("[[[   _transformEventData(%s)   ]]]" % (eventFields))
		# debug(*args)

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

		print(json.dumps(eventData, indent=2))
		# return args
		return eventData


	def _queryEPG(self, criteria):
		eventFields = criteria[0]

		def _callEventTransform(*args):
			return self._transformEventData(eventFields, *args)

		epgEvents = self._instance.lookupEvent(criteria, _callEventTransform)

		debug(epgEvents)
		return epgEvents

# openatv_enigma2/lib/dvb/epgcache.cpp
#
# // here we get a python list
# // the first entry in the list is a python string to specify the format of the returned tuples (in a list)
# //   0 = PyLong(0)
# //   I = Event Id
# //   B = Event Begin Time
# //   D = Event Duration
# //   T = Event Title
# //   S = Event Short Description
# //   E = Event Extended Description
# //   P = Event Parental Rating
# //   W = Event Content Description ('W'hat)
# //   C = Current Time
# //   R = Service Reference
# //   N = Service Name
# //   n = Short Service Name
# //   X = Return a minimum of one tuple per service in the result list... even when no event was found.
# //       The returned tuple is filled with all available infos... non avail is filled as None
# //       The position and existence of 'X' in the format string has no influence on the result tuple... its completely ignored..
# //   M = see X just 10 items are returned
# // then for each service follows a tuple
# //   first tuple entry is the servicereference (as string... use the ref.toString() function)
# //   the second is the type of query
# //     2 = event_id
# //    -1 = event before given start_time
# //     0 = event intersects given start_time
# //    +1 = event after given start_time
# //   the third
# //      when type is eventid it is the event_id
# //      when type is time then it is the start_time ( -1 for now_time )
# //   the fourth is the end_time .. ( optional .. for query all events in time range)


	def getChannelEvents(self, sRef, startTime, endTime=None):
		debug("[[[   getChannelEvents(%s, %s, %s)   ]]]" % (sRef, startTime, endTime))
		if not sRef:
			debug("A required parameter 'sRef' is missing!")
			# return None
		else:
			sRef = str(sRef)

		criteria = ['IBDTSENCW']
		criteria.append((sRef, NOW_EVENT, startTime, endTime))
		epgEvents = self._queryEPG(criteria)

		debug(epgEvents)
		return epgEvents


	def _gcnne(self, sRef, nowOrNext):
		if not sRef:
			debug("A required parameter 'sRef' is missing!")
			# return None
		else:
			sRef = str(sRef)

		epgEvent = self.getEventByTime(sRef, TIME_NOW, nowOrNext)
		evtupl = (
			epgEvent.getEventId(),
			epgEvent.getBeginTime(),
			epgEvent.getDuration(),
			localtime(None),
			epgEvent.getEventName(),
			epgEvent.getShortDescription(),
			epgEvent.getExtendedDescription(),
			sRef,
			ServiceReference(sRef).getServiceName(),
			epgEvent.getGenreDataList()
		)

		debug(evtupl)
		return evtupl


	def getChannelNowEvent(self, sRef):
		debug("[[[   getChannelNowEvent(%s)   ]]]" % (sRef))
		return self._gcnne(sRef, NOW_EVENT)


	def getChannelNextEvent(self, sRef):
		debug("[[[   getChannelNextEvent(%s)   ]]]" % (sRef))
		return self._gcnne(sRef, NEXT_EVENT)


	def getMultiChannelEvents(self, sRefs, startTime, endTime=None, criteria=['IBTSRND']):
		debug("[[[   getMultiChannelEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		if not sRefs:
			debug("A required parameter [sRefs] is missing!")
			# return None

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, NOW_EVENT, startTime, endTime))

		epgEvents = self._queryEPG(criteria)

		debug(epgEvents)
		return epgEvents


	def getMultiChannelNowNextEvents(self, sRefs, criteria=['IBDCTSERNX']):
		debug("[[[   getMultiChannelNowNextEvents(%s)   ]]]" % (sRefs))
		if not sRefs:
			debug("A required parameter [sRefs] is missing!")
			# return None

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, NOW_EVENT, TIME_NOW))
			criteria.append((sRef, NEXT_EVENT, TIME_NOW))

		epgEvents = self._queryEPG(criteria)

		debug(epgEvents)
		return epgEvents


	def getBouquetEvents(self, sRefs, startTime, endTime=None):
		debug("[[[   getBouquetEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		#TODO: accept only a bq ref and get list of srefs here
		return self.getMultiChannelEvents(sRefs, startTime, endTime, ['IBDCTSERNWX'])


	def _gbnne(self, bqRef, nowOrNext):
		if not bqRef:
			debug("A required parameter 'bqRef' is missing!")
			# return None

		criteria = ['IBDCTSERNWX']
		sRefs = bqRef

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, nowOrNext, TIME_NOW))

		epgEvents = self._queryEPG(criteria)

		debug(epgEvents)
		return epgEvents


	def getBouquetNowEvents(self, bqRef):
		debug("[[[   getBouquetNowEvents(%s)   ]]]" % (bqRef))
		return self._gbnne(sRefs, NOW_EVENT)


	def getBouquetNextEvents(self, bqRef):
		debug("[[[   getBouquetNowEvents(%s)   ]]]" % (bqRef))
		return self._gbnne(sRefs, NEXT_EVENT)


	def getBouquetNowNextEvents(self, sRefs):
		debug("[[[   getBouquetNowNextEvents(%s)   ]]]" % (sRefs))
		#TODO: accept only a bq ref and get list of srefs here
		return self.getMultiChannelNowNextEvents(sRefs, ['IBDCTSERNWX'])


# /**
#  * @brief Look up an event in the EPG database by service reference and time.
#  * The service reference is specified in @p service.
#  * The lookup time is in @p t.
#  * The @p direction specifies whether to return the event matching @p t, its
#  * predecessor or successor.
#  *
#  * @param service as an eServiceReference.
#  * @param t the lookup time. If t == -1, look up the current time.
#  * @param result the matched event, if one is found.
#  * @param direction The event offset from the match.
#  * @p direction > 0 return the earliest event that starts after t.
#  * @p direction == 0 return the event that spans t. If t is spanned by a gap in the EPG, return None.
#  * @p direction < 0 return the event immediately before the event that spans t.  * If t is spanned by a gap in the EPG, return the event immediately before the gap.
#  * @return 0 for successful match and valid data in @p result,
#  * -1 for unsuccessful.
#  * In a call from Python, a return of -1 corresponds to a return value of None.
#  */
	def getCurrentEvent(self, sRef):
		debug("[[[   getCurrentEvent(%s)   ]]]" % (sRef))
		if not sRef:
			debug("A required parameter 'sRef' is missing!")
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

		debug(epgEvent)
		return epgEvent


	def getEventById(self, sRef, eventId):
		debug("[[[   getEventById(%s, %s)   ]]]" % (sRef, eventId))
		if not sRef or not eventId:
			debug("A required parameter 'sRef' or eventId is missing!")
			# return None
		elif not isinstance(sRef, eServiceReference):
			sRef = eServiceReference(sRef)

		eventId = int(eventId)
		epgEvent = self._instance.lookupEventId(sRef, eventId)

		# debug(json.dumps(epgEvent, indent = 2)) # Object of type eServiceEvent is not JSON serializable
		debug(epgEvent and epgEvent.getEventName() or None)
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


# /**
#  * @brief Look up an event in the EPG database by service reference and time.
#  * The service reference is specified in @p service.
#  * The lookup time is in @p t.
#  * @p direction specifies whether to return the event matching @p t,
#  * its predecessor, or its successor.
#  *
#  * @param service as an eServiceReference.
#  * @param t the lookup time. If t == -1, look up the current time.
#  * @param result the matched event, if one is found.
#  * @param direction the event offset from the match.
#  * @p direction > 0 return the earliest event that starts after t.
#  * @p direction == 0 return the event that spans t. If t is spanned by a gap in the EPG, return None.
#  * @p direction < 0 return the event immediately before the event that spans t.
#  * If t is spanned by a gap in the EPG, return the event immediately before the gap.
#  * @return 0 for successful match and valid data in @p result,
#  * -1 for unsuccessful.
#  * In a call from Python, a return of -1 corresponds to a return value of None.
#  */
	def getEventByTime(self, sRef, eventTime, direction=NOW_EVENT):
		debug("[[[   getEventByTime(%s, %s)   ]]]" % (sRef, eventTime))
		if not sRef or not eventTime:
			debug("A required parameter 'sRef' or eventTime is missing!")
			# return None
		elif not isinstance(sRef, eServiceReference):
			sRef = eServiceReference(sRef)

		epgEvent = self._instance.lookupEventTime(sRef, eventTime, direction)

		# Object of type eServiceEvent is not JSON serializable
		debug(epgEvent)
		return epgEvent


	def getEvent(self, sRef, eventId):
		debug("[[[   getEvent(%s, %s)   ]]]" % (sRef, eventId))
		if not sRef or not eventId:
			debug("A required parameter 'sRef' or eventId is missing!")
			# return None
		else:
			sRef = str(sRef)
			eventId = int(eventId)

		epgEvent = self.getEventById(sRef, eventId)

		if epgEvent:
			print(epgEvent)
			genreData = epgEvent.getGenreDataList()
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

		debug(epgEvent)
		return epgEvent


	def getEventDescription(self, sRef, eventId):
		debug("[[[   getEventDescription(%s, %s)   ]]]" % (sRef, eventId))
		if not sRef or not eventId:
			debug("A required parameter 'sRef' or eventId is missing!")
			return None
		else:
			sRef = str(sRef)
			eventId = int(eventId)

		description = None
		epgEvent = self.getEventById(sRef, eventId)

		if epgEvent:
			description = epgEvent.getExtendedDescription() or epgEvent.getShortDescription() or ""

		debug(description)
		return description


	# /web/loadepg
	def load(self):
		self._instance.load()


	# /web/saveepg
	def save(self):
		self._instance.save()
