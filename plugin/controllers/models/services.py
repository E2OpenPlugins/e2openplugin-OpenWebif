##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from Tools.Directories import fileExists
from Screens.ChannelSelection import service_types_tv, service_types_radio, FLAG_SERVICE_NEW_FOUND
from enigma import eServiceCenter, eServiceReference, iServiceInformation, eEPGCache
from time import time, localtime, strftime
from info import getPiconPath

def getServiceInfoString(info, what):
	v = info.getInfo(what)
	if v == -1:
		return "N/A"
	if v == -2:
		return info.getInfoString(what)
	return v

def getCurrentService(session):
	try:
		info = session.nav.getCurrentService().info()
		return {
			"result": True,
			"name": info.getName(),
			"namespace": getServiceInfoString(info, iServiceInformation.sNamespace),
			"aspect": getServiceInfoString(info, iServiceInformation.sAspect),
			"provider": getServiceInfoString(info, iServiceInformation.sProvider),
			"width": getServiceInfoString(info, iServiceInformation.sVideoWidth),
			"height": getServiceInfoString(info, iServiceInformation.sVideoHeight),
			"apid": getServiceInfoString(info, iServiceInformation.sAudioPID),
			"vpid": getServiceInfoString(info, iServiceInformation.sVideoPID),
			"pcrpid": getServiceInfoString(info, iServiceInformation.sPCRPID),
			"pmtpid": getServiceInfoString(info, iServiceInformation.sPMTPID),
			"txtpid": getServiceInfoString(info, iServiceInformation.sTXTPID),
			"tsid": getServiceInfoString(info, iServiceInformation.sTSID),
			"onid": getServiceInfoString(info, iServiceInformation.sONID),
			"sid": getServiceInfoString(info, iServiceInformation.sSID)
		}
	except Exception, e:
		return {
			"result": False,
			"name": "",
			"namespace": "",
			"aspect": 0,
			"provider": "",
			"width": 0,
			"height": 0,
			"apid": 0,
			"vpid": 0,
			"pcrpid": 0,
			"pmtpid": 0,
			"txtpid": 0,
			"tsid": 0,
			"onid": 0,
			"sid": 0
		}

def getCurrentFullInfo(session):
	now = next = {}
	inf = getCurrentService(session)
	info = session.nav.getCurrentService().info()
	subservices = session.nav.getCurrentService().subServices()
	audio = session.nav.getCurrentService().audioTracks()
	ref = session.nav.getCurrentlyPlayingServiceReference().toString()
	
	inf['picon'] = getPicon(ref)
	inf['date'] = strftime("%d.%m.%Y", (localtime()))
	inf['wide'] = inf['aspect'] in (3, 4, 7, 8, 0xB, 0xC, 0xF, 0x10)
	inf['ttext'] = getServiceInfoString(info, iServiceInformation.sTXTPID)
	inf['crypt'] = getServiceInfoString(info, iServiceInformation.sIsCrypted)
	inf['subs'] = str(subservices and subservices.getNumberOfSubservices() > 0 )
	inf['dolby'] = False
	if audio:
		n = audio.getNumberOfTracks()
		idx = 0
		while idx < n:
			i = audio.getTrackInfo(idx)
			description = i.getDescription();
			if "AC3" in description or "DTS" in description or "Dolby Digital" in description:
				inf['dolby'] = True
			idx += 1	
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
			inf['snr_db'] = inf['snr'] #Fixme
		percent = frontendStatus.get("tuner_signal_power")
		if percent is not None:
			inf['agc'] = int(percent * 100 / 65536)
		percent =  frontendStatus.get("tuner_bit_error_rate")
		if percent is not None:
			inf['ber'] = int(percent * 100 / 65536)
			
	
	recordings = session.nav.getRecordings()
	inf['rec_state'] = False
	if recordings:
		inf['rec_state'] = True	
	
	ev = getChannelEpg(ref)
	if len(ev['events']) > 1:
		now = ev['events'][0]
		next = ev['events'][1]
		if len(now['title']) > 50:
			now['title'] = now['title'][0:48] + "..."
		if len(next['title']) > 50:
			next['title'] = next['title'][0:48] + "..."
	
	return { "info": inf, "now": now, "next": next }


def getBouquets(stype):
	s_type = service_types_tv
	s_type2 = "bouquets.tv"
	if stype == "radio":
		s_type = service_types_radio
		s_type2 = "bouquets.radio"
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "%s" ORDER BY bouquet'%(s_type, s_type2)))
	bouquets = services and services.getContent("SN", True)
	return { "bouquets": bouquets }
	
def getProviders(stype):
	s_type = service_types_tv
	if stype == "radio":
		s_type = service_types_radio
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s FROM PROVIDERS ORDER BY name'%(s_type)))
	providers = services and services.getContent("SN", True)	
	return { "providers": providers }
	

def getSatellites(stype):
	ret = []
	s_type = service_types_tv
	if stype == "radio":
		s_type = service_types_radio
	refstr = '%s FROM SATELLITES ORDER BY satellitePosition'%(s_type)
	ref = eServiceReference(refstr)
	serviceHandler = eServiceCenter.getInstance()
	servicelist = serviceHandler.list(ref)
	if servicelist is not None:
		while True:
			service = servicelist.getNext()
			if not service.valid():
				break
			unsigned_orbpos = service.getUnsignedData(4) >> 16
			orbpos = service.getData(4) >> 16
			if orbpos < 0:
				orbpos += 3600
			if service.getPath().find("FROM PROVIDER") != -1:
