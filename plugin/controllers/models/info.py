##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from Components.About import about
from Components.config import config
from Components.NimManager import nimmanager
from Components.Harddisk import harddiskmanager
from Components.Network import iNetwork
from RecordTimer import parseEvent
from Screens.Standby import inStandby
from Tools.Directories import fileExists, pathExists
from time import time, localtime, strftime
from enigma import eDVBVolumecontrol, eServiceCenter

import os
import sys
import time

OPENWEBIFVER = "OWIF 0.1.6"

def getOpenWebifVer():
	return OPENWEBIFVER

def formatIp(ip):
	if ip is None or len(ip) != 4:
		return "0.0.0.0"
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
	elif pathExists("/media/hdd/picon/"):
		return "/media/hdd/picon/"
	elif pathExists("/usr/share/enigma2/picon/"):
		return "/usr/share/enigma2/picon/"
	elif pathExists("/picon/"):
		return "/picon/"
	else:
		return ""
	
def getInfo():
	# TODO: get webif versione somewhere!
	info = {}

	brand = "Dream Multimedia"
	model = "unknown"
	chipset = "unknown"
	
	if fileExists("/proc/stb/info/boxtype"):
		brand = "Xtrend"
		f = open("/proc/stb/info/boxtype",'r')
		model = f.readline().strip().lower()
 		if model.startswith("et"):
		    brand = "Xtrend"
		elif model.startswith("ini"):
			if model.endswith("sv"):
				brand = "MiracleBox"
			elif model.endswith("ru"):
				brand = "Sezam"
			else:
				brand = "Venton"
		elif model.startswith("xp"):
		    brand = "MaxDigital"
 		f.close()
	elif fileExists("/proc/stb/info/vumodel"):
		brand = "VuPlus"
		f = open("/proc/stb/info/vumodel",'r')
 		model = f.readline().strip().lower()
 		f.close()
	elif fileExists("/proc/stb/info/azmodel"):
		brand = "AZBox"
		f = open("/proc/stb/info/model",'r')
 		model = f.readline().strip().lower()
 		f.close()
 		if model == "me":
			chipset = "SIGMA 8655"
 		elif model == "minime":
			chipset = "SIGMA 8653"
 		else:
			chipset = "SIGMA 8634"
	else:
		f = open("/proc/stb/info/model",'r')
 		model = f.readline().strip().lower()
 		f.close()

	info['brand'] = brand
	info['model'] = model

	if fileExists("/proc/stb/info/chipset"):
		f = open("/proc/stb/info/chipset",'r')
 		chipset = f.readline().strip()
 		f.close()
		
	info['chipset'] = chipset
	
	memFree = 0
	for line in open("/proc/meminfo",'r'):
	 	parts = line.split(':')
		key = parts[0].strip()
		if key == "MemTotal":
			info['mem1'] = parts[1].strip()
		elif key in ("MemFree", "Buffers", "Cached"):
			memFree += int(parts[1].strip().split(' ',1)[0])
	info['mem2'] = "%s kB" % memFree
		
	try:
		f = open("/proc/uptime", "rb")
		uptime = int(float(f.readline().split(' ', 2)[0].strip()))
		f.close()
		uptimetext = ''
		if uptime > 86400:
			d = uptime/86400
			uptime = uptime % 86400
			uptimetext += '%dd ' % d
		uptimetext += "%d:%.2d" % (uptime/3600, (uptime%3600)/60)
	except:
		uptimetext = "?"
	info['uptime'] = uptimetext
		
	if fileExists("/etc/bhversion"):
		f = open("/etc/bhversion",'r')
		imagever = f.readline().strip()
		f.close()
	elif fileExists("/etc/vtiversion.info"):
		f = open("/etc/vtiversion.info",'r')
		imagever = f.readline().strip()
		f.close()
	else:
		imagever = about.getImageVersionString()
		
	info["webifver"] = getOpenWebifVer()
	info['imagever'] = imagever
	info['enigmaver'] = about.getEnigmaVersionString()
	info['kernelver'] = about.getKernelVersionString()

	try:
		from Tools.StbHardware import getFPVersion
	except ImportError:
		from Tools.DreamboxHardware import getFPVersion

	info['fp_version'] = getFPVersion()
	
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

