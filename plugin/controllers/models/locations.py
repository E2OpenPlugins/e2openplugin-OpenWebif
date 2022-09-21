# -*- coding: utf-8 -*-

##############################################################################
#                        2011 - 2017 E2OpenPlugin                            #
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
		"locations": config.movielist.videodirs.value,
		"default": config.usage.default_path.value
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
			except Exception:
				return {
					"result": False,
					"message": "Creation of folder '%s' failed" % dirname
				}
		else:
			return {
				"result": False,
				"message": "Folder '%s' does not exist" % dirname
			}

	locations = config.movielist.videodirs.value[:] or []
	if dirname in locations:
		return {
			"result": False,
			"message": "Location '%s' is already defined" % dirname
		}

	locations.append(dirname)
	config.movielist.videodirs.value = locations
	config.movielist.videodirs.save()

	return {
		"result": True,
		"message": "Location '%s' added succesfully" % dirname
	}


def removeLocation(dirname, remove):
	locations = config.movielist.videodirs.value[:] or []
	res = False
	msg = "Location '%s' is not defined" % dirname
	if dirname in locations:
		res = True
		locations.remove(dirname)
		config.movielist.videodirs.value = locations
		config.movielist.videodirs.save()
		if os.path.exists(dirname) and remove:
			try:
				os.rmdir(dirname)
				msg = "Location and Folder '%s' removed succesfully" % dirname
			except Exception:
				msg = "Location '%s' removed succesfully but the Folder not exists or is not empty" % dirname
		else:
			msg = "Location '%s' removed succesfully" % dirname
	return {
		"result": res,
		"message": msg
	}
