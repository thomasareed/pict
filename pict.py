#!/usr/bin/python

# Collector class for PICT (Post-Infection Collection Toolkit)

# Must be initialized with a JSON string describing the configuration as in this example:
# {
# 	"collection_dest" : "/Users/thomas/Desktop/",
# 	"all_users" : true,
# 	
# 	"collectors" : {
# 		"browser" : "BrowserExtCollector",
# 		"persist" : "PersistenceCollector"
# 	},
# 	
# 	"settings" : {
# 		"keepLSData" : false,
# 		"zipIt" : true
# 	},
# 	
# 	"moduleSettings" : {
# 		"browser" : {
# 			"collectArtifacts" : false
# 		}
# 	},
# 	
# 	"unused" : {
# 		"suspicious" : "SuspiciousBehaviorCollector",
# 		"browserhist" : "BrowserHistoryCollector",
# 		"bash_config" : "BashConfigCollector",
# 		"bash_hist" : "BashHistoryCollector",
# 		"processes" : "ProcessCollector",
# 		"network_config" : "NetworkConfigCollector",
# 		"profiles" : "ProfileCollector",
# 		"certs" : "TrustedCertCollector",
# 		"installs" : "InstallationCollector"
# 	}
# }

import json
import os, subprocess
import sys, getopt
import collectors.tools.util as util
from datetime import datetime, date
from collectors.collector import Collector
from collectors.basics import BasicsCollector

class PICT:

	config = {}
	destPath = "/Users/Shared/"
	collectionPath = ""
	allUsers = True
	
	def __init__(self, configJSON):
		self.config = json.loads(configJSON)
		if "collection_dest" in self.config:
			self.destPath = self.config["collection_dest"].encode("utf-8")
			if self.destPath[0] == "~":
				self.destPath = os.path.expanduser(self.destPath)
		if "all_users" in self.config:
			self.allUsers = self.config["all_users"]
		self.initDestination()
	
	def printConfig(self):
		print self.config
	
	def initDestination(self):
		computerName = os.popen("scutil --get ComputerName | tr ' ' '_'").read().rstrip()
		today = str(date.today())
		collectionFolderName = 'PICT-{0}-{1}/'.format(computerName, today)
		self.collectionPath = util.safePathJoin(self.destPath, collectionFolderName)
		if not os.path.exists(self.collectionPath):
			os.makedirs(self.collectionPath)
	
	def collect(self):
		
		# Check for root
		if os.geteuid() != 0:
			print("Without root permissions, some operations will fail. Run again with root for more complete collection.")
		
		if "settings" in self.config:
			settingsToUse = self.config["settings"]
		else:
			settingsToUse = {}
		
		startTime = datetime.now()
		print("Beginning PICT collection ({0})".format(startTime.strftime("%-d %b %Y @ %H:%M:%S")))
		
		# Collect the basics that are collected no matter what the config says
		c = BasicsCollector(self.collectionPath, self.allUsers)
		c.printStartInfo()
		c.collect()
		
		# Collect output of lsregister -dump, which will be used in more than one other
		# collection script.
		c = LSCollector(self.collectionPath, self.allUsers)
		c.printStartInfo()
		c.collect()
		
		# Add code to collect the remaining traces, depending on configuration
		
		collectorsToUse = self.config["collectors"]
		if "moduleSettings" in self.config:
			moduleSettingsToUse = self.config["moduleSettings"]
		else:
			moduleSettingsToUse = {}
		for theModuleName in collectorsToUse:
			theClassName = collectorsToUse[theModuleName]
			if not theClassName or theClassName == "":
				continue
			mod = __import__("collectors.{0}".format(theModuleName), globals(), locals(), [theClassName])
			theCollectorClass = getattr(mod, theClassName)
			c = theCollectorClass(self.collectionPath, self.allUsers)
			if theModuleName in moduleSettingsToUse:
				moduleSettings = moduleSettingsToUse[theModuleName]
				if moduleSettings:
					c.applySettings(moduleSettings)
			c.printStartInfo()
			c.collect()
		
		# If the settings specify not to keep the lsregister data, remove the file
		if "keepLSData" in settingsToUse:
			if not settingsToUse["keepLSData"]:
				lsregisterFilePath = os.path.join(self.collectionPath, "lsregister.txt")
				if os.path.exists(lsregisterFilePath):
					os.remove(lsregisterFilePath)
		
		# Compress the collection folder to a zip file
		if "zipIt" in settingsToUse:
			if settingsToUse["zipIt"]:
				zipFilePath = self.collectionPath.rstrip("/") + ".zip"
				session = subprocess.Popen(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", self.collectionPath, zipFilePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				output, err = session.communicate()
				if err:
					print "Error creating zip file: " + str(err)
		
		endTime = datetime.now()
		elapsed = str(endTime - startTime)
		print("Collection complete (elapsed time: {0})".format(elapsed))


# Collects the output of lsregister -dump
class LSCollector(Collector):
	
	def printStartInfo(self):
		print "Collecting launch services data"
	
	def collect(self):
		filename = "lsregister.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		
		output = os.popen("/System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister -dump").read()
		f.write(output)
				
		f.close
		
		# No paths to add to self.pathsToCollect
		
		Collector.collect(self)


if __name__ == "__main__":
	configFile = ""
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'c:', ['config='])
	except getopt.GetoptError:
		print 'usage: pict.py -c | --config /path/to/file'
		sys.exit(1)
	for opt, arg in opts:
		if opt in ('-c', '--config'):
			configFile = arg

	if configFile == "":
		print 'Config file must be provided!'
		print 'usage: pict.py -c | --config /path/to/file'
		sys.exit(1)

	if not os.path.exists(configFile):
		print 'Config file not found'
		sys.exit(1)

	f = open(configFile, "r")
	configJSON = f.read()
	f.close()

	aCollector = PICT(configJSON)
	aCollector.collect()