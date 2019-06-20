#!/usr/bin/python

# BrowserHistoryCollector class for PICT (Post-Infection Collection Toolkit)

import os
import sqlite3
from collector import Collector
from datetime import datetime, date
import tools.util as util

class BrowserHistoryCollector(Collector):

	def printStartInfo(self):
		print "Collecting browser history data"
	
	def applySettings(self, settingsDict):
		Collector.applySettings(self, settingsDict)
	
	# Collect selected information from the last 3 months to text files, and collect
	# the full original history databases as artifacts.
	def collect(self):
		filename = "history_downloads.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		f.write("Downloads (QuarantineEventsV2)\n-----------------------------\n")
		output = self.collectDownloads()
		f.write(output)
		f.close
				
		filename = "history_safari.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		f.write("Safari history\n-----------------------------\n")
		output = self.collectSafari()
		f.write(output)
		f.close
	
		filename = "history_chrome.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		f.write("Chrome history\n-----------------------------\n")
		output = self.collectChrome()
		f.write(output)
		f.close
		
		filename = "history_firefox.txt"
		filePath = self.collectionPath + filename
		f = open(filePath, "w+")
		f.write("Firefox history\n-----------------------------\n")
		output = self.collectFirefox()
		f.write(output)
		f.close
		
		Collector.collect(self)

	
	def collectDownloads(self):
		output = ""
		for user in self.userList:
			output += "Downloads for user {0}:\n\n".format(user)
			
			try:
				dbFilePath = "/Users/{0}/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2".format(user)
				if not os.path.isfile(dbFilePath):
					output += "No download events\n\n"
				
				self.pathsToCollect.append(dbFilePath)
				
				db = sqlite3.connect(dbFilePath)
				curs = db.cursor()
			
				# Collect all entries, regardless of time
				# curs.execute("select strftime('%Y-%m-%d %H:%M:%S', datetime((strftime('%s','2001-01-01 00:00:00') + LSQuarantineTimeStamp), 'unixepoch'), 'utc'), LSQuarantineAgentBundleIdentifier, LSQuarantineDataURLString, LSQuarantineOriginURLString from LSQuarantineEvent where LSQuarantineDataURLString is not null;")
			
				# Collect only 3 months of data
				curs.execute("select strftime('%Y-%m-%d %H:%M:%S', datetime((strftime('%s','2001-01-01 00:00:00') + LSQuarantineTimeStamp), 'unixepoch'), 'utc'), LSQuarantineAgentBundleIdentifier, LSQuarantineDataURLString, LSQuarantineOriginURLString from LSQuarantineEvent where LSQuarantineDataURLString is not null and LSQuarantineTimeStamp > (strftime('%s','now') - strftime('%s','2001-01-01 00:00:00') - 2592000*3);")
		
				rows = curs.fetchall()
		
			except Exception as e:
				output += "Error reading data\n  {0}\n\n".format(str(e))
				continue
		
			for row in rows:
				if row[0]:
					downloadDate = row[0]
				else:
					downloadDate = "Unknown date"
				if row[1]:
					agent = row[1]
				else:
					agent = "Unknown agent"
				if row[2]:
					fileURL = row[2]
				else:
					fileURL = "Unknown file URL"
				if row[3]:
					originURL = row[3]
				else:
					originURL = "Unknown origin URL"
			
				output += "Downloaded: {0}\tby agent: {1}\n".format(downloadDate, agent)
				output += "File:\n\t{0}\n".format(fileURL)
				output += "Origin:\n\t{0}\n\n".format(originURL)
		
		return output.rstrip()
	
	
	def collectSafari(self):
		output = ""
		for user in self.userList:
			output += "History for user {0}:\n\n".format(user)
			
			dbFilePath = "/Users/{0}/Library/Safari/History.db".format(user)
			if os.path.isfile(dbFilePath):
				self.pathsToCollect.append(dbFilePath)
			else:
				output += "No history found\n\n"
				continue
			
			query = "select strftime('%Y-%m-%d %H:%M:%S', datetime((strftime('%s','2001-01-01 00:00:00') + history_visits.visit_time), 'unixepoch'), 'utc'), history_items.url from history_visits, history_items where history_visits.history_item=history_items.id and history_visits.visit_time > (strftime('%s', 'now') - strftime('%s', '2001-01-01 00:00:00') - 2592000*3) order by history_visits.visit_time;"
			
			output += self.collectForQuery(dbFilePath, query)
			output += "\n\n"
		
		return output.rstrip()
			
	
	def collectChrome(self):
		output = ""
		for user in self.userList:
			output += "History for user {0}:\n\n".format(user)
			
			profileList = util.getChromeProfilesForUser(user)
			for profile in profileList:
				output += " > History for profile {0}:\n\n".format(profile)
				
				profilePath = profileList[profile]
				dbFilePath = util.safePathJoin(profilePath, "History")
				if os.path.isfile(dbFilePath):
					self.pathsToCollect.append(dbFilePath)
				else:
					output += "No history found\n\n"
					continue
		
				query = "select strftime('%Y-%m-%d %H:%M:%S', datetime((strftime('%s','1601-01-01 00:00:00') + (visits.visit_time / 1000000)), 'unixepoch'), 'utc'), urls.url from visits, urls where visits.url=urls.id and visits.visit_time > (strftime('%s', 'now') - strftime('%s', '1601-01-01 00:00:00') - 2592000*3) order by visits.visit_time;"
			
				output += self.collectForQuery(dbFilePath, query)
				output += "\n\n"
		
		return output.rstrip()
		
		
	def collectFirefox(self):
		output = ""
		for user in self.userList:
			output += "History for user {0}:\n\n".format(user)
			
			profileList = util.getFirefoxProfilesForUser(user)
			for profile in profileList:
				output += " > History for profile {0}:\n\n".format(profile)
				
				profilePath = profileList[profile]
				dbFilePath = util.safePathJoin(profilePath, "places.sqlite")
				if os.path.isfile(dbFilePath):
					self.pathsToCollect.append(dbFilePath)
				else:
					output += "No history found\n\n"
					continue
		
				query = "select strftime('%Y-%m-%d %H:%M:%S', datetime((moz_historyvisits.visit_date / 1000000), 'unixepoch'), 'utc'), moz_places.url from moz_historyvisits, moz_places where moz_historyvisits.place_id=moz_places.id and moz_historyvisits.visit_date/1000000 > (strftime('%s', 'now') - 2592000*3) order by moz_historyvisits.visit_date;"
			
				output += self.collectForQuery(dbFilePath, query)
				output += "\n\n"
		
		return output.rstrip()
		
		
	# Collect the date and URL from a given database. It is assumed the query will
	# return the date as the first column and the URL as the second column.
	def collectForQuery(self, dbFilePath, query):
		if not dbFilePath:
			return "Error: missing file path"
		if not os.path.isfile(dbFilePath):
			return "No history found"
		if not query or query == "":
			return "Error: missing query"
		
		try:
			db = sqlite3.connect(dbFilePath)
			curs = db.cursor()
			curs.execute(query)
			rows = curs.fetchall()
		
		except Exception as e:
			return "Error reading data\n  {0}".format(str(e))
		
		output = "Date               \tURL\n"
		for row in rows:
			if row[0]:
				visitDate = row[0]
			else:
				visitDate = "Unknown date"
			if row[1]:
				url = row[1]
			else:
				url = "Unknown URL"
			
			output += "{0}\t{1}\n".format(visitDate, url)
		
		return output.rstrip()