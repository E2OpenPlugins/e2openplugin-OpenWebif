# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from enigma import eServiceReference, getBestPlayableServiceReference
from ServiceReference import ServiceReference
from six.moves.urllib.parse import unquote, quote
from six import ensure_str
import os
import re
from Components.config import config
from twisted.web.resource import Resource
from Tools.Directories import fileExists
from Plugins.Extensions.OpenWebif.controllers.models.info import getInfo
from Plugins.Extensions.OpenWebif.controllers.utilities import getUrlArg, PY3


class GetSession(Resource):
	def GetSID(self, request):
		sid = request.getSession().uid
		return sid

	def GetAuth(self, request):
		session = request.getSession().sessionNamespaces
		if "pwd" in list(session.keys()) and session["pwd"] is not None:
			return (session["user"], session["pwd"])
		else:
			return None


def getStream(session, request, m3ufile):
	sRef = getUrlArg(request, "ref")
	if sRef != None:
		if PY3:
			sRef = unquote(unquote(sRef))
		else:
			sRef = unquote(unquote(request.args["ref"][0]).decode('utf-8', 'ignore')).encode('utf-8')
	else:
		sRef = ""

	currentServiceRef = None
	if m3ufile == "streamcurrent.m3u":
		currentServiceRef = session.nav.getCurrentlyPlayingServiceReference()
		sRef = currentServiceRef.toString()

	if sRef.startswith("1:134:"):
		if currentServiceRef is None:
			currentServiceRef = session.nav.getCurrentlyPlayingServiceReference()
		if currentServiceRef is None:
			currentServiceRef = eServiceReference()
		ref = getBestPlayableServiceReference(eServiceReference(sRef), currentServiceRef)
		if ref is None:
			sRef = ""
		else:
			sRef = ref.toString()

	# #EXTINF:-1,%s\n adding back to show service name in programs like VLC
	progopt = ''
	name = getUrlArg(request, "name")
	if name != None:
		if config.OpenWebif.service_name_for_stream.value:
			progopt = "#EXTINF:-1,%s\n" % name

	name = "stream"
	portNumber = config.OpenWebif.streamport.value
	info = getInfo()
	model = info["model"]
	machinebuild = info["machinebuild"]
	urlparam = '?'
	if info["imagedistro"] in ('openpli', 'satdreamgr', 'openvision'):
		urlparam = '&'
	transcoder_port = None
	args = ""

	device = getUrlArg(request, "device")

	if fileExists("/dev/bcm_enc0"):
		try:
			transcoder_port = int(config.plugins.transcodingsetup.port.value)
		except Exception:
			# Transcoding Plugin is not installed or your STB does not support transcoding
			transcoder_port = None
		if device == "phone":
			portNumber = transcoder_port
		_port = getUrlArg(request, "port")
		if _port != None:
			portNumber = _port
	elif fileExists("/dev/encoder0") or fileExists("/proc/stb/encoder/0/apply"):
		transcoder_port = portNumber

	if fileExists("/dev/bcm_enc0") or fileExists("/dev/encoder0") or fileExists("/proc/stb/encoder/0/apply"):
		if device == "phone":
			try:
				bitrate = config.plugins.transcodingsetup.bitrate.value
				resolution = config.plugins.transcodingsetup.resolution.value
				(width, height) = tuple(resolution.split('x'))
				# framerate = config.plugins.transcodingsetup.framerate.value
				aspectratio = config.plugins.transcodingsetup.aspectratio.value
				interlaced = config.plugins.transcodingsetup.interlaced.value
				if fileExists("/proc/stb/encoder/0/vcodec"):
					vcodec = config.plugins.transcodingsetup.vcodec.value
					args = "?bitrate=%s__width=%s__height=%s__vcodec=%s__aspectratio=%s__interlaced=%s" % (bitrate, width, height, vcodec, aspectratio, interlaced)
				else:
					args = "?bitrate=%s__width=%s__height=%s__aspectratio=%s__interlaced=%s" % (bitrate, width, height, aspectratio, interlaced)
				args = args.replace('__', urlparam)
			except Exception:
				pass

	# When you use EXTVLCOPT:program in a transcoded stream, VLC does not play stream
	if config.OpenWebif.service_name_for_stream.value and sRef != '' and portNumber != transcoder_port:
		progopt = "%s#EXTVLCOPT:program=%d\n" % (progopt, int(sRef.split(':')[3], 16))

	if config.OpenWebif.auth_for_streaming.value:
		asession = GetSession()
		if asession.GetAuth(request) is not None:
			auth = ':'.join(asession.GetAuth(request)) + "@"
		else:
			auth = '-sid:' + ensure_str(asession.GetSID(request)) + "@"
	else:
		auth = ''

	response = "#EXTM3U \n#EXTVLCOPT:http-reconnect=true \n%shttp://%s%s:%s/%s%s\n" % (progopt, auth, request.getRequestHostname(), portNumber, sRef, args)
	if config.OpenWebif.playiptvdirect.value:
		if "http://" in sRef or "https://" in sRef:
			l = sRef.split(":http")[1]
			response = "#EXTM3U \n#EXTVLCOPT:http-reconnect=true\n%shttp%s\n" % (progopt, l)
	request.setHeader('Content-Type', 'application/x-mpegurl')
	# Note: do not rename the m3u file all the time
	fname = getUrlArg(request, "fname")
	if fname != None:
		request.setHeader('Content-Disposition', 'inline; filename=%s.%s;' % (fname, 'm3u8'))
	return response


