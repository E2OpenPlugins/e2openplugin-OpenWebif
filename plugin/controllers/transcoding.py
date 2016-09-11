# -*- coding: utf-8 -*-

##############################################################################
#                        2013 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from twisted.web import static, resource, http
from Components.config import config

def get_transcoding_features(encoder = 0):
	features = {
		"automode": "automode",
		"bitrate": "bitrate",
		"framerate": "framerate",
		"resolution": "display_format",
		"aspectratio": "aspectratio",
		"audiocodec" : "audio_codec",
		"videocodec" : "video_codec",
		"gopframeb" : "gop_frameb",
		"gopframep" :"gop_framep",
		"level" : "level",
		"profile" : "profile",
		"width" : "width", # not in use
		"height" : "height", # not in use
	}
	encoder_features = {}
	for feature in features:
		if encoder == 0:
			if hasattr(config.plugins.transcodingsetup, feature):
				try:
					encoder_features[feature] = getattr(config.plugins.transcodingsetup, feature)
				except KeyError:
					pass
		else:
			if hasattr(config.plugins.transcodingsetup, "%s_%s" % (feature, encoder)):
				try:
					encoder_features[feature] = getattr(config.plugins.transcodingsetup, "%s_%s" % (feature, encoder))
				except KeyError:
					pass
	return encoder_features

class TranscodingController(resource.Resource):

	def __init__(self, path = ""):
		resource.Resource.__init__(self)

	def render(self, request):
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')
		try:
			port = config.plugins.transcodingsetup.port
		except KeyError:
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>Transcoding Plugin is not installed or your STB does not support transcoding</e2statetext></e2simplexmlresult>'

		encoders = (0, 1)
		if len(request.args):
			config_changed = False
			if "port" in request.args:
				new_port = request.args["port"][0]
				if not new_port in port.choices:
					new_port = port.value
				if new_port != config.plugins.transcodingsetup.port.value:
					config.plugins.transcodingsetup.port.value = new_port
					config_changed = True
			encoder = 0
			if "encoder" in request.args:
				try:
					encoder = int(request.args["encoder"][0])
				except ValueError:
					return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>wrong argument for encoder</e2statetext></e2simplexmlresult>'
			encoder_features = get_transcoding_features(encoder)
			if not len(encoder_features):
				return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>choosen encoder is not available</e2statetext></e2simplexmlresult>'

			for arg in request.args:
				if arg in encoder_features:
					attr = encoder_features[arg]
					if hasattr(attr, "limits"):
						try:
							new_value = int(request.args[arg][0])
						except ValueError:
							return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>wrong argument for %s</e2statetext></e2simplexmlresult>' % arg
						if new_value < int(attr.limits[0][0]):
							new_value = int(attr.limits[0][0])
						elif new_value > int(attr.limits[0][1]):
							new_value = int(attr.limits[0][1])
						if new_value != attr.value:
							attr.value = new_value
							config_changed = True
					elif hasattr(attr, "choices"):
						new_value = request.args[arg][0]
						if not new_value in attr.choices:
							return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>wrong argument for %s</e2statetext></e2simplexmlresult>' % arg
						if new_value != attr.value:
							attr.value = new_value
							config_changed = True
				elif arg not in ("encoder", "port"):
					return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>choosen feature %s is not available</e2statetext></e2simplexmlresult>' % arg
			if config_changed:
				config.plugins.transcodingsetup.save()

		str_result = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<e2configs>\n"

		for encoder in encoders:
			encoder_features = get_transcoding_features(encoder)
			if len(encoder_features):
				str_result += "<encoder number=\"%s\">\n" % str(encoder)
			for arg in encoder_features:
				attr = encoder_features[arg]
				value = str(attr.value)
				if hasattr(attr, "limits"):
					attr_min = str(attr.limits[0][0])
					attr_max = str(attr.limits[0][1])
					str_result += "<e2config>\n<e2configname>%s</e2configname>\n<e2configlimits>%s-%s</e2configlimits>\n<e2configvalue>%s</e2configvalue>\n</e2config>\n" % (arg, attr_min, attr_max, value)
				elif hasattr(attr, "choices"):
					choices = ""
					for choice in attr.choices:
						choices += choice + ", "
					choices = choices.rstrip(', ')
					str_result += "<e2config>\n<e2configname>%s</e2configname>\n<e2configchoices>%s</e2configchoices>\n<e2configvalue>%s</e2configvalue>\n</e2config>\n" % (arg, choices, value)
			if len(encoder_features):
				str_result += "</encoder>\n"
		attr, arg = port, "port"
		value = str(attr.value)
		choices = ""
		for choice in attr.choices:
			choices += choice + ", "
		choices = choices.rstrip(', ')
		str_result += "<e2config>\n<e2configname>%s</e2configname>\n<e2configchoices>%s</e2configchoices>\n<e2configvalue>%s</e2configvalue>\n</e2config>\n</e2configs>\n" % (arg, choices, value)
		return str_result
