# -*- coding: utf-8 -*-

##############################################################################
#                    2013 E2OpenPlugins, tweaked by oe-alliance              #
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
		if hasattr(config.plugins.transcodingsetup.encoder[int(encoder)], feature):
			try:
				encoder_features[feature] = getattr(config.plugins.transcodingsetup.encoder[int(encoder)], feature)
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
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2error>Transcoding Plugin is not installed or your STB does not support transcoding</error></e2simplexmlresult>'
		
		encoders = config.plugins.transcodingsetup.encodernum.choices
		if len(request.args):
			config_changed = False
			if "port" in request.args:
				new_port = int(request.args['port'][0])
				attr_min = str(port.limits[0][0])
				attr_max = str(port.limits[0][1])
				if new_port < int(port.limits[0][0]) or new_port > int(port.limits[0][1]):
					return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><port>%s</port><e2configlimits>%s-%s</e2configlimits><e2error>choosen port is not available</error></e2simplexmlresult>' % (new_port, attr_min, attr_max)
				if new_port != port.value:
					port.setValue(new_port)
					config_changed = True

			encoder = 0
			numencoder = config.plugins.transcodingsetup.encodernum
			if "encoder" in request.args:
				numencoders = ""
				for enc in encoders:
					numencoders += enc + ", "
				numencoders = numencoders.rstrip(', ')
				new_encoder = int(request.args["encoder"][0])
				if new_encoder > len(encoders)-1:
					return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2encoder>%s</e2encoder><e2configchoices>%s</e2configchoices><e2error>choosen encoder is not available</error></e2simplexmlresult>' % (new_encoder, numencoders)
				if new_encoder != numencoder.value:
					numencoder.setValue(new_encoder)
					config_changed = True

			encoder_features = get_transcoding_features(encoder)
			for arg in request.args:
				if arg in encoder_features:
					attr = encoder_features[arg]
					if hasattr(attr, "limits"):
						try:
							new_value = int(request.args[arg][0])
						except ValueError:
							return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><%s>%s</%s><e2configlimits>%s-%s</e2configlimits><e2error>choosen value is not available</error></e2simplexmlresult>' % (arg, new_value, arg, attr_min, attr_max)
						if new_value < int(attr.limits[0][0]):
							new_value = int(attr.limits[0][0])
						elif new_value > int(attr.limits[0][1]):
							new_value = int(attr.limits[0][1])
						if new_value != attr.value:
							attr.setValue(new_value)
							config_changed = True
					elif hasattr(attr, "choices"):
						new_value = request.args[arg][0]
						choices = ""
						for choice in attr.choices:
							choices += choice + ", "
						choices = choices.rstrip(', ')
						if not str(new_value) in attr.choices and not int(new_value) in attr.choices:
							return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><%s>%s</%s><e2configchoices>%s</e2configchoices><e2error>choosen value is not available</error></e2simplexmlresult>' % (arg, new_value, arg, choices)
						if new_value != attr.value:
							attr.setValue(new_value)
							config_changed = True
				elif arg not in ("encoder", "port"):
					return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2error>choosen feature %s is not available</error></e2simplexmlresult>' % arg
			if config_changed:
				config.plugins.transcodingsetup.save()

		str_result = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<e2configs>\n"
		
		attr, arg = port, "port"
		value = str(attr.value)
		attr_min = str(attr.limits[0][0])
		attr_max = str(attr.limits[0][1])
		str_result += "<e2config>\n<e2configname>%s</e2configname>\n<e2configlimits>%s-%s</e2configlimits>\n<e2configvalue>%s</e2configvalue>\n</e2config>\n" % (arg, attr_min, attr_max, value)
		for encoder in encoders:
			encoder_features = get_transcoding_features(encoder)
			if len(encoder_features):
				str_result += "<e2encoder number=\"%s\">\n" % str(encoder)
			for arg in encoder_features:
				attr = encoder_features[arg]
				value = attr.value
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
				str_result += "</e2encoder>\n"
		str_result += "</e2configs>\n"
		return str_result

