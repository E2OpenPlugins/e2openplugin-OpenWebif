##########################################################################
# OpenWebif: EPG
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

from datetime import datetime, timedelta
from json import dumps

from enigma import eEPGCache, eServiceCenter, eServiceReference
from ServiceReference import ServiceReference
from Components.config import config
from .defaults import DEBUG_ENABLED
from .epgevent import EPGEvent


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


logging.basicConfig(level=logging.DEBUG, stream=logging.StreamHandler(), format='%(levelname)s: %(funcName)s(): %(message)s')
# logger = logging.getLogger(__name__) # Plugins.Extensions.OpenWebif.controllers.epg:
logger = logging.getLogger('[OpenWebif] [EPG]')


DEBUG_ENABLED = True
if DEBUG_ENABLED:
	logger.setLevel(logging.DEBUG)
else:
	logger.disabled = True


# TODO: load configgy stuff once


def getBouquetServices(bqRef, fields = 'SN'):
	bqServices = eServiceCenter.getInstance().list(eServiceReference(bqRef))

	return bqServices.getContent(fields)


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


class EPG():
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
