#!/usr/bin/python
# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: services
##########################################################################
# Copyright (C) 2011 - 2020 E2OpenPlugins
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
##########################################################################

from __future__ import print_function
import re
import unicodedata
import six
from time import time, localtime, strftime, mktime

import NavigationInstance
from Tools.Directories import fileExists
from Components.Sources.ServiceList import ServiceList
from Components.ParentalControl import parentalControl
from Components.config import config
from Components.NimManager import nimmanager
from ServiceReference import ServiceReference
from Screens.ChannelSelection import service_types_tv, service_types_radio, FLAG_SERVICE_NEW_FOUND
from Screens.InfoBar import InfoBar
from enigma import eServiceCenter, eServiceReference, iServiceInformation, eEPGCache
from six.moves.urllib.parse import quote, unquote
from Plugins.Extensions.OpenWebif.controllers.models.info import GetWithAlternative, getOrbitalText, getOrb
from Plugins.Extensions.OpenWebif.controllers.utilities import parse_servicereference, SERVICE_TYPE_LOOKUP, NS_LOOKUP, PY3
from Plugins.Extensions.OpenWebif.controllers.i18n import _, tstrings
from Plugins.Extensions.OpenWebif.controllers.defaults import PICON_PATH

try:
	from Components.Converter.genre import getGenreStringLong
except ImportError:
	from Plugins.Extensions.OpenWebif.controllers.utilities import getGenreStringLong

try:
	from collections import OrderedDict
except ImportError:
	from Plugins.Extensions.OpenWebif.backport.OrderedDict import OrderedDict

# The fields fetched by filterName() and convertDesc() all need to be
# html-escaped, so do it there.
#

if PY3:
	from html import escape as html_escape
else:
	from cgi import escape as html_escape


def getIPTVLink(ref):
	first = ref.split(":")[0]
	if first in ['4097', '5003', '5002', '5001'] or "%3A" in ref or "%3a" in ref:
		if 'http' in ref:
			if ref.index('http') < ref.rindex(':'):
				ref = ref[:ref.rindex(':')]
			ref = ref[ref.index('http'):]
			ref = ref.replace('%3a', ':').replace('%3A', ':').replace('http://127.0.0.1:8088/', '')
			return ref
	return ''


def filterName(name, encode=True):
	if name is not None:
		name = six.ensure_str(removeBadChars(six.ensure_binary(name)))
		if encode is True:
			return html_escape(name, quote=True)
	return name


def removeBadChars(val):
	return val.replace(b'\x1a', b'').replace(b'\xc2\x86', b'').replace(b'\xc2\x87', b'').replace(b'\xc2\x8a', b'')


def convertUnicode(val):
	if PY3:
		return val
	else:
		return six.text_type(val, 'utf_8', errors='ignore').encode('utf_8', 'ignore')


def convertDesc(val, encode=True):
	if val is not None:
		if encode is True:
			if PY3:
				return html_escape(val, quote=True).replace(u'\x8a', '\n')
			else:
				return html_escape(six.text_type(val, 'utf_8', errors='ignore').encode('utf_8', 'ignore'), quote=True).replace(u'\x8a', '\n')
		else:
			# remove control chars
			val = removeBadChars(six.ensure_binary(val))
			if PY3:
				return val.decode('utf_8', errors='ignore')
			else:
				return six.text_type(val, 'utf_8', errors='ignore').encode('utf_8', 'ignore')
	return val


def convertGenre(val):
	if val is not None and len(val) > 0:
		val = val[0]
		if len(val) > 1:
			if val[0] > 0:
				gid = val[0] * 16 + val[1]
				return str(getGenreStringLong(val[0], val[1])).strip(), gid
	return "", 0


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
		ref = str(getServiceInfoString(info, iServiceInformation.sServiceref))
		if len(ref) < 10:
			serviceref = session.nav.getCurrentlyPlayingServiceReference()
			if serviceref is not None:
				ref = serviceref.toString()

		ns = getServiceInfoString(info, iServiceInformation.sNamespace)
		try:
			ns = int(ns)
		except ValueError:
			ns = 0

		bqname = ""
		bqref = ""

		try:
			servicelist = InfoBar.instance.servicelist
			epg_bouquet = servicelist and servicelist.getRoot()
			if epg_bouquet:
				bqname = ServiceReference(epg_bouquet).getServiceName()
				bqref = ServiceReference(epg_bouquet).ref.toString()
		except:  # nosec # noqa: E722
			pass

		return {
			"result": True,
			"name": filterName(info.getName()),
			"namespace": 0xffffffff & ns,
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
			"ref": quote(ref, safe=' ~@#$&()*!+=:;,.?/\''),
			"iswidescreen": info.getInfo(iServiceInformation.sAspect) in (3, 4, 7, 8, 0xB, 0xC, 0xF, 0x10),
			"bqref": quote(bqref, safe=' ~@#$&()*!+=:;,.?/\''),
			"bqname": bqname
		}
	except Exception as e:
		print(str(e))
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
			"iswidescreen": False,
			"bqref": "",
			"bqname": ""
		}


