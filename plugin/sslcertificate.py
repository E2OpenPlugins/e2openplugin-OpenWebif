# -*- coding: utf-8 -*-

##############################################################################
#                        2011 E2OpenPlugins                                  #
#                                                                            #
#  This file is open source software; you can redistribute it and/or modify  #
#     it under the terms of the GNU General Public License version 2 as      #
#               published by the Free Software Foundation.                   #
#                                                                            #
##############################################################################

from OpenSSL import crypto
from socket import gethostname
from time import time

from Tools.Directories import resolveFilename, SCOPE_CONFIG

import os

CA_FILE = resolveFilename(SCOPE_CONFIG, "ca.pem")
KEY_FILE = resolveFilename(SCOPE_CONFIG, "key.pem")
CERT_FILE = resolveFilename(SCOPE_CONFIG, "cert.pem")

class SSLCertificateGenerator:

	def __init__(self):
		# define some defaults 
		self.type = crypto.TYPE_RSA
		self.bits = 1024
		self.digest = 'sha1'
		self.certSubjectOptions = {
			'O': 'Home',
			'OU': gethostname(),
			'CN': gethostname()
		}

	# generate and install a self signed SSL certificate if none exists
	def installCertificates(self):
		if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
			return
		keypair = self.__genKeyPair()
		certificate = self.__genCertificate(keypair)
		print "[OpenWebif] Install newly generated key pair and certificate"
		open(KEY_FILE, "wt").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, keypair))
		open(CERT_FILE, "wt").write(crypto.dump_certificate(crypto.FILETYPE_PEM, certificate))

	# generate a key pair
	def __genKeyPair(self):
		keypair = crypto.PKey()
		keypair.generate_key(self.type, self.bits)
		return keypair

	# create a SSL certificate and sign it
	def __genCertificate(self, keypair):
		certificate = crypto.X509()
		subject = certificate.get_subject()
		for key, val in self.certSubjectOptions.iteritems():
			setattr(subject, key, val)
		certificate.set_serial_number( int(time()) )
		certificate.gmtime_adj_notBefore( 0 )
		certificate.gmtime_adj_notAfter( 60*60*24*365*5 )
		certificate.set_issuer(subject)
		certificate.set_pubkey(keypair)
		certificate.sign(keypair, self.digest)
		return certificate

