# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: EPGEvent
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

from enigma import eServiceCenter, eServiceEvent, eServiceReference
from ServiceReference import ServiceReference
from Components.config import config

from Plugins.Extensions.OpenWebif.controllers.defaults import DEBUG_ENABLED


try:
	from Components.Converter.genre import getGenreStringLong
except ImportError:
	def getGenreStringLong(*args): return ""


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
	deltaDays = timedelta(seconds=timeDiff).days

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
