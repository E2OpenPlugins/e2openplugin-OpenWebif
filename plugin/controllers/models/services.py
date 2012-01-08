##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from Tools.Directories import fileExists
from Components.Sources.ServiceList import ServiceList
from Screens.ChannelSelection import service_types_tv, service_types_radio, FLAG_SERVICE_NEW_FOUND
from enigma import eServiceCenter, eServiceReference, iServiceInformation, eEPGCache
from time import time, localtime, strftime
from info import getPiconPath


def filterName(name):
	if name is not None:
		name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
	return name

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
			"name": filterName(info.getName()),
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
			"sid": getServiceInfoString(info, iServiceInformation.sSID),
			"ref": getServiceInfoString(info, iServiceInformation.sServiceref),
			"iswidescreen": info.getInfo(iServiceInformation.sAspect) in (3, 4, 7, 8, 0xB, 0xC, 0xF, 0x10)
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
			"txtpid": "N/A",
			"tsid": 0,
			"onid": 0,
			"sid": 0,
			"ref": ""
		}

def getCurrentFullInfo(session):
	now = next = {}
	
	inf = getCurrentService(session)
	
	try:
		info = session.nav.getCurrentService().info()
	except:
		info = None

	try:
		subservices = session.nav.getCurrentService().subServices()
	except:
		subservices = None

	try:
		audio = session.nav.getCurrentService().audioTracks()
	except:
		audio = None

	try:
		ref = session.nav.getCurrentlyPlayingServiceReference().toString()
	except:
		ref = None

	if ref is not None:
		inf['picon'] = getPicon(ref)
		inf['wide'] = inf['aspect'] in (3, 4, 7, 8, 0xB, 0xC, 0xF, 0x10)
		inf['ttext'] = getServiceInfoString(info, iServiceInformation.sTXTPID)
		inf['crypt'] = getServiceInfoString(info, iServiceInformation.sIsCrypted)
		inf['subs'] = str(subservices and subservices.getNumberOfSubservices() > 0 )
	else:
		inf['picon'] = None
		inf['wide'] = None
		inf['ttext'] = None
		inf['crypt'] = None
		inf['subs'] = None
		
	inf['date'] = strftime("%d.%m.%Y", (localtime()))
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
	try:
		feinfo = session.nav.getCurrentService().frontendInfo()
	except:
		feinfo = None
	
	frontendData = feinfo and feinfo.getAll(True)
	
	if frontendData is not None:
		inf['tunertype'] = frontendData.get("tuner_type", "UNKNOWN")
		if frontendData.get("system", -1) == 1:
			inf['tunertype'] = "DVB-S2"
		inf['tunernumber'] = frontendData.get("tuner_number")
	else:
		inf['tunernumber'] = "N/A"
		inf['tunertype'] = "N/A"
	
	try:
		frontendStatus = feinfo and feinfo.getFrontendStatus()
	except:
		frontendStatus = None
	
	if frontendStatus is not None:
		percent = frontendStatus.get("tuner_signal_quality")
		if percent is not None:
			inf['snr'] = int(percent * 100 / 65536)
			inf['snr_db'] = inf['snr']
		percent = frontendStatus.get("tuner_signal_quality_db")
		if percent is not None:
			inf['snr_db'] = "%3.02f dB" % (percent / 100.0)
		percent = frontendStatus.get("tuner_signal_power")
		if percent is not None:
			inf['agc'] = int(percent * 100 / 65536)
		percent =  frontendStatus.get("tuner_bit_error_rate")
		if percent is not None:
			inf['ber'] = int(percent * 100 / 65536)
	else:
		inf['snr'] = 0
		inf['snr_db'] = inf['snr']
		inf['agc'] = 0
		inf['ber'] = 0
	
	try:
		recordings = session.nav.getRecordings()
	except:
		recordings = None
	
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
	idp = 0
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
		if not int(channel[0].split(":")[1]) & 64:
			chan = {}
			chan['ref'] = channel[0]
			chan['name'] = filterName(channel[1])
			nowevent = epgcache.lookupEvent(['TBDCIX', (channel[0], 0, -1)])
			if nowevent[0][0] is not None:
				chan['now_title'] = filterName(nowevent[0][0])
				chan['now_begin'] =  strftime("%H:%M", (localtime(nowevent[0][1])))
				chan['now_end'] = strftime("%H:%M",(localtime(nowevent[0][1] + nowevent[0][2])))
				chan['now_left'] = int (((nowevent[0][1] + nowevent[0][2]) - nowevent[0][3]) / 60)
				chan['progress'] = int(((nowevent[0][3] - nowevent[0][1]) * 100 / nowevent[0][2]) )
				chan['now_ev_id'] = nowevent[0][4]
				chan['now_idp'] = "nowd" + str(idp)
				nextevent = epgcache.lookupEvent(['TBDIX', (channel[0], +1, -1)])
				chan['next_title'] = filterName(nextevent[0][0])
				chan['next_begin'] =  strftime("%H:%M", (localtime(nextevent[0][1])))
				chan['next_end'] = strftime("%H:%M",(localtime(nextevent[0][1] + nextevent[0][2])))
				chan['next_duration'] = int(nextevent[0][2] / 60)
				chan['next_ev_id'] = nextevent[0][3]
				chan['next_idp'] = "nextd" + str(idp)
				idp += 1
			ret.append(chan)
			
	return { "channels": ret }
		
