#!/usr/bin/python
# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: plugin
##########################################################################
# Copyright (C) 2011 - 2020 E2OpenPlugins
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
#
# Authors: meo <lupomeo@hotmail.com>, skaman <sandro@skanetwork.com>
# Graphics: .....

from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, ConfigSelection, configfile
from enigma import getDesktop
from Plugins.Extensions.OpenWebif.controllers.models.info import getInfo
from Plugins.Extensions.OpenWebif.controllers.defaults import EXT_EVENT_INFO_SOURCE, getIP, setDebugEnabled
from Plugins.Extensions.OpenWebif.httpserver import HttpdStart, HttpdStop, HttpdRestart
from Plugins.Extensions.OpenWebif.controllers.i18n import _

# not used redmond -> original , trontastic , ui-lightness
THEMES = [
	'original', 'base', 'black-tie', 'blitzer', 'clear', 'cupertino', 'dark-hive',
	'dot-luv', 'eggplant', 'excite-bike', 'flick', 'hot-sneaks', 'humanity',
	'le-frog', 'mint-choc', 'overcast', 'pepper-grinder', 'smoothness',
	'south-street', 'start', 'sunny', 'swanky-purse', 'ui-darkness', 'vader',
	'original-small-screen'
]

config.OpenWebif = ConfigSubsection()
config.OpenWebif.enabled = ConfigYesNo(default=True)
config.OpenWebif.identifier = ConfigYesNo(default=True)
config.OpenWebif.identifier_custom = ConfigYesNo(default=False)
config.OpenWebif.identifier_text = ConfigText(default="", fixed_size=False)
config.OpenWebif.port = ConfigInteger(default=80, limits=(1, 65535))
config.OpenWebif.streamport = ConfigInteger(default=8001, limits=(1, 65535))
config.OpenWebif.auth = ConfigYesNo(default=False)
config.OpenWebif.xbmcservices = ConfigYesNo(default=False)
config.OpenWebif.webcache = ConfigSubsection()
# FIXME: anything better than a ConfigText?
config.OpenWebif.webcache.collapsedmenus = ConfigText(default="", fixed_size=False)
config.OpenWebif.webcache.zapstream = ConfigYesNo(default=False)
config.OpenWebif.webcache.theme = ConfigSelection(default='original', choices=THEMES)
config.OpenWebif.webcache.moviesort = ConfigSelection(default='name', choices=['name', 'named', 'date', 'dated'])
config.OpenWebif.webcache.showpicons = ConfigYesNo(default=True)
config.OpenWebif.webcache.moviedb = ConfigSelection(default=EXT_EVENT_INFO_SOURCE, choices=['-', 'Kinopoisk', 'CSFD', 'TVguideUK', 'IMDb'])
config.OpenWebif.webcache.mepgmode = ConfigInteger(default=1, limits=(1, 2))
config.OpenWebif.webcache.showchanneldetails = ConfigYesNo(default=False)
config.OpenWebif.webcache.showiptvchannelsinselection = ConfigYesNo(default=True)
config.OpenWebif.webcache.screenshotchannelname = ConfigYesNo(default=False)
config.OpenWebif.webcache.showallpackages = ConfigYesNo(default=False)
config.OpenWebif.webcache.smallremote = ConfigSelection(default='new', choices=['new', 'old', 'ims'])
config.OpenWebif.webcache.screenshot_high_resolution = ConfigYesNo(default=True)
config.OpenWebif.webcache.screenshot_refresh_auto = ConfigYesNo(default=False)
config.OpenWebif.webcache.screenshot_refresh_time = ConfigInteger(default=30)

