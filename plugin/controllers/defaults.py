#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from Components.Language import language
from Components.config import config as comp_config

from enigma import eEnv

OPENWEBIFVER = "OWIF 1.3.5"

PLUGIN_NAME = 'OpenWebif'
PLUGIN_DESCRIPTION = "OpenWebif Configuration"
PLUGIN_WINDOW_TITLE = PLUGIN_DESCRIPTION

PLUGIN_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
PUBLIC_PATH = PLUGIN_ROOT_PATH + '/public'
VIEWS_PATH = PLUGIN_ROOT_PATH + '/controllers/views'

sys.path.insert(0, PLUGIN_ROOT_PATH)

GLOBALPICONPATH = None

#: get transcoding feature
def getTranscoding():
	transcoding = False
	if os.path.isfile("/proc/stb/encoder/0/bitrate"):
		if os.path.exists(eEnv.resolve('${libdir}/enigma2/python/Plugins/SystemPlugins/TransCodingSetup/plugin.pyo')) or os.path.exists(eEnv.resolve('${libdir}/enigma2/python/Plugins/SystemPlugins/TranscodingSetup/plugin.pyo')) or os.path.exists(eEnv.resolve('${libdir}/enigma2/python/Plugins/SystemPlugins/MultiTransCodingSetup/plugin.pyo')):
			transcoding = True

	return transcoding

#: get kinopoisk feature
def getKinopoisk():
	if language.getLanguage()[0:2] in ['ru', 'uk', 'lv', 'lt', 'et']:
		return True
	return False

def getViewsPath(file=""):
	if comp_config.OpenWebif.responsive_enabled.value and os.path.exists(VIEWS_PATH + "/responsive") and not (file.startswith('web/') or file.startswith('/web/')):
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
					print "Current Picon Path : %s" % current
					GLOBALPICONPATH = current
					return GLOBALPICONPATH
#: TODO discuss
#					for item in os.listdir(current):
#						if os.path.isfile(current + item) and item.endswith(PICON_EXT):
#							PICONPATH = current
#							return PICONPATH

	return None

#: PICON PATH FIXME: check path again after a few hours to detect new paths
PICON_PATH = getPiconPath()

KINOPOISK = getKinopoisk()

TRANSCODING = getTranscoding()
