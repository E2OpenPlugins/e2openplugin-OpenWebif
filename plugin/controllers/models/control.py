##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from Components.config import config
from enigma import eServiceReference, eActionMap

def zapService(session, id, title = ""):
	service = eServiceReference(id)
	
	if len(title) > 0:
		service.setName(title)
	else:
		title = id
	
	if config.ParentalControl.configured.value:
		config.ParentalControl.configured.value = False
		session.nav.playService(service)
		config.ParentalControl.configured.value = True
	else:
		session.nav.playService(service)
	
	return {
		"result": True,
		"message": "Active service is now '%s'" % title
	}

def remoteControl(key, type = "", rcu = ""):
	# TODO: do something better here
	if rcu == "standard":
		remotetype = "dreambox remote control (native)"
	elif rcu == "advanced":
		remotetype = "dreambox advanced remote control (native)"
	elif rcu == "keyboard":
		remotetype = "dreambox ir keyboard"
	else:
		if config.misc.rcused.value == 0:
			remotetype = "dreambox advanced remote control (native)"
		else:
			remotetype = "dreambox remote control (native)"
			
	amap = eActionMap.getInstance()
	if type == "long":
		amap.keyPressed(remotetype, key, 0)
		amap.keyPressed(remotetype, key, 3)
	elif type == "ascii":
		amap.keyPressed(remotetype, key, 4)
	else:
		amap.keyPressed(remotetype, key, 0)
		
	amap.keyPressed(remotetype, key, 1)
	return {
		"result": True,
		"message": "RC command '%s' has been issued" % str(key)
	}
	
def setPowerState(session, state):
	from Screens.Standby import Standby, TryQuitMainloop, inStandby
	state = int(state)
	
	if state == 0: # Toggle StandBy
		if inStandby == None:					
			session.open(Standby)
		else:
			inStandby.Power()
	elif state == 1: # DeepStandBy
		session.open(TryQuitMainloop, state)
	elif state == 2: # Reboot
		session.open(TryQuitMainloop, state)
	elif state == 3: # Restart Enigma
		session.open(TryQuitMainloop, state)
		
	return {
		"result": True,
		"instandby": inStandby != None
	}
	
def getStandbyState(session):
	from Screens.Standby import inStandby
	return {
		"result": True,
		"instandby": inStandby != None
	}
	