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
from Components.config import config

DEBUG_ENABLED = False

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

class Epg():
	NOW = 'now'
	NEXT = 'next'
	NOW_NEXT = 'nowNext'

	def __init__(self):
		self._instance = eEPGCache.getInstance()


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

	def search(self, queryString, searchFullDescription):
		debug("[[[   search(%s, %s)   ]]]" % (queryString, searchFullDescription))
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

		debug(json.dumps(epgEvents, indent = 2))
		return epgEvents


	def findSimilarEvents(self, sRef, eventId):
		debug("[[[   findSimilarEvents(%s, %s)   ]]]" % (sRef, eventId))
		eventId = int(eventId)
		eventFields = 'IBDTSENRW'
		# sRef is expected to be a string
		criteria = (eventFields, MAX_RESULTS, eEPGCache.SIMILAR_BROADCASTINGS_SEARCH, sRef, eventId)
		epgEvents = self._instance.search(criteria)

		debug(json.dumps(epgEvents, indent = 2))
		return epgEvents


	def _transformEventData(self, eventFields, *args):
		eventData = {
			"service": {}
		}
		dateAndTime = {}
		currentTime = 0

		# for index, arg in enumerate(args):
		# 	key = eventFields[index]
		#
		# 	if key == 'I':
		# 		eventData['eventId'] = arg
		# 	elif key == 'B':
		# 		dateAndTime['start'] = arg
		# 		dateAndTime['startDateTime'] = strftime('%c', (localtime(arg)))
		# 		dateAndTime['startDate'] = strftime('%x', (localtime(arg)))
		# 		dateAndTime['startTime'] = strftime('%X', (localtime(arg)))
		# 	elif key == 'D':
		# 		dateAndTime['duration'] = arg
		# 		dateAndTime['durationFormatted'] = strftime("%-Hh %-Mm", gmtime(arg))
		# 	elif key == 'T':
		# 		eventData['title'] = arg
		# 	elif key == 'S':
		# 		eventData['shortDescription'] = arg
		# 	elif key == 'E':
		# 		eventData['extendedDescription'] = arg
		# 	elif key == 'P':
		# 		eventData['parentalRating'] = arg
		# 	elif key == 'W':
		# 		eventData['genre'] = arg
		# 	elif key == 'C':
		# 		currentTime = arg
		# 	elif key == 'R':
		# 		eventData['service']['reference'] = arg
		# 	elif key == 'n':
		# 		eventData['service']['shortName'] = arg
		# 	elif key == 'N':
		# 		eventData['service']['name'] = arg
		# 	# elif key == 'X':
		# 	# 	#ignored
		# 	elif key == 'M':
		# 		eventData['maxResults'] = arg
		# 	else:
		# 		eventData[key] = arg
		#
		# endTimeEpoch = int(dateAndTime['start'] + dateAndTime['duration'])
		# remainingTime = int((endTimeEpoch - dateAndTime['current']) / 60)
		# progressPercent = int(((currentTime - dateAndTime['start']) / dateAndTime['duration']) * 100)
		# progressPercent = progressPercent if progressPercent >= 0 else 0
		# dateAndTime['end'] = endTimeEpoch
		# dateAndTime['endDateTime'] = strftime('%c', (localtime(endTimeEpoch)))
		# dateAndTime['endDate'] = strftime('%x', (localtime(endTimeEpoch)))
		# dateAndTime['endTime'] = strftime('%X', (localtime(endTimeEpoch)))
		# dateAndTime['remaining'] = remainingTime
		# dateAndTime['progressPercent'] = '{0}%'.format(progressPercent)
		# eventData['dateTime'] = dateAndTime

		# debug(json.dumps(eventData, indent=2))
		return args


	def _queryEPG(self, criteria):
		eventFields = criteria[0]

		def _callEventTransform(*args):
			return self._transformEventData(eventFields, *args)

		epgEvents = self._instance.lookupEvent(criteria, _callEventTransform)

		return epgEvents


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

	#TODO: investigate using `get event by id`
	def getEvent(self, sRef, eventId):
		debug("[[[   getEvent(%s, %s)   ]]]" % (sRef, eventId))
		eventId = int(eventId)
		# sRef is not expected to be an instance of eServiceReference
		criteria = ['IBDTSENRW', (sRef, MATCH_EVENT_ID, eventId)]
		epgEvent = self._queryEPG(criteria)

		debug(epgEvent)
		epgEvent = epgEvent[0] if len(epgEvent) > 0 else None

		# debug(json.dumps(epgEvent, indent = 2))
		# debug(epgEvent)
		return epgEvent


	def getChannelEvents(self, sRef, startTime, endTime):
		debug("[[[   getChannelEvents(%s, %s, %s)   ]]]" % (sRef, startTime, endTime))
		# sRef is not expected to be an instance of eServiceReference
		criteria = ['IBDTSENCW', (sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, startTime, endTime)]
		epgEvents = self._queryEPG(criteria)

		# debug(json.dumps(epgEvents, indent = 2))
		debug(epgEvents)
		return epgEvents


	#TODO: investigate using `get event by time`
	def getChannelNowEvent(self, sRef):
		debug("[[[   getChannelNowEvent(%s)   ]]]" % (sRef))
		criteria = ['IBDCTSERNWX', (sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, TIME_NOW)]
		epgEvent = self._queryEPG(criteria)

		# debug(json.dumps(epgEvent, indent = 2))
		debug(epgEvent)
		return epgEvent


	#TODO: investigate using `get event by time`
	def getChannelNextEvent(self, sRef):
		debug("[[[   getChannelNextEvent(%s)   ]]]" % (sRef))
		criteria = ['IBDCTSERNWX', (sRef, MATCH_EVENT_AFTER_GIVEN_START_TIME, TIME_NOW)]
		epgEvent = self._queryEPG(criteria)

		# debug(json.dumps(epgEvent, indent = 2))
		debug(epgEvent)
		return epgEvent


	def getMultiChannelEvents(self, sRefs, startTime, endTime=None):
		debug("[[[   getMultiChannelEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		criteria = ['IBTSRND']

		# sRef is not expected to be an instance of eServiceReference
		for sRef in sRefs:
			# sub-bouquets will cause a `tuple index out of range` error
			if not sRef.startswith('1:7:'):
				if endTime:
					criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, startTime, endTime))
				else:
					criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, startTime))

		epgEvents = self._queryEPG(criteria)

		debug(json.dumps(epgEvents, indent = 2))
		debug(epgEvents)
		return epgEvents


	def getMultiChannelNowNextEvents(self, sRefs=[]):
		debug("[[[   getMultiChannelNowNextEvents(%s)   ]]]" % (sRefs))
		criteria = ['IBDCTSERNX']

		# sRef is not expected to be an instance of eServiceReference
		for sRef in sRefs:
			criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, TIME_NOW))
			criteria.append((sRef, MATCH_EVENT_AFTER_GIVEN_START_TIME, TIME_NOW))

		epgEvents = self._queryEPG(criteria)

		# debug(json.dumps(epgEvents, indent = 2))
		debug(epgEvents)
		return epgEvents


	def getBouquetEvents(self, sRefs, startTime, endTime=-1):
		debug("[[[   getBouquetEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		# prevent crash #TODO: investigate if this is still needed (if so, use now + year or similar)
		if endTime > 100000:
			endTime = -1

		criteria = ['IBDCTSERNWX'] # remove X

		for sRef in sRefs:
			criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, startTime, endTime))

		# sRef is not expected to be an instance of eServiceReference
		epgEvents = self._queryEPG(criteria)

		# debug(json.dumps(epgEvents, indent = 2))
		debug(epgEvents)
		return epgEvents


	#TODO: investigate using `get event by time`
	def getBouquetNowEvents(self, sRefs):
		debug("[[[   getBouquetNowEvents(%s)   ]]]" % (sRefs))
		criteria = ['IBDCTSERNWX']

		for sRef in sRefs:
			criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, TIME_NOW))

		# sRef is not expected to be an instance of eServiceReference
		epgEvents = self._queryEPG(criteria)

		# debug(json.dumps(epgEvents, indent = 2))
		debug(epgEvents)
		return epgEvents


	#TODO: investigate using `get event by time`
	def getBouquetNextEvents(self, sRefs):
		debug("[[[   getBouquetNextEvents(%s)   ]]]" % (sRefs))
		criteria = ['IBDCTSERNWX']

		for sRef in sRefs:
			criteria.append((sRef, MATCH_EVENT_AFTER_GIVEN_START_TIME, TIME_NOW))

		# sRef is not expected to be an instance of eServiceReference
		epgEvents = self._queryEPG(criteria)

		# debug(json.dumps(epgEvents, indent = 2))
		debug(epgEvents)
		return epgEvents


	def getBouquetNowNextEvents(self, sRefs):
		debug("[[[   getBouquetNowNextEvents(%s)   ]]]" % (sRefs))
		criteria = ['IBDCTSERNWX']

		for sRef in sRefs:
			criteria.append((sRef, MATCH_EVENT_INTERSECTING_GIVEN_START_TIME, TIME_NOW))
			criteria.append((sRef, MATCH_EVENT_AFTER_GIVEN_START_TIME, TIME_NOW))

		# sRef is not expected to be an instance of eServiceReference
		epgEvents = self._queryEPG(criteria)

		# debug(json.dumps(epgEvents, indent = 2))
		debug(epgEvents)
		return epgEvents


	# TODO: get event by id instead
	def getEventDescription(self, sRef, eventId):
		debug("[[[   getEventDescription(%s, %s, %s)   ]]]" % (sRef, 'MATCH_EVENT_ID', eventId))
		sRef = str(sRef)
		eventId = int(eventId)
		criteria = ['ESX', (sRef, MATCH_EVENT_ID, eventId)]
		description = ""
		epgEvent = self._queryEPG(criteria)

		if len(epgEvent) > 0:

			description = epgEvent[0][0] or epgEvent[0][1] or ""
		return description


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
		if not isinstance(sRef, eServiceReference):
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

		# debug(json.dumps(epgEvent, indent = 2))
		debug(epgEvent)
		return epgEvent


	def getEventById(self, sRef, eventId):
		debug("[[[   getEventById(%s, %s)   ]]]" % (sRef, eventId))
		if not isinstance(sRef, eServiceReference):
			sRef = eServiceReference(sRef)

		eventId = int(eventId)
		epgEvent = self._instance.lookupEventId(sRef, eventId)

		# debug(json.dumps(epgEvent, indent = 2)) # Object of type eServiceEvent is not JSON serializable
		debug(epgEvent)
		return epgEvent


	# /web/loadepg
	def load(self):
		self._instance.load()


	# /web/saveepg
	def save(self):
		self._instance.save()
