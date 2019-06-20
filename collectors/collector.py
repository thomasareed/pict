import os
import subprocess
import tools.util as util

class Collector:
	collectionPath = ""
	allUsers = True
	userList = []
	pathsToCollect = []
	artifactsFolderName = "artifacts"
	collectArtifacts = True
	
	def __init__(self, collectionPath, allUsers):
		self.collectionPath = collectionPath
		self.allUsers = allUsers
		if self.allUsers:
			self.userList = util.getUserList()
		else:
			self.userList = [].append(os.popen("logname").read().rstrip())
	
	def applySettings(self, settingsDict):
		if "collectArtifacts" in settingsDict:
			self.collectArtifacts = settingsDict["collectArtifacts"]
	
	def printStartInfo(self):
		# Display something about what you're about to do
		pass
	
	def collect(self):
		self.collectFileList(self.pathsToCollect, self.collectionPath)
	
	# Given a list of paths and a location, this will copy each of the paths to the
	# collectionDir, using ditto. The full path hierarchy will be maintained
	# within collectionDir.
	def collectFileList(self, pathList, collectionDir):
		if not self.collectArtifacts:
			return
		
		if not pathList:
			return
		if not collectionDir:
			return
		if collectionDir == "" or not os.path.isdir(collectionDir):
			return
		artifactsFolder = util.safePathJoin(collectionDir, self.artifactsFolderName)
		for onePath in pathList:
			if os.path.exists(onePath):
				try:
					thisDestPath = os.path.join(artifactsFolder, onePath.lstrip("/"))
					# Use subprocess.call to ensure paths are properly escaped
					err = subprocess.call(["ditto", onePath, thisDestPath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					if err:
						print "Error collecting path: {0}".format(onePath)
						print "error = {0}".format(err)
				except Exception as e:
					print "Error collecting path: {0}".format(onePath)
					print e
