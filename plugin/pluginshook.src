loaded_plugins = []

def addExternalChild(plugin_args):
	if len(plugin_args) == 4:
		for plugin in loaded_plugins:
			if plugin[0] == plugin_args[0]:
				print "[OpenWebif] error: path '%s' already registered" % plugin[0]
				return
		loaded_plugins.append(plugin_args)
