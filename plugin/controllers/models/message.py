##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################
from Screens.MessageBox import MessageBox

lastreply = None

def messageReply(reply):
	global lastreply
	lastreply = reply
	
def sendMessage(session, message, ttype, timeout):
	if ttype not in [MessageBox.TYPE_YESNO, MessageBox.TYPE_INFO, MessageBox.TYPE_WARNING, MessageBox.TYPE_ERROR]:
		ttype = MessageBox.TYPE_INFO
		
	if ttype == MessageBox.TYPE_YESNO:
		session.openWithCallback(messageReply, MessageBox, message, type=ttype, timeout=timeout)
	else:
		session.open(MessageBox, message, type=ttype, timeout=timeout)
		
	return {
		"result": True,
		"message": "Message sent successfully!"
	}
	
def getMessageAnswer():
	global lastreply
	reply = lastreply
	lastreply = None
	
	if reply is None:
		return {
			"result": False,
			"message": "No answer in time"
		}
		
	return {
		"result": True,
		"message": "Answer is YES!" if reply else "Answer is NO!"
	}