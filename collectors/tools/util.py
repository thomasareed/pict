#!/usr/bin/python

import os
import subprocess
import json

userList = []


# Safely join two paths
# os.path.join can fail to properly join paths if the second path component
# begins with '/'. In such a case, it returns only the second path.
# So, it's necessary to strip any leading '/' from the second path.
def safePathJoin(firstPart, secondPart):
	newPath = os.path.join(firstPart, secondPart.lstrip("/"))
	return newPath


# Build a list of the names of all user folders in /Users/
def getUserList():
	if not userList:
		# userList is empty, need to build it
		userFolderItems = os.listdir("/Users/")
		for item in userFolderItems:
			itemPath = os.path.join("/Users", item)
			if os.path.isdir(itemPath) and (item != "Shared") and (item != "Guest"):
				userList.append(item)
	return userList


# Build a list of paths to all Chrome profile folders for the given user
def getChromeProfilesForUser(user):
	localStatePath = "/Users/{0}/Library/Application Support/Google/Chrome/Local State".format(user)
	if not os.path.isfile(localStatePath):
		return {}
	f = open(localStatePath, "r")
	localStateJSON = f.read()
	f.close
	localStateDict = json.loads(localStateJSON)
	profileList = localStateDict['profile']['info_cache'].keys()
	profilePathList = {}
	for profile in profileList:
		profilePathList[profile] = "/Users/{0}/Library/Application Support/Google/Chrome/{1}".format(user, profile)
	return profilePathList

# Build a list of paths to all Firefox profile folders for the given user
def getFirefoxProfilesForUser(user):
	profilesFolder = "/Users/{0}/Library/Application Support/Firefox/Profiles/".format(user)
	if not os.path.isdir(profilesFolder):
		return {}
	profileList = os.listdir(profilesFolder)
	profilePathList = {}
	for profile in profileList:
		profilePathList[profile] = safePathJoin(profilesFolder, profile)
	return profilePathList
