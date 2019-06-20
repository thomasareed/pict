#!/usr/bin/python

# BashConfigCollector class for PICT (Post-Infection Collection Toolkit)

import os
from datetime import datetime, date
from collector import Collector
import tools.util as util

class BashConfigCollector(Collector):
	
	def printStartInfo(self):
		print "Collecting bash config data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		
		self.pathsToCollect.append("/etc/profile")
		self.pathsToCollect.append("/etc/bashrc")
		self.pathsToCollect.append("/etc/sudoers")
		
		for user in self.userList:
		
			p = "/Users/{0}/.bash_profile".format(user)
			if os.path.isfile(p):
				self.pathsToCollect.append(p)
				
			p = "/Users/{0}/.bash_login".format(user)
			if os.path.isfile(p):
				self.pathsToCollect.append(p)
		
			p = "/Users/{0}/.profile".format(user)
			if os.path.isfile(p):
				self.pathsToCollect.append(p)
			
			p = "/Users/{0}/.bash_logout".format(user)
			if os.path.isfile(p):
				self.pathsToCollect.append(p)
			
		Collector.collect(self)
