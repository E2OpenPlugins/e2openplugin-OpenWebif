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

import logging

from time import time, localtime, gmtime, strftime
from datetime import datetime, timedelta
from json import dumps

from enigma import eEPGCache, eServiceCenter, eServiceEvent, eServiceReference
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

BOUQUET_NOWNEXT_FIELDS = 'IBDCTSERNWX' # getBouquetNowNextEvents, _getBouquetNowOrNext
BOUQUET_FIELDS         = 'IBDCTSERNW'  # getBouquetEvents
MULTI_CHANNEL_FIELDS   = 'IBTSRND'     # getMultiChannelEvents
MULTI_NOWNEXT_FIELDS   = 'TBDCIESX'    # getMultiChannelNowNextEvents
SINGLE_CHANNEL_FIELDS  = 'IBDTSENCW'   # getChannelEvents;
SEARCH_FIELDS          = 'IBDTSENRW'   # search, findSimilarEvents

TEXT_YESTERDAY         = 'Yesterday, %R'
TEXT_TODAY             = 'Today, %R'
TEXT_TOMORROW          = 'Tomorrow, %R'


logging.basicConfig(level=logging.DEBUG, stream=logging.StreamHandler(), format='%(levelname)s: %(funcName)s(): %(message)s')
# logger = logging.getLogger(__name__) # Plugins.Extensions.OpenWebif.controllers.epg:
logger = logging.getLogger('[OpenWebif] [EPG]')

if DEBUG_ENABLED:
	logger.setLevel(logging.DEBUG)
else:
	logger.disabled = True


# TODO: load configgy stuff once


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

# TODO: move to utilities
def getFuzzyDayTime(timestamp, defaultFormat):
	timeNow = int(time())
	timeDiff = timestamp - timeNow
	deltaDays = timedelta(seconds = timeDiff).days

	if -2 <= deltaDays <= 2:
		dayDiff = localtime(timestamp)[2] - localtime(timeNow)[2]
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


# TODO: move to utilities
def getCustomTimeFormats(timestamp):
	return {
		'timestamp': timestamp,
		'date': strftime(config.usage.date.displayday.value, (localtime(timestamp))),
		'time': strftime(config.usage.time.short.value, (localtime(timestamp))),
		'dateTime': strftime('%c', (localtime(timestamp))),
		'fuzzy': getFuzzyDayTime(timestamp, '%c'),
		'iso': datetime.fromtimestamp(timestamp).isoformat() if not None else ''
	}


# TODO: move to utilities
def getFuzzyHoursMinutes(timestamp = 0):
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


def getBouquetServices(bqRef, fields = 'SN'):
	bqServices = eServiceCenter.getInstance().list(eServiceReference(bqRef))

	return bqServices.getContent(fields)


# TODO: move to utilities
# TODO: fixme
def convertGenre(val):
	logger.debug("[[[   convertGenre(%s)   ]]]" % (val))
	value = "", 0
	try:
		if val is not None and len(val) > 0:
			val = val[0]
			if len(val) > 1:
				if val[0] > 0:
					genreId = val[0] * 16 + val[1]
					return str(getGenreStringLong(val[0], val[1])).strip(), genreId
	except Exception as exc:
		logging.error(exc)

	logger.debug(value)
	return value


def getServiceDetails(sRef):
	try:
		sRefStr = str(ServiceReference(sRef))
	except:
		sRefStr = sRef

	value = None

	if sRef:
		value = {
			'sRef': sRefStr,
			'name': ServiceReference(sRef).getServiceName(),
			# 'path': ServiceReference(sRef).getPath(),
			# 'sType': ServiceReference(sRef).getType(),
			# 'flags': ServiceReference(sRef).getFlags(),
		}

	return value


# TODO: move to utilities
class TimedProcess:
	def __init__(self):
		self.timeTaken = 0
		pass

	def __enter__(self):
		self.tick = datetime.now()
		return self

	def __exit__(self, exc_type, exc_value, exc_tb):
		self.timeTaken = datetime.now() - self.tick
		logger.debug('Process took {}'.format(self.timeTaken))

	def getTimeTaken(self):
		return self.timeTaken