def getCurrentFullInfo(session):
	now = next = {}
	inf = getCurrentService(session)
	inf['tuners'] = list(map(chr, list(range(65, 65 + nimmanager.getSlotCount()))))

	try:
		info = session.nav.getCurrentService().info()
	except:  # nosec # noqa: E722
		info = None

	try:
		subservices = session.nav.getCurrentService().subServices()
	except:  # nosec # noqa: E722
		subservices = None

	try:
		audio = session.nav.getCurrentService().audioTracks()
	except:  # nosec # noqa: E722
		audio = None

	try:
		ref = session.nav.getCurrentlyPlayingServiceReference().toString()
	except:  # nosec # noqa: E722
		ref = None

	if ref is not None:
		inf['sref'] = '_'.join(ref.split(':', 10)[:10])
		inf['srefv2'] = ref
		inf['picon'] = getPicon(ref)
		inf['wide'] = inf['aspect'] in (3, 4, 7, 8, 0xB, 0xC, 0xF, 0x10)
		inf['ttext'] = getServiceInfoString(info, iServiceInformation.sTXTPID)
		inf['crypt'] = getServiceInfoString(info, iServiceInformation.sIsCrypted)
		inf['subs'] = str(subservices and subservices.getNumberOfSubservices() > 0)
	else:
		inf['sref'] = None
		inf['picon'] = None
		inf['wide'] = None
		inf['ttext'] = None
		inf['crypt'] = None
		inf['subs'] = None

	inf['date'] = strftime(_("%d.%m.%Y"), (localtime()))
	inf['dolby'] = False

	if audio:
		n = audio.getNumberOfTracks()
		idx = 0
		while idx < n:
			i = audio.getTrackInfo(idx)
			description = i.getDescription()
			if "AC3" in description or "DTS" in description or "Dolby Digital" in description:
				inf['dolby'] = True
			idx += 1
	try:
		feinfo = session.nav.getCurrentService().frontendInfo()
	except:  # nosec # noqa: E722
		feinfo = None

	frontendData = feinfo and feinfo.getAll(True)

	if frontendData is not None:
		cur_info = feinfo.getTransponderData(True)
		inf['tunertype'] = frontendData.get("tuner_type", "UNKNOWN")
		if frontendData.get("system", -1) == 1:
			inf['tunertype'] += "2"
		inf['tunernumber'] = frontendData.get("tuner_number")
		orb = getOrbitalText(cur_info)
		inf['orbital_position'] = orb
		if cur_info:
			if cur_info.get('tuner_type') == "DVB-S":
				inf['orbital_position'] = _("Orbital Position") + ': ' + orb
	else:
		inf['tunernumber'] = "N/A"
		inf['tunertype'] = "N/A"

	try:
		frontendStatus = feinfo and feinfo.getFrontendStatus()
	except:  # nosec # noqa: E722
		frontendStatus = None

	if frontendStatus is not None:
		percent = frontendStatus.get("tuner_signal_quality")
		if percent is not None:
			inf['snr'] = int(percent * 100 / 65535)
			inf['snr_db'] = inf['snr']
		percent = frontendStatus.get("tuner_signal_quality_db")
		if percent is not None:
			inf['snr_db'] = "%3.02f dB" % (percent / 100.0)
		percent = frontendStatus.get("tuner_signal_power")
		if percent is not None:
			inf['agc'] = int(percent * 100 / 65535)
		percent = frontendStatus.get("tuner_bit_error_rate")
		if percent is not None:
			inf['ber'] = int(percent * 100 / 65535)
	else:
		inf['snr'] = 0
		inf['snr_db'] = inf['snr']
		inf['agc'] = 0
		inf['ber'] = 0

	try:
		recordings = session.nav.getRecordings()
	except:  # nosec # noqa: E722
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

	return {"info": inf, "now": now, "next": next}


def getBouquets(stype):
	s_type = service_types_tv
	s_type2 = "bouquets.tv"
	if stype == "radio":
		s_type = service_types_radio
		s_type2 = "bouquets.radio"
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "%s" ORDER BY bouquet' % (s_type, s_type2)))
	bouquets = services and services.getContent("SN", True)
	bouquets = removeHiddenBouquets(bouquets)
	return {"bouquets": bouquets}


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
	services = serviceHandler.list(eServiceReference('%s FROM PROVIDERS ORDER BY name' % (s_type)))
	providers = services and services.getContent("SN", True)
	return {"providers": providers}


