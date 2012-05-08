from enigma import eEnv
from Components.SystemInfo import SystemInfo
from Components.config import config
import xml.etree.cElementTree

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
		
	elif cnf.__class__.__name__ == "ConfigNumber" or cnf.__class__.__name__ == "ConfigInteger":
		return {
			"result": True,
			"type": "number",
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
		elif cnf.__class__.__name__ == "ConfigNumber" or cnf.__class__.__name__ == "ConfigInteger":
			cnf.value = int(value)
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
	
	setupfile = file(eEnv.resolve('${datadir}/enigma2/setup.xml'), 'r')
	setupdom = xml.etree.cElementTree.parse(setupfile)
	setupfile.close()
	xmldata = setupdom.getroot()
	for section in xmldata.findall("setup"):
		if section.get("key") != key:
			continue
			
		for entry in section:
			if entry.tag == "item":
				requires = entry.get("requires")
				if requires and not SystemInfo.get(requires, False):
					continue;
				
				if int(entry.get("level", 0)) > config.usage.setup_level.index:
					continue
				
				try:
					configs.append({
						"description": entry.get("text", ""),
						"path": entry.text or "",
						"data": getJsonFromConfig(eval(entry.text or ""))
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
	allowedsections = ["usage", "recording", "subtitlesetup", "autolanguagesetup", "avsetup", "harddisk", "keyboard", "timezone"]
	sections = []
	
	setupfile = file(eEnv.resolve('${datadir}/enigma2/setup.xml'), 'r')
	setupdom = xml.etree.cElementTree.parse(setupfile)
	setupfile.close()
	xmldata = setupdom.getroot()
	for section in xmldata.findall("setup"):
		key = section.get("key")
		if key not in allowedsections:
			continue
		
		count = 0
		for entry in section:
			if entry.tag == "item":
				requires = entry.get("requires")
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
	