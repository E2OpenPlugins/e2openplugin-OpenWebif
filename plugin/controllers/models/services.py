# -*- coding: utf-8 -*-

##########################################################################
# OpenWebif: services
##########################################################################
# Copyright (C) 2011 - 2022 E2OpenPlugins
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

from datetime import datetime
import re
import six
from six.moves.urllib.parse import quote, unquote
from time import time, localtime, strftime, mktime
from unicodedata import normalize
from enigma import eServiceCenter, eServiceReference, iServiceInformation

from Components.ParentalControl import parentalControl
from Components.config import config
from Components.NimManager import nimmanager
import NavigationInstance
from ServiceReference import ServiceReference
from Screens.ChannelSelection import service_types_tv, service_types_radio, FLAG_SERVICE_NEW_FOUND
from Screens.InfoBar import InfoBar
from Tools.Directories import fileExists

from Plugins.Extensions.OpenWebif.controllers.models.info import GetWithAlternative, getOrbitalText, getOrb
from Plugins.Extensions.OpenWebif.controllers.utilities import parse_servicereference, SERVICE_TYPE_LOOKUP, NS_LOOKUP, PY3
from Plugins.Extensions.OpenWebif.controllers.i18n import _, tstrings
from Plugins.Extensions.OpenWebif.controllers.defaults import PICON_PATH
from Plugins.Extensions.OpenWebif.controllers.epg import EPG

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
	inf['audio_desc'] = ""
	inf['audio_lang'] = ""

	if audio:
		# n = audio.getNumberOfTracks()
		# idx = 0
		# while idx < n:
		# 	i = audio.getTrackInfo(idx)
		# 	description = i.getDescription()
		# 	inf['audio'] = inf['audio'] + description + i.getLanguage() + "["+audio.getTrackInfo(audio.getCurrentTrack()).getLanguage()+"]"
		# 	if "AC3" in description or "DTS" in description or "Dolby Digital" in description:
		# 		inf['dolby'] = True
		# 	idx += 1
		audio_info = audio.getTrackInfo(audio.getCurrentTrack())
		description = audio_info.getDescription()
		if description in ["AC3", "DTS", "Dolby Digital"]:
			inf['dolby'] = True
		inf['audio_desc'] = audio_info.getDescription()
		inf['audio_lang'] = audio_info.getLanguage()

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
		# if cur_info:
		# 	if cur_info.get('tuner_type') == "DVB-S":
		# 		inf['orbital_position'] = _("Orbital Position") + ': ' + orb
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
						isProtected = '5'
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

	epg = EPG()
	serviceHandler = eServiceCenter.getInstance()
	services = serviceHandler.list(eServiceReference(idbouquet))
	channels = services and services.getContent("SN", True)
	epgNowNextEvents = epg.getMultiChannelNowNextEvents([item[0] for item in channels])
	index = -2

	for channel in channels:
		index = index + 2  # each channel has a `now` and a `next` event entry
		chan = {
			'ref': quote(channel[0], safe=' ~@%#$&()*!+=:;,.?/\'')
		}

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

			nowevent = [epgNowNextEvents[index]][0]

			if nowevent.eventId:
				chan['now_title'] = filterName(nowevent.title)
				chan['now_begin'] = nowevent.start['time']
				chan['now_end'] = nowevent.end['time']
				chan['now_left'] = nowevent.remaining['minutes']
				chan['progress'] = nowevent.progress['number']
				chan['now_ev_id'] = nowevent.eventId
				chan['now_idp'] = "nowd" + str(idp)
				chan['now_shortdesc'] = nowevent.shortDescription
				chan['now_extdesc'] = nowevent.longDescription
				nextevent = [epgNowNextEvents[index + 1]][0]

