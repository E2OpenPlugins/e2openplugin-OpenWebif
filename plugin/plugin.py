##############################################################################
#                         <<< OpenWebif >>>                           
#                                                                            
#                        2011 E2OpenPlugins          
#                                                                            
#  This file is open source software; you can redistribute it and/or modify  
#     it under the terms of the GNU General Public License version 2 as      
#               published by the Free Software Foundation.                   
#                                                                            
##############################################################################
#
#
#
# Authors: meo <lupomeo@hotmail.com>, ....
# Graphics: .....

from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigInteger, ConfigYesNo

from http_server import HttpdStart, HttpdStop

config.OpenWebif = ConfigSubsection()
config.OpenWebif.enabled = ConfigYesNo(default=True)
# Use temporary port 8088 to avoid conflict with Webinterface
config.OpenWebif.port = ConfigInteger(default = 8088, limits=(1, 65535) )
config.OpenWebif.auth = ConfigYesNo(default=False)

class OpenWebifConfig(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="900,340" title="OpenWebif Configuration">
		<widget name="lab1" position="20,30" halign="center" size="860,60" zPosition="1" font="Regular;24" valign="top" transparent="1" />
		<widget name="config" position="20,100" size="860,160" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="200,270" size="140,40" alphatest="on" />
		<widget name="key_red" position="200,270" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" />
		<ePixmap position="550,270" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="on" zPosition="1" />
		<widget name="key_green" position="550,270" zPosition="2" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="green" transparent="1" />
	</screen>"""
	
	def __init__(self, session):
		self.skin = OpenWebifConfig.skin
		Screen.__init__(self, session)
		
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["key_red"] = Label(_("Save"))
		self["key_green"] = Label(_("Cancel"))
		self["lab1"] = Label("To access to OpenWebif point your browser to http://yourip:port")
		
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"red": self.keySave,
			"back": self.keyCancel,
			"green": self.keyCancel,

		}, -2)
		
		self.list.append(getConfigListEntry(_("OpenWebInterface Enabled"), config.OpenWebif.enabled))
		self.list.append(getConfigListEntry(_("Http port"), config.OpenWebif.port))
		self.list.append(getConfigListEntry(_("Enable Http Authentication"), config.OpenWebif.auth))
	
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()
#TODO: add defer before to restart server-
#		HttpdStop(global_session)
#		HttpdStart(global_session)
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
		PluginDescriptor(name="OpenWebif", description="OpenWebif Configuration", where=[PluginDescriptor.WHERE_PLUGINMENU], fnc=confplug)]


