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
from Components.SystemInfo import SystemInfo

class TranscodingController(resource.Resource):

	def __init__(self, path = ""):
		resource.Resource.__init__(self)

	def render(self, request):
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')

		encoder = 0
		numencoder = config.plugins.transcodingsetup.encodernum
		if SystemInfo["MultipleEncoders"]:
			encoders = ""
			for resolution_available in numencoder.choices:
				encoders += resolution_available + ", "
			encoders = encoders.rstrip(', ')
			if len(request.args):
				for arg in request.args:
					if arg == "encoder":
						try:
							encoder = int(request.args[arg][0])
							break
						except:
							return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2encoder>%s</e2encoder><e2configchoices>%s</e2configchoices><e2encodertext>wrong argument for encoder</e2encodertext></e2simplexmlresult>' % (request.args[arg][0], encoders)

		if encoder > len(numencoder.choices)-1:
			curencoder = encoder
			encoder = numencoder.getValue()
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2encoder>%s</e2encoder><e2configchoices>%s</e2configchoices></e2simplexmlresult>' % (curencoder, encoders)

		try:
			transcoding = config.plugins.transcodingsetup.transcoding
			port = config.plugins.transcodingsetup.port
			bitrate = config.plugins.transcodingsetup.encoder[encoder].bitrate
			framerate = config.plugins.transcodingsetup.encoder[encoder].framerate
			if SystemInfo["AdvancedTranscoding"]:
				resolution = config.plugins.transcodingsetup.encoder[encoder].resolution
				audiocodec = config.plugins.transcodingsetup.encoder[encoder].audiocodec
				videocodec = config.plugins.transcodingsetup.encoder[encoder].videocodec
				gopframeb = config.plugins.transcodingsetup.encoder[encoder].gopframeb
				gopframep = config.plugins.transcodingsetup.encoder[encoder].gopframep
				level = config.plugins.transcodingsetup.encoder[encoder].level
				profile = config.plugins.transcodingsetup.encoder[encoder].profile
		except KeyError:
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>Transcoding Plugin is not installed or your STB does not support transcoding</e2statetext></e2simplexmlresult>'

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
				if new_bitrate != config.plugins.transcodingsetup.encoder[encoder].bitrate.getValue():
					config.plugins.transcodingsetup.encoder[encoder].bitrate.setValue(new_bitrate)
					config_changed = True
			elif arg == "framerate":
				new_framerate = request.args[arg][0]
				if not new_framerate in framerate.choices:
					new_framerate = framerate.getValue()
				if new_framerate != config.plugins.transcodingsetup.encoder[encoder].framerate.getValue():
					config.plugins.transcodingsetup.encoder[encoder].framerate.setValue(new_framerate)
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
			if SystemInfo["AdvancedTranscoding"]:
				if arg == "automode":
					if (hasattr(config.plugins.transcodingsetup.encoder[int(encoder)], "bitrate") or hasattr(config.plugins.transcodingsetup.encoder[int(encoder)], "framerate")):
						new_automode = str(request.args[arg][0]).lower()
						if new_automode in ('true', '1', 'enabled', 'enable', 'active', 'on'):
							config.plugins.transcodingsetup.transcoding.setValue("On")
						elif new_automode in ('false', '0', 'disabled', 'disable', 'inactive', 'off'):
							config.plugins.transcodingsetup.transcoding.setValue("Off")
						config_changed = True
				elif arg == "resolution":
					new_resolution = request.args[arg][0]
					if not new_resolution in resolution.choices:
						new_resolution = resolution.getValue()
					if new_resolution != config.plugins.transcodingsetup.encoder[encoder].resolution.getValue():
						config.plugins.transcodingsetup.encoder[encoder].resolution.setValue(new_resolution)
						config_changed = True
				elif arg == "audiocodec":
					new_audiocodec = request.args[arg][0]
					if not new_audiocodec in audiocodec.choices:
						new_audiocodec = audiocodec.getValue()
					if new_audiocodec != config.plugins.transcodingsetup.encoder[encoder].audiocodec.getValue():
						config.plugins.transcodingsetup.encoder[encoder].audiocodec.setValue(new_audiocodec)
						config_changed = True
				elif arg == "videocodec":
					new_videocodec = request.args[arg][0]
					if not new_videocodec in videocodec.choices:
						new_videocodec = videocodec.getValue()
					if new_videocodec != config.plugins.transcodingsetup.encoder[encoder].videocodec.getValue():
						config.plugins.transcodingsetup.encoder[encoder].videocodec.setValue(new_videocodec)
						config_changed = True
				elif arg == "gopframeb":
					new_gopframeb = int(request.args[arg][0])
					if new_gopframeb < int(gopframeb.limits[0][0]):
						new_gopframeb = int(gopframeb.limits[0][0])
					elif new_gopframeb > int(gopframeb.limits[0][1]):
						new_gopframeb = int(gopframeb.limits[0][1])
					if new_gopframeb != config.plugins.transcodingsetup.encoder[encoder].gopframeb.getValue():
						config.plugins.transcodingsetup.encoder[encoder].gopframeb.setValue(new_gopframeb)
						config_changed = True
				elif arg == "gopframep":
					new_gopframep = int(request.args[arg][0])
					if new_gopframep < int(gopframep.limits[0][0]):
						new_gopframep = int(gopframep.limits[0][0])
					elif new_gopframep > int(gopframep.limits[0][1]):
						new_gopframep = int(gopframep.limits[0][1])
					if new_gopframep != config.plugins.transcodingsetup.encoder[encoder].gopframep.getValue():
						config.plugins.transcodingsetup.encoder[encoder].gopframep.setValue(new_gopframep)
						config_changed = True
				elif arg == "level":
					new_level = request.args[arg][0]
					if not new_level in level.choices:
						new_level = level.getValue()
					if new_level != config.plugins.transcodingsetup.encoder[encoder].level.getValue():
						config.plugins.transcodingsetup.encoder[encoder].level.setValue(new_level)
						config_changed = True
				elif arg == "profile":
					new_profile = request.args[arg][0]
					if not new_profile in profile.choices:
						new_profile = profile.getValue()
					if new_profile != config.plugins.transcodingsetup.encoder[encoder].profile.getValue():
						config.plugins.transcodingsetup.encoder[encoder].profile.setValue(new_profile)
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
		if SystemInfo["AdvancedTranscoding"]:
			resolutions = ""
			for resolution_available in resolution.choices:
				resolutions += resolution_available + ", "
			resolutions = resolutions.rstrip(', ')
			audiocodecs = ""
			for audiocodec_available in audiocodec.choices:
				audiocodecs += audiocodec_available + ", "
			audiocodecs = audiocodecs.rstrip(', ')
			videocodecs = ""
			for videocodec_available in videocodec.choices:
				videocodecs += videocodec_available + ", "
			videocodecs = videocodecs.rstrip(', ')
			gopframeb_min = str(gopframeb.limits[0][0])
			gopframeb_max = str(gopframeb.limits[0][1])
			gopframep_min = str(gopframep.limits[0][0])
			gopframep_max = str(gopframep.limits[0][1])
			levels = ""
			for level_available in level.choices:
				levels += level_available + ", "
			levels = levels.rstrip(', ')
			profiles = ""
			for profile_available in profile.choices:
				profiles += profile_available + ", "
			profiles = profiles.rstrip(', ')

			return """<?xml version=\"1.0\" encoding=\"UTF-8\" ?>
					<e2configs>
						<e2config>
							<e2configname>transcoding</e2configname>
							<e2configvalue>%s</e2configvalue>
						</e2config>
						<e2config>
							<e2configname>encoder</e2configname>
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
						<e2config>
							<e2configname>automode</e2configname>
							<e2configvalue>%s</e2configvalue>
						</e2config>
						<e2config>
							<e2configname>resolution</e2configname>
							<e2configchoices>%s</e2configchoices>
							<e2configvalue>%s</e2configvalue>
						</e2config>
						<e2config>
							<e2configname>audiocodec</e2configname>
							<e2configchoices>%s</e2configchoices>
							<e2configvalue>%s</e2configvalue>
						</e2config>
						<e2config>
							<e2configname>videocodec</e2configname>
							<e2configchoices>%s</e2configchoices>
							<e2configvalue>%s</e2configvalue>
						</e2config>
						<e2config>
							<e2configname>gopframeb</e2configname>
							<e2configlimits>%s-%s</e2configlimits>
							<e2configvalue>%s</e2configvalue>
						</e2config>
						<e2config>
							<e2configname>gopframep</e2configname>
							<e2configlimits>%s-%s</e2configlimits>
							<e2configvalue>%s</e2configvalue>
						</e2config>
						<e2config>
							<e2configname>level</e2configname>
							<e2configchoices>%s</e2configchoices>
							<e2configvalue>%s</e2configvalue>
						</e2config>
						<e2config>
							<e2configname>profile</e2configname>
							<e2configchoices>%s</e2configchoices>
							<e2configvalue>%s</e2configvalue>
						</e2config>
					</e2configs>""" % (str(config.plugins.transcodingsetup.transcoding.getValue()),
								str(encoder),
								port_min, port_max, str(config.plugins.transcodingsetup.port.getValue()),
								bitrates, str(config.plugins.transcodingsetup.encoder[encoder].bitrate.getValue()),
								framerates, str(config.plugins.transcodingsetup.encoder[encoder].framerate.getValue()),
								str(config.plugins.transcodingsetup.encoder[encoder].automode.getValue()),
								resolutions, str(config.plugins.transcodingsetup.encoder[encoder].resolution.getValue()),
								audiocodecs, str(config.plugins.transcodingsetup.encoder[encoder].audiocodec.getValue()),
								videocodecs, str(config.plugins.transcodingsetup.encoder[encoder].videocodec.getValue()),
								gopframeb_min, gopframeb_max, str(config.plugins.transcodingsetup.encoder[encoder].gopframeb.getValue()),
								gopframep_min, gopframep_max, str(config.plugins.transcodingsetup.encoder[encoder].gopframep.getValue()),
								levels, str(config.plugins.transcodingsetup.encoder[encoder].level.getValue()),
								profiles, str(config.plugins.transcodingsetup.encoder[encoder].profile.getValue()))
		else:
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
					</e2configs>""" % (str(config.plugins.transcodingsetup.transcoding.getValue()),
								port_min, port_max, str(config.plugins.transcodingsetup.port.getValue()),
								bitrates, str(config.plugins.transcodingsetup.encoder[encoder].bitrate.getValue()),
								framerates, str(config.plugins.transcodingsetup.encoder[encoder].framerate.getValue()),
								)

