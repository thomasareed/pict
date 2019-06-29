#!/usr/bin/python

# NetworkConfigCollector class for PICT (Post-Infection Collection Toolkit)

import os
from datetime import datetime, date
from collector import Collector
import tools.util as util

class NetworkConfigCollector(Collector):

	def printStartInfo(self):
		print "Collecting network config data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		filename = "network_config.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		
		f.write("en0\n-----------------------------\n")
		output = os.popen("ifconfig en0").read().rstrip()
		f.write(output + "\n\n")
		
		f.write("en1\n-----------------------------\n")
		output = os.popen("ifconfig en1").read().rstrip()
		f.write(output + "\n\n")
		
		# Output will already have a "DNS configuration" heading, no need to add one
		output = os.popen("scutil --dns 2>&1").read().rstrip()
		f.write(output + "\n\n")
				
		f.write("Proxies\n-----------------------------\n")
		output = os.popen("scutil --proxy 2>&1").read().rstrip()
		f.write(output + "\n\n")
				
		f.write("pf rules\n-----------------------------\n")
		output = os.popen("sudo pfctl -s rules 2>&1").read().rstrip()
		f.write(output + "\n\n")
				
		f.close
		
		self.pathsToCollect.append("/etc/hosts")
		
		Collector.collect(self)
