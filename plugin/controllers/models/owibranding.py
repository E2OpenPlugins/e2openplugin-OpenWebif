# -*- coding: utf-8 -*-

##############################################################################
#                        2014 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
# Simulate the oe-a boxbranding module (Only functions required by OWIF)     #
##############################################################################

from Plugins.Extensions.OpenWebif.__init__ import _
from Components.About import about
from socket import has_ipv6
from Tools.Directories import fileExists, pathExists
import string
import os, hashlib

try:
	from Components.About import about
except:
	pass

tpmloaded = 1
try:
	from enigma import eTPM
	if not hasattr(eTPM, 'getData'):
		tpmloaded = 0
except:
	tpmloaded = 0

def validate_certificate(cert, key):
	buf = decrypt_block(cert[8:], key)
	if buf is None:
		return None
	return buf[36:107] + cert[139:196]

def get_random():
	try:
		xor = lambda a,b: ''.join(chr(ord(c)^ord(d)) for c,d in zip(a,b*100))
		random = urandom(8)
		x = str(time())[-8:]
		result = xor(random, x)

		return result
	except:
		return None

def bin2long(s):
	return reduce( lambda x,y:(x<<8L)+y, map(ord, s))

def long2bin(l):
	res = ""
	for byte in range(128):
		res += chr((l >> (1024 - (byte + 1) * 8)) & 0xff)
	return res

def rsa_pub1024(src, mod):
	return long2bin(pow(bin2long(src), 65537, bin2long(mod)))

def decrypt_block(src, mod):
	if len(src) != 128 and len(src) != 202:
		return None
	dest = rsa_pub1024(src[:128], mod)
	hash = hashlib.sha1(dest[1:107])
	if len(src) == 202:
		hash.update(src[131:192])
	result = hash.digest()
	if result == dest[107:127]:
		return dest
	return None

def tpm_check():
	try:
		tpm = eTPM()
		rootkey = ['\x9f', '|', '\xe4', 'G', '\xc9', '\xb4', '\xf4', '#', '&', '\xce', '\xb3', '\xfe', '\xda', '\xc9', 'U', '`', '\xd8', '\x8c', 's', 'o', '\x90', '\x9b', '\\', 'b', '\xc0', '\x89', '\xd1', '\x8c', '\x9e', 'J', 'T', '\xc5', 'X', '\xa1', '\xb8', '\x13', '5', 'E', '\x02', '\xc9', '\xb2', '\xe6', 't', '\x89', '\xde', '\xcd', '\x9d', '\x11', '\xdd', '\xc7', '\xf4', '\xe4', '\xe4', '\xbc', '\xdb', '\x9c', '\xea', '}', '\xad', '\xda', 't', 'r', '\x9b', '\xdc', '\xbc', '\x18', '3', '\xe7', '\xaf', '|', '\xae', '\x0c', '\xe3', '\xb5', '\x84', '\x8d', '\r', '\x8d', '\x9d', '2', '\xd0', '\xce', '\xd5', 'q', '\t', '\x84', 'c', '\xa8', ')', '\x99', '\xdc', '<', '"', 'x', '\xe8', '\x87', '\x8f', '\x02', ';', 'S', 'm', '\xd5', '\xf0', '\xa3', '_', '\xb7', 'T', '\t', '\xde', '\xa7', '\xf1', '\xc9', '\xae', '\x8a', '\xd7', '\xd2', '\xcf', '\xb2', '.', '\x13', '\xfb', '\xac', 'j', '\xdf', '\xb1', '\x1d', ':', '?']
		random = None
		result = None
		l2r = False
		l2k = None
		l3k = None

		l2c = tpm.getData(eTPM.DT_LEVEL2_CERT)
		if l2c is None:
			return 0

		l2k = validate_certificate(l2c, rootkey)
		if l2k is None:
			return 0

		l3c = tpm.getData(eTPM.DT_LEVEL3_CERT)
		if l3c is None:
			return 0

		l3k = validate_certificate(l3c, l2k)
		if l3k is None:
			return 0

		random = get_random()
		if random is None:
			return 0

		value = tpm.computeSignature(random)
		result = decrypt_block(value, l3k)
		if result is None:
			return 0

		if result [80:88] != random:
			return 0

		return 1
	except:
		return 0

