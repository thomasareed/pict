#!/usr/bin/python

# ProfileCollector class for PICT (Post-Infection Collection Toolkit)

import os
from datetime import datetime, date
from collector import Collector
import tools.util as util

class ProfileCollector(Collector):

	def printStartInfo(self):
		print "Collecting profile data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		filename = "profiles.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		
		f.write("Installed configuration profiles\n-----------------------------\n")
		output = os.popen("profiles show -all").read()
		f.write(output)
				
		f.close
		
		# Add any paths to self.pathsToCollect
		
		Collector.collect(self)
