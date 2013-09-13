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
from enigma import eDVBVolumecontrol, eServiceCenter, eServiceReference
try: 
	getDistro, getBoxType
except: pass

import os
import sys
import time

OPENWEBIFVER = "OWIF 0.2.1"

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

	if fileExists("/proc/stb/info/hwmodel"):
		file = open("/proc/stb/info/hwmodel")
		model = file.read().strip().lower()
		file.close()
		if model == "tmtwinoe":
			model = "TM-TWIN-OE"
			brand = "Technomate"
		elif model == "tm2toe":
			model = "TM-2T-OE"
			brand = "Technomate"
		elif model == "tmsingle":
			model = "TM-SINGLE"
			brand = "Technomate"
		elif model == "tmnanooe":
			model = "TM-NANO-OE"
			brand = "Technomate"
		elif model == "ios100hd":
			model = "IOS-100HD"
			brand = "Iqon"
		elif model == "ios200hd":
			model = "IOS-200HD"
			brand = "Iqon"
		elif model == "ios300hd":
			model = "IOS-300HD"
			brand = "Iqon"
		elif model == "optimussos1":
			model = "Optimuss-OS1"
			brand = "Edision"
		elif model == "optimussos2":
			model = "Optimuss-OS2"
			brand = "Edision"
	elif fileExists("/proc/stb/info/boxtype"):
		file = open("/proc/stb/info/boxtype")
		model = file.read().strip().lower()
		file.close()
		if model == "gigablue":
			brand = "GigaBlue"
			if fileExists("/proc/stb/info/gbmodel"):
				file = open("/proc/stb/info/gbmodel")
				model = file.read().strip().lower()
				file.close()
			else:
				model = 'gb800solo'
		elif model.startswith("et"):
			brand = "Clarke-Xtrend"
			if model == "et9500":
				model = "et9x00"
		elif model.startswith("ini"):
			if model.endswith("sv"):
				brand = "MiracleBox"
				if model == "ini-5000sv":
					model = "Premium Twin"
				elif model == "ini-1000sv":
					model = "Premium Mini"
				else:
					model
			elif model.endswith("de"):
				brand = "Golden Interstar"
				if model == "ini-1000de":
					model = "Xpeed LX"
				elif model == "ini-9000de":
					model = "Xpeed LX3"
				else:
					model
			elif model.endswith("ru"):
				brand = "Sezam"
			else:
				brand = "Venton"
		elif model == "xp1000":
			brand = "XP-Series"
		elif model == "xp1000s":
			brand = "Octagon"
			model = "SF8 HD"
		elif model == "odinm9":
			brand = "Odin-Series"
		elif model == "odinm7":
			if getDistro() == 'axassupport':
				brand = "AXAS"
				model = "Class M"
			elif getBoxType() == 'odinm6':
				brand = "TELESTAR"
				model = "STARSAT LX"
			else:
				brand = "Odin-Series"
		elif model == "e3hd":
			if getDistro() == 'axassupport':
				brand = "AXAS"
				model = "Class E"
			else:
				brand = "E3-Series"
		elif model == "ebox5000":
			brand = "MixOs-Series"
			model = "MixOs F5"
		elif model == "ebox5100":
			brand = "MixOs-Series"
			model = "MixOs F5mini"
		elif model == "ebox7358":
			brand = "MixOs-Series"
			model = "MixOs F7"
		elif model.startswith("ixuss"):
			brand = "Ixuss-Series"
			chipset = "BCM7405"
	elif fileExists("/proc/stb/info/azmodel"):
		brand = "AZBOX"
		file = open("/proc/stb/info/model")
		model = file.read().strip().lower()
		file.close()
		if model == "me":
			chipset = "SIGMA 8655"
		elif model == "minime":
			chipset = "SIGMA 8653"
		else:
			chipset = "SIGMA 8634"
	elif fileExists("/proc/stb/info/vumodel"):
		brand = "Vu Plus"
		file = open("/proc/stb/info/vumodel")
		model = file.read().strip().lower()
		file.close()
	else:
		file = open("/proc/stb/info/model")
		model = file.read().strip().lower()
		file.close()

	info['brand'] = brand
	info['model'] = model

	if fileExists("/proc/stb/info/chipset"):
		f = open("/proc/stb/info/chipset",'r')
		chipset = f.readline().strip()
		f.close()

	info['chipset'] = chipset

	memFree = 0
	file = open("/proc/meminfo",'r')
	for line in file:
		parts = line.split(':')
		key = parts[0].strip()
		if key == "MemTotal":
			info['mem1'] = parts[1].strip()
		elif key in ("MemFree", "Buffers", "Cached"):
			memFree += int(parts[1].strip().split(' ',1)[0])
	info['mem2'] = "%s kB" % memFree
	file.close()

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

	info["webifver"] = getOpenWebifVer()
	try:
		from enigma import getImageVersionString, getBuildVersionString, getEnigmaVersionString
		info['imagever'] = getImageVersionString() + '.' + getBuildVersionString()
		info['enigmaver'] = getEnigmaVersionString()
	except:
		info['imagever'] = about.getImageVersionString()
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

	service = session.nav.getCurrentService()
	if service is None:
		return inf
	feinfo = service.frontendInfo()
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
		statusinfo['currservice_begin'] = strftime("%H:%M", (localtime(int(curEvent[0])+(config.recording.margin_before.getValue()*60))))
		statusinfo['currservice_end'] = strftime("%H:%M", (localtime(int(curEvent[1])-(config.recording.margin_after.getValue()*60))))
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

def getAlternativeChannels(service):
	alternativeServices = eServiceCenter.getInstance().list(eServiceReference(service))
	return alternativeServices and alternativeServices.getContent("S", True)

def GetWithAlternative(service,onlyFirst = True):
	if service.startswith('1:134:'):
		channels = getAlternativeChannels(service)
		if channels:
			if onlyFirst:
				return channels[0]
			else:
				return channels
	if onlyFirst:
		return service
	else:
		return None