class EPGEvent():
	def __init__(self, evt):
		eventId = None
		startTimestamp = None
		durationSeconds = None
		title = None
		shortDescription = None
		longDescription = None
		parentalRatingData = None
		genreData = None
		currentTimestamp = None
		service = {}

		if isinstance(evt, eServiceEvent):
			eventId = evt.getEventId()
			startTimestamp = evt.getBeginTime()
			durationSeconds = evt.getDuration()
			currentTimestamp = int(time())
			title = evt.getEventName()
			shortDescription = evt.getShortDescription()
			longDescription = evt.getExtendedDescription()
			parentalRatingData = evt.getParentalData()
			genreData = evt.getGenreData()

		elif isinstance(evt, tuple):
			eventFields = evt[0]
			eventData = evt[1]

			for index, value in enumerate(eventData):
				try:
					key = eventFields[index]
					if key == 'I':
						eventId = value
					elif key == 'B':
						startTimestamp = value
					elif key == 'D':
						durationSeconds = value
					elif key == 'T':
						title = value
					elif key == 'S':
						shortDescription = value
					elif key == 'E':
						longDescription = value
					elif key == 'P':
						parentalRatingData = value
					elif key == 'W':
						genreData = value
					elif key == 'C':
						currentTimestamp = value
					elif key == 'R':
						service['sRef'] = value
					elif key == 'n':
						service['shortName'] = value
					elif key == 'N':
						service['name'] = value
					elif key == 'X':
						pass
					elif key == 'M':
						self.maxResults = value
					# else:
					# 	eventData[key] = value

				except Exception as error:
					logger.warning(error)

		self.eventId = eventId
		self.title = (title or '').strip()
		self.shortDescription = (shortDescription or '').strip()
		self.longDescription = (longDescription or '').strip()
		self.description = (longDescription or shortDescription or '').strip()
		self.parentalRating = parentalRatingData
		self.genre, self.genreId = convertGenre(genreData)

		if len(service) > 0:
			self.service = service

		if startTimestamp is not None:
			self.start = getCustomTimeFormats(startTimestamp)

		if durationSeconds is not None:
			self.duration = {
				'seconds': durationSeconds,
				'minutes': int(durationSeconds / 60),
				'fuzzy': getFuzzyHoursMinutes(durationSeconds),
			}

		if currentTimestamp is not None:
			self.currentTimestamp = currentTimestamp

		if startTimestamp and durationSeconds is not None:
			endTimestamp = startTimestamp + durationSeconds
			try:
				self.end = getCustomTimeFormats(endTimestamp)
			except Exception as error:
				logger.warning(error)
			if currentTimestamp:
				remaining = endTimestamp - currentTimestamp if currentTimestamp > startTimestamp else durationSeconds
				try:
					progressPercent = int(((currentTimestamp - startTimestamp) / durationSeconds) * 100)
					progressPercent = progressPercent if progressPercent >= 0 else 0
					self.progress = {
						'number': progressPercent,
						'text': '{0}%'.format(progressPercent),
					}
					self.remaining = {
						'seconds': remaining,
						'minutes': int(remaining / 60),
						'text': getFuzzyHoursMinutes(remaining),
					}
				except Exception as error:
					logger.warning(error)


	def toJSON(self, **kwargs):
		# dict keys that are not of a basic type (str, int, float, bool, None) will raise a TypeError.
		return dumps(self.__dict__, **kwargs)


