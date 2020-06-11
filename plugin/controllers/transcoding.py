# -*- coding: utf-8 -*-

##############################################################################
#                        2013 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
import six
from twisted.web import resource
from Components.config import config
from Plugins.Extensions.OpenWebif.controllers.utilities import getUrlArg


def get_transcoding_features(encoder=0):
	features = {
		"automode": "automode",
		"bitrate": "bitrate",
		"framerate": "framerate",
		"resolution": "display_format",
		"aspectratio": "aspectratio",
		"audiocodec": "audio_codec",
		"videocodec": "video_codec",
		"gopframeb": "gop_frameb",
		"gopframep": "gop_framep",
		"level": "level",
		"profile": "profile",
		"width": "width",  # not in use
		"height": "height",  # not in use
	}
	encoder_features = {}
	for feature in features:
		if encoder == 0:
			if hasattr(config.plugins.transcodingsetup, feature):
				try:
					encoder_features[feature] = getattr(config.plugins.transcodingsetup, feature)
				except:  # noqa: E722
					pass
		else:
			if hasattr(config.plugins.transcodingsetup, "%s_%s" % (feature, encoder)):
				try:
					encoder_features[feature] = getattr(config.plugins.transcodingsetup, "%s_%s" % (feature, encoder))
				except:  # noqa: E722
					pass
	return encoder_features


class TranscodingController(resource.Resource):
	def render(self, request):
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')
		try:
			port = config.plugins.transcodingsetup.port
		except:  # noqa: E722
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>Transcoding Plugin is not installed or your STB does not support transcoding</e2statetext></e2simplexmlresult>'

		encoders = (0, 1)
		if len(request.args):
			config_changed = False
			new_port = getUrlArg(request, "port")
			if new_port:
				if self.setcheck(config.plugins.transcodingsetup.port, new_port):
					config_changed = True
				else:
					return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>wrong argument for port</e2statetext></e2simplexmlresult>' 
			encoder = 0
			_encoder = getUrlArg(request, "encoder")
			if _encoder:
				try:
					encoder = int(_encoder)
				except ValueError:
					return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>wrong argument for encoder</e2statetext></e2simplexmlresult>'
			encoder_features = get_transcoding_features(encoder)
			if not len(encoder_features):
				return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>choosen encoder is not available</e2statetext></e2simplexmlresult>'


			for arg in request.args:
				a = six.ensure_text(arg)
				if a in encoder_features:
					attr = encoder_features[arg]
					aa = six.ensure_binary(arg)
					new_value = six.ensure_text(request.args[aa][0])
					if self.setcheck(attr, new_value):
						config_changed = True
					else:
						return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>wrong argument for %s</e2statetext></e2simplexmlresult>' % arg
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
				str_result += self.getparam(attr, arg)
			if len(encoder_features):
				str_result += "</encoder>\n"
		attr, arg = port, "port"
		str_result += self.getparam(attr, arg)

		str_result += "</e2configs>\n" 
		return str_result


# check methode for setting parameter
	def setcheck(self, attr, new_value):
		if hasattr(attr, "limits"):
			try:
				new_value = int(new_value)
			except ValueError:
				return False
			if new_value < int(attr.limits[0][0]):
				new_value = int(attr.limits[0][0])
			elif new_value > int(attr.limits[0][1]):
				new_value = int(attr.limits[0][1])
		elif hasattr(attr, "choices"):
			if new_value not in attr.choices:
				return False
		attr.value = new_value
		return True


# build parameter value and limit or choices
	def getparam(self, attr, arg):
		value = str(attr.value)
		str_result = "<e2config>\n<e2configname>%s</e2configname>\n" % arg
		if hasattr(attr, "limits"):
			attr_min = str(attr.limits[0][0])
			attr_max = str(attr.limits[0][1])
			str_result += "<e2configlimits>%s-%s</e2configlimits>\n" % (attr_min, attr_max)
		elif hasattr(attr, "choices"):
			choices = ""
			for choice in attr.choices:
				choices += choice + ", "
			choices = choices.rstrip(', ')
			str_result += "<e2configchoices>%s</e2configchoices>\n" % choices
		str_result += "<e2configvalue>%s</e2configvalue>\n</e2config>\n" % value
		return str_result