# HTTPS
config.OpenWebif.https_enabled = ConfigYesNo(default=False)
config.OpenWebif.https_port = ConfigInteger(default=443, limits=(1, 65535))
config.OpenWebif.https_auth = ConfigYesNo(default=True)
config.OpenWebif.https_clientcert = ConfigYesNo(default=False)
config.OpenWebif.parentalenabled = ConfigYesNo(default=False)
# Use service name for stream
config.OpenWebif.service_name_for_stream = ConfigYesNo(default=True)
# authentication for streaming
config.OpenWebif.auth_for_streaming = ConfigYesNo(default=False)
config.OpenWebif.no_root_access = ConfigYesNo(default=False)
config.OpenWebif.local_access_only = ConfigSelection(default=' ', choices=[' '])
config.OpenWebif.vpn_access = ConfigYesNo(default=False)
config.OpenWebif.allow_upload_ipk = ConfigYesNo(default=False)
# encoding of EPG data
config.OpenWebif.epg_encoding = ConfigSelection(default='utf-8', choices=['utf-8',
										'iso-8859-15',
										'iso-8859-1',
										'iso-8859-2',
										'iso-8859-3',
										'iso-8859-4',
										'iso-8859-5',
										'iso-8859-6',
										'iso-8859-7',
										'iso-8859-8',
										'iso-8859-9',
										'iso-8859-10',
										'iso-8859-16'])

config.OpenWebif.displayTracebacks = ConfigYesNo(default=False)
config.OpenWebif.playiptvdirect = ConfigYesNo(default=True)
config.OpenWebif.verbose_debug_enabled = ConfigYesNo(default=False)

setDebugEnabled(config.OpenWebif.verbose_debug_enabled.value)

from Plugins.Extensions.OpenWebif import vtiaddon
vtiaddon.expandConfig()

imagedistro = getInfo()['imagedistro']


class OpenWebifConfig(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="700,340" title="OpenWebif Configuration">
		<widget name="lab1" position="10,30" halign="center" size="680,60" zPosition="1" font="Regular;24" valign="top" transparent="1" />
		<widget name="config" position="10,100" size="680,180" scrollbarMode="showOnDemand" />
		<ePixmap position="140,290" size="140,40" pixmap="skin_default/buttons/red.png" alphatest="on" />
		<widget name="key_red" position="140,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="420,290" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="420,290" zPosition="2" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""

	def __init__(self, session):
		self.skin = OpenWebifConfig.skin
		Screen.__init__(self, session)

		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Save"))

		owif_protocol = "https" if config.OpenWebif.https_enabled.value else "http"
		owif_port = config.OpenWebif.https_port.value if config.OpenWebif.https_enabled.value else config.OpenWebif.port.value
		ip = getIP()
		if ip == None:
			ip = _("box_ip")

		ports = ":%d" % owif_port
		if (owif_protocol == "http" and owif_port == 80) or (owif_protocol == "https" and owif_port == 443):
			ports = ""

		self["lab1"] = Label("%s %s://%s%s" % (_("OpenWebif url:"), owif_protocol, ip, ports))

		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)
		self.runSetup()
		self.onLayoutFinish.append(self.setWindowTitle)

	def runSetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("OpenWebInterface Enabled"), config.OpenWebif.enabled))
		if config.OpenWebif.enabled.value:
			self.list.append(getConfigListEntry(_("Use modern interface"), config.OpenWebif.responsive_enabled))
			if config.OpenWebif.responsive_enabled.value:
				self.list.append(getConfigListEntry(_("Theme mode"), config.OpenWebif.responsive_themeMode))
				self.list.append(getConfigListEntry(_("Use custom Color"), config.OpenWebif.responsive_skinColor))
			self.list.append(getConfigListEntry(_("Show box name in header"), config.OpenWebif.identifier))
			if config.OpenWebif.identifier.value:
				self.list.append(getConfigListEntry(_("Use custom box name"), config.OpenWebif.identifier_custom))
				if config.OpenWebif.identifier_custom.value:
					self.list.append(getConfigListEntry(_("Custom box name"), config.OpenWebif.identifier_text))
			self.list.append(getConfigListEntry(_("HTTP port"), config.OpenWebif.port))
			self.list.append(getConfigListEntry(_("Enable HTTP Authentication"), config.OpenWebif.auth))
			self.list.append(getConfigListEntry(_("Enable HTTPS"), config.OpenWebif.https_enabled))
			if config.OpenWebif.https_enabled.value:
				self.list.append(getConfigListEntry(_("HTTPS port"), config.OpenWebif.https_port))
				self.list.append(getConfigListEntry(_("Enable HTTPS Authentication"), config.OpenWebif.https_auth))
				self.list.append(getConfigListEntry(_("Require client cert for HTTPS"), config.OpenWebif.https_clientcert))
			if config.OpenWebif.auth.value:
				self.list.append(getConfigListEntry(_("Enable Authentication for streaming"), config.OpenWebif.auth_for_streaming))
				self.list.append(getConfigListEntry(_("Disable remote access for user root"), config.OpenWebif.no_root_access))
			if not config.OpenWebif.auth.value or (config.OpenWebif.https_enabled.value and not config.OpenWebif.https_auth.value):
				self.list.append(getConfigListEntry(_("Without auth only local access is allowed!"), config.OpenWebif.local_access_only))
				self.list.append(getConfigListEntry(_("Enable access from VPNs"), config.OpenWebif.vpn_access))
			self.list.append(getConfigListEntry(_("Enable Parental Control"), config.OpenWebif.parentalenabled))
			self.list.append(getConfigListEntry(_("Streaming port"), config.OpenWebif.streamport))
			self.list.append(getConfigListEntry(_("Add service name to stream information"), config.OpenWebif.service_name_for_stream))
			if imagedistro in ("VTi-Team Image"):
				self.list.append(getConfigListEntry(_("Character encoding for EPG data"), config.OpenWebif.epg_encoding))
			self.list.append(getConfigListEntry(_("Allow IPK Upload"), config.OpenWebif.allow_upload_ipk))
			self.list.append(getConfigListEntry(_("Playback IPTV Streams in browser"), config.OpenWebif.playiptvdirect))
			self.list.append(getConfigListEntry(_("Debug - Display Tracebacks in browser"), config.OpenWebif.displayTracebacks))
			# FIXME Submenu
			# self.list.append(getConfigListEntry(_("Webinterface jQuery UI Theme"), config.OpenWebif.webcache.theme))
			# self.list.append(getConfigListEntry(_("Movie List Sort"), config.OpenWebif.webcache.moviesort))

		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def setWindowTitle(self):
		self.setTitle(_("OpenWebif Configuration"))

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.runSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.runSetup()

	def keySave(self):
		for x in self["config"].list:
			x[1].save()

		if not config.OpenWebif.auth.value is True:
			config.OpenWebif.auth_for_streaming.value = False
			config.OpenWebif.auth_for_streaming.save()

		if not config.OpenWebif.https_enabled.value is True:
			config.OpenWebif.https_clientcert.value = False
			config.OpenWebif.https_clientcert.save()

		if config.OpenWebif.enabled.value is True:
			HttpdRestart(global_session)
		else:
			HttpdStop(global_session)
		configfile.save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()