def getSatellites(stype):
	ret = []
	s_type = service_types_tv
	if stype == "radio":
		s_type = service_types_radio
	refstr = '%s FROM SATELLITES ORDER BY satellitePosition' % (s_type)
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
				# service_type = _("Providers")
				continue
			elif service.getPath().find("flags == %d" % (FLAG_SERVICE_NEW_FOUND)) != -1:
				service_type = _("New")
			else:
				service_type = _("Services")
			try:
				service_name = str(nimmanager.getSatDescription(orbpos))
			except:  # nosec # noqa: E722
				if unsigned_orbpos == 0xFFFF:  # Cable
					service_name = _("Cable")
				elif unsigned_orbpos == 0xEEEE:  # Terrestrial
					service_name = _("Terrestrial")
				else:
					service_name = getOrb(orbpos)
			service.setName("%s - %s" % (service_name, service_type))
			ret.append({
				"service": service.toString(),
				"name": service.getName()
			})
	ret = sortSatellites(ret)
	return {"satellites": ret}


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
		if orb not in sortDict:
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
				if sref in parentalControl.blacklist:
					if "SERVICE" in parentalControl.blacklist[sref]:
						isProtected = '1'
					elif "BOUQUET" in parentalControl.blacklist[sref]:
						isProtected = '2'
					else:
						isProtected = '3'
			elif config.ParentalControl.type.value == "whitelist":
				if sref not in parentalControl.whitelist:
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
		idbouquet = '%s ORDER BY name' % (s_type)

	epgcache = eEPGCache.getInstance()
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference(idbouquet))
	channels = services and services.getContent("SN", True)
	for channel in channels:
		chan = {}
		chan['ref'] = quote(channel[0], safe=' ~@%#$&()*!+=:;,.?/\'')
		if chan['ref'].split(":")[1] == '320':  # Hide hidden number markers
			continue
		chan['name'] = filterName(channel[1])
		if chan['ref'].split(":")[0] == '5002':  # BAD fix !!! this needs to fix in enigma2 !!!
			chan['name'] = chan['ref'].split(":")[-1]
		# IPTV
		chan['link'] = getIPTVLink(chan['ref'])

		if not int(channel[0].split(":")[1]) & 64:
			psref = parse_servicereference(channel[0])
			chan['service_type'] = SERVICE_TYPE_LOOKUP.get(psref.get('service_type'), "UNKNOWN")
			nsi = psref.get('ns')
			ns = NS_LOOKUP.get(nsi, "DVB-S")
			if ns == "DVB-S":
				chan['ns'] = getOrb(nsi >> 16 & 0xFFF)
			else:
				chan['ns'] = ns
			chan['picon'] = getPicon(chan['ref'])
			if config.OpenWebif.parentalenabled.value and config.ParentalControl.configured.value and config.ParentalControl.servicepinactive.value:
				chan['protection'] = getProtection(channel[0])
			else:
				chan['protection'] = "0"
			nowevent = epgcache.lookupEvent(['TBDCIXS', (channel[0], 0, -1)])
			if len(nowevent) > 0 and nowevent[0][0] is not None:
				chan['now_title'] = filterName(nowevent[0][0])
				chan['now_begin'] = strftime("%H:%M", (localtime(nowevent[0][1])))
				chan['now_end'] = strftime("%H:%M", (localtime(nowevent[0][1] + nowevent[0][2])))
				chan['now_left'] = int(((nowevent[0][1] + nowevent[0][2]) - nowevent[0][3]) / 60)
				chan['progress'] = int(((nowevent[0][3] - nowevent[0][1]) * 100 / nowevent[0][2]))
				chan['now_ev_id'] = nowevent[0][4]
				chan['now_idp'] = "nowd" + str(idp)
				chan['now_shortdesc'] = nowevent[0][5].strip()
				nextevent = epgcache.lookupEvent(['TBDIXS', (channel[0], +1, -1)])
# Some fields have been seen to be missing from the next event...
				if len(nextevent) > 0 and nextevent[0][0] is not None:
					if nextevent[0][1] is None:
						nextevent[0][1] = time()
					if nextevent[0][2] is None:
						nextevent[0][2] = 0
					chan['next_title'] = filterName(nextevent[0][0])
					chan['next_begin'] = strftime("%H:%M", (localtime(nextevent[0][1])))
					chan['next_end'] = strftime("%H:%M", (localtime(nextevent[0][1] + nextevent[0][2])))
					chan['next_duration'] = int(nextevent[0][2] / 60)
					chan['next_ev_id'] = nextevent[0][3]
					chan['next_idp'] = "nextd" + str(idp)
					chan['next_shortdesc'] = nextevent[0][4].strip()
				else:   # Have to fudge one in, as rest of OWI code expects it...
					chan['next_title'] = "<<absent>>"
					chan['next_begin'] = chan['now_end']
					chan['next_end'] = chan['now_end']
					chan['next_duration'] = 0
					chan['next_ev_id'] = chan['now_ev_id']
					chan['next_idp'] = chan['now_idp']
					chan['next_shortdesc'] = ""
				idp += 1
		if int(channel[0].split(":")[1]) != 832:
			ret.append(chan)
	return {"channels": ret}


