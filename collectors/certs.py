#!/usr/bin/python

# TrustedCertCollector class for PICT (Post-Infection Collection Toolkit)

import os, subprocess
import re
from datetime import datetime, date
from collector import Collector
import tools.util as util

class TrustedCertCollector(Collector):

	def printStartInfo(self):
		print "Collecting certificate data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		filename = "trusted_certificates.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		
		f.write("Certificate trust settings\n-----------------------------\n")
		for user in self.userList:
			f.write("For user {0}:\n\n".format(user))
			output = os.popen("sudo -u {0} security dump-trust-settings 2>&1".format(user)).read().rstrip()
			f.write(output + "\n\n")
				
		f.write("Admin certificate info\n-----------------------------\n")
		output = os.popen("security dump-trust-settings -d").read().rstrip()
		f.write(output + "\n\n")
				
		f.write("System certificate info\n-----------------------------\n")
		output = os.popen("security dump-trust-settings -s").read().rstrip()
		f.write(output + "\n\n")
				
		f.write("All certificates\n-----------------------------\n")
		output = self.collectAllCerts()
		f.write(output)
		
		f.close
		
		# Add any paths to self.pathsToCollect
		
		Collector.collect(self)

	def collectAllCerts(self):
		
		# Get raw cert data
		certData = os.popen("security find-certificate -a -p").read().rstrip()
		
		# Build list of all certs in the certData string
		certPattern = "(-----BEGIN .+?-----(?s).+?-----END .+?-----)"
		allCerts = re.findall(certPattern, certData)
		if not allCerts:
			return "Error parsing certificate data"
		
		# Iterate over each cert in the data and decode it
		output = ""
		for oneCert in allCerts:
			session = subprocess.Popen(['openssl', 'x509', '-text', '-noout'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
			decodedCertData, err = session.communicate(input=oneCert)
			if err:
				output += err
			else:
				output += decodedCertData
			output += "\n\n-----------------------------\n\n"
		
		return output.rstrip("\n\n-----------------------------\n\n")