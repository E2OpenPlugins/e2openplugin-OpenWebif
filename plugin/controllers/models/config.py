from Components.config import config

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
	