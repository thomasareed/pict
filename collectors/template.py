#!/usr/bin/python

# BlahCollector class for PICT (Post-Infection Collection Toolkit)

import os, subprocess
from collector import Collector
import tools.util as util

class BlahCollector(Collector):

	def printStartInfo(self):
		print "Collecting blah data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		filename = "blah.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		
		f.write("Label\n-----------------------------\n")
		output = self.collectSomething()
		f.write(output + "\n\n")
				
		f.close
		
		# Add any paths to self.pathsToCollect
		
		Collector.collect(self)