class Epg():
	NOW = 10
	NEXT = 11
	NOW_NEXT = 21

	def __init__(self):
		self._instance = eEPGCache.getInstance()

	@staticmethod
	def getEncoding():
		return config.OpenWebif.epg_encoding.value


	# TODO: make search type fully customisable
	def search(self, queryString, searchFullDescription = False):
		logger.debug("search[[[   (%s, %s)   ]]]" % (queryString, searchFullDescription))
		if not queryString:
			logger.error("A required parameter 'queryString' is missing!")

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
		with TimedProcess() as tp:
			epgEvents = self._instance.search(criteria)

		logger.debug(tp.getTimeTaken())

		logger.debug(epgEvents[-1].toJSON(indent = 2) if len(epgEvents) else epgEvents)
		return epgEvents


	def findSimilarEvents(self, sRef, eventId):
		logger.debug("[[[   findSimilarEvents(%s, %s)   ]]]" % (sRef, eventId))
		if not sRef or not eventId:
			logger.error("A required parameter 'sRef' or eventId is missing!")
			# return None
		else:
			sRef = str(sRef)
			eventId = int(eventId)

		criteria = (SEARCH_FIELDS, MAX_RESULTS, eEPGCache.SIMILAR_BROADCASTINGS_SEARCH, sRef, eventId)
		with TimedProcess() as tp:
			epgEvents = self._instance.search(criteria)

		logger.debug(tp.getTimeTaken())

		logger.debug(epgEvents[-1].toJSON(indent = 2) if len(epgEvents) else epgEvents)
		return epgEvents


	@staticmethod
	def _transformEventData(eventFields, data):
		# logger.debug("[[[   _transformEventData(%s)   ]]]" % (eventFields))
		# logger.debug(data)

		# TODO: skip processing if there isn't a valid event (id is None)
		# TODO: skip 1:7:1: (sub-bouquets)
		# TODO: remove 'currentStart' (currently still needed?)
		# TODO: auto add currentTimestamp if progress or remaining fields are requested

		return EPGEvent((eventFields, data))


	def _queryEPG(self, fields = '', criteria = []):
		if not fields or not criteria:
			logger.error("A required parameter 'fields' or [criteria] is missing!")
			# return None

		criteria.insert(0, fields)
		epgEvents = self._instance.lookupEvent(criteria)
		with TimedProcess() as tp:
			epgEvents = [self._transformEventData(fields, evt) for evt in epgEvents]

		logger.debug(tp.getTimeTaken())

		logger.debug(epgEvents[-1].toJSON(indent = 2) if len(epgEvents) else epgEvents)
		return epgEvents


	def _getChannelNowOrNext(self, sRef, nowOrNext):
		if not sRef:
			logger.error("A required parameter 'sRef' is missing!")
			# return None
		else:
			sRef = str(sRef)

		with TimedProcess() as tp:
			epgEvent = self.getEventByTime(sRef, TIME_NOW, nowOrNext)

		logger.debug(epgEvent.toJSON(indent = 2))
		return epgEvent


	def _getBouquetNowOrNext(self, bqRef, nowOrNext):
		if not bqRef:
			logger.error("A required parameter 'bqRef' is missing!")
			# return None

		sRefs = getBouquetServices(bqRef, 'S')
		criteria = []

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, nowOrNext, TIME_NOW))

		with TimedProcess() as tp:
			epgEvents = self._queryEPG(BOUQUET_NOWNEXT_FIELDS, criteria)

		logger.debug(epgEvents[-1].toJSON(indent = 2) if len(epgEvents) else epgEvents)
		return epgEvents


	def getChannelEvents(self, sRef, startTime, endTime = None):
		logger.debug("[[[   getChannelEvents(%s, %s, %s)   ]]]" % (sRef, startTime, endTime))
		if not sRef:
			logger.error("A required parameter 'sRef' is missing!")
			# return None
		else:
			sRef = str(sRef)

		criteria = [(sRef, NOW_EVENT, startTime, endTime)]

		with TimedProcess() as tp:
			epgEvents = self._queryEPG(SINGLE_CHANNEL_FIELDS, criteria)

		logger.debug(epgEvents[-1].toJSON(indent = 2) if len(epgEvents) else epgEvents)
		return epgEvents


	def getChannelNowEvent(self, sRef):
		logger.debug("[[[   getChannelNowEvent(%s)   ]]]" % (sRef))
		return self._getChannelNowOrNext(sRef, NOW_EVENT)


	def getChannelNextEvent(self, sRef):
		logger.debug("[[[   getChannelNextEvent(%s)   ]]]" % (sRef))
		return self._getChannelNowOrNext(sRef, NEXT_EVENT)


	def getMultiChannelEvents(self, sRefs, startTime, endTime = None, fields = MULTI_CHANNEL_FIELDS):
		logger.debug("[[[   getMultiChannelEvents(%s, %s, %s)   ]]]" % (sRefs, startTime, endTime))
		if not sRefs:
			logger.error("A required parameter [sRefs] is missing!")
			# return None

		criteria = []

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, NOW_EVENT, startTime, endTime))

		with TimedProcess() as tp:
			epgEvents = self._queryEPG(fields, criteria)

		logger.debug(epgEvents[-1].toJSON(indent = 2) if len(epgEvents) else epgEvents)
		return epgEvents


	def getMultiChannelNowNextEvents(self, sRefs, fields = MULTI_NOWNEXT_FIELDS):
		logger.debug("[[[   getMultiChannelNowNextEvents(%s)   ]]]" % (sRefs))
		if not sRefs:
			logger.error("A required parameter [sRefs] is missing!")
			# return None

		criteria = []

		for sRef in sRefs:
			sRef = str(sRef)
			criteria.append((sRef, NOW_EVENT, TIME_NOW))
			criteria.append((sRef, NEXT_EVENT, TIME_NOW))

		with TimedProcess() as tp:
			epgEvents = self._queryEPG(fields, criteria)

		logger.debug(epgEvents[-1].toJSON(indent = 2) if len(epgEvents) else epgEvents)
		return epgEvents


	def getBouquetEvents(self, bqRef, startTime, endTime = None):
		logger.debug("[[[   getBouquetEvents(%s, %s, %s)   ]]]" % (bqRef, startTime, endTime))
		sRefs = getBouquetServices(bqRef, 'S')

		return self.getMultiChannelEvents(sRefs, startTime, endTime, BOUQUET_FIELDS)


	def getBouquetNowEvents(self, bqRef):
		logger.debug("[[[   getBouquetNowEvents(%s)   ]]]" % (bqRef))

		return self._getBouquetNowOrNext(bqRef, NOW_EVENT)


	def getBouquetNextEvents(self, bqRef):
		logger.debug("[[[   getBouquetNowEvents(%s)   ]]]" % (bqRef))

		return self._getBouquetNowOrNext(bqRef, NEXT_EVENT)


	def getBouquetNowNextEvents(self, bqRef):
		logger.debug("[[[   getBouquetNowNextEvents(%s)   ]]]" % (bqRef))
		sRefs = getBouquetServices(bqRef, 'S')

		return self.getMultiChannelNowNextEvents(sRefs, BOUQUET_NOWNEXT_FIELDS)


	def getCurrentEvent(self, sRef):
		logger.debug("[[[   getCurrentEvent(%s)   ]]]" % (sRef))
		if not sRef:
			logger.error("A required parameter 'sRef' is missing!")
			# return None
		elif not isinstance(sRef, eServiceReference):
			sRef = eServiceReference(sRef)

		with TimedProcess() as tp:
			epgEvent = self._instance.lookupEventTime(sRef, TIME_NOW, 0)

		epgEvent = EPGEvent(epgEvent)

		logger.debug(epgEvent.toJSON(indent = 2))
		return epgEvent


	def getEventById(self, sRef, eventId):
		logger.debug("[[[   getEventById(%s, %s)   ]]]" % (str(sRef), eventId))
		if not sRef or not eventId:
			logger.error("A required parameter 'sRef' or eventId is missing!")
			# return None
		elif not isinstance(sRef, eServiceReference):
			sRef = eServiceReference(sRef)

		eventId = int(eventId)

		with TimedProcess() as tp:
			epgEvent = self._instance.lookupEventId(sRef, eventId)

		epgEvent = EPGEvent(epgEvent)
		epgEvent.service = getServiceDetails(sRef)

		logger.debug(epgEvent.toJSON(indent = 2))
		return epgEvent

		# ServiceReference(sRef).getServiceName(),
		# sRef,
		# epgEvent.getSeriesCrid(),
		# epgEvent.getEpisodeCrid(),
		# epgEvent.getRunningStatus(),
		# epgEvent.getExtraEventData(),
		# epgEvent.getPdcPil()


	def getEventByTime(self, sRef, eventTime, direction = NOW_EVENT):
		logger.debug("[[[   getEventByTime(%s, %s)   ]]]" % (sRef, eventTime))
		if not sRef or not eventTime:
			logger.error("A required parameter 'sRef' or eventTime is missing!")
			# return None
		elif not isinstance(sRef, eServiceReference):
			sRef = eServiceReference(sRef)

		with TimedProcess() as tp:
			epgEvent = self._instance.lookupEventTime(sRef, eventTime, direction)

		epgEvent = EPGEvent(epgEvent)
		epgEvent.service = getServiceDetails(sRef)

		logger.debug(epgEvent.toJSON(indent = 2))
		return epgEvent


	def getEvent(self, sRef, eventId):
		logger.debug("[[[   getEvent(%s, %s)   ]]]" % (sRef, eventId))

		epgEvent = self.getEventById(sRef, eventId)
		# epgEvent = EPGEvent(epgEvent) # already transformed by `getEventById()`

		logger.debug(epgEvent.toJSON(indent = 2))
		return epgEvent


	def getEventDescription(self, sRef, eventId):
		logger.debug("[[[   getEventDescription(%s, %s)   ]]]" % (sRef, eventId))
		if not sRef or not eventId:
			logger.error("A required parameter 'sRef' or eventId is missing!")
			return None
		else:
			sRef = str(sRef)
			eventId = int(eventId)

		description = None
		epgEvent = self.getEventById(sRef, eventId)

		if epgEvent:
			description = epgEvent.description

		logger.debug(description)
		return description


	# /web/loadepg
	def load(self):
		self._instance.load()


	# /web/saveepg
	def save(self):
		self._instance.save()
