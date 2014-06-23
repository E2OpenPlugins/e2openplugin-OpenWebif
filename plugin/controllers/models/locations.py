# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from Components.config import config
import os

def getLocations():
	return {
		"result": True,
		"locations": config.movielist.videodirs.value
	}

def getCurrentLocation():
	path = config.movielist.last_videodir.value or "/hdd/movie"
	if not os.path.exists(path):
		path = "/hdd/movie"

	return {
		"result": True,
		"location": path
	}

def addLocation(dirname, create):
	if not os.path.exists(dirname):
		if create:
			try:
				os.makedirs(dirname)
			except Exception, e:
				return {
					"result": False,
					"message": "Path '%s' can not be created" % dirname
				}
		else:
			return {
				"result": False,
				"message": "Path '%s' does not exist" % dirname
			}

	locations = config.movielist.videodirs.value[:] or []
	if dirname in locations:
		return {
			"result": False,
			"message": "Location '%s' is already existing" % dirname
		}

	locations.append(dirname)
	config.movielist.videodirs.value = locations
	config.movielist.videodirs.save()

	return {
		"result": True,
		"message": "Location '%s' added succesfully" % dirname
	}

def removeLocation(dirname):
	locations = config.movielist.videodirs.value[:] or []
	if dirname in locations:
		locations.remove(dirname)
		config.movielist.videodirs.value = locations
		config.movielist.videodirs.save()
		return {
			"result": True,
			"message": "Location '%s' removed succesfully" % dirname
		}

	return {
		"result": False,
		"message": "Location '%s' does not exist" % dirname
	}