def getServices(sRef, showAll=True, showHidden=False, pos=0, provider=False, picon=False, noiptv=False):
	services = []
	allproviders = {}

	CalcPos = False

	if sRef == "":
		sRef = '%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet' % (service_types_tv)
		CalcPos = True
	elif ' "bouquets.radio" ' in sRef:
		CalcPos = True
	elif ' "bouquets.tv" ' in sRef:
		CalcPos = True

	if provider:
		s_type = service_types_tv
		if "radio" in sRef:
			s_type = service_types_radio
		pserviceHandler = eServiceCenter.getInstance()
		pservices = pserviceHandler.list(eServiceReference('%s FROM PROVIDERS ORDER BY name' % (s_type)))
		providers = pservices and pservices.getContent("SN", True)

		if provider:
			for provider in providers:
				servicelist = ServiceList(eServiceReference(provider[0]))
				slist = servicelist.getServicesAsList()
				for sitem in slist:
					allproviders[sitem[0]] = provider[1]

	servicelist = ServiceList(eServiceReference(sRef))
	slist = servicelist.getServicesAsList()
	serviceHandler = eServiceCenter.getInstance()

	oPos = 0
	for sitem in slist:
		oldoPos = oPos
		sref = sitem[0]
		if CalcPos and 'userbouquet' in sref:
			serviceslist = serviceHandler.list(eServiceReference(sref))
			sfulllist = serviceslist and serviceslist.getContent("RN", True)
			for citem in sfulllist:
				sref = citem[0].toString()
				hs = (int(sref.split(":")[1]) & 512)
				sp = (sref[:7] == '1:832:D') or (sref[:7] == '1:832:1') or (sref[:6] == '1:320:')
				if not hs or sp:  # 512 is hidden service on sifteam image. Doesn't affect other images
					oPos = oPos + 1
					if not sp and citem[0].flags & eServiceReference.isMarker:
						oPos = oPos - 1
		showiptv = True
		if noiptv:
			if '4097:' in sref or '5002:' in sref or 'http%3a' in sref or 'https%3a' in sref:
				showiptv = False

		st = int(sitem[0].split(":")[1])
		sp = (sitem[0][:7] == '1:832:D') or (sitem[0][:7] == '1:832:1') or (sitem[0][:6] == '1:320:')
		if sp or (not (st & 512) and not (st & 64)):
			pos = pos + 1
		if showiptv and (not st & 512 or showHidden):
			if showAll or st == 0:
				service = {}
				service['pos'] = 0 if (st & 64) else pos
				sr = convertUnicode(sitem[0])
				if CalcPos:
					service['startpos'] = oldoPos
				if picon:
					service['picon'] = getPicon(sr)
				service['servicereference'] = sr
				service['program'] = int(service['servicereference'].split(':')[3], 16)
				service['servicename'] = convertUnicode(sitem[1])
				if provider:
					if sitem[0] in allproviders:
						service['provider'] = allproviders[sitem[0]]
					else:
						service['provider'] = ""
				services.append(service)

	return {"services": services, "pos": pos}


def getAllServices(type, noiptv=False, nolastscanned=False):
	services = []
	if type is None:
		type = "tv"
	bouquets = getBouquets(type)["bouquets"]
	pos = 0
	for bouquet in bouquets:
		if nolastscanned and 'LastScanned' in bouquet[0]:
			continue
		sv = getServices(sRef=bouquet[0], showAll=True, showHidden=False, pos=pos, noiptv=noiptv)
		services.append({
			"servicereference": bouquet[0],
			"servicename": bouquet[1],
			"subservices": sv["services"]
		})
		pos = sv["pos"]

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
		if not int(service.split(":")[1]) & 512:  # 512 is hidden service on sifteam image. Doesn't affect other images
			service2 = {}
			service2['servicereference'] = service
			info = servicecenter.info(eServiceReference(service))
			service2['isplayable'] = info.isPlayable(eServiceReference(service), eServiceReference(sRefPlaying)) > 0
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
			"isplayable": info.isPlayable(eServiceReference(sRef), eServiceReference(sRefPlaying)) > 0
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
			print(subservices.getNumberOfSubservices())
			for i in list(range(subservices.getNumberOfSubservices())):
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

	return {"services": services}


def getEventDesc(ref, idev, encode=True):
	ref = unquote(ref)
	epgcache = eEPGCache.getInstance()
	event = epgcache.lookupEvent(['ESX', (ref, 2, int(idev))])
	if len(event[0][0]) > 1:
		description = convertDesc(event[0][0], encode)
	elif len(event[0][1]) > 1:
		description = convertDesc(event[0][1], encode)
	else:
		description = "No description available"

	return {"description": description}


def getTimerEventStatus(event, eventLookupTable, timers=None):
	# Check if an event has an associated timer. Unfortunately
	# we cannot simply check against timer.eit, because a timer
	# does not necessarily have one belonging to an epg event id.

	#catch ValueError
	startTime = event[eventLookupTable.index('B')]
	endTime = event[eventLookupTable.index('B')] + event[eventLookupTable.index('D')] - 120
	serviceref = event[eventLookupTable.index('R')]
	timerlist = {}
	if not timers:
		timers = NavigationInstance.instance.RecordTimer.timer_list
	for timer in timers:
		if str(timer.service_ref) not in timerlist:
			timerlist[str(timer.service_ref)] = []
		timerlist[str(timer.service_ref)].append(timer)
	if serviceref in timerlist:
		for timer in timerlist[serviceref]:
			timerDetails = {}
			if timer.begin <= startTime and timer.end >= endTime:
				if timer.disabled:
					timerDetails = {
						'isEnabled': 0,
						'basicStatus': 'timer disabled'
					}
				else:
					timerDetails = {
						'isEnabled': 1,
						'isZapOnly': int(timer.justplay),
						'basicStatus': 'timer'
					}
				try:
					timerDetails['isAutoTimer'] = timer.isAutoTimer
				except AttributeError:
					timerDetails['isAutoTimer'] = 0
				return timerDetails

	return None


