#!/usr/bin/python

# BasicsCollector class for PICT (Post-Infection Collection Toolkit)

import os
from datetime import datetime, date
from collector import Collector
import tools.util as util

class BasicsCollector(Collector):

	def printStartInfo(self):
		print "Collecting basic machine info"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		basicsFilename = "basic_info.txt"
		basicsFilePath = util.safePathJoin(self.collectionPath, basicsFilename)
		f = open(basicsFilePath, "w+")
		
		user = os.popen("logname").read().rstrip()
		when = datetime.utcnow().strftime("%-d %b %Y @ %H:%M:%S UTC")
		whenlocal = datetime.now().strftime("%-d %b %Y @ %H:%M:%S")
		f.write("Collected by user {0} on {1} (local {2})\n".format(user, when, whenlocal))
		uptime = os.popen("uptime").read().rstrip()
		f.write("Uptime: {0}\n".format(uptime))
		hostname = os.popen("hostname").read().rstrip()
		f.write("Hostname: {0}\n".format(hostname))
		spctlStatus = os.popen("spctl --status").read().rstrip()
		f.write("System policy security: {0}\n".format(spctlStatus))
		if spctlStatus != "assessments enabled":
			f.write("  Gatekeeper is disabled!\n")
		sipStatus = os.popen("csrutil status").read().rstrip() + "\n"
		f.write(sipStatus)
		filevaultStatus = os.popen("fdesetup status").read().rstrip()
		f.write("FileVault status: {0}\n".format(filevaultStatus))
		firewallStatus = os.popen("defaults read /Library/Preferences/com.apple.alf globalstate").read().rstrip()
		if firewallStatus == "0":
			f.write("Application firewall is not enabled\n")
		else:
			f.write("Application firewall is enabled\n")
		
		# Concerning things...
		if os.path.exists("/private/etc/kcpassword"):
			f.write("WARNING! Automatic login is enabled by user!\n")
		
		# System profiler stuff
		f.write("\n")
		systemOverview = os.popen("system_profiler SPSoftwareDataType").read().rstrip()
		f.write(systemOverview)
		f.write("\n\n")
		hardwareOverview = os.popen("system_profiler SPHardwareDataType").read().rstrip()
		f.write(hardwareOverview)
		f.write("\n\n")
		
		# Users
		f.write("User list\n-----------------------------\n")
		users = os.popen("dscl . list /Users | grep -v '^_'").read().rstrip()
		userlist = users.split("\n")
		for user in userlist:
			if user != "daemon" and user != "nobody":
				userInfo = os.popen("dscacheutil -q user -a name {0}".format(user)).read().rstrip()
				f.write(userInfo + "\n\n")
		
		f.write("Admin users\n-----------------------------\n")
		users = os.popen("dscl . -read /Groups/admin GroupMembership").read().rstrip()
		userlist = users.split()[1:]
		for user in userlist:
			f.write(user + "\n")
		f.write("\n")
		
		# Login activity
		
		f.write("Users logged in\n-----------------------------\n")
		users = os.popen("w").read().rstrip()
		f.write(users + "\n\n")
		
		f.write("Last logins\n-----------------------------\n")
		users = os.popen("last").read().rstrip()
		f.write(users + "\n\n")
				
		f.close
				
		Collector.collect(self)
