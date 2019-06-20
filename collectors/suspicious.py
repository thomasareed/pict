#!/usr/bin/python

# SuspiciousBehaviorCollector class for PICT (Post-Infection Collection Toolkit)

import os, subprocess
import re
import json
import glob
from datetime import datetime, date
from collector import Collector
import tools.util as util
import tools.FoundationPlist as FoundationPlist

class SuspiciousBehaviorCollector(Collector):

	def printStartInfo(self):
		print "Collecting suspicious behavior data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		filename = "suspicious_behaviors.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		
		hiddenPattern = "/\.[^\.]"
		
		# Get a list of processes running from suspicious paths
		f.write("Suspicious processes\n-----------------------------\n")
		processData = os.popen("ps axo pid,comm").read().rstrip()
		processList = processData.split("\n")
		output = ""
		for oneLine in processList:
			if (  re.search(hiddenPattern, oneLine) or
			      "/tmp/" in oneLine or
			      "/var/folders/" in oneLine or
			      "/Users/Shared/" in oneLine or
			      "/Library/Containers/" in oneLine ):
				output += oneLine + "\n"
		if output == "":
			output = "None"
		f.write(output + "\n\n")
		
		
		# Get a list of suspicious launch agents and daemons
		paths = glob.glob("/Library/LaunchAgents/*")
		paths += glob.glob("/Library/LaunchDaemons/*")
		paths += glob.glob("/Users/*/Library/LaunchAgents/*")
		
		suspiciousPaths = []
		for onePath in paths:
			
			# Examine the path itself
			if "com.apple" in onePath:
				if (  "aelwriter" not in onePath and
				      "installer.cleanupinstaller" not in onePath and
				      "installer.osmessagetracing" not in onePath ):
				  suspiciousPaths.append(onePath)
				  continue
			if onePath[0] == ".":
				suspiciousPaths.append(onePath)
				continue
			
			# Read the plist data into a dictionary
			plistDict = FoundationPlist.readPlist(onePath)
			if not plistDict:
				print "Error interpreting contents of {0}".format(onePath)
				continue
			
			# Parse the array containing the program and arguments from plistDict
			if "Program" in plistDict:
				program = plistDict["Program"]
			elif "ProgramArguments" in plistDict:
				program = plistDict["ProgramArguments"]
			else:
				# This plist does not launch anything
				continue
			
			# Examine the program and arguments for suspicious behaviors
			progValueType = type(program)
			if progValueType == type(str()) or progValueType == type(unicode()):
				# There's just a single string with the program name, no arguments
				program = [program]
			if (  re.search(hiddenPattern, program[0]) or
						"/tmp/" in program[0] or
						"/var/folders/" in program[0] or
						"/Users/Shared/" in program[0] or
						"/Library/Containers/" in program[0] or 
						"/var/root/" in program[0] ):
				suspiciousPaths.append(onePath)
				continue
			if (  program[0] == "python" or
			      program[0] == "sh" or
			      program[0] == "/bin/sh" or
			      program[0] == "java" ):
				suspiciousPaths.append(onePath)
				continue
			badFound = False
			for oneArg in program:
				if (  "curl" in oneArg or
				      "exec" in oneArg and "base64.b64decode" in oneArg ):
					badFound = True
			if badFound:
				suspiciousPaths.append(onePath)
				continue
		
		# Iterate suspicious paths to build output
		output = ""
		for onePath in suspiciousPaths:
			output += onePath + "\n"
		
		f.write("Suspicious agents & daemons\n-----------------------------\n")
		if output == "":
			output = "None\n\n"
		else:
			f.write(output + "\n\n")
		
		
		# Identify suspicious lines in the sudoers file
		sudoersFile = open("/etc/sudoers", "r")
		sudoersData = sudoersFile.read()
		sudoersFile.close
		suspiciousLines = re.findall("^[^#].*NOPASSWD: ALL", sudoersData, re.MULTILINE)
		if suspiciousLines:
			f.write("No password required for sudo\n-----------------------------\n")
			for oneLine in suspiciousLines:
				f.write(oneLine.rstrip() + "\n")
			f.write("\n")
		suspiciousLines = re.findall("Defaults !tty_tickets", sudoersData, re.MULTILINE)
		if suspiciousLines:
			f.write("Sudo allowed for all shells\n-----------------------------\n")
			for oneLine in suspiciousLines:
				f.write(oneLine.rstrip() + "\n")
			f.write("\n")
				
		f.close
		
		# Add any paths to self.pathsToCollect
		
		Collector.collect(self)