# Some fields have been seen to be missing from the next event...
				if nextevent.eventId:
					if nextevent.start['time'] is None:
						nextevent.start['time'] = time()

					if nextevent.duration['minutes'] is None:
						nextevent.duration['minutes'] = 0
					chan['next_title'] = nextevent.title
					chan['next_begin'] = nextevent.start['time']
					chan['next_end'] = nextevent.end['time']
					chan['next_duration'] = nextevent.duration['minutes']
					chan['next_ev_id'] = nextevent.eventId
					chan['next_idp'] = "nextd" + str(idp)
					chan['next_shortdesc'] = nextevent.shortDescription
					chan['next_extdesc'] = nextevent.longDescription
				else:   # Have to fudge one in, as rest of OWI code expects it...
					# TODO: investigate use of X to stuff an empty entry
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


def getServices(sRef, showAll=True, showHidden=False, pos=0, showProviders=False, picon=False, noiptv=False, removeNameFromsref=False):
	starttime = datetime.now()
	services = []
	allproviders = {}
	CalcPos = False
	serviceHandler = eServiceCenter.getInstance()

	if not sRef:
		sRef = '%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet' % (service_types_tv)
		CalcPos = True
	elif ' "bouquets.radio" ' in sRef:
		CalcPos = True
	elif ' "bouquets.tv" ' in sRef:
		CalcPos = True

	if showProviders:
		s_type = service_types_tv
		if "radio" in sRef:
			s_type = service_types_radio
		pservices = serviceHandler.list(eServiceReference('%s FROM PROVIDERS ORDER BY name' % (s_type)))
		providers = pservices and pservices.getContent("SN", True)

		for provider in providers:
			pservices = serviceHandler.list(eServiceReference(provider[0]))
			slist = pservices and pservices.getContent("CN" if removeNameFromsref else "SN", True)
			for sitem in slist:
				allproviders[sitem[0]] = provider[1]

	bqservices = serviceHandler.list(eServiceReference(sRef))
	slist = bqservices and bqservices.getContent("CN" if removeNameFromsref else "SN", True)

	oPos = 0
	for sitem in slist:
		oldoPos = oPos
		sref = sitem[0]
		if CalcPos and 'userbouquet' in sref:
			serviceslist = serviceHandler.list(eServiceReference(sref))
			sfulllist = serviceslist and serviceslist.getContent("C", True)
			for sref in sfulllist:
				flags = int(sref.split(":")[1])
				hs = flags & 512  # eServiceReference.isInvisible
				sp = flags & 256  # eServiceReference.isNumberedMarker
				#sp = (sref[:7] == '1:832:D') or (sref[:7] == '1:832:1') or (sref[:6] == '1:320:')
				if not hs or sp:  # 512 is hidden service on sifteam image. Doesn't affect other images
					oPos = oPos + 1
					if not sp and flags & 64:  # eServiceReference.isMarker:
						oPos = oPos - 1
		showiptv = True
		if noiptv:
			if '4097:' in sref or '5002:' in sref or 'http%3a' in sref or 'https%3a' in sref:
				showiptv = False

		flags = int(sitem[0].split(":")[1])
		sp = flags & 256  # (sitem[0][:7] == '1:832:D') or (sitem[0][:7] == '1:832:1') or (sitem[0][:6] == '1:320:')
		if sp or (not (flags & 512) and not (flags & 64)):
			pos = pos + 1
		if showiptv and (not flags & 512 or showHidden):
			if showAll or flags == 0:
				service = {}
				service['pos'] = 0 if (flags & 64) else pos
				sr = convertUnicode(sitem[0])
				if CalcPos:
					service['startpos'] = oldoPos
				if picon:
					service['picon'] = getPicon(sr)
				service['servicename'] = convertUnicode(sitem[1])
				service['servicereference'] = sr
				service['program'] = int(service['servicereference'].split(':')[3], 16)
				if showProviders:
					if sitem[0] in allproviders:
						service['provider'] = allproviders[sitem[0]]
					else:
						service['provider'] = ""
				services.append(service)

	timeelapsed = datetime.now() - starttime
	return {
		"result": True,
		"processingtime": "{}".format(timeelapsed),
		"pos": pos,
		"services": services
	}


