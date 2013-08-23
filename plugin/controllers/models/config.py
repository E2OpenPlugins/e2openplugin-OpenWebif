from enigma import eEnv
from Components.SystemInfo import SystemInfo
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN, fileExists
from os import path, listdir
import xml.etree.cElementTree

class ConfigFiles:
	def __init__(self):
		self.setupfiles = []
		self.allowedsections = ["usage", "recording", "subtitlesetup", "autolanguagesetup", "avsetup", "harddisk", "keyboard", "timezone"]
		self.getConfigFiles()

	def getConfigFiles(self):
		setupfiles = [eEnv.resolve('${datadir}/enigma2/setup.xml')]
		locations = ('SystemPlugins', 'Extensions')
		libdir = eEnv.resolve('${libdir}')
		for location in locations:
			plugins = listdir(('%s/enigma2/python/Plugins/%s' % (libdir,location)))
			for plugin in plugins:
				setupfiles.append(('%s/enigma2/python/Plugins/%s/%s/setup.xml' % (libdir, location, plugin)))
		for setupfile in setupfiles:
			if path.exists(setupfile):
				print "[OpenWebif] loading configuration file :", setupfile
				self.setupfiles.append(setupfile)

configfiles = ConfigFiles()

def addCollapsedMenu(name):
	tags = config.OpenWebif.webcache.collapsedmenus.value.split("|")
	if name not in tags:
		tags.append(name)
		
	config.OpenWebif.webcache.collapsedmenus.value = "|".join(tags).strip("|")
	config.OpenWebif.webcache.collapsedmenus.save()
	
	return {
		"result": True
	}
	
def removeCollapsedMenu(name):
	tags = config.OpenWebif.webcache.collapsedmenus.value.split("|")
	if name in tags:
		tags.remove(name)

	config.OpenWebif.webcache.collapsedmenus.value = "|".join(tags).strip("|")
	config.OpenWebif.webcache.collapsedmenus.save()

	return {
		"result": True
	}

def getCollapsedMenus():
	return {
		"result": True,
		"collapsed": config.OpenWebif.webcache.collapsedmenus.value.split("|")
	}

def setRemoteGrabScreenshot(value):
	config.OpenWebif.webcache.remotegrabscreenshot.value = value
	config.OpenWebif.webcache.remotegrabscreenshot.save()
	return {
		"result": True
	}

def getRemoteGrabScreenshot():
	return {
		"result": True,
		"remotegrabscreenshot": config.OpenWebif.webcache.remotegrabscreenshot.value
	}

def setZapStream(value):
	config.OpenWebif.webcache.zapstream.value = value
	config.OpenWebif.webcache.zapstream.save()
	return {
		"result": True
	}

def getZapStream():
	return {
		"result": True,
		"zapstream": config.OpenWebif.webcache.zapstream.value
	}

def getJsonFromConfig(cnf):
	if cnf.__class__.__name__ == "ConfigSelection" or cnf.__class__.__name__ == "ConfigSelectionNumber":
		if type(cnf.choices.choices) == dict:
			choices = []
			for choice in cnf.choices.choices:
				choices.append((choice, cnf.choices.choices[choice]))
		elif type(cnf.choices.choices[0]) == tuple:
			choices = cnf.choices.choices
		else:
			choices = []
			for choice in cnf.choices.choices:
				choices.append((choice, choice))
				
		return {
			"result": True,
			"type": "select",
			"choices": choices,
			"current": cnf.value
		}
	elif cnf.__class__.__name__ == "ConfigBoolean" or cnf.__class__.__name__ == "ConfigEnableDisable" or cnf.__class__.__name__ == "ConfigYesNo":
		return {
			"result": True,
			"type": "checkbox",
			"current": cnf.value
		}
	elif cnf.__class__.__name__ == "ConfigSet":
		return {
			"result": True,
			"type": "multicheckbox",
			"choices": cnf.choices.choices,
			"current": cnf.value
		}

	elif cnf.__class__.__name__ == "ConfigNumber":
		return {
			"result": True,
			"type": "number",
			"current": cnf.value
		}
	elif cnf.__class__.__name__ == "ConfigInteger":
		return {
			"result": True,
			"type": "number",
			"current": cnf.value,
			"limits": (cnf.limits[0][0], cnf.limits[0][1])
		}

	elif cnf.__class__.__name__ == "ConfigText":
		return {
			"result": True,
			"type": "text",
			"current": cnf.value
		}

	print "[OpenWebif] Unknown class ", cnf.__class__.__name__
	return {
		"result": False,
		"type": "unknown"
	}

