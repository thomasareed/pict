#!/usr/bin/python

# ProcessCollector class for PICT (Post-Infection Collection Toolkit)

import os
import re
from datetime import datetime, date
from collector import Collector
import tools.util as util

class ProcessCollector(Collector):

	def printStartInfo(self):
		print "Collecting process data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		filename = "processes.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		f.write("Processes\n-----------------------------\n")
		processData = os.popen("ps axo user,pid,ppid,start,time,command").read().rstrip()
		f.write(processData + "\n\n")
		f.close
				
		filename = "processes_files.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		f.write("Files open by process\n-----------------------------\n")
		output = os.popen("lsof").read().rstrip()
		f.write(output + "\n\n")
		f.close
		
		filename = "processes_network.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		f.write("Network connections open by process\n-----------------------------\n")
		output = os.popen("lsof -i").read().rstrip()
		f.write(output + "\n\n")
		f.close

		# No file paths to collect
		
		Collector.collect(self)
