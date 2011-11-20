##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Components.About import about
from Components.NimManager import nimmanager
from Components.Harddisk import harddiskmanager
from Components.Network import iNetwork
from RecordTimer import parseEvent
from Screens.Standby import inStandby
from Tools.DreamboxHardware import getFPVersion
from Tools.Directories import fileExists, pathExists
from enigma import eDVBVolumecontrol, eServiceCenter

import os
import sys
import json

def formatIp(ip):
	if len(ip) != 4:
		return None
	return "%d.%d.%d.%d" % (ip[0], ip[1], ip[2], ip[3])

def getBasePath():
	path = os.path.dirname(sys.modules[__name__].__file__)
	chunks = path.split("/")
	chunks.pop()
	chunks.pop()
	return "/".join(chunks)
	
def getPublicPath(file = ""):
	return getBasePath() + "/public/" + file
	
def getViewsPath(file = ""):
	return getBasePath() + "/controllers/views/" + file
	
def getPiconPath():
	if pathExists("/media/usb/picon/"):
		return "/media/usb/picon/"
	elif pathExists("/media/cf/picon/"):
		return "/media/cf/picon/"
	elif pathExists("/usr/share/enigma2/picon/"):
		return "/usr/share/enigma2/picon/"
	else:
		return ""
	
def getInfo():
	# TODO: get webif versione somewhere!
	info = {}

	brand = "Dream Multimedia"
	model = "unknown"
	chipset = "unknown"
	
	if fileExists("/proc/stb/info/vumodel"):
		brand = "Vuplus"
		f = open("/proc/stb/info/vumodel",'r')
 		model = f.readline().strip()
 		f.close()
	elif fileExists("/proc/stb/info/boxtype"):
		brand = "Clarke-Xtrend"
		f = open("/proc/stb/info/boxtype",'r')
 		model = f.readline().strip()
 		f.close()
	else:
		f = open("/proc/stb/info/model",'r')
 		model = f.readline().strip()
 		f.close()

	info['brand'] = brand
	info['model'] = model

	if fileExists("/proc/stb/info/chipset"):
		f = open("/proc/stb/info/chipset",'r')
 		chipset = f.readline().strip()
 		f.close()
		
	info['chipset'] = chipset
	
	f = open("/proc/meminfo",'r')
 	parts = f.readline().split(':')
	info['mem1'] = parts[1].strip()
	parts = f.readline().split(':')
	info['mem2'] = parts[1].strip()
	f.close()
		
	f = os.popen("uptime")
	parts = f.readline().split(',')
	info['uptime'] = parts[0].strip()
	f.close()
		
	if fileExists("/etc/bhversion"):
		f = open("/etc/bhversion",'r')
		imagever = f.readline().strip()
		f.close()
	else:
		imagever = about.getImageVersionString()
		
	info["webifver"] = "0.0.0"
	info['imagever'] = imagever
	info['enigmaver'] = about.getEnigmaVersionString()
	info['kernelver'] = about.getKernelVersionString()
	
	fp_version = getFPVersion()
	if fp_version is None:
		fp_version = 0

	info['fp_version'] = str(fp_version)
	
	info['tuners'] = []
	for i in range(0, nimmanager.getSlotCount()):
		info['tuners'].append({
			"name": nimmanager.getNim(i).getSlotName(),
			"type": nimmanager.getNimName(i) + " (" + nimmanager.getNim(i).getFriendlyType() + ")"
		})

	info['ifaces'] = []
	ifaces = iNetwork.getConfiguredAdapters()
	for iface in ifaces:
		info['ifaces'].append({
			"name": iNetwork.getAdapterName(iface),
			"mac": iNetwork.getAdapterAttribute(iface, "mac"),
			"dhcp": iNetwork.getAdapterAttribute(iface, "dhcp"),
			"ip": formatIp(iNetwork.getAdapterAttribute(iface, "ip")),
			"mask": formatIp(iNetwork.getAdapterAttribute(iface, "netmask")),
			"gw": formatIp(iNetwork.getAdapterAttribute(iface, "gateway"))
		})
			
	info['hdd'] = []
	for hdd in harddiskmanager.hdd:
		if hdd.free() <= 1024:
			free = "%i MB" % (hdd.free())
		else:
			free = float(hdd.free()) / float(1024)
			free = "%.3f GB" % free
		info['hdd'].append({
			"model": hdd.model(),
			"capacity": hdd.capacity(),
			"free": free
		})
	return info

def getStatusInfo(self):
	statusinfo = {}

	# Get Current Volume and Mute Status
	vcontrol = eDVBVolumecontrol.getInstance()
	
	statusinfo['volume'] = vcontrol.getVolume()
	statusinfo['muted'] = vcontrol.isMuted()

	# Get currently running Service
	serviceref = self.session.nav.getCurrentlyPlayingServiceReference()
	serviceHandler = eServiceCenter.getInstance()
	serviceHandlerInfo = serviceHandler.info(serviceref)

	service = self.session.nav.getCurrentService()
	serviceinfo = service and service.info()
	event = serviceinfo and serviceinfo.getEvent(0)

	if event is not None:
		curEvent = parseEvent(event)
		statusinfo['currservice_name'] = curEvent[2]
		statusinfo['currservice_serviceref'] = serviceref.toString()
		statusinfo['currservice_begin'] = int(curEvent[0])
		statusinfo['currservice_end'] = int(curEvent[1])
		statusinfo['currservice_description'] = curEvent[3]
		statusinfo['currservice_station'] = serviceHandlerInfo.getName(serviceref)
	else:
		statusinfo['currservice_name'] = "N/A"
		statusinfo['currservice_serviceref'] = ""
		statusinfo['currservice_begin'] = 0
		statusinfo['currservice_end'] = 0
		statusinfo['currservice_name'] = ""
		statusinfo['currservice_description'] = ""
		statusinfo['currservice_station'] = ""
		
	# Get Standby State
	if inStandby == None:
		statusinfo['inStandby'] = "false"
	else:
		statusinfo['inStandby'] = "true"

	return json.dumps(statusinfo)