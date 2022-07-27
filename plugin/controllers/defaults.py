# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import glob
import re

from Components.Language import language
from Components.config import config as comp_config
from Components.Network import iNetwork

try:
	from Tools.Directories import isPluginInstalled
except ImportError:
	# fallback for old images
	from Tools.Directories import resolveFilename, SCOPE_PLUGINS

	def isPluginInstalled(p, plugin="plugin"):
		for ext in ['', 'c', 'o']:
			if os.path.exists(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/%s/%s.py%s" % (p, plugin, ext))):
				return True
			if os.path.exists(resolveFilename(SCOPE_PLUGINS, "Extensions/%s/%s.py%s" % (p, plugin, ext))):
				return True


def _isPluginInstalled(p, plugin="plugin"):
	return isPluginInstalled(p, plugin)


OPENWEBIFVER = "OWIF 1.5.2"

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

DEBUG_ENABLED = False

#: get transcoding feature


def setDebugEnabled(enabled):
	global DEBUG_ENABLED
	DEBUG_ENABLED = enabled


def getTranscoding():
	if os.path.isfile("/proc/stb/encoder/0/bitrate"):
		return isPluginInstalled("TranscodingSetup") or isPluginInstalled("TransCodingSetup") or isPluginInstalled("MultiTransCodingSetup")
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
	if (comp_config.OpenWebif.responsive_enabled.value or MOBILEDEVICE) and os.path.exists(VIEWS_PATH + "/responsive") and not (file.startswith('web/') or file.startswith('/web/')):
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


def getIP():
	ifaces = iNetwork.getConfiguredAdapters()
	if len(ifaces):
		ip_list = iNetwork.getAdapterAttribute(ifaces[0], "ip")  # use only the first configured interface
		if ip_list:
			return "%d.%d.%d.%d" % (ip_list[0], ip_list[1], ip_list[2], ip_list[3])
	return None


PICON_PATH = getPiconPath()

EXT_EVENT_INFO_SOURCE = getExtEventInfoProvider()

TRANSCODING = getTranscoding()

# TODO: improve PICON_PATH, GLOBALPICONPATH


def getOpenwebifPackageVersion():
	control = glob.glob('/var/lib/opkg/info/*openwebif.control')
	version = 'unknown'
	if len(control):
		with open(control[0]) as file:
			lines = file.read()
			try:
				version = re.search(r'^Version:\s*(.*)', lines, re.MULTILINE).group(1)
			except AttributeError:
				pass
	return version


def getUserCSS(fn):
	if os.path.isfile(fn):
		return open(fn, 'r').read()
	else:
		return ''


def getAutoTimer():
	try:
		from Plugins.Extensions.AutoTimer.AutoTimer import AutoTimer  # noqa: F401
		return True
	except ImportError:
		return False


def getAutoTimerChangeResource():
	if HASAUTOTIMER:
		try:
			from Plugins.Extensions.AutoTimer.AutoTimerResource import AutoTimerChangeResource  # noqa: F401
			return True
		except ImportError:
			return False
	else:
		return False


def getAutoTimerTestResource():
	if HASAUTOTIMER:
		try:
			from Plugins.Extensions.AutoTimer.AutoTimerResource import AutoTimerTestResource  # noqa: F401
			return True
		except ImportError:
			return False
	else:
		return False


def getVPSPlugin():
	try:
		from Plugins.SystemPlugins.vps import Vps  # noqa: F401
		return True
	except ImportError:
		return False


def getSeriesPlugin():
	try:
		from Plugins.Extensions.SeriesPlugin.plugin import Plugins  # noqa: F401
		return True
	except ImportError:
		return False


def getATSearchtypes():
	try:
		from Plugins.Extensions.AutoTimer.AutoTimer import typeMap
		return typeMap
	except ImportError:
		return {}


def getTextInputSupport():
	try:
		from enigma import setPrevAsciiCode
		return True
	except ImportError:
		return False


def getDefaultRcu():
	remotetype = "standard"
	if comp_config.misc.rcused.value == 0:
		remotetype = "advanced"
	else:
		try:
			# FIXME remove HardwareInfo
			from Tools.HardwareInfo import HardwareInfo
			if HardwareInfo().get_device_model() in ("xp1000", "formuler1", "formuler3", "et9000", "et9200", "hd1100", "hd1200"):
				remotetype = "advanced"
		except:  # nosec # noqa: E722
			print("[OpenWebif] wrong hw detection")
	return remotetype


OPENWEBIFPACKAGEVERSION = getOpenwebifPackageVersion()

USERCSSCLASSIC = getUserCSS('/etc/enigma2/owfclassic.css')

USERCSSRESPONSIVE = getUserCSS('/etc/enigma2/owfresponsive.css')

HASAUTOTIMER = getAutoTimer()

HASAUTOTIMERCHANGE = getAutoTimerChangeResource()

HASAUTOTIMERTEST = getAutoTimerTestResource()

HASVPS = getVPSPlugin()

HASSERIES = getSeriesPlugin()

ATSEARCHTYPES = getATSearchtypes()

TEXTINPUTSUPPORT = getTextInputSupport()

DEFAULT_RCU = getDefaultRcu()