def getAllServices(type, noiptv=False, nolastscanned=False, removeNameFromsref=False, showAll=True, showProviders=False):
	starttime = datetime.now()
	services = []
	if type is None:
		type = "tv"
	bouquets = getBouquets(type)["bouquets"]
	pos = 0
	for bouquet in bouquets:
		if nolastscanned and 'LastScanned' in bouquet[0]:
			continue
		sv = getServices(sRef=bouquet[0], showAll=showAll, showHidden=False, pos=pos, showProviders=showProviders, noiptv=noiptv, removeNameFromsref=removeNameFromsref)
		services.append({
			"servicereference": bouquet[0],
			"servicename": bouquet[1],
			"subservices": sv["services"]
		})
		pos = sv["pos"]

	timeelapsed = datetime.now() - starttime

	return {
		"result": True,
		"processingtime": "{}".format(timeelapsed),
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
			# print(subservices.getNumberOfSubservices())

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
	epg = EPG()
	description = epg.getEventDescription(ref, idev)
	# 'ESX'
	description = description and convertDesc(description, encode) or "No description available"  # TODO: translate #TODO: move to epy.py?

	return {"description": description}


def getTimerEventStatus(epgEvent, sRef, timers=None):
	# Check if an epgEvent has an associated timer. Unfortunately
	# we cannot simply check against timer.eit, because a timer
	# does not necessarily have one belonging to an epg event id.

	#catch ValueError
	startTime = epgEvent.start['timestamp']
	endTime = epgEvent.end['timestamp'] - 120  # TODO: find out what this 120 means
	timerlist = {}
	if not timers:
		timers = NavigationInstance.instance.RecordTimer.timer_list
	for timer in timers:
		if str(timer.service_ref) not in timerlist:
			timerlist[str(timer.service_ref)] = []
		timerlist[str(timer.service_ref)].append(timer)
	if sRef in timerlist:
		for timer in timerlist[sRef]:
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


def getEvent(sRef, eventId, encode=True):
	epg = EPG()
	epgEvent = epg.getEvent(sRef, eventId)

	info = {}

	if epgEvent:
		info['id'] = epgEvent.eventId
		info['begin_str'] = epgEvent.start['time']
		info['begin'] = epgEvent.start['timestamp']
		info['end'] = epgEvent.end['time']
		info['duration'] = epgEvent.duration['seconds']
		info['title'] = filterName(epgEvent.title, encode)
		info['shortdesc'] = convertDesc(epgEvent.shortDescription, encode)
		info['longdesc'] = convertDesc(epgEvent.longDescription, encode)
		info['channel'] = filterName(epgEvent.service['name'], encode)
		info['sref'] = epgEvent.service['sRef']
		info['genre'] = epgEvent.genre
		info['genreId'] = epgEvent.genreId
		info['picon'] = getPicon(sRef)
		info['timer'] = getTimerEventStatus(epgEvent, sRef, None)
		info['link'] = getIPTVLink(sRef)
		return {'event': info}
	else:
		return None


def getChannelEpg(ref, begintime=-1, endtime=-1, encode=True, eventId=None):
	ret = []
	ev = {}
	use_empty_ev = False
	if ref:
		ref = unquote(ref)

		# When querying EPG, we don't need URL; also getPicon doesn't like URL
		if "://" in ref:
			_ref = ":".join(ref.split(":")[:10]) + "::" + ref.split(":")[-1]
		else:
			_ref = ref

		picon = getPicon(_ref)
		epg = EPG()

		if eventId is not None:
			epgEvents = epg.findSimilarEvents(ref, eventId)
		else:
			epgEvents = epg.getChannelEvents(ref, begintime, endtime)

		if epgEvents is not None:
			for epgEvent in epgEvents:
				eventId = epgEvent.eventId
				ev = {
					'id': eventId,
					'sref': ref,
					'picon': picon
				}

				if eventId:
					ev['date'] = epgEvent.start['date']
					ev['begin'] = epgEvent.start['time']
					ev['begin_timestamp'] = epgEvent.start['timestamp']
					ev['duration'] = epgEvent.duration['minutes']
					ev['duration_sec'] = epgEvent.duration['seconds']
					ev['end'] = epgEvent.end['time']
					ev['title'] = filterName(epgEvent.title, encode)
					ev['shortdesc'] = convertDesc(epgEvent.shortDescription, encode)
					ev['longdesc'] = convertDesc(epgEvent.longDescription, encode)
					ev['sname'] = filterName(epgEvent.service['name'], encode)
					ev['now_timestamp'] = 0
					ev['genre'] = epgEvent.genre
					ev['genreid'] = epgEvent.genreId
					if eventId is None:
						ev['tleft'] = epgEvent.remaining['minutes']
						ev['progress'] = epgEvent.progress['number']
					ret.append(ev)
				else:
					use_empty_ev = True
	else:
		use_empty_ev = True
		ev['sref'] = ""

	# TODO: investigate use of X to stuff an empty entry
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


def getSimilarEpg(sRef, eventId, encode=False):
	return getChannelEpg(sRef, None, None, encode, eventId)


def getBouquetEpg(bqRef, begintime=-1, endtime=-1, encode=False):
	bqRef = unquote(bqRef)
	epg = EPG()
	epgEvents = epg.getBouquetEvents(bqRef, begintime, endtime)
	ret = []

	if epgEvents is not None:
		for epgEvent in epgEvents:
			ev = {
				'id': epgEvent.eventId,
				'begin_timestamp': epgEvent.start['timestamp'],
				'duration_sec': epgEvent.duration['seconds'],
				'title': filterName(epgEvent.title, encode),
				'shortdesc': convertDesc(epgEvent.shortDescription, encode),
				'longdesc': convertDesc(epgEvent.longDescription, encode),
				'sref': epgEvent.service['sRef'],
				'sname': filterName(epgEvent.service['name'], encode),
				'now_timestamp': epgEvent.currentTimestamp,
				'genre': epgEvent.genre,
				'genreid': epgEvent.genreId
			}
			ret.append(ev)

	return {"events": ret, "result": True}


def getMultiChannelNowNextEpg(sList, encode=False):
	ret = []
	if not sList:
		return {"events": ret, "result": False}

	if not isinstance(sList, list):
		sList = sList.split(",")

	epg = EPG()
	epgEvents = epg.getMultiChannelNowNextEvents(sList)

	if epgEvents is not None:
		for epgEvent in epgEvents:
			ev = {}
			ev['id'] = epgEvent[0]
			ev['begin_timestamp'] = epgEvent[1]
			ev['duration_sec'] = epgEvent[2]
			ev['title'] = filterName(epgEvent[4], encode)
			ev['shortdesc'] = convertDesc(epgEvent[5], encode)
			ev['longdesc'] = convertDesc(epgEvent[6], encode)
			# if event[7] is not None:
			#  achannels = GetWithAlternative(event[7], False)
			#   if achannels:
			#    ev['asrefs'] = achannels
			ev['sref'] = epgEvent[7]
			ev['sname'] = filterName(epgEvent[8], encode)
			ev['now_timestamp'] = epgEvent[3]
			ret.append(ev)

	return {"events": ret, "result": True}


def getBouquetNowNextEpg(bqRef, nowOrNext, encode=False):
	bqRef = unquote(bqRef)
	epg = EPG()
	ret = []

	if nowOrNext == EPG.NOW:
		epgEvents = epg.getBouquetNowEvents(bqRef)
	elif nowOrNext == EPG.NEXT:
		epgEvents = epg.getBouquetNextEvents(bqRef)
	else:
		epgEvents = epg.getBouquetNowNextEvents(bqRef)

	if epgEvents is not None:
		for epgEvent in epgEvents:
			eventId = epgEvent.eventId

			if not eventId:
				continue

			serviceReference = epgEvent.service['sRef']
			serviceName = filterName(epgEvent.service['name'], encode)
			ev = {
				'id': eventId,
				'begin_timestamp': epgEvent.start['timestamp'],
				'duration_sec': epgEvent.duration['seconds'],
				'title': filterName(epgEvent.title, encode),
				'shortdesc': convertDesc(epgEvent.shortDescription, encode),
				'longdesc': convertDesc(epgEvent.longDescription, encode),
				'sref': serviceReference,
				'sname': filterName(serviceName, encode),
				'now_timestamp': epgEvent.currentTimestamp,
				'genre': epgEvent.genre,
				'genreid': epgEvent.genreId
			}

			if serviceReference:
				achannels = GetWithAlternative(serviceReference, False)

				if achannels:
					ev['asrefs'] = achannels

			ret.append(ev)

	return {"events": ret, "result": True}


def convertEvent(event, encode):
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
	return ev


def convertEventEncoded(*event):
	return convertEvent(event, True)


def convertEventNonEncoded(*event):
	return convertEvent(event, False)


def getNowNextEpg(sRef, nowOrNext, encode=False):
	sRef = unquote(sRef)
	epg = EPG()
	convertFunc = convertEventEncoded if encode else convertEventNonEncoded
	nn = 0 if nowOrNext == EPG.NOW else 1
	events = epg._instance.lookupEvent(['IBDCTSERNWX', (sRef, nn, -1)], convertFunc)
	return {"events": events, "result": True}


# TODO: add sort options
def getSearchEpg(sstr, endtime=None, fulldesc=False, bouquetsonly=False, encode=False):
	ret = []
	epg = EPG()
	epgEvents = epg.search(sstr, fulldesc)

	if epgEvents is not None:
		# TODO : discuss #677
		# events.sort(key = lambda x: (x[1],x[6])) # sort by date,sname
		# events.sort(key = lambda x: x[1]) # sort by date
		if bouquetsonly:
			# collect service references from TV bouquets
			bsref = {}
			for service in getAllServices('tv', removeNameFromsref=True, showAll=False, nolastscanned=True)['services']:
				for service2 in service['subservices']:
					bsref[service2['servicereference']] = True
				else:
					bsref[service['servicereference']] = True

		for epgEvent in epgEvents:
			if bouquetsonly and not epgEvent[7] in bsref:
				continue
			ev = {}
			ev['id'] = epgEvent[0]
			ev['date'] = "%s %s" % (tstrings[("day_" + strftime("%w", (localtime(epgEvent[1]))))], strftime(_("%d.%m.%Y"), (localtime(epgEvent[1]))))
			ev['begin_timestamp'] = epgEvent[1]
			ev['begin'] = strftime("%H:%M", (localtime(epgEvent[1])))
			ev['duration_sec'] = epgEvent[2]
			ev['duration'] = int(epgEvent[2] / 60)
			ev['end'] = strftime("%H:%M", (localtime(epgEvent[1] + epgEvent[2])))
			ev['title'] = filterName(epgEvent[3], encode)
			ev['shortdesc'] = convertDesc(epgEvent[4], encode)
			ev['longdesc'] = convertDesc(epgEvent[5], encode)
			ev['sref'] = epgEvent[7]
			ev['sname'] = filterName(epgEvent[6], encode)
			ev['picon'] = getPicon(epgEvent[7])
			ev['now_timestamp'] = None
			ev['genre'], ev['genreid'] = convertGenre(epgEvent[8])

			if endtime:
				# don't show events if begin after endtime
				if epgEvent[1] <= endtime:
					ret.append(ev)
			else:
				ret.append(ev)

			psref = parse_servicereference(epgEvent[7])
			ev['service_type'] = SERVICE_TYPE_LOOKUP.get(psref.get('service_type'), "UNKNOWN")
			nsi = psref.get('ns')
			ns = NS_LOOKUP.get(nsi, "DVB-S")
			if ns == "DVB-S":
				ev['ns'] = getOrb(nsi >> 16 & 0xFFF)
			else:
				ev['ns'] = ns

	return {"events": ret, "result": True}


def getMultiEpg(self, ref, begintime=-1, endtime=None, Mode=1):
	# Fill out details for a timer matching an event
	def getTimerDetails(timer):
		basicStatus = 'timer'
		isEnabled = 1
		isAutoTimer = -1
		if hasattr(timer, "isAutoTimer"):
			isAutoTimer = timer.isAutoTimer
		if timer.disabled:
			basicStatus = 'timer disabled'
			isEnabled = 0
		txt = "REC" if timer.justplay == 0 else "ZAP"
		if timer.justplay == 1 and timer.always_zap == 1:
			txt = "R+Z"
		if isAutoTimer == 1:
			txt = "AT"
		if hasattr(timer, "ice_timer_id"):
			if timer.ice_timer_id:
				txt = "Ice"
		timerDetails = {
				'isEnabled': isEnabled,
				'isZapOnly': int(timer.justplay),
				'basicStatus': basicStatus,
				'isAutoTimer': isAutoTimer,
				'text': txt
			}
		return timerDetails

	ret = OrderedDict()
	services = eServiceCenter.getInstance().list(eServiceReference(ref))
	if not services:
		return {"events": ret, "result": False, "slot": None}

	sRefs = services.getContent('S')
	epg = EPG()
	epgEvents = epg.getMultiChannelEvents(sRefs, begintime, endtime)
	offset = None
	picons = {}

	if epgEvents is not None:
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

		# We want to display if an event is covered by a timer.
		# To keep the costs low for a nested loop against the timer list, we
		# partition the timers by service reference. For an event we then only
		# have to check the part of the timers that belong to that specific
		# service reference. Partition is generated here.
		timerlist = {}
		timers = self.session.nav.RecordTimer.timer_list + self.session.nav.RecordTimer.processed_timers
		for timer in timers:
			if timer.end >= begintime and timer.begin <= lastevent:
				if str(timer.service_ref) not in timerlist:
					timerlist[str(timer.service_ref)] = []
				timerlist[str(timer.service_ref)].append(timer)

		for epgEvent in epgEvents:
			sref = epgEvent.service['sRef']
			# Cut description
			f = sref.rfind("::")
			if f != -1:
				sref = sref[:f + 1]
			# If we can expect that events and timerlist are sorted by begin time,
			# we should be able to always pick the first timer from the timers list
			# and check if it belongs to the currently processed event.
			# Unfortunately it's not that simple: timers might overlap, so we
			# loop over the timers for the service reference of the event processed.
			# Here we can eliminate the head of the list, when we find a matching timer:
			# it only can contain timer entries older than the currently processed event.
			timer = None
			if sref in timerlist and len(timerlist[sref]) > 0:
				for i, first in enumerate(timerlist[sref]):
					if first.begin <= epgEvent.start['timestamp'] and epgEvent.end['timestamp'] - 120 <= first.end:
						timer = getTimerDetails(first)
						timerlist[sref] = timerlist[sref][i:]
						break

			ev = {
				'id': epgEvent.eventId,
				'begin_timestamp': epgEvent.start['timestamp'],
				'title': epgEvent.title,
				'shortdesc': convertDesc(epgEvent.description),
				'ref': epgEvent.service['sRef'],
				'timer': timer
			}

			if timer:
				ev['timerStatus'] = timer['basicStatus']
			else:
				ev['timerStatus'] = ""

			if Mode == 2:
				ev['duration'] = epgEvent.duration['seconds']

			channel = filterName(epgEvent.service['name'])

			if channel not in ret:
				if Mode == 1:
					ret[channel] = [[], [], [], [], [], [], [], [], [], [], [], []]
				else:
					ret[channel] = [[]]

				picons[channel] = getPicon(epgEvent.service['sRef'])

			if Mode == 1:
				slot = int((epgEvent.start['timestamp'] - offset) / 7200)

				if slot < 0:
					slot = 0
				if slot < 12 and epgEvent.start['timestamp'] < lastevent:
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
				cname = normalize('NFKD', cname)
			else:
				cname = normalize('NFKD', six.text_type(cname, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
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
				cname = normalize('NFKD', cname)
			else:
				cname = normalize('NFKD', six.text_type(cname, 'utf_8', errors='ignore')).encode('ASCII', 'ignore')
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
