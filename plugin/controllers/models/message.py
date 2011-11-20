##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from Screens.MessageBox import MessageBox

def sendMessage(self, request):
	self.msgtext = ""
	self.msgtype = 2
	self.msgtimeout = -1
	
	if "text" in request.args.keys():
		self.msgtext = request.args["text"][0]
	if "type" in request.args.keys():
		self.msgtype = int(request.args["type"][0])
	if "timeout" in request.args.keys():
		self.msgtimeout = int(request.args["timeout"][0])
		
	self.session.open(MessageBox, self.msgtext, type=self.msgtype, timeout=self.msgtimeout)

	return {
		"result": True,
		"message": "Message successfully sent!"
	}