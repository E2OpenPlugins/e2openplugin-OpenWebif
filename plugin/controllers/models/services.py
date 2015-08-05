# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
import re, unicodedata
from Tools.Directories import fileExists
from Components.Sources.ServiceList import ServiceList
from Components.ParentalControl import parentalControl
from Components.config import config
from ServiceReference import ServiceReference
from Screens.ChannelSelection import service_types_tv, service_types_radio, FLAG_SERVICE_NEW_FOUND
from enigma import eServiceCenter, eServiceReference, iServiceInformation, eEPGCache, getBestPlayableServiceReference
from time import time, localtime, strftime, mktime
from info import getPiconPath, GetWithAlternative
from urllib import quote, unquote
from Plugins.Extensions.OpenWebif.local import tstrings #using the tstrings dic is faster than translating with _ func from __init__

try:
	from collections import OrderedDict
except ImportError:
	from Plugins.Extensions.OpenWebif.backport.OrderedDict import OrderedDict

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
			"ref": quote(getServiceInfoString(info, iServiceInformation.sServiceref), safe=' ~@#$&()*!+=:;,.?/\''),
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
			"ref": "",
			"iswidescreen" : False
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
		inf['sref'] = '_'.join(ref.split(':', 10)[:10])
		inf['picon'] = getPicon(ref)
		inf['wide'] = inf['aspect'] in (3, 4, 7, 8, 0xB, 0xC, 0xF, 0x10)
		inf['ttext'] = getServiceInfoString(info, iServiceInformation.sTXTPID)
		inf['crypt'] = getServiceInfoString(info, iServiceInformation.sIsCrypted)
		inf['subs'] = str(subservices and subservices.getNumberOfSubservices() > 0 )
	else:
		inf['sref'] = None
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
	bouquets = removeHiddenBouquets(bouquets)
	return { "bouquets": bouquets }

def removeHiddenBouquets(bouquetList):
	bouquets = bouquetList
	if hasattr(eServiceReference, 'isInvisible'):
		for bouquet in bouquetList:
			flags = int(bouquet[0].split(':')[1])
			if flags & eServiceReference.isInvisible and bouquet in bouquets:
				bouquets.remove(bouquet)
	return bouquets

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
			ret.append({
				"service": service.toString(),
				"name": service.getName()
			})
	ret = sortSatellites(ret)
	return { "satellites": ret }

def sortSatellites(satList):
	import re
	sortDict = {}
	i = 0
	for k in satList:
		result = re.search("[(]\s*satellitePosition\s*==\s*(\d+)\s*[)]", k["service"], re.IGNORECASE)
		if result is None:
			return satList
		orb = int(result.group(1))
		if orb > 3600:
			orb *= -1
		elif orb > 1800:
			orb -= 3600
		if not orb in sortDict:
			sortDict[orb] = []
		sortDict[orb].append(i)
		i += 1
	outList = []
	for l in sorted(sortDict.keys()):
		for v in sortDict[l]:
			outList.append(satList[v])
	return outList

def getProtection(sref):
	isProtected = "0"
	if config.ParentalControl.configured.value and config.ParentalControl.servicepinactive.value:
		protection = parentalControl.getProtectionLevel(sref)
		if protection != -1:
			if config.ParentalControl.type.value == "blacklist":
				if parentalControl.blacklist.has_key(sref):
					if "SERVICE" in parentalControl.blacklist[sref]:
						isProtected = '1'
					elif "BOUQUET" in parentalControl.blacklist[sref]:
						isProtected = '2'
					else:
						isProtected = '3'
			elif config.ParentalControl.type.value == "whitelist":
				if not parentalControl.whitelist.has_key(sref):
					service = eServiceReference(sref)
					if service.flags & eServiceReference.isGroup:
						isprotected = '5'
					else:
						isProtected = '4'
	return isProtected

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
			chan['ref'] = quote(channel[0], safe=' ~@%#$&()*!+=:;,.?/\'')
			chan['name'] = filterName(channel[1])
			if config.OpenWebif.parentalenabled.value and config.ParentalControl.configured.value and config.ParentalControl.servicepinactive.value:
				chan['protection'] = getProtection(channel[0])
			else:
				chan['protection'] = "0"
			nowevent = epgcache.lookupEvent(['TBDCIX', (channel[0], 0, -1)])
			if len(nowevent) > 0 and nowevent[0][0] is not None:
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