def getEvent(ref, idev, encode=True):
	epgcache = eEPGCache.getInstance()
	eventLookupTable = 'IBDTSENRWX'
	events = epgcache.lookupEvent([eventLookupTable, (ref, 2, int(idev))]) #IBTSRND
	info = {}
	for event in events:
		info['id'] = event[0]
		info['begin_str'] = strftime("%H:%M", (localtime(event[1])))
		info['begin'] = event[1]
		info['end'] = strftime("%H:%M", (localtime(event[1] + event[2])))
		info['duration'] = event[2]
		info['title'] = filterName(event[3], encode)
		info['shortdesc'] = convertDesc(event[4], encode)
		info['longdesc'] = convertDesc(event[5], encode)
		info['channel'] = filterName(event[6], encode)
		info['sref'] = event[7]
		info['genre'], info['genreid'] = convertGenre(event[8])
		info['picon'] = getPicon(event[7])
		info['timer'] = getTimerEventStatus(event, eventLookupTable, None)
		info['link'] = getIPTVLink(event[7])
		break
	return {'event': info}


def getChannelEpg(ref, begintime=-1, endtime=-1, encode=True):
	ret = []
	ev = {}
	use_empty_ev = False
	if ref:
		ref = unquote(ref)

		# When quering EPG we dont need URL, also getPicon doesn't like URL
		if "://" in ref:
			_ref = ":".join(ref.split(":")[:10]) + "::" + ref.split(":")[-1]
		else:
			_ref = ref

		picon = getPicon(_ref)
		epgcache = eEPGCache.getInstance()
		events = epgcache.lookupEvent(['IBDTSENCW', (_ref, 0, begintime, endtime)])
		if events is not None:
			for event in events:
				ev = {}
				ev['picon'] = picon
				ev['id'] = event[0]
				if event[1]:
					ev['date'] = "%s %s" % (tstrings[("day_" + strftime("%w", (localtime(event[1]))))], strftime(_("%d.%m.%Y"), (localtime(event[1]))))
					ev['begin'] = strftime("%H:%M", (localtime(event[1])))
					ev['begin_timestamp'] = event[1]
					ev['duration'] = int(event[2] / 60)
					ev['duration_sec'] = event[2]
					ev['end'] = strftime("%H:%M", (localtime(event[1] + event[2])))
					ev['title'] = filterName(event[3], encode)
					ev['shortdesc'] = convertDesc(event[4], encode)
					ev['longdesc'] = convertDesc(event[5], encode)
					ev['sref'] = ref
					ev['sname'] = filterName(event[6], encode)
					ev['tleft'] = int(((event[1] + event[2]) - event[7]) / 60)
					if ev['duration_sec'] == 0:
						ev['progress'] = 0
					else:
						ev['progress'] = int(((event[7] - event[1]) * 100 / event[2]) * 4)
					ev['now_timestamp'] = event[7]
					ev['genre'], ev['genreid'] = convertGenre(event[8])
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
		ev['genre'] = ""
		ev['genreid'] = 0
		ret.append(ev)

	return {"events": ret, "result": True}


def getBouquetEpg(ref, begintime=-1, endtime=None, encode=False):
	ref = unquote(ref)
	ret = []
	services = eServiceCenter.getInstance().list(eServiceReference(ref))
	if not services:
		return {"events": ret, "result": False}

	if endtime == None:
		endtime = -1

	# prevent crash
	if endtime > 100000:
		endtime = -1

	search = ['IBDCTSERNW']
	for service in services.getContent('S'):
		search.append((service, 0, begintime, endtime))

	epgcache = eEPGCache.getInstance()
	events = epgcache.lookupEvent(search)
	if events is not None:
		for event in events:
			ev = {}
			ev['id'] = event[0]
			ev['begin_timestamp'] = event[1]
			ev['duration_sec'] = event[2]
			ev['title'] = filterName(event[4], encode)
			ev['shortdesc'] = convertDesc(event[5], encode)
			ev['longdesc'] = convertDesc(event[6], encode)
			ev['sref'] = event[7]
			ev['sname'] = filterName(event[8], encode)
			ev['now_timestamp'] = event[3]
			ev['genre'], ev['genreid'] = convertGenre(event[9])
			ret.append(ev)

	return {"events": ret, "result": True}


def getServicesNowNextEpg(sList, encode=False):
	ret = []
	if not sList:
		return {"events": ret, "result": False}

	sRefList = sList.split(",")
	search = ['IBDCTSERNX']
	for service in sRefList:
		search.append((service, 0, -1))
		search.append((service, 1, -1))

	epgcache = eEPGCache.getInstance()
	events = epgcache.lookupEvent(search)
	if events is not None:
		for event in events:
			ev = {}
			ev['id'] = event[0]
			ev['begin_timestamp'] = event[1]
			ev['duration_sec'] = event[2]
			ev['title'] = filterName(event[4], encode)
			ev['shortdesc'] = convertDesc(event[5], encode)
			ev['longdesc'] = convertDesc(event[6], encode)
			# if event[7] is not None:
			#  achannels = GetWithAlternative(event[7], False)
			#   if achannels:
			#    ev['asrefs'] = achannels
			ev['sref'] = event[7]
			ev['sname'] = filterName(event[8], encode)
			ev['now_timestamp'] = event[3]
			ret.append(ev)

	return {"events": ret, "result": True}