def confplug(session, **kwargs):
	session.open(OpenWebifConfig)


def IfUpIfDown(reason, **kwargs):
	if reason is True:
		HttpdStart(global_session)
	else:
		HttpdStop(global_session)


def startSession(reason, session):
	global global_session
	global_session = session
	HttpdStart(global_session)


def main_menu(menuid, **kwargs):
	if menuid == "network":
		return [("OpenWebif", confplug, "openwebif", 45)]
	else:
		return []


def Plugins(**kwargs):
	p = PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=startSession)
	p.weight = 100  # webif should start as last plugin
	result = [
		p,
		PluginDescriptor(where=[PluginDescriptor.WHERE_NETWORKCONFIG_READ], fnc=IfUpIfDown),
		]
	screenwidth = getDesktop(0).size().width()
	if imagedistro in ("openatv"):
		result.append(PluginDescriptor(name="OpenWebif", description=_("OpenWebif Configuration"), where=PluginDescriptor.WHERE_MENU, fnc=main_menu))
	if screenwidth and screenwidth == 1920:
		result.append(PluginDescriptor(name="OpenWebif", description=_("OpenWebif Configuration"), icon="openwebifhd.png", where=[PluginDescriptor.WHERE_PLUGINMENU], fnc=confplug))
	else:
		result.append(PluginDescriptor(name="OpenWebif", description=_("OpenWebif Configuration"), icon="openwebif.png", where=[PluginDescriptor.WHERE_PLUGINMENU], fnc=confplug))
	return result
