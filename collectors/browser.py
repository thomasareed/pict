#!/usr/bin/python

# BrowserExtCollector class for PICT (Post-Infection Collection Toolkit)

import os
import json
import re
import tempfile
import zipfile
import plistlib
from collector import Collector
import tools.util as util
from datetime import datetime, date

class BrowserExtCollector(Collector):

	def printStartInfo(self):
		print "Collecting browser extension data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		filename = "browser_extensions.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		
		f.write("Safari extensions\n-----------------------------\n")
		output = self.collectSafari()
		f.write(output + "\n\n")
				
		f.write("Chrome extensions\n-----------------------------\n")
		output = self.collectChrome()
		f.write(output + "\n\n")
				
		f.write("Firefox extensions\n-----------------------------\n")
		output = self.collectFirefox()
		f.write(output + "\n\n")
				
		f.write("Safari app extensions\n-----------------------------\n")
		output = self.collectSafariAppExtensions()
		f.write(output)
				
		f.close
		
		Collector.collect(self)
		
	
	def collectSafari(self):
		try:
			os.listdir(os.path.expanduser("~/Library/Safari/Extensions"))
		except Exception as e:
			if "Operation not permitted" in str(e):
				return "Unable to access due to TCC restrictions"
		
		output = ""
		extensionsForUsers = self.getSafariExtensionList()
		
		for user in extensionsForUsers:
			output += "Extensions for {0}:\n".format(user)
			extensionList = extensionsForUsers[user]
			
			# Iterate extensions for user
			for extPath in extensionList:
				# Mark this path for collection
				self.pathsToCollect.append(extPath)
				tempdir = tempfile.mkdtemp()
				err = os.system("cd {0}; xar -xf {1}".format(tempdir, extPath))
				if err:
					extName = "Unknown file format ({0})".format(err)
				else:
					# Expand the extension
					tempdirlist = os.listdir(tempdir)
					for oneItem in tempdirlist:
						oneItemPath = util.safePathJoin(tempdir, oneItem)
						if os.path.isdir(oneItemPath):
							expExtPath = oneItemPath
							break
					# Read the name from the Info.plist
					extInfoPlistPath = util.safePathJoin(expExtPath, "Info.plist")
					extInfoPlist = plistlib.readPlist(extInfoPlistPath)
					extName = extInfoPlist["CFBundleDisplayName"]
				# end if
				output += "  Extension: {0}\n".format(extPath)
				output += "  Name: {0}\n\n".format(extName)
		
		return output.rstrip()
	
	
	def collectChrome(self):
		output = ""
		
		profilesForUsers = {}
		for user in self.userList:
			profilesForUsers[user] = util.getChromeProfilesForUser(user)
		
		for user in profilesForUsers:
			profileList = profilesForUsers[user]
			for profile in profileList:
				profilePath = profileList[profile]
				self.pathsToCollect.append(util.safePathJoin(profilePath, "Preferences"))
				self.pathsToCollect.append(util.safePathJoin(profilePath, "Secure Preferences"))
		
		extensionsForUsers = self.getChromeExtensionList(profilesForUsers)

		for user in extensionsForUsers:
			output += "Extensions for {0}:\n".format(user)
			extensionsForProfiles = extensionsForUsers[user]
			
			# Iterate over all profiles
			for profile in extensionsForProfiles:
				output += "  Profile {0}:\n".format(profile)
				extensionList = extensionsForProfiles[profile]
				
				# Collect Preferences and Secure Preferences for each profile
				# self.pathsToCollect.append(???)
				
				# Iterate extensions for profile
				for extPath in extensionList:
					if not os.path.isdir(extPath):
						continue
					manifestPath = ""
					folderList = os.listdir(extPath)
					versFolderPath = ""
					for folder in folderList:
						versFolderPath = util.safePathJoin(extPath, folder)
						manifestPath = util.safePathJoin(versFolderPath, "manifest.json")
						if os.path.isfile(manifestPath):
							break
					if manifestPath == "":
						continue
					# A manifest.json file was found, this must be a valid extension
					# Mark this path for collection
					self.pathsToCollect.append(extPath)
					f = open(manifestPath, "r")
					manifestJSON = f.read()
					f.close
					manifestDict = json.loads(manifestJSON)
					extName = manifestDict['name']
					if extName.startswith("__MSG_") and extName.endswith("__"):
						# There's a localized name, look for it in English
						localePath = util.safePathJoin(versFolderPath, "_locales/en/messages.json")
						if not os.path.exists(localePath):
							localePath = util.safePathJoin(versFolderPath, "_locales/en_US/messages.json")
						if not os.path.exists(localePath):
							extName = "Unknown name"
						else:
							nameKey = extName[6:][:-2]
							f = open(localePath, "r")
							localeJSON = f.read()
							f.close
							localeDict = json.loads(localeJSON)
							extName = dict((key.lower(), value) for key, value in localeDict.iteritems())[nameKey.lower()]['message']
					#end if extName.startswith("__MSG_")
			
					output += "    Extension: {0}\n".format(extPath)
					output += "    Name: {0}\n\n".format(extName)
				#end for extension
			#end for profile
		#end for user
		
		return output.rstrip()
					
	
	def collectFirefox(self):
		output = ""
		
		profilesForUsers = {}
		for user in self.userList:
			profilesForUsers[user] = util.getFirefoxProfilesForUser(user)
		
		for user in profilesForUsers:
			profileList = profilesForUsers[user]
			for profile in profileList:
				profilePath = profileList[profile]
				self.pathsToCollect.append(util.safePathJoin(profilePath, "prefs.js"))
		
		extensionsForUsers = self.getFirefoxExtensionList(profilesForUsers)

		for user in extensionsForUsers:
			output += "Extensions for {0}:\n".format(user)
			extensionsForProfiles = extensionsForUsers[user]
	
			# Iterate over all profiles
			for profile in extensionsForProfiles:
				output += "  Profile {0}:\n".format(profile)
				extensionList = extensionsForProfiles[profile]
		
				# Iterate extensions for profile
				for extPath in extensionList:
					if extPath.endswith(".DS_Store"):
						continue
					# Mark this path for collection
					self.pathsToCollect.append(extPath)
					if os.path.isdir(extPath):
						# Older extension, look for name in install.rdf
						installrdfPath = util.safePathJoin(extPath, "install.rdf")
						if not os.path.isfile(installrdfPath):
							extName = "Unknown extension type"
						else:
							f = open(installrdfPath, "r")
							installrdfData = f.read()
							f.close
							m = re.search("<em:name>([^<]*)</em:name>", installrdfData, re.I)
							if m:
								extName = m.group(1)
							else:
								extName = "Unknown name"
					else:
						# Is it a .xpi? If so, decompress and get name
						if extPath.endswith(".xpi"):
							tempdir = tempfile.mkdtemp()
							zipf = open(extPath, "rb")
							zip = zipfile.ZipFile(zipf)
							zip.extract("manifest.json", tempdir)
							zipf.close
							manifestPath = util.safePathJoin(tempdir, "manifest.json")
							f = open(manifestPath, "r")
							manifestJSON = f.read()
							f.close
							manifestDict = json.loads(manifestJSON)
							extName = dict((key.lower(), value) for key, value in manifestDict.iteritems())['name']
						else:
							extName = "Unknown extension type"
				
					output += "    Extension: {0}\n".format(extPath)
					output += "    Name: {0}\n\n".format(extName)
				#end for extension
			#end for profile
		#end for user
		
		return output.rstrip()
	
	
 	def getSafariExtensionList(self):
		extensionsDict = {}
		
		for user in self.userList:
			extensionsForUser = []
			
			safariExtFolder = "/Users/{0}/Library/Safari/Extensions".format(user)
			if not os.path.isdir(safariExtFolder):
				continue
			safariExtList = os.listdir(safariExtFolder)
			for extension in safariExtList:
				if extension.endswith(".safariextz"):
					extensionsFolderPath = util.safePathJoin(safariExtFolder, extension)
					extensionsForUser.append(extensionsFolderPath)
			if extensionsForUser:
				extensionsDict[user] = extensionsForUser
		
		return extensionsDict
			
		
	def getChromeExtensionList(self, profilesForUsers):
		if profilesForUsers == {}:
			return {}
		
		extensionsDict = {}

		for user in profilesForUsers:
			profileList = profilesForUsers[user]
			extensionsForUser = {}
	
			# Iterate over all profiles
			for profile in profileList:
				extensionsForProfile = []
				extFolder = util.safePathJoin(profileList[profile], "Extensions")
				if not os.path.exists(extFolder):
					continue
				extensionList = os.listdir(extFolder)
				if not extensionList:
					continue
				
				# Iterate extensions for profile
				for extension in extensionList:
					extPath = util.safePathJoin(extFolder, extension)
					if not os.path.isdir(extPath):
						continue
					manifestPath = ""
					folderList = os.listdir(extPath)
					versFolderPath = ""
					for folder in folderList:
						versFolderPath = util.safePathJoin(extPath, folder)
						manifestPath = util.safePathJoin(versFolderPath, "manifest.json")
						if os.path.isfile(manifestPath):
							break
					if manifestPath == "":
						continue
					
					# A manifest.json file was found, this must be a valid extension
					extensionsForProfile.append(extPath)
				#end for extension
				
				extensionsForUser[profile] = extensionsForProfile
			#end for profile
			
			extensionsDict[user] = extensionsForUser
		#end for user

		return extensionsDict
		
		
	def getFirefoxExtensionList(self, profilesForUsers):
		if profilesForUsers == {}:
			return {}
		
		extensionsDict = {}

		for user in profilesForUsers:
			profileList = profilesForUsers[user]
			extensionsForUser = {}

			profileList = util.getFirefoxProfilesForUser(user)

			# Iterate over all profiles
			for profile in profileList:
				extensionsForProfile = []
				extFolder = util.safePathJoin(profileList[profile], "extensions")
				if not os.path.exists(extFolder):
					continue
				extensionList = os.listdir(extFolder)
				if not extensionList:
					continue
				
				# Iterate extensions for profile
				for extension in extensionList:
					if extension == ".DS_Store":
						continue
					extPath = util.safePathJoin(extFolder, extension)
					if os.path.isdir(extPath):
						# Older extension, is there an install.rdf?
						installrdfPath = util.safePathJoin(extPath, "install.rdf")
						if not os.path.isfile(installrdfPath):
							continue
					else:
						# Is it a .xpi?
						if not extension.endswith(".xpi"):
							continue
				
					# If we're still here, this must be a valid extension
					extensionsForProfile.append(extPath)
				#end for extension
			
				extensionsForUser[profile] = extensionsForProfile
			#end for profile
		
			extensionsDict[user] = extensionsForUser
		#end for user

		return extensionsDict
	
	
	# Get information about Safari app extensions from lsregister info
	def collectSafariAppExtensions(self):
		lsregisterInfoPath = util.safePathJoin(self.collectionPath, "lsregister.txt")
		extensions = os.popen("""egrep -i -10 'NSExtensionPointIdentifier\s*=\s*"com\.apple\.Safari' {0}""".format(lsregisterInfoPath)).read().rstrip()
		return extensions
