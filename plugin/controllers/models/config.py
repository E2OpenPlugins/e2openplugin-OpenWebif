# -*- coding: utf-8 -*-

from enigma import eEnv
from Components.SystemInfo import SystemInfo
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN, fileExists
from os import path, listdir
import xml.etree.cElementTree

from Plugins.Extensions.OpenWebif.__init__ import _

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

def setEPGSearchType(value):
	config.OpenWebif.webcache.epg_desc_search.value = value
	config.OpenWebif.webcache.epg_desc_search.save()
	return {
		"result": True
	}

def getEPGSearchType():
	return {
		"result": True,
		"epgsearchtype": config.OpenWebif.webcache.epg_desc_search.value
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

def getShowName():
	return {
		"result": True,
		"showname": config.OpenWebif.identifier.value
	}

def getCustomName():
	return {
		"result": True,
		"customname": config.OpenWebif.identifier.custom.value
	}

def getBoxName():
	return {
		"result": True,
		"boxname": config.OpenWebif.identifier.text.value
	}

def getJsonFromConfig(cnf):
	if cnf.__class__.__name__ == "ConfigSelection" or cnf.__class__.__name__ == "ConfigSelectionNumber":
		if type(cnf.choices.choices) == dict:
			choices = []
			for choice in cnf.choices.choices:
				choices.append((choice, _(cnf.choices.choices[choice])))
		elif type(cnf.choices.choices[0]) == tuple:
			choices = []
			for choice_tuple in cnf.choices.choices:
				choices.append((choice_tuple[0], _(choice_tuple[1])))
		else:
			choices = []
			for choice in cnf.choices.choices:
				choices.append((choice, _(choice)))
				
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
	title = None
	if not len(configfiles.sections):
		configfiles.getConfigs()
	if key in configfiles.section_config:
		config_entries = configfiles.section_config[key][1]
		title = configfiles.section_config[key][0]
	if config_entries:
		for entry in config_entries:
			try:
				data = getJsonFromConfig(eval(entry.text or ""))
				text = _(entry.get("text", ""))
				if "limits" in data:
					text = "%s (%d - %d)" % (text, data["limits"][0], data["limits"][1])
				configs.append({
						"description": text,
						"path": entry.text or "",
						"data": data
					})
			except Exception, e:
				pass
	return {
		"result": True,
		"configs": configs,
		"title": title
	}

def getConfigsSections():
	if not len(configfiles.sections):
		configfiles.parseConfigFiles()
	return {
		"result": True,
		"sections": configfiles.sections
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

class ConfigFiles:
	def __init__(self):
		self.setupfiles = []
		self.sections = []
		self.section_config = {}
		self.allowedsections = ["usage", "userinterface", "recording", "subtitlesetup", "autolanguagesetup", "avsetup", "harddisk", "keyboard", "timezone", "time", "osdsetup", "epgsetup", "display", "remotesetup", "softcamsetup", "logs", "timeshift", "channelselection", "epgsettings", "softwareupdate", "pluginbrowsersetup"]
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
				self.setupfiles.append(setupfile)

	def parseConfigFiles(self):
		sections = []
		for setupfile in self.setupfiles:
#			print "[OpenWebif] loading configuration file :", setupfile
			setupfile = file(setupfile, 'r')
			setupdom = xml.etree.cElementTree.parse(setupfile)
			setupfile.close()
			xmldata = setupdom.getroot()
			for section in xmldata.findall("setup"):
				configs = []
				requires = section.get("requires")
				if requires and not SystemInfo.get(requires, False):
					continue;
				key = section.get("key")
				if key not in self.allowedsections:
					showOpenWebIF = section.get("showOpenWebIF")
					if showOpenWebIF == "1":
						self.allowedsections.append(key)
					else:
						continue
#				print "[OpenWebif] loading configuration section :", key
				for entry in section:
					if entry.tag == "item":
						requires = entry.get("requires")
						if requires and not SystemInfo.get(requires, False):
							continue;

						if int(entry.get("level", 0)) > config.usage.setup_level.index:
							continue
						configs.append(entry)
				if len(configs):
					sections.append({
						"key": key,
						"description": _(section.get("title"))
					})
					title = _(section.get("title", ""))
					self.section_config[key] = (title, configs)
		sections = sorted(sections, key=lambda k: k['description'])
		self.sections = sections

configfiles = ConfigFiles()
