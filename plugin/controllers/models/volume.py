##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from enigma import eDVBVolumecontrol
from GlobalActions import globalActionMap

def getVolumeStatus():
	vcontrol = eDVBVolumecontrol.getInstance()
	return {
		"current": vcontrol.getVolume(),
		"ismute": vcontrol.isMuted()
	}

def setVolumeUp():
	globalActionMap.actions["volumeUp"]()
	return getVolumeStatus()
	
def setVolumeDown():
	globalActionMap.actions["volumeDown"]()
	return getVolumeStatus()

def setVolumeMute():
	globalActionMap.actions["volumeMute"]()
	return getVolumeStatus()

def setVolume(value):
	vcontrol = eDVBVolumecontrol.getInstance()
	if value < 0:
		value = 0
	if value > 100:
		value = 100
	vcontrol.setVolume(value, value)
	return getVolumeStatus()