def getServices(sRef):
	services = []
	
	if sRef == "":
		sRef = '%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet' % (service_types_tv)
		
	servicelist = ServiceList(eServiceReference(sRef))
	slist = servicelist.getServicesAsList()

	for sitem in slist:
		if not int(sitem[0].split(":")[1]) & 512:	# 512 is hidden service on sifteam image. Doesn't affect other images
			service = {}
			service['servicereference'] = sitem[0]
			service['servicename'] = sitem[1]
			services.append(service)
			
	return { "services": services }

def getAllServices():
	services = []
	bouquets = getBouquets("tv")["bouquets"]
	for bouquet in bouquets:
		services.append({
			"servicereference": bouquet[0],
			"servicename": bouquet[1],
			"subservices": getServices(bouquet[0])["services"]
		})
		
	return {
		"result": True,
		"services": services
	}

def getSubServices(session):
	services = []
	currentServiceRef = session.nav.getCurrentlyPlayingServiceReference()
	if currentServiceRef is not None:
		currentService = session.nav.getCurrentService()
		subservices = currentService.subServices()
		
		if subservices and subservices.getNumberOfSubservices() != 0:
			n = subservices and subservices.getNumberOfSubservices()
			z = 0
			while z < n:
				sub = subservices.getSubservice(z)
				services.append({
					"servicereference": sub.toString(), 
					"servicename": sub.getName()
				})
				z += 1
		
	else:
		services.append =({
			"servicereference": "N/A",
			"servicename": "N/A"
		})
		
	return { "services": services }

def getEventDesc(ref, idev):
	epgcache = eEPGCache.getInstance()
	event = epgcache.lookupEvent(['ESX', (ref, 2, int(idev))])
	if len(event[0][0]) > 1:
		description = event[0][0].replace('\xc2\x86', '').replace('\xc2\x87', '').replace('\xc2\x8a', '')
	elif len(event[0][1]) > 1:
		description = event[0][1].replace('\xc2\x86', '').replace('\xc2\x87', '').replace('\xc2\x8a', '')
	else:
		description = "No description available"
		
	return { "description": description }


def getChannelEpg(ref, begintime=-1, endtime=-1):
	ret = []
	ev = {}
	picon = getPicon(ref)
	epgcache = eEPGCache.getInstance()
	events = epgcache.lookupEvent(['IBDTSENC', (ref, 0, begintime, endtime)])
	if events is not None:
		for event in events:
			ev = {}
			ev['picon'] = picon
			ev['id'] = event[0]
			if event[1]:
				ev['date'] = strftime("%a %d.%b.%Y", (localtime(event[1])))
				ev['begin'] = strftime("%H:%M", (localtime(event[1])))
				ev['begin_timestamp'] = event[1]
				ev['duration'] = int(event[2] / 60)
				ev['duration_sec'] = event[2]
				ev['end'] = strftime("%H:%M",(localtime(event[1] + event[2])))
				ev['title'] = filterName(event[3])
				ev['shortdesc'] = event[4]
				ev['longdesc'] = event[5]
				ev['sref'] = ref
				ev['sname'] = filterName(event[6])
				ev['tleft'] = int (((event[1] + event[2]) - event[7]) / 60)
				ev['progress'] = int(((event[7] - event[1]) * 100 / event[2]) *4)
				ev['now_timestamp'] = event[7]
			else:
				ev['date'] = 0
				ev['begin'] = 0
				ev['begin_timestamp'] = 0
				ev['duration'] = 0
				ev['duration_sec'] = 0
				ev['end'] = 0
				ev['title'] = "N/A"
				ev['shortdesc'] = ""
				ev['longdesc'] = ""
				ev['sref'] = ref
				ev['sname'] = filterName(event[6])
				ev['tleft'] = 0
				ev['progress'] = 0
				ev['now_timestamp'] = 0
			ret.append(ev)
	
	return { "events": ret, "result": True }
	
def getBouquetEpg(ref, begintime=-1, endtime=None):
	ret = []
	services = eServiceCenter.getInstance().list(eServiceReference(ref))
	if not services:
		return { "events": ret, "result": False }
		
	search = ['IBDCTSERN']
	for service in services.getContent('S'):
		if endtime:
			search.append((service, 0, begintime, endtime))
		else:
			search.append((service, 0, begintime))
		
	epgcache = eEPGCache.getInstance()
	events = epgcache.lookupEvent(search)
	if events is not None:
		for event in events:
			ev = {}
			ev['id'] = event[0]
			ev['begin_timestamp'] = event[1]
			ev['duration_sec'] = event[2]
			ev['title'] = event[4]
			ev['shortdesc'] = event[5]
			ev['longdesc'] = event[6]
			ev['sref'] = event[7]
			ev['sname'] = filterName(event[8])
			ev['now_timestamp'] = event[3]
			ret.append(ev)
	
	return { "events": ret, "result": True }
	
