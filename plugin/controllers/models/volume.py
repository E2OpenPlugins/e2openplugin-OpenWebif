# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Components.VolumeControl import VolumeControl

def getVolumeStatus():
	owebif_vctrl = VolumeControl.instance
	return {
		"result": True,
		"message": "Status",
		"current": owebif_vctrl.volctrl.getVolume(),
		"ismute": owebif_vctrl.volctrl.isMuted()
	}

def setVolumeUp():
	owebif_vctrl = VolumeControl.instance
	owebif_vctrl.volUp()
	ret = getVolumeStatus()
	ret["message"] = "Volume changed"
	return ret
	
def setVolumeDown():
	owebif_vctrl = VolumeControl.instance
	owebif_vctrl.volDown()
	ret = getVolumeStatus()
	ret["message"] = "Volume changed"
	return ret

def setVolumeMute():
	owebif_vctrl = VolumeControl.instance
	owebif_vctrl.volMute()
	ret = getVolumeStatus()
	ret["message"] = "Mute toggled"
	return ret

def setVolume(value):
	owebif_vctrl = VolumeControl.instance
	owebif_vctrl.volumeDialog.show()
	if value < 0:
		value = 0
	if value > 100:
		value = 100
	owebif_vctrl.volctrl.setVolume(value, value)
	owebif_vctrl.volSave()
	owebif_vctrl.volumeDialog.setValue(value)
	owebif_vctrl.hideVolTimer.start(3000, True)
	ret = getVolumeStatus()
	ret["message"] = "Volume set to %i" % value
	return ret