def getAllInfo():
	info = {}

	brand = "unknown"
	model = "unknown"
	procmodel = "unknown"
	orgdream = 0
	if tpmloaded:
		orgdream = tpm_check()

	if fileExists("/proc/stb/info/hwmodel"):
		brand = "DAGS"
		f = open("/proc/stb/info/hwmodel",'r')
		procmodel = f.readline().strip()
		f.close()
		if (procmodel.startswith("optimuss") or procmodel.startswith("pingulux")):
			brand = "Edision"
			model = procmodel.replace("optimmuss", "Optimuss ").replace("plus", " Plus").replace(" os", " OS")
		elif (procmodel.startswith("fusion") or procmodel.startswith("purehd") or procmodel.startswith("revo4k") or procmodel.startswith("galaxy4k")):
			brand = "Xsarius"
			if procmodel == "fusionhd":
				model = procmodel.replace("fusionhd", "Fusion HD")
			elif procmodel == "fusionhdse":
				model = procmodel.replace("fusionhdse", "Fusion HD SE")
			elif procmodel == "purehd":
				model = procmodel.replace("purehd", "PureHD")
			elif procmodel == "revo4k":
				model = procmodel.replace("revo4k", "Revo4K")
			elif procmodel == "galaxy4k":
				model = procmodel.replace("galaxy4k", "Galaxy4K")
	elif fileExists("/proc/stb/info/azmodel"):
		brand = "AZBox"
		f = open("/proc/stb/info/model",'r') # To-Do: Check if "model" is really correct ...
		procmodel = f.readline().strip()
		f.close()
		model = procmodel.lower()
	elif fileExists("/proc/stb/info/gbmodel"):
		brand = "GigaBlue"
		f = open("/proc/stb/info/gbmodel",'r')
		procmodel = f.readline().strip()
		f.close()
		if procmodel == "GBQUAD PLUS":
			model = procmodel.replace("GBQUAD", "Quad").replace("PLUS", " Plus")
		elif procmodel == "gb7252":
			model = procmodel.replace("gb7252", "UHD Quad 4k")
	elif fileExists("/proc/stb/info/vumodel") and not fileExists("/proc/stb/info/boxtype"):
		brand = "Vu+"
		f = open("/proc/stb/info/vumodel",'r')
		procmodel = f.readline().strip()
		f.close()
		model = procmodel.title().replace("olose", "olo SE").replace("olo2se", "olo2 SE").replace("2", "²")
	elif fileExists("/proc/boxtype"):
		f = open("/proc/boxtype",'r')
		procmodel = f.readline().strip().lower()
		f.close()
		if procmodel in ("adb2850", "adb2849", "bska", "bsla", "bxzb", "bzzb"):
			brand = "Advanced Digital Broadcast"
			if procmodel in ("bska", "bxzb"):
				model = "ADB 5800S"
			elif procmodel in ("bsla", "bzzb"):
				model = "ADB 5800SX"
			elif procmodel == "adb2849":
				model = "ADB 2849ST"
			else:
				model = "ADB 2850ST"
		elif procmodel in ("esi88", "uhd88"):
			brand = "Sagemcom"
			if procmodel == "uhd88":
				model = "UHD 88"
			else:
				model = "ESI 88"
	elif fileExists("/proc/stb/info/boxtype"):
		f = open("/proc/stb/info/boxtype",'r')
		procmodel = f.readline().strip().lower()
		f.close()
		if procmodel.startswith("et"):
			if procmodel == "et7000mini":
				brand = "Galaxy Innovations"
				model = "ET-7000 Mini"
			elif procmodel == "et11000":
				brand = "Galaxy Innovations"
				model = "ET-11000"
			else:
				brand = "Xtrend"
				model = procmodel.upper()
		elif procmodel.startswith("xpeed"):
			brand = "Golden Interstar"
			model = procmodel
		elif procmodel.startswith("xp"):
			brand = "MaxDigital"
			model = procmodel.upper()
		elif procmodel.startswith("ixuss"):
			brand = "Medialink"
			model = procmodel.replace(" ", "")
		elif procmodel == "formuler4turbo":
			brand = "Formuler"
			model = "4 Turbo"
		elif procmodel.startswith("formuler"):
			brand = "Formuler"
			model = procmodel.replace("formuler","")
		elif procmodel.startswith("mbtwinplus"):
			brand = "Miraclebox"
			model = "Premium Twin+"
		elif procmodel.startswith("alphatriplehd"):
			brand = "SAB"
			model = "Alpha Triple HD"
		elif procmodel in ("7000s", "mbmicro"):
			procmodel = "mbmicro"
			brand = "Miraclebox"
			model = "Premium Micro"
		elif procmodel in ("7005s", "mbmicrov2"):
			procmodel = "mbmicrov2"
			brand = "Miraclebox"
			model = "Premium Micro v2"
		elif procmodel.startswith("ini"):
			if procmodel.endswith("9000ru"):
				brand = "Sezam"
				model = "Marvel"
			elif procmodel.endswith("5000ru"):
				brand = "Sezam"
				model = "hdx"
			elif procmodel.endswith("1000ru"):
				brand = "Sezam"
				model = "hde"
			elif procmodel.endswith("5000sv"):
				brand = "Miraclebox"
				model = "mbtwin"
			elif procmodel.endswith("1000sv"):
				brand = "Miraclebox"
				model = "mbmini"
			elif procmodel.endswith("1000de"):
				brand = "Golden Interstar"
				model = "Xpeed LX"
			elif procmodel.endswith("9000de"):
				brand = "Golden Interstar"
				model = "Xpeed LX3"
			elif procmodel.endswith("1000lx"):
				brand = "Golden Interstar"
				model = "Xpeed LX"
			elif procmodel.endswith("de"):
				brand = "Golden Interstar"
			elif procmodel.endswith("1000am"):
				brand = "Atemio"
				model = "5x00"
			else:
				brand = "Venton"
				model = "HDx"
		elif procmodel.startswith("unibox-"):
			brand = "Venton"
			model = "HDe"
		elif procmodel == "hd1100":
			brand = "Mut@nt"
			model = "HD1100"
		elif procmodel == "hd1200":
			brand = "Mut@nt"
			model = "HD1200"
		elif procmodel == "hd1265":
			brand = "Mut@nt"
			model = "HD1265"
		elif procmodel == "hd2400":
			brand = "Mut@nt"
			model = "HD2400"
		elif procmodel == "hd51":
			brand = "Mut@nt"
			model = "HD51"
		elif procmodel == "hd11":
			brand = "Mut@nt"
			model = "HD11"
		elif procmodel == "hd500c":
			brand = "Mut@nt"
			model = "HD500c"
		elif procmodel == "hd530c":
			brand = "Mut@nt"
			model = "HD530c"
		elif procmodel == "arivalink200":
			brand = "Ferguson"
			model = "Ariva @Link 200"
		elif procmodel.startswith("spark"):
			brand = "Fulan"
			if procmodel == "spark7162":
				model = "Spark 7162"
			else:
				model = "Spark"
		elif procmodel == "spycat":
			brand = "Spycat"
			model = "Spycat"
		elif procmodel == "spycatmini":
			brand = "Spycat"
			model = "Spycat Mini"
		elif procmodel == "spycatminiplus":
			brand = "Spycat"
			model = "Spycat Mini+"
		elif procmodel == "spycat4kmini":
			brand = "Spycat"
			model = "spycat 4K Mini"
		elif procmodel == "wetekplay":
			brand = "WeTeK"
			model = "Play"
		elif procmodel.startswith("osm"):
			brand = "Edision"
			if procmodel == "osmini":
				model = "OS Mini"
			elif procmodel == "osminiplus":
				model = "OS Mini+"
			elif procmodel == "osmega":
				model = "OS Mega"
			else:
				model = procmodel
		elif procmodel == "h3":
			brand = "Zgemma"
			model = "H3 series"
		elif procmodel == "h5":
			brand = "Zgemma"
			model = "H5 series"
		elif procmodel == "h7":
			brand = "Zgemma"
			model = "H7 series"
		elif procmodel == "lc":
			brand = "Zgemma"
			model = "LC"
		elif procmodel == "i55":
			brand = "Zgemma"
			model = "i55"
		elif procmodel == "vs1500":
			brand = "Vimastec"
			model = "vs1500"
		elif procmodel == "sf4008":
			brand = "Octagon"
			model = procmodel
	elif fileExists("/proc/stb/info/model"):
		f = open("/proc/stb/info/model",'r')
		procmodel = f.readline().strip().lower()
		f.close()
		if procmodel == "tf7700hdpvr":
			brand = "Topfield"
			model = "TF7700 HDPVR"
		elif procmodel == "dsi87":
			brand = "Sagemcom"
			model = "DSI 87"
		elif procmodel.startswith("spark"):
			brand = "Fulan"
			if procmodel == "spark7162":
				model = "Spark 7162"
			else:
				model = "Spark"
		elif (procmodel.startswith("dm")):
			brand = "Dream Multimedia"
			model = procmodel.replace("dm", "DM", 1)
		else:
			model = procmodel

	if fileExists("/etc/.box"):
		distro = "HDMU"
		f = open("/etc/.box",'r')
		tempmodel = f.readline().strip().lower()
		if tempmodel.startswith("ufs") or model.startswith("ufc"):
			brand = "Kathrein"
			model = tempmodel.upcase()
			procmodel = tempmodel
		elif tempmodel.startswith("spark"):
			brand = "Fulan"
			model = tempmodel.title()
			procmodel = tempmodel
		elif tempmodel.startswith("xcombo"):
			brand = "EVO"
			model = "enfinityX combo plus"
			procmodel = "vg2000"

	type = procmodel
	if type in ("et9000", "et9100", "et9200", "et9500"):
		type = "et9x00"
	elif type in ("et5000", "et6000", "et6x00"):
		type = "et5x00"
	elif type == "et4000":
		type = "et4x00"
	elif type == "xp1000":
		type = "xp1000"
	elif type in ("bska", "bxzb"):
		type = "nbox_white"
	elif type in ("bsla", "bzzb"):
		type = "nbox"
	elif type == "sagemcom88":
		type = "esi88"
	elif type in ("tf7700hdpvr", "topf"):
		type = "topf"

	info['brand'] = brand
	info['model'] = model
	info['procmodel'] = procmodel
	info['type'] = type

	remote = "dmm"
	if procmodel in ("solo", "duo", "uno", "solo2", "solose", "zero", "solo4k", "uno4k", "ultimo4k"):
		remote = "vu_normal"
	elif procmodel == "duo2":
		remote = "vu_duo2"
	elif procmodel == "ultimo":
		remote = "vu_ultimo"
	elif procmodel == "e3hd":
		remote = "e3hd"
	elif procmodel in ("et9x00", "et9000", "et9100", "et9200", "et9500"):
		remote = "et9x00"
	elif procmodel in ("et5x00", "et5000", "et6x00", "et6000"):
		remote = "et5x00"
	elif procmodel in ("et4x00", "et4000"):
		remote = "et4x00"
	elif procmodel == "et6500":
		remote = "et6500"
	elif procmodel in ("et8x00", "et8000", "et8500", "et8500s", "et10000"):
		remote = "et8000"
	elif procmodel in ("et7x00", "et7000", "et7500"):
		remote = "et7x00"
	elif procmodel in ("et7000mini", "et11000"):
		remote = "et7000mini"
	elif procmodel == "gbquad":
		remote = "gigablue"
	elif procmodel == "gbquadplus":
		remote = "gbquadplus"
	elif procmodel == "gb7252":
		remote = "gb7252"
	elif procmodel in ("formuler1", "formuler3", "formuler4", "formuler4turbo"):
		remote = "formuler1"
	elif procmodel in ("azboxme", "azboxminime", "me", "minime"):
		remote = "me"
	elif procmodel in ("optimussos1", "optimussos1plus", "optimussos2", "optimussos2plus"):
		remote = "optimuss"
	elif procmodel in ("premium", "premium+"):
		remote = "premium"
	elif procmodel in ("elite", "ultra"):
		remote = "elite"
	elif procmodel in ("ini-1000", "ini-1000ru"):
		remote = "ini-1000"
	elif procmodel in ("ini-1000sv", "ini-5000sv", "ini-9000de"):
		remote = "miraclebox"
	elif procmodel in ("mbtwinplus", "mbmicro", "mbmicrov2"):
		remote = "miraclebox2"
	elif procmodel == "alphatriplehd":
		remote = "alphatriplehd"
	elif procmodel == "ini-3000":
		remote = "ini-3000"
	elif procmodel in ("ini-7012", "ini-7000", "ini-5000", "ini-5000ru"):
		remote = "ini-7000"
	elif procmodel.startswith("spark"):
		remote = "spark"
	elif procmodel == "xp1000":
		remote = "xp1000"
	elif procmodel.startswith("xpeedlx"):
		remote = "xpeedlx"
	elif procmodel in ("adb2850", "adb2849", "bska", "bsla", "bxzb", "bzzb", "esi88", "uhd88", "dsi87", "arivalink200"):
		remote = "nbox"
	elif procmodel in ("hd1100", "hd1200", "hd1265", "hd1400", "hd51", "hd11", "hd500c", "hd530c"):
		remote = "hd1x00"
	elif procmodel == "hd2400":
		remote = "hd2400"
	elif procmodel in ("spycat", "spycatmini", "spycatminiplus", "spycat4kmini"):
		remote = "spycat"
	elif procmodel.startswith("ixuss"):
		remote = procmodel.replace(" ", "")
	elif procmodel == "vg2000":
		remote = "xcombo"
	elif procmodel == "dm8000":
		remote = "dmm1"
	elif procmodel in ("dm7080", "dm7020hd", "dm7020hdv2", "dm800sev2", "dm500hdv2", "dm520", "dm820", "dm900"):
		remote = "dmm2"
	elif procmodel == "wetekplay":
		remote = procmodel
	elif procmodel.startswith("osm"):
		remote = "osmini"
	elif procmodel in ("fusionhd"):
		remote = procmodel
	elif procmodel in ("fusionhdse"):
		remote = procmodel
	elif procmodel in ("purehd"):
		remote = procmodel
	elif procmodel in ("revo4k"):
		remote = procmodel
	elif procmodel in ("galaxy4k"):
		remote = procmodel
	elif procmodel in ("sh1", "lc"):
		remote = "sh1"
	elif procmodel in ("h3", "h5", "h7"):
		remote = "h3"
	elif procmodel == "i55":
		remote = "i55"
	elif procmodel == "sf4008":
		remote = "octagon"
	elif procmodel in ("vs1100", "vs1500"):
		remote = "vs1x00"

	info['remote'] = remote

	kernel = about.getKernelVersionString()[0]

	distro = "unknown"
	imagever = "unknown"
	imagebuild = ""
	driverdate = "unknown"

	# Assume OE 1.6
	oever = "OE 1.6"
	if kernel>2:
		oever = "OE 2.0"

	if fileExists("/etc/.box"):
		distro = "HDMU"
		oever = "private"
	elif fileExists("/etc/bhversion"):
		distro = "Black Hole"
		f = open("/etc/bhversion",'r')
		imagever = f.readline().strip()
		f.close()
		if kernel>2:
			oever = "OpenVuplus 2.1"
	elif fileExists("/etc/vtiversion.info"):
		distro = "VTi-Team Image"
		f = open("/etc/vtiversion.info",'r')
		imagever = f.readline().strip().replace("VTi-Team Image ", "").replace("Release ", "").replace("v.", "")
		f.close()
		oever = "OE 1.6"
		imagelist = imagever.split('.')
		imagebuild = imagelist.pop()
		imagever = ".".join(imagelist)
		if kernel>2:
			oever = "OpenVuplus 2.1"
		if ((imagever == "5.1") or (imagever[0] > 5)):
			oever = "OpenVuplus 2.1"
	elif fileExists("/var/grun/grcstype"):
		distro = "Graterlia OS"
		try:
			imagever = about.getImageVersionString()
		except:
			pass
	# ToDo: If your distro gets detected as OpenPLi, feel free to add a detection for your distro here ...
	else:
		# OE 2.2 uses apt, not opkg
		if not fileExists("/etc/opkg/all-feed.conf"):
			oever = "OE 2.2"
		else:
			try:
				f = open("/etc/opkg/all-feed.conf",'r')
				oeline = f.readline().strip().lower()
				f.close()
				distro = oeline.split( )[1].replace("-all","")
			except:
				pass

		if distro == "openpli":
			oever = "PLi-OE"
			try:
				imagelist = open("/etc/issue").readlines()[-2].split()[1].split('.')
				imagever = imagelist.pop(0)
				if imagelist:
					imagebuild = "".join(imagelist)
				else:
					# deal with major release versions only
					if imagever.isnumeric():
						imagebuild = "0"
			except:
				# just in case
				pass
		elif distro == "openrsi":
			oever = "PLi-OE"
		else:
			try:
				imagever = about.getImageVersionString()
			except:
				pass

		if (distro == "unknown" and brand == "Vu+" and fileExists("/etc/version")):
			# Since OE-A uses boxbranding and bh or vti can be detected, there isn't much else left for Vu+ boxes
			distro = "Vu+ original"
			f = open("/etc/version",'r')
			imagever = f.readline().strip()
			f.close()
			if kernel>2:
				oever = "OpenVuplus 2.1"

	# reporting the installed dvb-module version is as close as we get without too much hassle
	driverdate = 'unknown'
	try:
		driverdate = os.popen('/usr/bin/opkg -V0 list_installed *dvb-modules*').readline().split( )[2]
	except:
		try:
			driverdate = os.popen('/usr/bin/opkg -V0 list_installed *dvb-proxy*').readline().split( )[2]
		except:
			try:
				driverdate = os.popen('/usr/bin/opkg -V0 list_installed *kernel-core-default-gos*').readline().split( )[2]
			except:
				pass

	info['oever'] = oever
	info['distro'] = distro
	info['imagever'] = imagever
	info['imagebuild'] = imagebuild
	info['driverdate'] = driverdate

	return info

STATIC_INFO_DIC = getAllInfo()

def getMachineBuild():
	return STATIC_INFO_DIC['procmodel']

def getMachineBrand():
	return STATIC_INFO_DIC['brand']

def getMachineName():
	return STATIC_INFO_DIC['model']

def getMachineProcModel():
	return STATIC_INFO_DIC['procmodel']

def getBoxType():
	return STATIC_INFO_DIC['type']

def getOEVersion():
	return STATIC_INFO_DIC['oever']

def getDriverDate():
	return STATIC_INFO_DIC['driverdate']

def getImageVersion():
	return STATIC_INFO_DIC['imagever']

def getImageBuild():
	return STATIC_INFO_DIC['imagebuild']

def getImageDistro():
	return STATIC_INFO_DIC['distro']

class rc_model:
	def getRcFolder(self):
		return STATIC_INFO_DIC['remote']