def getBouquetNowNextEpg(ref, servicetype):
	ret = []
	services = eServiceCenter.getInstance().list(eServiceReference(ref))
	if not services:
		return { "events": ret, "result": False }
		
	search = ['IBDCTSERNX']
	for service in services.getContent('S'):
		search.append((service, servicetype, -1))
		
	epgcache = eEPGCache.getInstance()
	events = epgcache.lookupEvent(search)
	if events is not None:
		for event in events:
			ev = {}
			ev['id'] = event[0]
			ev['begin_timestamp'] = event[1]
			ev['duration_sec'] = event[2]
			ev['title'] = event[4]
			ev['shortdesc'] = event[5]
			ev['longdesc'] = event[6]
			ev['sref'] = event[7]
			ev['sname'] = filterName(event[8])
			ev['now_timestamp'] = event[3]
			ret.append(ev)
	
	return { "events": ret, "result": True }
	
def getNowNextEpg(ref, servicetype):
	ret = []
	epgcache = eEPGCache.getInstance()
	events = epgcache.lookupEvent(['IBDCTSERNX', (ref, servicetype, -1)])
	if events is not None:
		for event in events:
			ev = {}
			ev['id'] = event[0]
			if event[1]:
				ev['begin_timestamp'] = event[1]
				ev['duration_sec'] = event[2]
				ev['title'] = event[4]
				ev['shortdesc'] = event[5]
				ev['longdesc'] = event[6]
				ev['sref'] = event[7]
				ev['sname'] = filterName(event[8])
				ev['now_timestamp'] = event[3]
				ev['remaining'] = (event[1] + event[2]) - event[3]
			else:
				ev['begin_timestamp'] = 0
				ev['duration_sec'] = 0
				ev['title'] = "N/A"
				ev['shortdesc'] = ""
				ev['longdesc'] = ""
				ev['sref'] = event[7]
				ev['sname'] = filterName(event[8])
				ev['now_timestamp'] = 0
				ev['remaining'] = 0

				
			ret.append(ev)
	
	return { "events": ret, "result": True }
	
def getSearchEpg(sstr):
	ret = []
	ev = {}
	epgcache = eEPGCache.getInstance()
	events = epgcache.search(('IBDTSENR', 128, eEPGCache.PARTIAL_TITLE_SEARCH, sstr, 1));
	if events is not None:
		for event in events:
			ev = {}
			ev['id'] = event[0]
			ev['date'] = strftime("%a %d.%b.%Y", (localtime(event[1])))
			ev['begin_timestamp'] = event[1]
			ev['begin'] = strftime("%H:%M", (localtime(event[1])))
			ev['duration_sec'] = event[2]
			ev['duration'] = int(event[2] / 60)
			ev['end'] = strftime("%H:%M",(localtime(event[1] + event[2])))
			ev['title'] = filterName(event[3])
			ev['shortdesc'] = event[4]
			ev['longdesc'] = event[5]
			ev['sref'] = event[7]
			ev['sname'] = filterName(event[6])
			ev['picon'] = getPicon(event[7])
			ev['now_timestamp'] = None
			ret.append(ev)
	
	return { "events": ret, "result": True }

def getSearchSimilarEpg(ref, eventid):
	ret = []
	ev = {}
	epgcache = eEPGCache.getInstance()
	events = epgcache.search(('IBDTSENR', 128, eEPGCache.SIMILAR_BROADCASTINGS_SEARCH, ref, eventid));
	if events is not None:
		for event in events:
			ev = {}
			ev['id'] = event[0]
			ev['date'] = strftime("%a %d.%b.%Y", (localtime(event[1])))
			ev['begin_timestamp'] = event[1]
			ev['begin'] = strftime("%H:%M", (localtime(event[1])))
			ev['duration_sec'] = event[2]
			ev['duration'] = int(event[2] / 60)
			ev['end'] = strftime("%H:%M",(localtime(event[1] + event[2])))
			ev['title'] = event[3]
			ev['shortdesc'] = event[4]
			ev['longdesc'] = event[5]
			ev['sref'] = event[7]
			ev['sname'] = filterName(event[6])
			ev['picon'] = getPicon(event[7])
			ev['now_timestamp'] = None
			ret.append(ev)
	
	return { "events": ret, "result": True }
	
def getPicon(sname):
	pos = sname.rfind(':')
	if pos != -1:
		sname = sname[:pos].rstrip(':').replace(':','_') + ".png"
	filename = getPiconPath() + sname
	if fileExists(filename):
		return "/picon/" + sname
	return "/images/default_picon.png"
	
