#!/usr/bin/python

# FileInfoCollector class for PICT (Post-Infection Collection Toolkit)

# !!!Module settings must be provided!!!

# Provide an array named "paths", where the array contains one or more dictionaries with two keys:
# 
#   path = the path to walk, collecting info about all items inside recursively
#   ignoreRestricted = true to skip recursing into SIP-protected folders
# 
# 	"fileinfo" : {
# 		"paths" : [
# 			{
# 				"path" : "/Library",
# 				"ignoreRestricted" : true
# 			},
# 			{
# 				"path" : "~",
# 				"ignoreRestricted" : false
# 			}
# 		]
# 	}

# This data can be very large! On my machine (1 TB, 788 GB used), the listing for the entire hard drive ("path" : "/"), with ignoreRestricted set to true, is nearly 380 MB.


import os, subprocess
import time
from collector import Collector
import tools.util as util


def TimestampToGMTStr(theTime):
	return time.strftime("%Y-%m-%dT %H:%M:%S", time.gmtime(theTime))


class FileInfoCollector(Collector):
	
	paths = []
	statinfo = {}
	flagsMap = {
		"nodump" : 1,
		"uchg" : 2,
		"uappnd" : 4,
		"opaque" : 8,
		"compressed" : 32, 
		"hidden" : 32768,
		"arch" : 65536,
		"schg" : 131072,
		"sappnd" : 262144,
		"restricted" : 524288, 
		"sunlnk" : 1048576
	}

	def printStartInfo(self):
		print "Collecting file info data"
	
	def applySettings(self, settingsDict):
		if "paths" in settingsDict:
			self.paths = settingsDict["paths"]
		
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		filename = "fileinfo.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		
		f.write("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\r".format("Raw Flags", "Flags", "UID", "GID", "Mode (oct)", "Created", "Modified", "Accessed", "Path"))
		output = self.collectFromPaths()
		f.write(output + "\n\n")
				
		f.close
		
		# Add any paths to self.pathsToCollect
		
		Collector.collect(self)
	
	
	def collectFromPaths(self):
		
		if len(self.paths) == 0:
			return "No file paths provided"
			
		outputText = ""
		
		# iterate over array of paths
		
		for pathDescriptor in self.paths:
			if "path" in pathDescriptor:
				walkDir = pathDescriptor["path"]
				if walkDir.startswith("~"):
					walkDir = os.path.expanduser(walkDir)
			else:
				output += "Error: path missing from path descriptor\n"
			if "ignoreRestricted" in pathDescriptor:
				ignoreRestricted = pathDescriptor["ignoreRestricted"]
			else:
				ignoreRestricted = True
			
			for root, dirs, files in os.walk(walkDir, followlinks=False):
				i = len(dirs)-1
				while i >= 0:
					name = dirs[i]
					fileInfo = self.GetFileInfo(os.path.join(root, name).encode("utf-8"))
					if fileInfo != "":
						outputText += fileInfo
						if ignoreRestricted and self.statinfo.st_flags & self.flagsMap["restricted"]:
							del dirs[i]
					i = i - 1
				for name in files:
					fileInfo = self.GetFileInfo(os.path.join(root, name).encode("utf-8"))
					if fileInfo != "":
						outputText += fileInfo
		
		return outputText
		
		
	def GetFileInfo(self, path):
	
		# Is it an alias/link? If so, skip
		if os.path.islink(path):
			return ""
	
		# Get flags
		try:
			self.statinfo = os.stat(path)
		except:
			return ""
		flags = self.statinfo.st_flags
		flagsList = ""
		flagsFound = False
		for flagName in self.flagsMap:
			if flags & self.flagsMap[flagName]:
				if flagsFound:
					flagsList += ", "
				flagsList += flagName
				flagsFound = True
		if not flagsFound:
			flagsList = "none"
	
		uid = str(self.statinfo.st_uid)
		gid = str(self.statinfo.st_gid)
		mode = oct(self.statinfo.st_mode)
	
		# Get created, modified, accessed times
		cTime = TimestampToGMTStr(self.statinfo.st_birthtime)
		mTime = TimestampToGMTStr(self.statinfo.st_mtime)
		aTime = TimestampToGMTStr(self.statinfo.st_atime)
		
		output = hex(flags) + "\t"
		output += flagsList + "\t"
		output += uid + "\t"
		output += gid + "\t"
		output += mode + "\t"
		output += cTime + "\t"
		output += mTime + "\t"
		output += aTime + "\t"
		output += path + "\n"
		
		return output
	
		#return "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\r".format(hex(flags), flagsList, uid, gid, mode, cTime, mTime, aTime, path)

