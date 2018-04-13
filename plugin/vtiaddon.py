# -*- coding: utf-8 -*-

from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, ConfigSelection
from controllers.i18n import _, tstrings

tstrings['no_cancel'] = _("No, cancel")
tstrings['yes_delete'] = _("Yes, delete it")
tstrings['cancelled'] = _("Cancelled")
tstrings['deleted'] = _("Deleted")
tstrings['need_input'] = _("You need to write something!")
tstrings['common_settings'] = _("Common Settings")
tstrings['min_movie_list'] = _("Minimal movie list")
tstrings['min_timer_list'] = _("Minimal timer list")
tstrings['min_epg_list'] = _("Minimal EPG list")
tstrings['remove_package'] = _("Remove Package")
tstrings['update_package'] = _("Update Package")
tstrings['install_package'] = _("Install Package")
tstrings['packages'] = _("Packages")
tstrings['update'] = _("Update")
tstrings['installed'] = _("Installed")
tstrings['all'] = _("All")
tstrings['more'] = _("More")
tstrings['update_feed'] = _("Update from Feed")
tstrings['upgrade_packages'] = _("Upgrade all Packages")
tstrings['yes'] = _("Yes")
tstrings['inc_shortdesc'] = _("Include short description")
tstrings['inc_extdesc'] = _("Include extended description")
tstrings['moviesearch'] = _("Movie search")
tstrings['start_typing'] = _("START TYPING")
tstrings['select_ipk_upload'] = _("Select IPK File for Upload")
tstrings['uploaded_files'] = _("Uploaded Files")
tstrings['upload_package'] = _("Upload package")
tstrings['upload_error'] = _("Upload File Error")
tstrings['showfullremoteshort'] = _("Full remote")


def skinColor():
	return config.OpenWebif.responsive_skinColor.value

def setSkinColor(self, request):
	if "skincolor" in request.args.keys():
		skincolor = request.args["skincolor"][0]
		print "save color:", skincolor
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

def setVTiWebConfig(self, request):
	if "moviesearchextended" in request.args.keys():
		val = int(request.args["moviesearchextended"][0])
		print "save moviesearchextended:", val
		config.OpenWebif.responsive_moviesearch_extended.value = val == 1 and True or False
		config.OpenWebif.responsive_moviesearch_extended.save()
	if "moviesearchshort" in request.args.keys():
		val = int(request.args["moviesearchshort"][0])
		print "save moviesearchshort:", val
		config.OpenWebif.responsive_moviesearch_short.value = val == 1 and True or False
		config.OpenWebif.responsive_moviesearch_short.save()
	if "fullsearch" in request.args.keys():
		val = int(request.args["fullsearch"][0])
		print "save fullsearch:", val
		config.OpenWebif.responsive_epgsearch_full.value = val == 1 and True or False
		config.OpenWebif.responsive_epgsearch_full.save()
	if "bqonly" in request.args.keys():
		val = int(request.args["bqonly"][0])
		print "save bqonly:", val
		config.OpenWebif.responsive_epgsearch_only_bq.value = val == 1 and True or False
		config.OpenWebif.responsive_epgsearch_only_bq.save()
	if "rcugrabscreen" in request.args.keys():
		val = int(request.args["rcugrabscreen"][0])
		print "save rcugrabscreen:", val
		config.OpenWebif.responsive_rcu_screenshot.value = val == 1 and True or False
		config.OpenWebif.responsive_rcu_screenshot.save()
	if "minmovielist" in request.args.keys():
		val = int(request.args["minmovielist"][0])
		print "save minmovielist:", val
		config.OpenWebif.responsive_min_movielist.value = val == 1 and True or False
		config.OpenWebif.responsive_min_movielist.save()
	if "mintimerlist" in request.args.keys():
		val = int(request.args["mintimerlist"][0])
		print "save mintimerlist:", val
		config.OpenWebif.responsive_min_timerlist.value = val == 1 and True or False
		config.OpenWebif.responsive_min_timerlist.save()
	if "minepglist" in request.args.keys():
		val = int(request.args["minepglist"][0])
		print "save minepglist:", val
		config.OpenWebif.responsive_min_epglist.value = val == 1 and True or False
		config.OpenWebif.responsive_min_epglist.save()
	if "remotecontrolview" in request.args.keys():
		val = int(request.args["remotecontrolview"][0])
		print "save remotecontrolview:", val
		config.OpenWebif.responsive_rcu_full_view.value = val == 1 and True or False
		config.OpenWebif.responsive_rcu_full_view.save()
	return ''

def expand_BaseController():
	from Plugins.Extensions.OpenWebif.controllers.web import WebController
	WebController.P_setskincolor = setSkinColor
	WebController.P_setvtiwebconfig = setVTiWebConfig


expand_basecontroller = expand_BaseController()

def expandConfig():
	config.OpenWebif.responsive_enabled = ConfigYesNo(default = False)
	config.OpenWebif.responsive_skinColor = ConfigText(default = "indigo")
	config.OpenWebif.responsive_epgsearch_only_bq = ConfigYesNo(default=True)
	config.OpenWebif.responsive_epgsearch_full = ConfigYesNo(default=False)
	config.OpenWebif.responsive_rcu_screenshot = ConfigYesNo(default=True)
	config.OpenWebif.responsive_min_movielist = ConfigYesNo(default=False)
	config.OpenWebif.responsive_min_timerlist = ConfigYesNo(default=False)
	config.OpenWebif.responsive_min_epglist = ConfigYesNo(default=False)
	config.OpenWebif.responsive_moviesearch_extended = ConfigYesNo(default=False)
	config.OpenWebif.responsive_moviesearch_short = ConfigYesNo(default=False)
	config.OpenWebif.responsive_rcu_full_view = ConfigYesNo(default=False)
