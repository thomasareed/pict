#!/usr/bin/python

# PersistenceCollector class for PICT (Post-Infection Collection Toolkit)

import os, subprocess
from collector import Collector
import tools.util as util
from datetime import datetime, date

class PersistenceCollector(Collector):

	def printStartInfo(self):
		print "Collecting persistence data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		filename = "persistence.txt"
		filePath = util.safePathJoin(self.collectionPath, filename)
		f = open(filePath, "w+")
		
		f.write("PICT - Persistence information\n==============================\n\n")
		
		f.write("Login items (current user)\n------------------------------\n")
		logins = self.collectLoginItems()
		f.write(logins + "\n\n")
				
		f.write("Hidden login items\n------------------------------\n")
		logins = self.collectHiddenLoginItems()
		f.write(logins + "\n\n")
				
		f.write("Kernel extensions\n------------------------------\n")
		output = self.collectKexts()
		f.write(output + "\n\n")
				
		f.write("Cron jobs\n------------------------------\n")
		output = self.collectCronJobs()
		f.write(output + "\n\n")
				
		f.write("Startup items\n------------------------------\n")
		output = self.collectStartupItems()
		f.write(output + "\n\n")
				
		f.write("Login hooks\n------------------------------\n")
		output = self.collectLoginHooks()
		f.write(output + "\n\n")
				
		f.write("Launch agents\n------------------------------\n")
		output = self.collectLaunchAgents()
		f.write(output + "\n\n")
				
		f.write("Launch daemons\n------------------------------\n")
		output = self.collectLaunchDaemons()
		f.write(output + "\n\n")
				
		f.write("User launch agents\n------------------------------\n")
		output = self.collectUserLaunchAgents()
		f.write(output + "\n\n")
		
		f.write("launchctl list\n------------------------------\n")
		output = self.collectLaunchctlList()
		f.write(output + "\n\n")
		
		f.close
		
		self.collectMiscArtifacts()
		
		Collector.collect(self)
		
	
	def collectLoginItems(self):
		logins = os.popen("""osascript -e 'tell application "System Events" to get the path of every login item'""").read().rstrip()
		loginList = logins.split(", ")
		output = ""
		for oneLogin in loginList:
			output += oneLogin + "\n"
		return output.rstrip()
		
	
	def collectHiddenLoginItems(self):
		lsregisterInfoPath = util.safePathJoin(self.collectionPath, "lsregister.txt")
		logins = os.popen("egrep -oi '(/[^/]+)*/Contents/Library/LoginItems/.+\.app' {0} | grep -v '/Volumes/.*\.backupdb/'".format(lsregisterInfoPath)).read().rstrip()
		return logins
		
	
	def collectKexts(self):
		return os.popen("kextstat | grep -v com\.apple").read().rstrip()
		

	def collectCronJobs(self):
		output = "Root:\n"
		output += os.popen("crontab -l 2>&1").read().rstrip() + "\n\n"
		
		for user in self.userList:
			output += "{0}:\n".format(user)
			output += os.popen(u"crontab -u {0} -l 2>&1".format(user)).read().rstrip() + "\n\n"
		
		return output.rstrip()
		
	
	def collectStartupItems(self):
		folders = ["/System/Library/StartupItems", "/Library/StartupItems"]
		output = ""
		for oneFolder in folders:
			output += "{0}\n".format(oneFolder)
			output += os.popen("ls -aleO {0}".format(oneFolder)).read().rstrip()
			output += "\n\n"
		return output.rstrip()
		
	
	def collectLoginHooks(self):
		output = ""
		
		# hooks for all users
		output += "All users:\n"
		session = subprocess.Popen(["defaults", "read", "com.apple.loginwindow", "LoginHook"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		result, err = session.communicate()
		if err:
			output += "None"
		else:
			output += result
		output += "\n\n"
		
		# hooks for specific users
		for user in self.userList:
			output += "{0}:\n".format(user)
			
			plistPath = u"/Users/{0}/Library/Preferences/com.apple.loginwindow".format(user)
			if not os.path.isfile(plistPath):
				output += "None"
			else:
				session = subprocess.Popen(["defaults", "read", plistPath, "LoginHook"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				result, err = session.communicate()
				if err:
					output += "None"
				else:
					output += result
			output += "\n\n"
		return output.rstrip()
		
	
	def collectLaunchAgents(self):
		listing = os.popen("ls -aleO /Library/LaunchAgents").read().rstrip()
		self.pathsToCollect.append("/Library/LaunchAgents")
		return listing
		

	def collectLaunchDaemons(self):
		listing = os.popen("ls -aleO /Library/LaunchDaemons").read().rstrip()
		self.pathsToCollect.append("/Library/LaunchDaemons")
		return listing
		

	def collectUserLaunchAgents(self):
		userFolderPaths = []
		for user in self.userList:
			userFolderPaths.append(util.safePathJoin("/Users", user))
		
		output = ""
		collectFolders = []
		for userFolder in userFolderPaths:
			userLaunchAgentsFolder = util.safePathJoin(userFolder, "Library/LaunchAgents")
			if os.path.exists(userLaunchAgentsFolder):
				output += userLaunchAgentsFolder + "\n"
				output += os.popen("ls -aleO {0}".format(userLaunchAgentsFolder)).read().rstrip()
				output += "\n\n"
				self.pathsToCollect.append(userLaunchAgentsFolder)
					
		return output.rstrip()
		
		
	def collectLaunchctlList(self):
		whoami = os.popen("whoami").read().rstrip()
		if whoami == "root":
			output = "Root agents/daemons:\n"
			output += os.popen("launchctl list").read().rstrip() + "\n\n"
			
			user = os.popen("logname").read().rstrip()
			output += "User agents:\n"
			output += os.popen('su {0} -c "launchctl list"'.format(user)).read().rstrip()
		else:
			output += "User agents:\n"
			output += os.popen("launchctl list").read().rstrip()
			
		return output
		
	
	# Adds items to pathsToCollect, to mark them for collection
	def collectMiscArtifacts(self):
		self.pathsToCollect.append("/var/at/jobs")
		self.pathsToCollect.append("/etc/security/audit_warn")
		self.pathsToCollect.append("/etc/rc.common")
		self.pathsToCollect.append("/etc/launchd.conf")
		for user in self.userList:
			userFolder = util.safePathJoin("/Users", user)
			self.pathsToCollect.append(util.safePathJoin(userFolder, ".launchd.conf"))
