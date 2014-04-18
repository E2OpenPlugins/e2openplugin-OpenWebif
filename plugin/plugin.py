# -*- coding: utf-8 -*-

##############################################################################
#                         <<< OpenWebif >>>                                  #
#                                                                            #
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
#
#
#
# Authors: meo <lupomeo@hotmail.com>, skaman <sandro@skanetwork.com>
# Graphics: .....

from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText

from httpserver import HttpdStart, HttpdStop, HttpdRestart

from __init__ import _

config.OpenWebif = ConfigSubsection()
config.OpenWebif.enabled = ConfigYesNo(default=True)
# Use temporary port 8088 to avoid conflict with Webinterface
config.OpenWebif.port = ConfigInteger(default = 80, limits=(1, 65535) )
config.OpenWebif.streamport = ConfigInteger(default = 8001, limits=(1, 65535) )
config.OpenWebif.auth = ConfigYesNo(default=False)
config.OpenWebif.xbmcservices = ConfigYesNo(default=False)
config.OpenWebif.webcache = ConfigSubsection()
# FIXME: anything better than a ConfigText?
config.OpenWebif.webcache.collapsedmenus = ConfigText(default = "remote", fixed_size = False)
config.OpenWebif.webcache.remotegrabscreenshot = ConfigYesNo(default = True)
config.OpenWebif.webcache.zapstream = ConfigYesNo(default = False)
# HTTPS
config.OpenWebif.https_enabled = ConfigYesNo(default=True)
config.OpenWebif.https_port = ConfigInteger(default = 443, limits=(1, 65535) )
# Parental Control currently disabled for testing
config.OpenWebif.parentalenabled = ConfigYesNo(default=False)
# Use service name for stream
config.OpenWebif.service_name_for_stream = ConfigYesNo(default=False)
# authentication for streaming
config.OpenWebif.auth_for_streaming = ConfigYesNo(default=False)


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
		self["lab1"] = Label(_("OpenWebif url: http://yourip:port"))
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"back": self.keyCancel,
			"green": self.keySave,

		}, -2)
		
		self.list.append(getConfigListEntry(_("OpenWebInterface Enabled"), config.OpenWebif.enabled))
		self.list.append(getConfigListEntry(_("Http port"), config.OpenWebif.port))
		self.list.append(getConfigListEntry(_("Enable Http Authentication"), config.OpenWebif.auth))
		self.list.append(getConfigListEntry(_("Enable Https"), config.OpenWebif.https_enabled))
		self.list.append(getConfigListEntry(_("Https port"), config.OpenWebif.https_port))
		self.list.append(getConfigListEntry(_("Enable Authentication for streaming"), config.OpenWebif.auth_for_streaming))
		self.list.append(getConfigListEntry(_("Smart services renaming for XBMC"), config.OpenWebif.xbmcservices))
		self.list.append(getConfigListEntry(_("Enable Parental Control"), config.OpenWebif.parentalenabled))
		self.list.append(getConfigListEntry(_("Add service name to stream information"), config.OpenWebif.service_name_for_stream))
	
		self["config"].list = self.list
		self["config"].l.setList(self.list)

		self.onLayoutFinish.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_("OpenWebif Configuration"))

	def keySave(self):
		for x in self["config"].list:
			x[1].save()

		if config.OpenWebif.enabled.value == True:
			HttpdRestart(global_session)
		else:
			HttpdStop(global_session)
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

def Plugins(**kwargs):
	return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=startSession),
		PluginDescriptor(where=[PluginDescriptor.WHERE_NETWORKCONFIG_READ], fnc=IfUpIfDown),
		PluginDescriptor(name="OpenWebif", description=_("OpenWebif Configuration"), icon="openwebif.png", where=[PluginDescriptor.WHERE_PLUGINMENU], fnc=confplug)]