#				service_type = _("Providers")
				continue
			elif service.getPath().find("flags == %d" %(FLAG_SERVICE_NEW_FOUND)) != -1:
				service_type = _("New")
			else:
				service_type = _("Services")
			try:
				service_name = str(nimmanager.getSatDescription(orbpos))
			except:
				if unsigned_orbpos == 0xFFFF: #Cable
					service_name = _("Cable")
				elif unsigned_orbpos == 0xEEEE: #Terrestrial
					service_name = _("Terrestrial")
				else:
					if orbpos > 1800: # west
						orbpos = 3600 - orbpos
						h = _("W")
					else:
						h = _("E")
					service_name = ("%d.%d" + h) % (orbpos / 10, orbpos % 10)
			service.setName("%s - %s" % (service_name, service_type))
			s = service.toString()
			ret.append({
				"service": service.toString(),
				"name": service.getName()
			})

	return { "satellites": ret }
	
	
def getChannels(idbouquet, stype):
	ret = []
	s_type = service_types_tv
	if stype == "radio":
		s_type = service_types_radio
	if idbouquet == "ALL":
		idbouquet = '%s ORDER BY name'%(s_type)

	epgcache = eEPGCache.getInstance()
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference(idbouquet))
	channels = services and services.getContent("SN", True)	
	for channel in channels:
		if not channel[0].startswith("1:64:"):
			chan = {}
			chan['ref'] = channel[0]
			chan['name'] = channel[1]
			nowevent = epgcache.lookupEvent(['TBDCIX', (channel[0], 0, -1)])
			if nowevent[0][0] is not None:
				chan['now_title'] = nowevent[0][0]
				chan['now_begin'] =  strftime("%H:%M", (localtime(nowevent[0][1])))
				chan['now_end'] = strftime("%H:%M",(localtime(nowevent[0][1] + nowevent[0][2])))
				chan['now_left'] = int (((nowevent[0][1] + nowevent[0][2]) - nowevent[0][3]) / 60)
				chan['progress'] = int(((nowevent[0][3] - nowevent[0][1]) * 100 / nowevent[0][2]) )
				chan['now_ev_id'] = nowevent[0][4]
				nextevent = epgcache.lookupEvent(['TBDIX', (channel[0], +1, -1)])
				chan['next_title'] = nextevent[0][0]
				chan['next_begin'] =  strftime("%H:%M", (localtime(nextevent[0][1])))
				chan['next_end'] = strftime("%H:%M",(localtime(nextevent[0][1] + nextevent[0][2])))
				chan['next_duration'] = int(nextevent[0][2] / 60)
				chan['next_ev_id'] = nextevent[0][3]
			ret.append(chan)
			
	return { "channels": ret }
		

def getEventDesc(ref, idev):
	epgcache = eEPGCache.getInstance()
	event = epgcache.lookupEvent(['ESX', (ref, 2, int(idev))])
	if len(event[0][0]) > 1:
		description = event[0][0]
	elif len(event[0][1]) > 1:
		description = event[0][1]
	else:
		description = "No description available"
		
	return { "description": description }


def getChannelEpg(ref):
	ret = []
	ev = {}
	picon = getPicon(ref)
	epgcache = eEPGCache.getInstance()
	events = epgcache.lookupEvent(['IBDTSENC', (ref, 0, -1, -1)])
	if events is not None:
		for event in events:
			ev = {}
			ev['picon'] = picon
			ev['date'] = strftime("%a %d.%b.%Y", (localtime(event[1])))
			ev['begin'] = strftime("%H:%M", (localtime(event[1])))
			ev['duration'] = int(event[2] / 60)
			ev['end'] = strftime("%H:%M",(localtime(event[1] + event[2])))
			ev['title'] = event[3]
			ev['shortdesc'] = event[4]
			ev['longdesc'] = event[5]
			ev['sname'] = event[6]
			ev['tleft'] = int (((event[1] + event[2]) - event[7]) / 60)
			ev['progress'] = int(((event[7] - event[1]) * 100 / event[2]) *4)
			ret.append(ev)
	
	return { "events": ret }
	
def getSearchEpg(sstr):
	ret = []
	ev = {}
	epgcache = eEPGCache.getInstance()
	events = epgcache.search(('IBDTSENR', 128, eEPGCache.PARTIAL_TITLE_SEARCH, sstr, 1));
	if events is not None:
		for event in events:
			ev = {}
			ev['date'] = strftime("%a %d.%b.%Y", (localtime(event[1])))
			ev['begin'] = strftime("%H:%M", (localtime(event[1])))
			ev['duration'] = int(event[2] / 60)
			ev['end'] = strftime("%H:%M",(localtime(event[1] + event[2])))
			ev['title'] = event[3]
			ev['shortdesc'] = event[4]
			ev['longdesc'] = event[5]
			ev['sname'] = event[6]
			ev['picon'] = getPicon(event[7])
			ret.append(ev)
	
	return { "events": ret }

def getPicon(sname):
	pos = sname.rfind(':')
	if pos != -1:
		sname = sname[:pos].rstrip(':').replace(':','_') + ".png"
	filename = getPiconPath() + sname
	if fileExists(filename):
		return "/picon/" + sname
	return "/images/default_picon.png"
	