def getBouquetNowNextEpg(ref, servicetype, encode=False):
	ref = unquote(ref)
	ret = []
	services = eServiceCenter.getInstance().list(eServiceReference(ref))
	if not services:
		return {"events": ret, "result": False}

	search = ['IBDCTSERNWX']
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
			ev['title'] = filterName(event[4], encode)
			ev['shortdesc'] = convertDesc(event[5], encode)
			ev['longdesc'] = convertDesc(event[6], encode)
			if event[7] is not None:
				achannels = GetWithAlternative(event[7], False)
				if achannels:
					ev['asrefs'] = achannels
			ev['sref'] = event[7]
			ev['sname'] = filterName(event[8], encode)
			ev['now_timestamp'] = event[3]
			ev['genre'], ev['genreid'] = convertGenre(event[9])
			ret.append(ev)

	return {"events": ret, "result": True}


def getNowNextEpg(ref, servicetype, encode=False):
	ref = unquote(ref)
	ret = []
	epgcache = eEPGCache.getInstance()
	events = epgcache.lookupEvent(['IBDCTSERNWX', (ref, servicetype, -1)])
	if events is not None:
		for event in events:
			ev = {}
			ev['id'] = event[0]
			if event[1]:
				ev['begin_timestamp'] = event[1]
				ev['duration_sec'] = event[2]
				ev['title'] = filterName(event[4], encode)
				ev['shortdesc'] = convertDesc(event[5], encode)
				ev['longdesc'] = convertDesc(event[6], encode)
				ev['sref'] = event[7]
				ev['sname'] = filterName(event[8], encode)
				ev['now_timestamp'] = event[3]
				ev['remaining'] = (event[1] + event[2]) - event[3]
				ev['genre'], ev['genreid'] = convertGenre(event[9])
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
				ev['genre'] = ""
				ev['genreid'] = 0

			ret.append(ev)

	return {"events": ret, "result": True}


def getSearchEpg(sstr, endtime=None, fulldesc=False, bouquetsonly=False, encode=False):
	ret = []
	ev = {}
	if config.OpenWebif.epg_encoding.value != 'utf-8':
		try:
			sstr = sstr.encode(config.OpenWebif.epg_encoding.value)
		except UnicodeEncodeError:
			pass
	epgcache = eEPGCache.getInstance()
	search_type = eEPGCache.PARTIAL_TITLE_SEARCH
	if fulldesc:
		if hasattr(eEPGCache, 'FULL_DESCRIPTION_SEARCH'):
			search_type = eEPGCache.FULL_DESCRIPTION_SEARCH
		elif hasattr(eEPGCache, 'PARTIAL_DESCRIPTION_SEARCH'):
			search_type = eEPGCache.PARTIAL_DESCRIPTION_SEARCH
	events = epgcache.search(('IBDTSENRW', 128, search_type, sstr, 1))
	if events is not None:
		# TODO : discuss #677
		# events.sort(key = lambda x: (x[1],x[6])) # sort by date,sname
		# events.sort(key = lambda x: x[1]) # sort by date
		if bouquetsonly:
			# collect service references from TV bouquets
			bsref = {}
			for service in getAllServices('tv')['services']:
				for service2 in service['subservices']:
					bsref[service2['servicereference']] = True
				else:
					bsref[service['servicereference']] = True

		for event in events:
			if bouquetsonly and not event[7] in bsref:
				continue
			ev = {}
			ev['id'] = event[0]
			ev['date'] = "%s %s" % (tstrings[("day_" + strftime("%w", (localtime(event[1]))))], strftime(_("%d.%m.%Y"), (localtime(event[1]))))
			ev['begin_timestamp'] = event[1]
			ev['begin'] = strftime("%H:%M", (localtime(event[1])))
			ev['duration_sec'] = event[2]
			ev['duration'] = int(event[2] / 60)
			ev['end'] = strftime("%H:%M", (localtime(event[1] + event[2])))
			ev['title'] = filterName(event[3], encode)
			ev['shortdesc'] = convertDesc(event[4], encode)
			ev['longdesc'] = convertDesc(event[5], encode)
			ev['sref'] = event[7]
			ev['sname'] = filterName(event[6], encode)
			ev['picon'] = getPicon(event[7])
			ev['now_timestamp'] = None
			ev['genre'], ev['genreid'] = convertGenre(event[8])
			if endtime:
				# don't show events if begin after endtime
				if event[1] <= endtime:
					ret.append(ev)
			else:
				ret.append(ev)

			psref = parse_servicereference(event[7])
			ev['service_type'] = SERVICE_TYPE_LOOKUP.get(psref.get('service_type'), "UNKNOWN")
			nsi = psref.get('ns')
			ns = NS_LOOKUP.get(nsi, "DVB-S")
			if ns == "DVB-S":
				ev['ns'] = getOrb(nsi >> 16 & 0xFFF)
			else:
				ev['ns'] = ns

	return {"events": ret, "result": True}


