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

class TranscodingController(resource.Resource):

	def __init__(self, path = ""):
		resource.Resource.__init__(self)

	def render(self, request):
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')
		try:
			transcoding = config.plugins.transcodingsetup.transcoding
			port = config.plugins.transcodingsetup.port
			bitrate = config.plugins.transcodingsetup.encoder[0].bitrate
			framerate = config.plugins.transcodingsetup.encoder[0].framerate
		except KeyError:
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>Transcoding Plugin is not installed or your STB does not support transcoding</e2statetext></e2simplexmlresult>'
		
		if len(request.args):
			for arg in request.args:
				config_changed = False
				if arg == "transcoding":
					transcoding_state = str(request.args[arg][0]).lower()
					if transcoding_state in ('true', '1', 'enabled', 'enable', 'active'):
						config.plugins.transcodingsetup.transcoding.setValue("enable")
					elif transcoding_state in ('false', '0', 'disabled', 'disable', 'inactive'):
						config.plugins.transcodingsetup.transcoding.setValue("disable")
					config_changed = True
				elif arg == "bitrate":
					try:
						new_bitrate = request.args[arg][0]
					except ValueError:
						return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>wrong argument for bitrate</e2statetext></e2simplexmlresult>'
					if not new_bitrate in bitrate.choices:
						new_bitrate = bitrate.getValue()
					if new_bitrate != config.plugins.transcodingsetup.encoder[0].bitrate.getValue():
						config.plugins.transcodingsetup.encoder[0].bitrate.setValue(new_bitrate)
						config_changed = True
				elif arg == "framerate":
					new_framerate = request.args[arg][0]
					if not new_framerate in framerate.choices:
						new_framerate = framerate.getValue()
					if new_framerate != config.plugins.transcodingsetup.encoder[0].framerate.getValue():
						config.plugins.transcodingsetup.encoder[0].framerate.setValue(new_framerate)
						config_changed = True
				elif arg == "port":
					new_port = int(request.args[arg][0])
					if new_port < int(port.limits[0][0]):
						new_port = int(port.limits[0][0])
					elif new_port > int(port.limits[0][1]):
						new_port = int(port.limits[0][1])
					if new_port != config.plugins.transcodingsetup.port.getValue():
						config.plugins.transcodingsetup.port.setValue(new_port)
						config_changed = True
			if config_changed:
				config.plugins.transcodingsetup.save()
		port_min = str(port.limits[0][0])
		port_max = str(port.limits[0][1])
		framerates = ""
		for framerate_available in framerate.choices:
			framerates += framerate_available + ", "
		framerates = framerates.rstrip(', ')
		bitrates = ""
		for bitrate_available in bitrate.choices:
			bitrates += bitrate_available + ", "
		bitrates = bitrates.rstrip(', ')

		return """<?xml version=\"1.0\" encoding=\"UTF-8\" ?>
				<e2configs>
					<e2config>
						<e2configname>transcoding</e2configname>
						<e2configvalue>%s</e2configvalue>
					</e2config>
					<e2config>
						<e2configname>port</e2configname>
						<e2configlimits>%s-%s</e2configlimits>
						<e2configvalue>%s</e2configvalue>
					</e2config>
					<e2config>
						<e2configname>bitrate</e2configname>
						<e2configchoices>%s</e2configchoices>
						<e2configvalue>%s</e2configvalue>
					</e2config>
					<e2config>
						<e2configname>framerate</e2configname>
						<e2configchoices>%s</e2configchoices>
						<e2configvalue>%s</e2configvalue>
					</e2config>
				</e2configs>""" %      (str(config.plugins.transcodingsetup.transcoding.getValue()),
							port_min, port_max, str(config.plugins.transcodingsetup.port.getValue()),
							bitrates, str(config.plugins.transcodingsetup.encoder[0].bitrate.getValue()),
							framerates, str(config.plugins.transcodingsetup.encoder[0].framerate.getValue()))