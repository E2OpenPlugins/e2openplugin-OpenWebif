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
			bitrate = config.plugins.transcodingsetup.bitrate
			framerate = config.plugins.transcodingsetup.framerate
		except KeyError:
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>Transcoding Plugin is not installed or your STB does not support transcoding</e2statetext></e2simplexmlresult>'
		
		if len(request.args):
			for arg in request.args:
				config_changed = False
				if arg == "transcoding":
					transcoding_state = str(request.args[arg][0]).lower()
					if transcoding_state in ('true', '1', 'enabled', 'enable', 'active'):
						config.plugins.transcodingsetup.transcoding.value = "enable"
					elif transcoding_state in ('false', '0', 'disabled', 'disable', 'inactive'):
						config.plugins.transcodingsetup.transcoding.value = "disable"
					config_changed = True
				elif arg == "bitrate":
					try:
						new_bitrate = int(request.args[arg][0])
					except ValueError:
						return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>wrong argument for bitrate</e2statetext></e2simplexmlresult>'
					if new_bitrate < int(bitrate.limits[0][0]):
						new_bitrate = int(bitrate.limits[0][0])
					elif new_bitrate > int(bitrate.limits[0][1]):
						new_bitrate = int(bitrate.limits[0][1])
					if new_bitrate != config.plugins.transcodingsetup.bitrate.value:
						config.plugins.transcodingsetup.bitrate.value = new_bitrate
						config_changed = True
				elif arg == "framerate":
					new_framerate = request.args[arg][0]
					if not new_framerate in framerate.choices:
						new_framerate = framerate.value
					if new_framerate != config.plugins.transcodingsetup.framerate:
						config.plugins.transcodingsetup.framerate.value = new_framerate
						config_changed = True
				elif arg == "port":
					new_port = request.args[arg][0]
					if not new_port in port.choices:
						new_port = port.value
					if new_port != config.plugins.transcodingsetup.port.value:
						config.plugins.transcodingsetup.port.value = new_port
						config_changed = True
				if config_changed:
					config.plugins.transcodingsetup.save()
		ports = ""
		for port_available in port.choices:
			ports += port_available + ", "
		ports = ports.rstrip(', ')
		framerates = ""
		for framerate_available in framerate.choices:
			framerates += framerate_available + ", "
		framerates = framerates.rstrip(', ')
		bitrate_min = str(bitrate.limits[0][0])
		bitrate_max = str(bitrate.limits[0][1])

		return """<?xml version=\"1.0\" encoding=\"UTF-8\" ?>
				<e2configs>
					<e2config>
						<e2configname>transcoding</e2configname>
						<e2configvalue>%s</e2configvalue>
					</e2config>
					<e2config>
						<e2configname>port</e2configname>
						<e2configchoices>%s</e2configchoices>
						<e2configvalue>%s</e2configvalue>
					</e2config>
					<e2config>
						<e2configname>bitrate</e2configname>
						<e2configlimits>%s-%s</e2configlimits>
						<e2configvalue>%s</e2configvalue>
					</e2config>
					<e2config>
						<e2configname>framerate</e2configname>
						<e2configchoices>%s</e2configchoices>
						<e2configvalue>%s</e2configvalue>
					</e2config>
				</e2configs>""" %      (str(config.plugins.transcodingsetup.transcoding.value),
							ports, str(config.plugins.transcodingsetup.port.value),
							bitrate_min, bitrate_max, str(config.plugins.transcodingsetup.bitrate.value),
							framerates, str(config.plugins.transcodingsetup.framerate.value))
