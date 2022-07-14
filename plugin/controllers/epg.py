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
MATCH_EVENT_BEFORE_GIVEN_START_TIME = -1
MATCH_EVENT_INTERSECTING_GIVEN_START_TIME = 0
MATCH_EVENT_AFTER_GIVEN_START_TIME = +1
TIME_NOW = -1


def debug(msg):
	if DEBUG_ENABLED:
		print(msg)


def getHoursMinutesFormatted(timestamp=0):
	timeStruct = gmtime(timestamp)
	textParts = []
	if timeStruct[3]:
		textParts.append("%-Hh")
	if timeStruct[4]:
		textParts.append("%-Mm")
	formatted = strftime(" ".join(textParts), timeStruct)  # if remaining is not None else None
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
		debug(*args)

		eventData = {}
		dateAndTime = {}
		service = {}
		startTimestamp = 0
		duration = 0
		currentTimestamp = 0
		longDescription = ""
		shortDescription = ""


		# TODO: skip processing if there isn't a valid event (id is None)

		for index, arg in enumerate(args):
			key = eventFields[index]

			if key == 'I':
				eventData['eventId'] = arg
			elif key == 'B':
				startTimestamp = arg
				dateAndTime['start'] = arg
				dateAndTime['startDate'] = strftime(config.usage.date.displayday.value, (localtime(arg))) if arg is not None else None
				dateAndTime['startTime'] = strftime(config.usage.time.short.value, (localtime(arg))) if arg is not None else None
				dateAndTime['startDateTime'] = strftime('%c', (localtime(arg))) if arg is not None else None
				dateAndTime['startFuzzy'] = "" if arg is not None else None
			elif key == 'D':
				duration = arg or 0
				dateAndTime['duration'] = duration
				dateAndTime['durationMinutes'] = int(duration / 60)
				dateAndTime['durationFormatted'] = getHoursMinutesFormatted(duration)
			elif key == 'T':
				eventData['title'] = arg
			elif key == 'S':
				shortDescription = arg.strip() if arg is not None else None
				eventData['shortDescription'] = shortDescription
			elif key == 'E':
				longDescription = arg.strip() if arg is not None else None
				eventData['longDescription'] = longDescription
			elif key == 'P':
				eventData['parentalRating'] = arg
			elif key == 'W':
				eventData['genre'], eventData['genreId'] = convertGenre(arg)
			elif key == 'C':
				currentTimestamp = arg
				dateAndTime['current'] = currentTimestamp
			elif key == 'R':
				service['sRef'] = arg
			elif key == 'n':
				service['nameShort'] = arg
			elif key == 'N':
				service['name'] = arg
			elif key == 'X':
				#ignored
				pass
			elif key == 'M':
				eventData['maxResults'] = arg
			else:
				eventData[key] = arg

		if startTimestamp and duration:
			endTimestamp = dateAndTime['start'] + duration
			dateAndTime['end'] = endTimestamp
			dateAndTime['endDate'] = strftime('%x', (localtime(endTimestamp)))
			dateAndTime['endTime'] = strftime(config.usage.time.short.value, (localtime(endTimestamp))) if endTimestamp is not None else None
			dateAndTime['endDateTime'] = strftime('%c', (localtime(endTimestamp)))
			dateAndTime['endFuzzy'] = ""
			if currentTimestamp:
				remaining = endTimestamp - currentTimestamp if currentTimestamp > startTimestamp else duration
				dateAndTime['remaining'] = remaining
				dateAndTime['remainingMinutes'] = int(remaining / 60)
				dateAndTime['remainingFormatted'] = getHoursMinutesFormatted(remaining)
				progressPercent = int(((currentTimestamp - startTimestamp) / duration) * 100)
				progressPercent = progressPercent if progressPercent >= 0 else 0
				dateAndTime['progress'] = progressPercent
				dateAndTime['progressFormatted'] = '{0}%'.format(progressPercent)

		eventData['dateTime'] = dateAndTime
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
		criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, startTime, endTime))
		epgEvents = self._queryEPG(criteria)

		debug(epgEvents)
		return epgEvents


	#TODO: investigate using `get event by time`
	def getChannelNowEvent(self, sRef):
		debug("[[[   getChannelNowEvent(%s)   ]]]" % (sRef))
		if not sRef:
			debug("A required parameter 'sRef' is missing!")
			# return None
		else:
			sRef = str(sRef)

		criteria = ['IBDCTSERNWX']
		criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, TIME_NOW))
		epgEvent = self._queryEPG(criteria)

		#epgEvent = self.getEventByTime(sRef, None)

		debug(epgEvent)
		return epgEvent


	#TODO: investigate using `get event by time`
	def getChannelNextEvent(self, sRef):
		debug("[[[   getChannelNextEvent(%s)   ]]]" % (sRef))
		if not sRef:
			debug("A required parameter 'sRef' is missing!")
			# return None
		else:
			sRef = str(sRef)

		criteria = ['IBDCTSERNWX']
		criteria.append((sRef, MATCH_EVENT_AFTER_GIVEN_START_TIME, TIME_NOW))
		epgEvent = self._queryEPG(criteria)

		#epgEvent = self.getEventByTime(sRef, None)

		debug(epgEvent)
		return epgEvent


	def getMultiChannelEvents(self, sRefs, startTime, endTime=None):
		debug("[[[   getMultiChannelEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		if not sRefs:
			debug("A required parameter [sRefs] is missing!")
			# return None

		criteria = ['IBTSRND']

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, startTime, endTime))

		epgEvents = self._queryEPG(criteria)

		debug(epgEvents)
		return epgEvents


	def getMultiChannelNowNextEvents(self, sRefs):
		debug("[[[   getMultiChannelNowNextEvents(%s)   ]]]" % (sRefs))
		if not sRefs:
			debug("A required parameter [sRefs] is missing!")
			# return None

		criteria = ['IBDCTSERNX']

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, TIME_NOW))
			criteria.append((sRef, MATCH_EVENT_AFTER_GIVEN_START_TIME, TIME_NOW))

		epgEvents = self._queryEPG(criteria)

		debug(epgEvents)
		return epgEvents


	def getBouquetEvents(self, sRefs, startTime, endTime=None):
		debug("[[[   getBouquetEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		if not sRefs:
			debug("A required parameter [sRefs] is missing!")
			# return None

		# prevent crash #TODO: investigate if this is still needed (if so, use now + year or similar)
		if endTime > 100000:
			endTime = -1

		criteria = ['IBDCTSERNWX'] # remove X

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, startTime, endTime))

		epgEvents = self._queryEPG(criteria)

		debug(epgEvents)
		return epgEvents


	#TODO: investigate using `get event by time`
	def getBouquetNowEvents(self, sRefs):
		debug("[[[   getBouquetNowEvents(%s)   ]]]" % (sRefs))
		if not sRefs:
			debug("A required parameter [sRefs] is missing!")
			# return None

		criteria = ['IBDCTSERNWX']

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, TIME_NOW))

		epgEvents = self._queryEPG(criteria)

		debug(epgEvents)
		return epgEvents


	#TODO: investigate using `get event by time`
	def getBouquetNextEvents(self, sRefs):
		debug("[[[   getBouquetNextEvents(%s)   ]]]" % (sRefs))
		if not sRefs:
			debug("A required parameter [sRefs] is missing!")
			# return None

		criteria = ['IBDCTSERNWX']

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, MATCH_EVENT_AFTER_GIVEN_START_TIME, TIME_NOW))

		epgEvents = self._queryEPG(criteria)

		debug(epgEvents)
		return epgEvents


	def getBouquetNowNextEvents(self, sRefs):
		debug("[[[   getBouquetNowNextEvents(%s)   ]]]" % (sRefs))
		if not sRefs:
			debug("A required parameter [sRefs] is missing!")
			# return None

		criteria = ['IBDCTSERNWX']

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, TIME_NOW))
			criteria.append((sRef, MATCH_EVENT_AFTER_GIVEN_START_TIME, TIME_NOW))

		epgEvents = self._queryEPG(criteria)

		debug(epgEvents)
		return epgEvents


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
	def getEventByTime(self, sRef, eventTime):
		debug("[[[   getEventByTime(%s, %s)   ]]]" % (sRef, eventTime))
		if not sRef or not eventId:
			debug("A required parameter 'sRef' or eventTime is missing!")
			# return None
		elif not isinstance(sRef, eServiceReference):
			sRef = eServiceReference(sRef)

		epgEvent = self._instance.lookupEventTime(sRef, eventTime)

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
			genreData = epgEvent.getGenreDataList()
			def getEndTime(): return epgEvent.getBeginTime() + epgEvent.getDuration()
			def getServiceReference(): return sRef
			def getServiceName(): return ServiceReference(sRef).getServiceName()
			def getGenre(): return genreData[0]
			def getGenreId(): return genreData[1]
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