def getSearchSimilarEpg(ref, eventid, encode=False):
	ref = unquote(ref)
	ret = []
	ev = {}
	epgcache = eEPGCache.getInstance()
	events = epgcache.search(('IBDTSENRW', 128, eEPGCache.SIMILAR_BROADCASTINGS_SEARCH, ref, eventid))
	if events is not None:
		# TODO : discuss #677
		# events.sort(key = lambda x: (x[1],x[6])) # sort by date,sname
		# events.sort(key = lambda x: x[1]) # sort by date
		for event in events:
			ev = {}
			ev['id'] = event[0]
			ev['date'] = "%s %s" % (tstrings[("day_" + strftime("%w", (localtime(event[1]))))], strftime(_("%d.%m.%Y"), (localtime(event[1]))))
			ev['begin_timestamp'] = event[1]
			ev['begin'] = strftime("%H:%M", (localtime(event[1])))
			ev['duration_sec'] = event[2]
			ev['duration'] = int(event[2] / 60)
			ev['end'] = strftime("%H:%M", (localtime(event[1] + event[2])))
			ev['title'] = filterName(event[3], encode)
			ev['shortdesc'] = convertDesc(event[4], encode)
			ev['longdesc'] = convertDesc(event[5], encode)
			ev['sref'] = event[7]
			ev['sname'] = filterName(event[6], encode)
			ev['picon'] = getPicon(event[7])
			ev['now_timestamp'] = None
			ev['genre'], ev['genreid'] = convertGenre(event[8])
			ret.append(ev)

	return {"events": ret, "result": True}


def getMultiEpg(self, ref, begintime=-1, endtime=None, Mode=1):
	# Check if an event has an associated timer. Unfortunately
	# we cannot simply check against timer.eit, because a timer
	# does not necessarily have one belonging to an epg event id.
	def getTimerEventStatus(event, eventLookupTable):
		startTime = event[eventLookupTable.index('B')]
		endTime = event[eventLookupTable.index('B')] + event[eventLookupTable.index('D')] - 120
		serviceref = event[eventLookupTable.index('R')]
		if serviceref not in timerlist:
			return None
		for timer in timerlist[serviceref]:
			if timer.begin <= startTime and timer.end >= endTime:
				basicStatus = 'timer'
				isEnabled = 1
				isAutoTimer = -1
				if hasattr(timer, "isAutoTimer"):
					isAutoTimer = timer.isAutoTimer
				if timer.disabled:
					basicStatus = 'timer disabled'
					isEnabled = 0
				timerDetails = {
						'isEnabled': isEnabled,
						'isZapOnly': int(timer.justplay),
						'basicStatus': basicStatus,
						'isAutoTimer': isAutoTimer
					}
				return timerDetails

		return None
	ret = OrderedDict()
	services = eServiceCenter.getInstance().list(eServiceReference(ref))
	if not services:
		return {"events": ret, "result": False, "slot": None}

	eventLookupTable = 'IBTSRND'
	search = [eventLookupTable]
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
		timers = self.session.nav.RecordTimer.timer_list + self.session.nav.RecordTimer.processed_timers
		for timer in timers:
			if str(timer.service_ref) not in timerlist:
				timerlist[str(timer.service_ref)] = []
			timerlist[str(timer.service_ref)].append(timer)

		if begintime == -1:
			# If no start time is requested, use current time as start time and extend
			# show all events until 6:00 next day
			bt = localtime()
			offset = mktime((bt.tm_year, bt.tm_mon, bt.tm_mday, bt.tm_hour - bt.tm_hour % 2, 0, 0, -1, -1, -1))
			lastevent = mktime((bt.tm_year, bt.tm_mon, bt.tm_mday, 23, 59, 0, -1, -1, -1)) + 6 * 3600
		else:
			# If a start time is requested, show all events in a 24 hour frame
			bt = localtime(begintime)
			offset = mktime((bt.tm_year, bt.tm_mon, bt.tm_mday, bt.tm_hour - bt.tm_hour % 2, 0, 0, -1, -1, -1))
			lastevent = offset + 86399

		for event in events:
			timer = getTimerEventStatus(event, eventLookupTable)
			# timerStatus is kept for backwards compatibility
			basicStatus = ''
			if timer:
				basicStatus = timer['basicStatus']

			ev = {}
			ev['id'] = event[0]
			ev['begin_timestamp'] = event[1]
			ev['title'] = event[2]
			ev['shortdesc'] = convertDesc(event[3])
			ev['ref'] = event[4]
			ev['timerStatus'] = basicStatus
			ev['timer'] = timer
			if Mode == 2:
				ev['duration'] = event[6]

			channel = filterName(event[5])
			if channel not in ret:
				if Mode == 1:
					ret[channel] = [[], [], [], [], [], [], [], [], [], [], [], []]
				else:
					ret[channel] = [[]]
				picons[channel] = getPicon(event[4])

			if Mode == 1:
				slot = int((event[1] - offset) / 7200)
				if slot < 0:
					slot = 0
				if slot < 12 and event[1] < lastevent:
					ret[channel][slot].append(ev)
			else:
				ret[channel][0].append(ev)
	return {"events": ret, "result": True, "picons": picons}


