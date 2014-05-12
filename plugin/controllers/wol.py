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

class WOLSetupController(resource.Resource):

	def __init__(self, session, path = ""):
		resource.Resource.__init__(self)
		self.session = session

	def render(self, request):
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')
		try:
			wol_active = config.plugins.wolconfig.activate.value
			wol_location = config.plugins.wolconfig.location.value
		except KeyError:
			return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>WOLSetup plugin is not installed or your STB does not support WOL</e2statetext></e2simplexmlresult>'

		if len(request.args):
			config_changed = False
			if "wol" in request.args:
				wol_state = str(request.args["wol"][0]).lower()
				if wol_state in ('true', '1', 'enabled', 'enable', 'active'):
					config.plugins.wolconfig.activate.value = True
				elif wol_state in ('false', '0', 'disabled', 'disable', 'inactive'):
					config.plugins.wolconfig.activate.value = False
				if wol_active != config.plugins.wolconfig.activate.value:
					config_changed = True
			elif "location" in request.args:
				location = request.args["location"][0]
				if not location in config.plugins.wolconfig.location.choices:
					location = wol_location
				if location != config.plugins.wolconfig.location.value:
					config.plugins.wolconfig.location.value = location
					config_changed = True
			elif "wolstandby" in request.args:
				wol_standby = str(request.args["wolstandby"][0]).lower()
				if wol_standby in ('true', '1', 'enabled', 'enable', 'active'):
					try:
						from Plugins.SystemPlugins.WOLSetup.plugin import WOLSetup, _deviseWOL, _flagForceEnable, _flagSupportWol, _tryQuitTable, _ethDevice
						from Screens.Standby import TryQuitMainloop
					except ImportError:
						return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>WOLSetup plugin is not installed or your STB does not support WOL</e2statetext></e2simplexmlresult>'
					WOLSetup.ActivateWOL(self.session, writeDevice=True)
					self.session.open(TryQuitMainloop, _tryQuitTable["deepstandby"])
			if config_changed:
				config.plugins.wolconfig.save()

		locations = ""
		for location_available in config.plugins.wolconfig.location.choices:
			locations += location_available + ", "
		locations = locations.rstrip(', ')

		return """<?xml version=\"1.0\" encoding=\"UTF-8\" ?>
				<e2configs>
					<e2config>
						<e2configname>wol_active</e2configname>
						<e2configvalue>%s</e2configvalue>
					</e2config>
					<e2config>
						<e2configname>wol_location</e2configname>
						<e2configchoices>%s</e2configchoices>
						<e2configvalue>%s</e2configvalue>
					</e2config>
				</e2configs>""" %      (str(config.plugins.wolconfig.activate.value),
							locations, str(config.plugins.wolconfig.location.value))

class WOLClientController(resource.Resource):

	def __init__(self, path = ""):
		resource.Resource.__init__(self)

	def render(self, request):
		import struct, socket
		request.setHeader('Content-type', 'application/xhtml+xml')
		request.setHeader('charset', 'UTF-8')
		if len(request.args):
			port = 9
			mac = ""
			ip = ""
			if "port" in request.args:
				man_port = str(request.args["port"][0]).lower()
				try:
					port = int(man_port)
				except ValueError:
					pass
			if "mac" in request.args:
				mac = str(request.args["mac"][0]).lower()
				mac = mac.split(':')
				if len(mac) != 6:
					return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>MAC address invalid see example: AA:BB:CC:DD:EE:FF</e2statetext></e2simplexmlresult>'
			if "ip" in request.args:
				ip = str(request.args["ip"][0]).lower()
				ip = ip.split('.')
				if len(ip) != 4:
					return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>IP address invalid see example: 192.168.2.10</e2statetext></e2simplexmlresult>'
				try:
					for digit in ip:
						is_int = int(digit)
				except ValueError:
					return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>IP address invalid see example: 192.168.2.10</e2statetext></e2simplexmlresult>'
				ip = ip[0] + "." + ip[1] + "." + ip[2] + ".255"
			if ip and mac:
				mac_struct = struct.pack('BBBBBB', int(mac[0], 16), int(mac[1], 16), int(mac[2], 16), int(mac[3], 16), int(mac[4], 16), int(mac[5], 16))
				magic = '\xff' * 6 + mac_struct * 16
				my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
				my_socket.sendto(magic,(ip,port))
				my_socket.close()
				return """<?xml version=\"1.0\" encoding=\"UTF-8\" ?><e2simplexmlresult><e2state>true</e2state><e2statetext>MagicPacket send to IP %s at port %d</e2statetext></e2simplexmlresult> """ % (ip, port)
			else:
				return '<?xml version="1.0" encoding="UTF-8" ?><e2simplexmlresult><e2state>false</e2state><e2statetext>IP address and MAC address are mandatory arguments</e2statetext></e2simplexmlresult>'
