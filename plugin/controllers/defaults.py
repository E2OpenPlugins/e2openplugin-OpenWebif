#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys

from Components.Language import language
from Components.config import config as comp_config

from enigma import eEnv

OPENWEBIFVER = "OWIF 1.4.4"

PLUGIN_NAME = 'OpenWebif'
PLUGIN_DESCRIPTION = "OpenWebif Configuration"
PLUGIN_WINDOW_TITLE = PLUGIN_DESCRIPTION

PLUGIN_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
PUBLIC_PATH = PLUGIN_ROOT_PATH + '/public'
VIEWS_PATH = PLUGIN_ROOT_PATH + '/controllers/views'

sys.path.insert(0, PLUGIN_ROOT_PATH)

GLOBALPICONPATH = None

STB_LANG = language.getLanguage()

MOBILEDEVICE = False

#: get transcoding feature
def getTranscoding():
	if os.path.isfile("/proc/stb/encoder/0/bitrate"):
		lp = eEnv.resolve('${libdir}/enigma2/python/Plugins/SystemPlugins/')
		for p in ['TranscodingSetup', 'TransCodingSetup', 'MultiTransCodingSetup']:
			if os.path.exists(lp + p + '/plugin.py') or os.path.exists(lp + p + '/plugin.pyo'):
				return True
	return False

def getExtEventInfoProvider():
	if STB_LANG[0:2] in ['ru', 'uk', 'lv', 'lt', 'et']:
		defaultValue = 'Kinopoisk'
	elif STB_LANG[0:2] in ['cz', 'sk']:
		defaultValue = 'CSFD'
	elif STB_LANG[0:5] in ['en_GB']:
		defaultValue = 'TVguideUK'
	else:
		defaultValue = 'IMDb'
	return defaultValue

def setMobile(isMobile=False):
# TODO: do we need this?
	global MOBILEDEVICE
	MOBILEDEVICE = isMobile

def getViewsPath(file=""):
	global MOBILEDEVICE
	if ( comp_config.OpenWebif.responsive_enabled.value or MOBILEDEVICE ) and os.path.exists(VIEWS_PATH + "/responsive") and not (file.startswith('web/') or file.startswith('/web/')):
		return VIEWS_PATH + "/responsive/" + file
	else:
		return VIEWS_PATH + "/" + file


def getPublicPath(file=""):
	return PUBLIC_PATH + "/" + file


def getPiconPath():

	# Alternative locations need to come first, as the default location always exists and needs to be the last resort
	# Sort alternative locations in order of likelyness that they are non-rotational media:
	# CF/MMC are always memory cards
	# USB can be memory stick or magnetic hdd or SSD, but stick is most likely
	# HDD can be magnetic hdd, SSD or even memory stick (if no hdd present) or a NAS
	PICON_PREFIXES = [
		"/media/cf/",
		"/media/mmc/",
		"/media/usb/",
		"/media/hdd/",
		"/usr/share/enigma2/",
		"/"
	]

	#: subfolders containing picons
	PICON_FOLDERS = ('owipicon', 'picon')

	#: extension of picon files
	PICON_EXT = ".png"

	for prefix in PICON_PREFIXES:
		if os.path.isdir(prefix):
			for folder in PICON_FOLDERS:
				current = prefix + folder + '/'
				if os.path.isdir(current):
					print("Current Picon Path : %s" % current)
					GLOBALPICONPATH = current
					return GLOBALPICONPATH
#: TODO discuss
#					for item in os.listdir(current):
#						if os.path.isfile(current + item) and item.endswith(PICON_EXT):
#							PICONPATH = current
#							return PICONPATH

	return None

# TODO : test !!
def refreshPiconPath():
	PICON_PATH = getPiconPath()

PICON_PATH = getPiconPath()

EXT_EVENT_INFO_SOURCE = getExtEventInfoProvider()

TRANSCODING = getTranscoding()

# TODO: improve PICON_PATH, GLOBALPICONPATH
