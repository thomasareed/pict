#!/usr/bin/python

# LogCollector class for PICT (Post-Infection Collection Toolkit)

# Collects the following artifacts, on any system:
#   /var/log/system*
#   /var/log/asl/

# On Sierra and higher, also collects unified log data into a log archive. You can control how much data is output using a module-specific setting in the config file:

# 	"moduleSettings" : {
# 		"logs" : {
# 			"logArguments" : "--last 12h"
# 		}
# 	}

# The logArguments setting provides arguments to pass to the log command.
# Arguments will be inserted in the command where shown by "[args]" below:

#   log collect [args] --output /path/to/collection/folder/

# Thus, the above settings example will result in the following log command being called:

#   log collect --last 12h --output /path/to/collection/folder/


import os, subprocess
import glob
from collector import Collector
import tools.util as util

class LogCollector(Collector):
	
	unifiedLogArguments = ""

	def printStartInfo(self):
		print "Collecting log data"
	
	def applySettings(self, settingsDict):
		if "logArguments" in settingsDict:
			self.unifiedLogArguments = settingsDict["logArguments"]
		
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		# Collect unified logs, using arguments passed in settings
		if os.path.exists("/usr/bin/log"):
			outputPath = self.collectionPath
			if self.unifiedLogArguments:
				logCommand = "log collect {0} --output {1} 2>/dev/null".format(self.unifiedLogArguments, outputPath)
			else:
				logCommand = "log collect --output {0} 2>/dev/null".format(outputPath)
				print "WARNING: collecting unified logs without arguments will result in a very large amount of data!"
			os.popen(logCommand)
		
		# Collect pre-unified log artifacts
		systemLogPaths = glob.glob("/var/log/system*")
		if len(systemLogPaths) > 0:
			self.pathsToCollect = self.pathsToCollect + systemLogPaths
		self.pathsToCollect.append("/var/log/asl/")
		
		Collector.collect(self)
