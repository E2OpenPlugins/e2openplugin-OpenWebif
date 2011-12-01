from Components.config import config

def addCollapsedMenu(name):
	tags = config.OpenWebif.webcache.collapsedmenus.value.split("|")
	if name not in tags:
		tags.append(name)
		
	config.OpenWebif.webcache.collapsedmenus.value = "|".join(tags).strip("|")
	config.OpenWebif.webcache.collapsedmenus.save()
	
	print "add", config.OpenWebif.webcache.collapsedmenus.value
	
	return {
		"result": True
	}
	
def removeCollapsedMenu(name):
	tags = config.OpenWebif.webcache.collapsedmenus.value.split("|")
	if name in tags:
		tags.remove(name)

	config.OpenWebif.webcache.collapsedmenus.value = "|".join(tags).strip("|")
	config.OpenWebif.webcache.collapsedmenus.save()

	print "remove", config.OpenWebif.webcache.collapsedmenus.value

	return {
		"result": True
	}

def getCollapsedMenus():
	return {
		"result": True,
		"collapsed": config.OpenWebif.webcache.collapsedmenus.value.split("|")
	}