def saveConfig(path, value):
	try:
		cnf = eval(path)
		if cnf.__class__.__name__ == "ConfigBoolean" or cnf.__class__.__name__ == "ConfigEnableDisable" or cnf.__class__.__name__ == "ConfigYesNo":
			cnf.value = value == "true"
		elif cnf.__class__.__name__ == "ConfigSet":
			values = cnf.value
			if int(value) in values:
				values.remove(int(value))
			else:
				values.append(int(value))
			cnf.value = values
		elif cnf.__class__.__name__ == "ConfigNumber":
			cnf.value = int(value)
		elif  cnf.__class__.__name__ == "ConfigInteger":
			cnf_min = int(cnf.limits[0][0])
			cnf_max = int(cnf.limits[0][1])
			cnf_value = int(value)
			if cnf_value < cnf_min:
				cnf_value = cnf_min
			elif cnf_value > cnf_max:
				cnf_value = cnf_max
			cnf.value = cnf_value
		else:
			cnf.value = value
		cnf.save()
	except Exception, e:
		print "[OpenWebif] ", e
		return {
			"result": False
		}
		
	return {
		"result": True
	}

def getConfigs(key):
	configs = []
	title = ""
	setup_data = []
	if fileExists(resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/TransCodingSetup/setup.xml")):
		setupfile = file(resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/TransCodingSetup/setup.xml"), 'r')
		setupdom = xml.etree.cElementTree.parse(setupfile)
		setupfile.close()
		setup_data.append(setupdom.getroot())
	setupfile = file(eEnv.resolve('${datadir}/enigma2/setup.xml'), 'r')
	setupdom = xml.etree.cElementTree.parse(setupfile)
	setupfile.close()
	setup_xmldata = setupdom.getroot()
	setup_data.append(setupdom.getroot())

	for xmldata in setup_data:
		for section in xmldata.findall("setup"):
			if section.get("key") != key:
				continue
			
			for entry in section:
				if entry.tag == "item":
					requires = entry.get("requires")
					if requires and requires.startswith('config.'):
						item = eval(requires or "");
						if item.value and not item.value == "0":
							SystemInfo[requires] = True
						else:
							SystemInfo[requires] = False
					if requires and not SystemInfo.get(requires, False):
						continue;
				
					if int(entry.get("level", 0)) > config.usage.setup_level.index:
						continue
				
					try:
						data = getJsonFromConfig(eval(entry.text or ""))
						text = entry.get("text", "")
						if "limits" in data:
							text = "%s (%d - %d)" % (text, data["limits"][0], data["limits"][1])
						configs.append({
							"description": text,
							"path": entry.text or "",
							"data": data
						})		
					except Exception, e:
						pass
					
			title = section.get("title", "")
			break
		
	return {
		"result": True,
		"configs": configs,
		"title": title
	}
	
def getConfigsSections():
	allowedsections = configfiles.allowedsections
	sections = []
	setup_data = []
	if fileExists(resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/TransCodingSetup/setup.xml")):
		setupfile = file(resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/TransCodingSetup/setup.xml"), 'r')
		setupdom = xml.etree.cElementTree.parse(setupfile)
		setupfile.close()
		setup_data.append(setupdom.getroot())
	setupfile = file(eEnv.resolve('${datadir}/enigma2/setup.xml'), 'r')
	setupdom = xml.etree.cElementTree.parse(setupfile)
	setupfile.close()
	setup_xmldata = setupdom.getroot()
	setup_data.append(setupdom.getroot())

	for xmldata in setup_data:
		for section in xmldata.findall("setup"):
			key = section.get("key")
			showOpenWebIF = section.get("showOpenWebIF")
			if showOpenWebIF == "1":
				allowedsections.append(key)
			if key not in allowedsections:
				continue
		
			count = 0
			for entry in section:
				if entry.tag == "item":
					requires = entry.get("requires")
					if requires and requires.startswith('config.'):
						item = eval(requires or "");
						if item.value and not item.value == "0":
							SystemInfo[requires] = True
						else:
							SystemInfo[requires] = False
					if requires and not SystemInfo.get(requires, False):
						continue;
					
					if int(entry.get("level", 0)) > config.usage.setup_level.index:
						continue
					
					count += 1
				
			if count > 0:
				sections.append({
					"key": key,
					"description": section.get("title")
				})

	sections = sorted(sections, key=lambda k: k['description']) 
	return {
		"result": True,
		"sections": sections
	}

def privSettingValues(prefix, top, result):
	for (key, val) in top.items():
		name = prefix + "." + key
		if isinstance(val, dict):
			privSettingValues(name, val, result)
		elif isinstance(val, tuple):
			result.append((name, val[0]))
		else:
			result.append((name, val))	

def getSettings():
	configkeyval = []
	privSettingValues("config", config.saved_value, configkeyval)
	return {
		"result": True,
		"settings": configkeyval
	}

