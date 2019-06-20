#!/usr/bin/python

# BashHistoryCollector class for PICT (Post-Infection Collection Toolkit)

import os
from datetime import datetime, date
from collector import Collector
import tools.util as util

class BashHistoryCollector(Collector):

	def printStartInfo(self):
		print "Collecting bash history data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	def collect(self):
		
		for user in self.userList:
			bashHistPath = "/Users/{0}/.bash_history".format(user)
			if os.path.isfile(bashHistPath):
				self.pathsToCollect.append(bashHistPath)
		
		Collector.collect(self)
