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
from datetime import datetime, timedelta
from json import dumps

from enigma import eEPGCache, eServiceCenter, eServiceReference
from ServiceReference import ServiceReference
from Components.config import config
from .defaults import DEBUG_ENABLED

try:
	from Components.Converter.genre import getGenreStringLong
except ImportError:
	def getGenreStringLong(*args): return ""


CASE_SENSITIVE_QUERY   = 0
CASE_INSENSITIVE_QUERY = 1
REGEX_QUERY            = 2
MAX_RESULTS            = 128
MATCH_EVENT_ID         = 2
PREVIOUS_EVENT         = -1
NOW_EVENT              = 0
NEXT_EVENT             = +1
TIME_NOW               = -1
REGEX_QUERY = 2
MAX_RESULTS = 128
MATCH_EVENT_ID = 2
MATCH_EVENT_BEFORE_GIVEN_START_TIME = -1
MATCH_EVENT_INTERSECTING_GIVEN_START_TIME = 0
MATCH_EVENT_AFTER_GIVEN_START_TIME = +1
TIME_NOW = -1

BOUQUET_FIELDS         = 'IBDCTSERNW'  # getBouquetEvents

def debug(msg):
	if DEBUG_ENABLED:
		print(msg)


class Epg():
	NOW = 10
	NEXT = 11
	NOW_NEXT = 21

	def __init__(self):
		self._instance = eEPGCache.getInstance()


	def getEncoding(self):
		return config.OpenWebif.epg_encoding.value


	def search(self, queryString, searchFullDescription):
		debug("[[[   search(%s, %s)   ]]]" % (queryString, searchFullDescription))
		queryType = eEPGCache.PARTIAL_TITLE_SEARCH
		epgEncoding = config.OpenWebif.epg_encoding.value

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

		criteria = (SEARCH_FIELDS, MAX_RESULTS, queryType, queryString, CASE_INSENSITIVE_QUERY)
		epgEvents = self._instance.search(criteria)

		debug(json.dumps(epgEvents, indent=2))
		return epgEvents

	def findSimilarEvents(self, sRef, eventId):
		_debug("[[[   findSimilarEvents(%s, %s)   ]]]" % (sRef, eventId))
		if not sRef or not eventId:
			_debug("A required parameter 'sRef' or eventId is missing!")
			# return None
		else:
			sRef = str(sRef)
			eventId = int(eventId)

		criteria = (SEARCH_FIELDS, MAX_RESULTS, eEPGCache.SIMILAR_BROADCASTINGS_SEARCH, sRef, eventId)
		epgEvents = self._instance.search(criteria)

		debug(json.dumps(epgEvents, indent=2))
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
		# TODO: skip 1:7:1: (sub-bouquets)

	def _queryEPG(self, criteria):
		eventFields = criteria[0]

		if startTimestamp and duration:
			endTimestamp = startTimestamp + duration
			try:
				endTimeFormats = getCustomTimeFormats(endTimestamp)
				dateAndTime['end'] = endTimeFormats['timestamp']
				dateAndTime['endDate'] = endTimeFormats['date']
				dateAndTime['endTime'] = endTimeFormats['time']
				dateAndTime['endDateTime'] = endTimeFormats['dateTime']
				dateAndTime['endFuzzy'] = endTimeFormats['fuzzy']
			except Exception as error:
				print(error)
			if currentTimestamp:
				remaining = endTimestamp - currentTimestamp if currentTimestamp > startTimestamp else duration
				try:
					dateAndTime['remaining'] = remaining
					dateAndTime['remainingMinutes'] = int(remaining / 60)
					dateAndTime['remainingFormatted'] = getFuzzyHoursMinutes(remaining)
					progressPercent = int(((currentTimestamp - startTimestamp) / duration) * 100)
					progressPercent = progressPercent if progressPercent >= 0 else 0
					dateAndTime['progress'] = progressPercent
					dateAndTime['progressFormatted'] = '{0}%'.format(progressPercent)
				except Exception as error:
					print(error)

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

	#TODO: investigate using `get event by id`

	def getEvent(self, sRef, eventId):
		debug("[[[   getEvent(%s, %s)   ]]]" % (sRef, eventId))
		eventId = int(eventId)
		# sRef is not expected to be an instance of eServiceReference
		criteria = ['IBDTSENRW', (sRef, MATCH_EVENT_ID, eventId)]
		epgEvent = self._queryEPG(criteria)

		def _callEventTransform(*args):
			return self._transformEventData(fields, *args)

		epgEvents = self._instance.lookupEvent(criteria, _callEventTransform)

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

		epgEvent = self.getEventByTime(sRef, TIME_NOW, nowOrNext)

	#TODO: investigate using `get event by time`

	def getChannelNextEvent(self, sRef):
		debug("[[[   getChannelNextEvent(%s)   ]]]" % (sRef))
		criteria = ['IBDCTSERNWX', (sRef, MATCH_EVENT_AFTER_GIVEN_START_TIME, TIME_NOW)]
		epgEvent = self._queryEPG(criteria)


	def getMultiChannelEvents(self, sRefs, startTime, endTime=None):
		debug("[[[   getMultiChannelEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		criteria = ['IBTSRND']

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, nowOrNext, TIME_NOW))

		epgEvents = self._queryEPG(BOUQUET_NOWNEXT_FIELDS, criteria)

		debug(json.dumps(epgEvents, indent=2))
		debug(epgEvents)
		return epgEvents

	def getMultiChannelNowNextEvents(self, sRefs=[]):
		debug("[[[   getMultiChannelNowNextEvents(%s)   ]]]" % (sRefs))
		criteria = ['IBDCTSERNX']

		criteria = []
		criteria.append((sRef, NOW_EVENT, startTime, endTime))
		epgEvents = self._queryEPG(SINGLE_CHANNEL_FIELDS, criteria)

		_debug(epgEvents)
		return epgEvents

	def getBouquetEvents(self, sRefs, startTime, endTime=-1):
		debug("[[[   getBouquetEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		# prevent crash #TODO: investigate if this is still needed (if so, use now + year or similar)
		if endTime > 100000:
			endTime = -1

		criteria = ['IBDCTSERNWX']  # remove X

	def getChannelNextEvent(self, sRef):
		_debug("[[[   getChannelNextEvent(%s)   ]]]" % (sRef))
		return self._getChannelNowOrNext(sRef, NEXT_EVENT)


	def getMultiChannelEvents(self, sRefs, startTime, endTime=None, fields=MULTI_CHANNEL_FIELDS):
		_debug("[[[   getMultiChannelEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		if not sRefs:
			_debug("A required parameter [sRefs] is missing!")
			# return None

	#TODO: investigate using `get event by time`

	def getBouquetNowEvents(self, sRefs):
		debug("[[[   getBouquetNowEvents(%s)   ]]]" % (sRefs))
		criteria = ['IBDCTSERNWX']

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, NOW_EVENT, startTime, endTime))

		epgEvents = self._queryEPG(fields, criteria)

		_debug(epgEvents)
		return epgEvents

	#TODO: investigate using `get event by time`

	def getBouquetNextEvents(self, sRefs):
		debug("[[[   getBouquetNextEvents(%s)   ]]]" % (sRefs))
		criteria = ['IBDCTSERNWX']

		criteria = []

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, NOW_EVENT, TIME_NOW))
			criteria.append((sRef, NEXT_EVENT, TIME_NOW))

		epgEvents = self._queryEPG(fields, criteria)

		_debug(epgEvents)
		return epgEvents

	def getBouquetNowNextEvents(self, sRefs):
		debug("[[[   getBouquetNowNextEvents(%s)   ]]]" % (sRefs))
		criteria = ['IBDCTSERNWX']

		return self.getMultiChannelEvents(sRefs, startTime, endTime, BOUQUET_FIELDS)


	def getBouquetNowEvents(self, bqRef):
		_debug("[[[   getBouquetNowEvents(%s)   ]]]" % (bqRef))

	# TODO: get event by id instead

	def getEventDescription(self, sRef, eventId):
		debug("[[[   getEventDescription(%s, %s, %s)   ]]]" % (sRef, 'MATCH_EVENT_ID', eventId))
		sRef = str(sRef)
		eventId = int(eventId)
		criteria = ['ESX', (sRef, MATCH_EVENT_ID, eventId)]
		description = ""
		epgEvent = self._queryEPG(criteria)

	def getBouquetNextEvents(self, bqRef):
		_debug("[[[   getBouquetNowEvents(%s)   ]]]" % (bqRef))

		return self._getBouquetNowOrNext(bqRef, NEXT_EVENT)


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

	def getEventByTime(self, sRef, eventTime):
		debug("[[[   getEventByTime(%s, %s)   ]]]" % (sRef, eventTime))
		if not isinstance(sRef, eServiceReference):
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