def getServices(sRef, showAll = True, showHidden = False):
	services = []

	if sRef == "":
		sRef = '%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet' % (service_types_tv)

	servicelist = ServiceList(eServiceReference(sRef))
	slist = servicelist.getServicesAsList()

	for sitem in slist:
		st = int(sitem[0].split(":")[1])
		if not st & 512 or showHidden:
			if showAll or st == 0:
				service = {}
				service['servicereference'] = sitem[0].encode("utf8")
				service['servicename'] = sitem[1].encode("utf8")
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

def getPlayableServices(sRef, sRefPlaying):
	if sRef == "":
		sRef = '%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet' % (service_types_tv)

	services = []
	servicecenter = eServiceCenter.getInstance()
	servicelist = servicecenter.list(eServiceReference(sRef))
	servicelist2 = servicelist and servicelist.getContent('S') or []

	for service in servicelist2:
		if not int(service.split(":")[1]) & 512:	# 512 is hidden service on sifteam image. Doesn't affect other images
			service2 = {}
			service2['servicereference'] = service
			info = servicecenter.info(eServiceReference(service))
			service2['isplayable'] = info.isPlayable(eServiceReference(service),eServiceReference(sRefPlaying))>0
			services.append(service2)

	return {
		"result": True,
		"services": services
	}

def getPlayableService(sRef, sRefPlaying):
	servicecenter = eServiceCenter.getInstance()
	info = servicecenter.info(eServiceReference(sRef))
	return {
		"result": True,
		"service": {
			"servicereference": sRef,
			"isplayable": info.isPlayable(eServiceReference(sRef),eServiceReference(sRefPlaying))>0
		}
	}

def getSubServices(session):
	services = []
	service = session.nav.getCurrentService()
	if service is not None:
		services.append({
			"servicereference": service.info().getInfoString(iServiceInformation.sServiceref),
			"servicename": service.info().getName()
		})
		subservices = service.subServices()
		if subservices and subservices.getNumberOfSubservices() > 0:
			print subservices.getNumberOfSubservices()
			for i in range(subservices.getNumberOfSubservices()):
				sub = subservices.getSubservice(i)
				services.append({
					"servicereference": sub.toString(),
					"servicename": sub.getName()
				})
	else:
		services.append({
			"servicereference": "N/A",
			"servicename": "N/A"
		})

	return { "services": services }

def getEventDesc(ref, idev):
	ref = unquote(ref)
	epgcache = eEPGCache.getInstance()
	event = epgcache.lookupEvent(['ESX', (ref, 2, int(idev))])
	if len(event[0][0]) > 1:
		description = event[0][0].replace('\xc2\x86', '').replace('\xc2\x87', '').replace('\xc2\x8a', '')
	elif len(event[0][1]) > 1:
		description = event[0][1].replace('\xc2\x86', '').replace('\xc2\x87', '').replace('\xc2\x8a', '')
	else:
		description = "No description available"

	return { "description": description }

def getEvent(ref, idev):
	epgcache = eEPGCache.getInstance()
	events = epgcache.lookupEvent(['IBDTSENRX', (ref, 2, int(idev))])
	info = {}
	for event in events:
		info['id'] = event[0]
		info['begin_str'] = strftime("%H:%M", (localtime(event[1])))
		info['begin'] = event[1]
		info['end'] = strftime("%H:%M",(localtime(event[1] + event[2])))
		info['duration'] = event[2]
		info['title'] = filterName(event[3])
		info['shortdesc'] = event[4]
		info['longdesc'] = event[5]
		info['channel'] = filterName(event[6])
		info['sref'] = event[7]
		break;
	return { 'event': info }

