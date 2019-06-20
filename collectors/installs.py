#!/usr/bin/python

# InstallationCollector class for PICT (Post-Infection Collection Toolkit)

import os, subprocess
import glob
import json
from datetime import datetime, date
from collector import Collector
import tools.FoundationPlist as FoundationPlist

class InstallationCollector(Collector):

	def printStartInfo(self):
		print "Collecting installation data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		
		output = ""
		receiptPlistPaths = glob.glob("/private/var/db/receipts/*.plist")
		for onePlistPath in receiptPlistPaths:
			if os.path.isfile(onePlistPath) and onePlistPath.endswith(".plist"):
				plistDict = FoundationPlist.readPlist(onePlistPath)
				if not plistDict:
					continue
				output += str(plistDict["InstallDate"]) + "\t"
				output += plistDict["InstallPrefixPath"] + "\t"
				output += plistDict["InstallProcessName"] + "\t"
				output += plistDict["PackageFileName"] + "\t"
				output += plistDict["PackageIdentifier"] + "\t"
				output += plistDict["PackageVersion"] + "\n"
		
		output = "Install Date\tPrefix Path\tProcess Name\tFile Name\tIdentifier\tVersion\n" + "\n".join(sorted(output.split("\n")))
		
		filename = "installs.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		f.write(output)
		f.close
		
		self.pathsToCollect.append("/Library/Receipts/InstallHistory.plist")
		
		Collector.collect(self)