def getFrontendStatus(session):
	inf = {}
	inf['tunertype'] = ""
	inf['tunernumber'] = ""
	inf['snr'] = ""
	inf['snr_db'] = ""
	inf['agc'] = ""
	inf['ber'] = ""
	
	feinfo = session.nav.getCurrentService().frontendInfo()
	frontendData = feinfo and feinfo.getAll(True)
	
	if frontendData is not None:
		inf['tunertype'] = frontendData.get("tuner_type", "UNKNOWN")
		inf['tunernumber'] = frontendData.get("tuner_number")
		
	frontendStatus = feinfo and feinfo.getFrontendStatus()
	if frontendStatus is not None:
		percent = frontendStatus.get("tuner_signal_quality")
		if percent is not None:
			inf['snr'] = int(percent * 100 / 65536)
			inf['snr_db'] = inf['snr']
		percent = frontendStatus.get("tuner_signal_quality_db")
		if percent is not None:
			inf['snr_db'] = "%3.02f" % (percent / 100.0)
		percent = frontendStatus.get("tuner_signal_power")
		if percent is not None:
			inf['agc'] = int(percent * 100 / 65536)
		percent =  frontendStatus.get("tuner_bit_error_rate")
		if percent is not None:
			inf['ber'] = int(percent * 100 / 65536)

	return inf

def getCurrentTime():
	t = time.localtime()
	return {
		"status": True,
		"time": "%2d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)
	}

def getStatusInfo(self):
	statusinfo = {}

	# Get Current Volume and Mute Status
	vcontrol = eDVBVolumecontrol.getInstance()
	
	statusinfo['volume'] = vcontrol.getVolume()
	statusinfo['muted'] = vcontrol.isMuted()

	# Get currently running Service
	event = None
	serviceref = self.session.nav.getCurrentlyPlayingServiceReference()
	if serviceref is not None:
		serviceHandler = eServiceCenter.getInstance()
		serviceHandlerInfo = serviceHandler.info(serviceref)
	
		service = self.session.nav.getCurrentService()
		serviceinfo = service and service.info()
		event = serviceinfo and serviceinfo.getEvent(0)
	else:
		event = None

	if event is not None:
		curEvent = parseEvent(event)
		statusinfo['currservice_name'] = curEvent[2].replace('\xc2\x86', '').replace('\xc2\x87', '')
		statusinfo['currservice_serviceref'] = serviceref.toString()
		statusinfo['currservice_begin'] = strftime("%H:%M", (localtime(int(curEvent[0])+(config.recording.margin_before.value*60))))
		statusinfo['currservice_end'] = strftime("%H:%M", (localtime(int(curEvent[1])-(config.recording.margin_after.value*60))))
		statusinfo['currservice_description'] = curEvent[3]
		if len(curEvent[3]) > 220:
			statusinfo['currservice_description'] = curEvent[3][0:220] + "..."
		statusinfo['currservice_station'] = serviceHandlerInfo.getName(serviceref).replace('\xc2\x86', '').replace('\xc2\x87', '')
	else:
		statusinfo['currservice_name'] = "N/A"
		statusinfo['currservice_begin'] = ""
		statusinfo['currservice_end'] = ""
		statusinfo['currservice_description'] = ""
		if serviceref:
			statusinfo['currservice_serviceref'] = serviceref.toString()
			statusinfo['currservice_station'] = serviceHandlerInfo.getName(serviceref).replace('\xc2\x86', '').replace('\xc2\x87', '')
		
	# Get Standby State
	if inStandby == None:
		statusinfo['inStandby'] = "false"
	else:
		statusinfo['inStandby'] = "true"

	return statusinfo