def getChannelEpg(ref, begintime=-1, endtime=-1):
	ret = []
	ev = {}
	use_empty_ev = False
	if ref:
		ref = unquote(ref)

		# When quering EPG we dont need URL, also getPicon doesn't like URL
		if "://" in ref:
			ref = ":".join(ref.split(":")[:10]) + "::" + ref.split(":")[-1]

		picon = getPicon(ref)
		epgcache = eEPGCache.getInstance()
		events = epgcache.lookupEvent(['IBDTSENC', (ref, 0, begintime, endtime)])
		if events is not None:
			for event in events:
				ev = {}
				ev['picon'] = picon
				ev['id'] = event[0]
				if event[1]:
					ev['date'] = "%s %s" % (tstrings[("day_" + strftime("%w", (localtime(event[1]))))], strftime("%d.%m.%Y", (localtime(event[1]))))
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
					if ev['duration_sec'] == 0:
						ev['progress'] = 0
					else:
						ev['progress'] = int(((event[7] - event[1]) * 100 / event[2]) *4)
					ev['now_timestamp'] = event[7]
					ret.append(ev)
				else:
					use_empty_ev = True
					ev['sref'] = ref
	else:
		use_empty_ev = True
		ev['sref'] = ""

	if use_empty_ev:
		ev['date'] = 0
		ev['begin'] = 0
		ev['begin_timestamp'] = 0
		ev['duration'] = 0
		ev['duration_sec'] = 0
		ev['end'] = 0
		ev['title'] = "N/A"
		ev['shortdesc'] = ""
		ev['sname'] = ""
		ev['longdesc'] = ""
		ev['tleft'] = 0
		ev['progress'] = 0
		ev['now_timestamp'] = 0
		ret.append(ev)

	return { "events": ret, "result": True }

def getBouquetEpg(ref, begintime=-1, endtime=None):
	ref = unquote(ref)
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
	ref = unquote(ref)
	ret = []
	services = eServiceCenter.getInstance().list(eServiceReference(ref))
	if not services:
		return { "events": ret, "result": False }

	search = ['IBDCTSERNX']
	if servicetype == -1:
		for service in services.getContent('S'):
			search.append((service, 0, -1))
			search.append((service, 1, -1))
	else:
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
			if event[7] is not None:
				achannels = GetWithAlternative(event[7], False)
				if achannels:
					ev['asrefs'] = achannels
			ev['sref'] = event[7]
			ev['sname'] = filterName(event[8])
			ev['now_timestamp'] = event[3]
			ret.append(ev)

	return { "events": ret, "result": True }

def getNowNextEpg(ref, servicetype):
	ref = unquote(ref)
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

def getSearchEpg(sstr, endtime=None):
	ret = []
	ev = {}
	if config.OpenWebif.epg_encoding.value != 'utf-8':
		try:
			sstr = sstr.encode(config.OpenWebif.epg_encoding.value)
		except UnicodeEncodeError:
			pass
	epgcache = eEPGCache.getInstance()
	search_type = eEPGCache.PARTIAL_TITLE_SEARCH
	if config.OpenWebif.webcache.epg_desc_search.value:
		search_type = eEPGCache.FULL_DESCRIPTION_SEARCH
	events = epgcache.search(('IBDTSENR', 128, search_type, sstr, 1));
	if events is not None:
		for event in events:
			ev = {}
			ev['id'] = event[0]
			ev['date'] = "%s %s" % (tstrings[("day_" + strftime("%w", (localtime(event[1]))))], strftime("%d.%m.%Y", (localtime(event[1]))))
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
			if endtime:
				# don't show events if begin after endtime
				if event[1] <= endtime:
					ret.append(ev)
			else:
				ret.append(ev)

	return { "events": ret, "result": True }

def getSearchSimilarEpg(ref, eventid):
	ref = unquote(ref)
	ret = []
	ev = {}
	epgcache = eEPGCache.getInstance()
	events = epgcache.search(('IBDTSENR', 128, eEPGCache.SIMILAR_BROADCASTINGS_SEARCH, ref, eventid));
	if events is not None:
		for event in events:
			ev = {}
			ev['id'] = event[0]
			ev['date'] = "%s %s" % (tstrings[("day_" + strftime("%w", (localtime(event[1]))))], strftime("%d.%m.%Y", (localtime(event[1]))))
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