def getPicon(sname, pp=None, defaultpicon=True):

	if pp is None:
		pp = PICON_PATH
	if pp is not None:
		# remove URL part
		if ("://" in sname) or ("%3a//" in sname) or ("%3A//" in sname):
			cname = unquote(sname.split(":")[-1])
			sname = unquote(sname)
			# sname = ":".join(sname.split(":")[:10]) -> old way
			sname = ":".join(sname.split("://")[:1])
			sname = GetWithAlternative(sname)
			if PY3:
				cname = unicodedata.normalize('NFKD', cname)
			else:
				cname = unicodedata.normalize('NFKD', six.text_type(cname, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
			cname = re.sub('[^a-z0-9]', '', cname.replace('&', 'and').replace('+', 'plus').replace('*', 'star').replace(':', '').lower())
			# picon by channel name for URL
			if len(cname) > 0 and fileExists(pp + cname + ".png"):
				return "/picon/" + cname + ".png"
			if len(cname) > 2 and cname.endswith('hd') and fileExists(pp + cname[:-2] + ".png"):
				return "/picon/" + cname[:-2] + ".png"
			if len(cname) > 5:
				series = re.sub(r's[0-9]*e[0-9]*$', '', cname)
				if fileExists(pp + series + ".png"):
					return "/picon/" + series + ".png"

		sname = GetWithAlternative(sname)
		if sname is not None:
			pos = sname.rfind(':')
		else:
			return "/images/default_picon.png"
		cname = None
		if pos != -1:
			cname = ServiceReference(sname[:pos].rstrip(':')).getServiceName()
			sname = sname[:pos].rstrip(':').replace(':', '_') + ".png"
		filename = pp + sname
		if fileExists(filename):
			return "/picon/" + sname
		fields = sname.split('_', 8)
		if len(fields) > 7 and not fields[6].endswith("0000"):
			# remove "sub-network" from namespace
			fields[6] = fields[6][:-4] + "0000"
			sname = '_'.join(fields)
			filename = pp + sname
			if fileExists(filename):
				return "/picon/" + sname
		if len(fields) > 1 and fields[0] != '1':
			# fallback to 1 for other reftypes
			fields[0] = '1'
			sname = '_'.join(fields)
			filename = pp + sname
			if fileExists(filename):
				return "/picon/" + sname
		if len(fields) > 3 and fields[2] != '1':
			# fallback to 1 for tv services with nonstandard servicetypes
			fields[2] = '1'
			sname = '_'.join(fields)
			filename = pp + sname
			if fileExists(filename):
				return "/picon/" + sname
		if cname is not None:  # picon by channel name
			cname1 = filterName(cname).replace('/', '_')
			if not PY3:
				cname1 = cname1.encode('utf-8', 'ignore')

			if fileExists(pp + cname1 + ".png"):
				return "/picon/" + cname1 + ".png"
			if PY3:
				cname = unicodedata.normalize('NFKD', cname)
			else:
				cname = unicodedata.normalize('NFKD', six.text_type(cname, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
			cname = re.sub('[^a-z0-9]', '', cname.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())
			if len(cname) > 0:
				filename = pp + cname + ".png"
			if fileExists(filename):
				return "/picon/" + cname + ".png"
			if len(cname) > 2 and cname.endswith('hd') and fileExists(pp + cname[:-2] + ".png"):
				return "/picon/" + cname[:-2] + ".png"
	if defaultpicon:
		return "/images/default_picon.png"
	else:
		return None


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


def getServiceRef(name, searchinBouquetsOnly=False, bRef=None):
	# TODO Radio
	# TODO bRef

	sfulllist = []
	serviceHandler = eServiceCenter.getInstance()
	if searchinBouquetsOnly:
		s_type = service_types_tv
		s_type2 = "bouquets.tv"
	#		if stype == "radio":
	#			s_type = service_types_radio
	#			s_type2 = "bouquets.radio"
		if bRef is None:
			services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "%s" ORDER BY bouquet' % (s_type, s_type2)))
			bouquets = services and services.getContent("SN", True)
			bouquets = removeHiddenBouquets(bouquets)

		for bouquet in bouquets:
			serviceslist = serviceHandler.list(eServiceReference(bouquet[0]))
			sfulllist = serviceslist and serviceslist.getContent("SN", True)
			for sv in sfulllist:
				if sv[1] == name:
					return {
						"result": True,
						"sRef": sv[0]
					}

	else:
		refstr = '%s ORDER BY name' % (service_types_tv)
		serviceslist = serviceHandler.list(eServiceReference(refstr))
		sfulllist = serviceslist and serviceslist.getContent("SN", True)
		for sv in sfulllist:
			if sv[1] == name:
				return {
					"result": True,
					"sRef": sv[0]
				}

	return {
		"result": True,
		"sRef": ""
	}