def getTS(self, request):
	file = getUrlArg(request, "file")
	if file != None:
		if PY3:
			filename = unquote(file)
		else:
			filename = unquote(file).decode('utf-8', 'ignore').encode('utf-8')
		if not os.path.exists(filename):
			return "File '%s' not found" % (filename)

# ServiceReference is not part of filename so look in the '.ts.meta' file
		sRef = ""
		progopt = ''

		if os.path.exists(filename + '.meta'):
			metafile = open(filename + '.meta', "r")
			name = ''
			seconds = -1  # unknown duration default
			line = metafile.readline()  # service ref
			if line:
				sRef = eServiceReference(line.strip()).toString()
			line2 = metafile.readline()  # name
			if line2:
				name = line2.strip()
			line6 = metafile.readline()  # description
			line6 = metafile.readline()  # recording time
			line6 = metafile.readline()  # tags
			line6 = metafile.readline()  # length

			if line6:
				seconds = float(line6.strip()) / 90000  # In seconds

			if config.OpenWebif.service_name_for_stream.value:
				progopt = "%s#EXTINF:%d,%s\n" % (progopt, seconds, name)

			metafile.close()

		portNumber = None
		proto = 'http'
		info = getInfo()
		model = info["model"]
		machinebuild = info["machinebuild"]
		transcoder_port = None
		args = ""
		urlparam = '?'
		if info["imagedistro"] in ('openpli', 'satdreamgr', 'openvision'):
			urlparam = '&'

		device = getUrlArg(request, "device")

		if fileExists("/dev/bcm_enc0") or fileExists("/dev/encoder0") or fileExists("/proc/stb/encoder/0/apply"):
			try:
				transcoder_port = int(config.plugins.transcodingsetup.port.value)
			except Exception:
				# Transcoding Plugin is not installed or your STB does not support transcoding
				transcoder_port = None
			if device == "phone":
				portNumber = transcoder_port
			_port = getUrlArg(request, "port")
			if _port != None:
				portNumber = _port

		if fileExists("/dev/bcm_enc0") or fileExists("/dev/encoder0") or fileExists("/proc/stb/encoder/0/apply"):
			if device == "phone":
				try:
					bitrate = config.plugins.transcodingsetup.bitrate.value
					resolution = config.plugins.transcodingsetup.resolution.value
					(width, height) = tuple(resolution.split('x'))
					# framerate = config.plugins.transcodingsetup.framerate.value
					aspectratio = config.plugins.transcodingsetup.aspectratio.value
					interlaced = config.plugins.transcodingsetup.interlaced.value
					if fileExists("/proc/stb/encoder/0/vcodec"):
						vcodec = config.plugins.transcodingsetup.vcodec.value
						args = "?bitrate=%s__width=%s__height=%s__vcodec=%s__aspectratio=%s__interlaced=%s" % (bitrate, width, height, vcodec, aspectratio, interlaced)
					else:
						args = "?bitrate=%s__width=%s__height=%s__aspectratio=%s__interlaced=%s" % (bitrate, width, height, aspectratio, interlaced)
					args = args.replace('__', urlparam)
				except Exception:
					pass
			# Add position parameter to m3u link
			position = getUrlArg(request, "position")
			if position != None:
				args = args + "&position=" + position

		# When you use EXTVLCOPT:program in a transcoded stream, VLC does not play stream
		if config.OpenWebif.service_name_for_stream.value and sRef != '' and portNumber != transcoder_port:
			progopt = "%s#EXTVLCOPT:program=%d\n" % (progopt, int(sRef.split(':')[3], 16))

		if portNumber is None:
			portNumber = config.OpenWebif.port.value
			if request.isSecure():
				portNumber = config.OpenWebif.https_port.value
				proto = 'https'
			ourhost = request.getHeader('host')
			m = re.match('.+\:(\d+)$', ourhost)
			if m is not None:
				portNumber = m.group(1)

		if config.OpenWebif.auth_for_streaming.value:
			asession = GetSession()
			if asession.GetAuth(request) is not None:
				auth = ':'.join(asession.GetAuth(request)) + "@"
			else:
				auth = '-sid:' + ensure_str(asession.GetSID(request)) + "@"
		else:
			auth = ''

		response = "#EXTM3U \n#EXTVLCOPT:http-reconnect=true \n%s%s://%s%s:%s/file?file=%s%s\n" % ((progopt, proto, auth, request.getRequestHostname(), portNumber, quote(filename), args))
		request.setHeader('Content-Type', 'application/x-mpegurl')
		return response
	else:
		return "Missing file parameter"


def getStreamSubservices(session, request):
	services = []
	currentServiceRef = session.nav.getCurrentlyPlayingServiceReference()

	# TODO : this will only work if sref = current channel
	# the DMM webif can also show subservices for other channels like the current
	# ideas are welcome

	sRef = getUrlArg(request, "sRef")
	if sRef != None:
		currentServiceRef = eServiceReference(sRef)

	if currentServiceRef is not None:
		currentService = session.nav.getCurrentService()
		subservices = currentService.subServices()

		services.append({
			"servicereference": currentServiceRef.toString(),
			"servicename": ServiceReference(currentServiceRef).getServiceName()
		})
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
		services.append({
			"servicereference": "N/A",
			"servicename": "N/A"
		})

	return {"services": services}