def getMultiEpg(self, ref, begintime=-1, endtime=None):
	# Check if an event has an associated timer. Unfortunately
	# we cannot simply check against timer.eit, because a timer
	# does not necessarily have one belonging to an epg event id.
	def getTimerEventStatus(event):
		startTime = event[1]
		endTime = event[1] + event[6] - 120
		serviceref = event[4]
		if not timerlist.has_key(serviceref):
			return ''
		for timer in timerlist[serviceref]:
			if timer.begin <= startTime and timer.end >= endTime:
				if timer.disabled:
					return 'timer disabled'
				else:
					return 'timer'
		return ''

	ret = OrderedDict()
	services = eServiceCenter.getInstance().list(eServiceReference(ref))
	if not services:
		return { "events": ret, "result": False, "slot": None }

	search = ['IBTSRND']
	for service in services.getContent('S'):
		if endtime:
			search.append((service, 0, begintime, endtime))
		else:
			search.append((service, 0, begintime))

	epgcache = eEPGCache.getInstance()
	events = epgcache.lookupEvent(search)
	offset = None
	picons = {}

	if events is not None:
		# We want to display if an event is covered by a timer.
		# To keep the costs low for a nested loop against the timer list, we
		# partition the timers by service reference. For an event we then only
		# have to check the part of the timers that belong to that specific
		# service reference. Partition is generated here.
		timerlist = {}
		for timer in self.session.nav.RecordTimer.timer_list + self.session.nav.RecordTimer.processed_timers:
			if not timerlist.has_key(str(timer.service_ref)):
				timerlist[str(timer.service_ref)] = []
			timerlist[str(timer.service_ref)].append(timer)

		for event in events:
			ev = {}
			ev['id'] = event[0]
			ev['begin_timestamp'] = event[1]
			ev['title'] = event[2]
			ev['shortdesc'] = event[3]
			ev['ref'] = event[4]
			ev['timerStatus'] = getTimerEventStatus(event)

			channel = filterName(event[5])
			if not ret.has_key(channel):
				ret[channel] = [ [], [], [], [], [], [], [], [], [], [], [], [] ]
				picons[channel] = getPicon(event[4])

			if offset is None:
				bt = event[1]
				if begintime > event[1]:
					bt = begintime
				et = localtime(bt)
				offset = mktime( (et.tm_year, et.tm_mon, et.tm_mday, 0, 0, 0, -1, -1, -1) )
				lastevent = mktime( (et.tm_year, et.tm_mon, et.tm_mday, 23, 59, 0, -1, -1, -1) )

			slot = int((event[1]-offset) / 7200)
			if slot > -1 and slot < 12 and event[1] < lastevent:
				ret[channel][slot].append(ev)

	return { "events": ret, "result": True, "picons": picons }

def getPicon(sname):
	# remove URL part
	if ("://" in sname) or ("%3a//" in sname) or ("%3A//" in sname):
		sname = unquote(sname)
		sname = ":".join(sname.split(":")[:10]) + "::" + sname.split(":")[-1]

	sname = GetWithAlternative(sname)
	if sname is not None:
		pos = sname.rfind(':')
	else:
		return "/images/default_picon.png"
	cname = None
	if pos != -1:
		cname = ServiceReference(sname[:pos].rstrip(':')).getServiceName()
		sname = sname[:pos].rstrip(':').replace(':','_') + ".png"
	filename = getPiconPath() + sname
	if fileExists(filename):
		return "/picon/" + sname
	fields = sname.split('_', 3)
	if len(fields) > 2 and fields[2] != '2':
		#fallback to 1 for tv services with nonstandard servicetypes
		fields[2] = '1'
		sname='_'.join(fields)
		filename = getPiconPath() + sname
		if fileExists(filename):
			return "/picon/" + sname
	if cname is not None: # picon by channel name
		cname = unicodedata.normalize('NFKD', unicode(cname, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
		cname = re.sub('[^a-z0-9]', '', cname.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())
		if len(cname) > 0:
			filename = getPiconPath() + cname + ".png"
		if fileExists(filename):
			return "/picon/" + cname + ".png"
		if len(cname) > 2 and cname.endswith('hd') and fileExists(getPiconPath() + cname[:-2] + ".png"):
			return "/picon/" + cname[:-2] + ".png"
	return "/images/default_picon.png"

def getParentalControlList():
	if config.ParentalControl.configured.value:
		return {
			"result": True,
			"services": []
		}
	parentalControl.open()
	if config.ParentalControl.type.value == "whitelist":
		tservices = parentalControl.whitelist
	else:
		tservices = parentalControl.blacklist
	services = []
	if tservices is not None:
		for service in tservices:
			tservice = ServiceReference(service)
			services.append({
				"servicereference": service,
				"servicename": tservice.getServiceName()
			})
	return {
		"result": True,
		"type": config.ParentalControl.type.value,
		"services": services
	}

def loadEpg():
	epgcache = eEPGCache.getInstance()
	epgcache.load()
	return {
		"result": True,
		"message": ""
	}

def saveEpg():
	epgcache = eEPGCache.getInstance()
	epgcache.save()
	return {
		"result": True,
		"message": ""
	}
