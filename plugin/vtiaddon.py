#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

from Components.config import config, ConfigYesNo, ConfigSelection
from Plugins.Extensions.OpenWebif.controllers.utilities import getUrlArg


def themeMode():
	return config.OpenWebif.responsive_themeMode.value


def setThemeMode(self, request):
	themeMode = getUrlArg(request, "themeMode")
	if themeMode != None:
		print("save theme mode:", themeMode)
		config.OpenWebif.responsive_themeMode.value = themeMode
		config.OpenWebif.responsive_themeMode.save()
	return {}


def skinColor():
	return config.OpenWebif.responsive_skinColor.value


def setSkinColor(self, request):
	skincolor = getUrlArg(request, "skincolor")
	if skincolor != None:
		print("save color:", skincolor)
		config.OpenWebif.responsive_skinColor.value = skincolor
		config.OpenWebif.responsive_skinColor.save()
	return {}


def MovieSearchShort():
	if config.OpenWebif.responsive_moviesearch_short.value:
		return 'checked'
	return ''


def MovieSearchExtended():
	if config.OpenWebif.responsive_moviesearch_extended.value:
		return 'checked'
	return ''


def EPGSearchFull():
	if config.OpenWebif.responsive_epgsearch_full.value:
		return 'checked'
	return ''


def EPGSearchBQonly():
	if config.OpenWebif.responsive_epgsearch_only_bq.value:
		return 'checked'
	return ''


def ScreenshotOnRCU():
	if config.OpenWebif.responsive_rcu_screenshot.value:
		return 'checked'
	return ''


def MinMovieList():
	if config.OpenWebif.responsive_min_movielist.value:
		return 'checked'
	return ''


def MinTimerList():
	if config.OpenWebif.responsive_min_timerlist.value:
		return 'checked'
	return ''


def MinEPGList():
	if config.OpenWebif.responsive_min_epglist.value:
		return 'checked'
	return ''


def RemoteControlView():
	if config.OpenWebif.responsive_rcu_full_view.value:
		return 'checked'
	return ''


def ZapStream():
	if config.OpenWebif.webcache.zapstream.value:
		return 'checked'
	return ''


def showPicons():
	if config.OpenWebif.webcache.showpicons.value:
		return 'checked'
	return ''


def showPiconBackground():
	if config.OpenWebif.responsive_show_picon_background.value:
		return 'checked'
	return ''


def showIPTVChannelsInSelection():
	if config.OpenWebif.webcache.showiptvchannelsinselection.value:
		return 'checked'
	return ''


def useSreenshotChannelName():
	if config.OpenWebif.webcache.screenshotchannelname.value:
		return 'checked'
	return ''


def useNowNextColumns():
	if config.OpenWebif.responsive_nownext_columns_enabled.value:
		return 'checked'
	return ''


def setVTiWebConfig(self, request):
	if b"moviesearchextended" in list(request.args.keys()):
		val = int(getUrlArg(request, "moviesearchextended"))
		print("save moviesearchextended:", val)
		config.OpenWebif.responsive_moviesearch_extended.value = val == 1 and True or False
		config.OpenWebif.responsive_moviesearch_extended.save()
	if b"moviesearchshort" in list(request.args.keys()):
		val = int(getUrlArg(request, "moviesearchshort"))
		print("save moviesearchshort:", val)
		config.OpenWebif.responsive_moviesearch_short.value = val == 1 and True or False
		config.OpenWebif.responsive_moviesearch_short.save()
	if b"fullsearch" in list(request.args.keys()):
		val = int(getUrlArg(request, "fullsearch"))
		print("save fullsearch:", val)
		config.OpenWebif.responsive_epgsearch_full.value = val == 1 and True or False
		config.OpenWebif.responsive_epgsearch_full.save()
	if b"bqonly" in list(request.args.keys()):
		val = int(getUrlArg(request, "bqonly"))
		print("save bqonly:", val)
		config.OpenWebif.responsive_epgsearch_only_bq.value = val == 1 and True or False
		config.OpenWebif.responsive_epgsearch_only_bq.save()
	if b"rcugrabscreen" in list(request.args.keys()):
		val = int(getUrlArg(request, "rcugrabscreen"))
		print("save rcugrabscreen:", val)
		config.OpenWebif.responsive_rcu_screenshot.value = val == 1 and True or False
		config.OpenWebif.responsive_rcu_screenshot.save()
	if b"minmovielist" in list(request.args.keys()):
		val = int(getUrlArg(request, "minmovielist"))
		print("save minmovielist:", val)
		config.OpenWebif.responsive_min_movielist.value = val == 1 and True or False
		config.OpenWebif.responsive_min_movielist.save()
	if b"mintimerlist" in list(request.args.keys()):
		val = int(getUrlArg(request, "mintimerlist"))
		print("save mintimerlist:", val)
		config.OpenWebif.responsive_min_timerlist.value = val == 1 and True or False
		config.OpenWebif.responsive_min_timerlist.save()
	if b"minepglist" in list(request.args.keys()):
		val = int(getUrlArg(request, "minepglist"))
		print("save minepglist:", val)
		config.OpenWebif.responsive_min_epglist.value = val == 1 and True or False
		config.OpenWebif.responsive_min_epglist.save()
	if b"remotecontrolview" in list(request.args.keys()):
		val = int(getUrlArg(request, "remotecontrolview"))
		print("save remotecontrolview:", val)
		config.OpenWebif.responsive_rcu_full_view.value = val == 1 and True or False
		config.OpenWebif.responsive_rcu_full_view.save()
	if b"zapstream" in list(request.args.keys()):
		val = int(getUrlArg(request, "zapstream"))
		print("save zapstream:", val)
		config.OpenWebif.webcache.zapstream.value = val == 1 and True or False
		config.OpenWebif.webcache.zapstream.save()
	if b"showpicons" in list(request.args.keys()):
		val = int(getUrlArg(request, "showpicons"))
		print("save showpicons:", val)
		config.OpenWebif.webcache.showpicons.value = val == 1 and True or False
		config.OpenWebif.webcache.showpicons.save()
	if b"showpiconbackground" in list(request.args.keys()):
		val = int(getUrlArg(request, "showpiconbackground"))
		print("save showpiconbackground:", val)
		config.OpenWebif.responsive_show_picon_background.value = val == 1 and True or False
		config.OpenWebif.responsive_show_picon_background.save()
	if b"showiptvchannelsinselection" in list(request.args.keys()):
		val = int(getUrlArg(request, "showiptvchannelsinselection"))
		print("save showiptvchannelsinselection:", val)
		config.OpenWebif.webcache.showiptvchannelsinselection.value = val == 1 and True or False
		config.OpenWebif.webcache.showiptvchannelsinselection.save()
	if b"screenshotchannelname" in list(request.args.keys()):
		val = int(getUrlArg(request, "screenshotchannelname"))
		print("save screenshotchannelname:", val)
		config.OpenWebif.webcache.screenshotchannelname.value = val == 1 and True or False
		config.OpenWebif.webcache.screenshotchannelname.save()
	if b"nownext_columns" in list(request.args.keys()):
		val = int(getUrlArg(request, "nownext_columns"))
		print("save nownext_columns_enabled:", val)
		config.OpenWebif.responsive_nownext_columns_enabled.value = val == 1 and True or False
		config.OpenWebif.responsive_nownext_columns_enabled.save()
	return ''


def expand_BaseController():
	from Plugins.Extensions.OpenWebif.controllers.web import WebController
	WebController.P_setthememode = setThemeMode
	WebController.P_setskincolor = setSkinColor
	WebController.P_setvtiwebconfig = setVTiWebConfig


expand_basecontroller = expand_BaseController()

THEMES = [
	'supabright', ('city-lights', 'city lights'), ('neon-blackout', 'neon blackout')
]

COLORS = [
	'black', ('grey-darken-4', 'dark grey'), 'blue-grey', 'grey', 'red', 'pink', 'purple',
	('deep-purple', 'deep purple'), 'indigo', 'blue', ('light-blue', 'light blue'), 'cyan',
	'teal', 'green', ('light-green', 'light green'), 'lime', 'yellow', 'amber', 'orange',
	('deep-orange', 'deep orange'), 'brown', 'white'
]


def expandConfig():
	config.OpenWebif.responsive_enabled = ConfigYesNo(default=False)
	config.OpenWebif.responsive_themeMode = ConfigSelection(default="supabright", choices=THEMES)
	config.OpenWebif.responsive_skinColor = ConfigSelection(default="black", choices=COLORS)
	config.OpenWebif.responsive_epgsearch_only_bq = ConfigYesNo(default=True)
	config.OpenWebif.responsive_epgsearch_full = ConfigYesNo(default=False)
	config.OpenWebif.responsive_rcu_screenshot = ConfigYesNo(default=True)
	config.OpenWebif.responsive_min_movielist = ConfigYesNo(default=False)
	config.OpenWebif.responsive_min_timerlist = ConfigYesNo(default=False)
	config.OpenWebif.responsive_min_epglist = ConfigYesNo(default=False)
	config.OpenWebif.responsive_moviesearch_extended = ConfigYesNo(default=False)
	config.OpenWebif.responsive_moviesearch_short = ConfigYesNo(default=False)
	config.OpenWebif.responsive_rcu_full_view = ConfigYesNo(default=False)
	config.OpenWebif.responsive_show_picon_background = ConfigYesNo(default=False)
	config.OpenWebif.responsive_nownext_columns_enabled = ConfigYesNo(default=False)
	config.OpenWebif.autotimer_regex_searchtype = ConfigYesNo(default=False)
