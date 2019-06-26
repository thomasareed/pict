# PICT - Post-Infection Collection Toolkit
## Version history

### June 26, 2019

* Improved processing of the hosts file
	* Added detection of suspicious lines in the hosts file
	* Removed buggy and more limited hosts file check from basics.py

### June 24, 2019

* Added collection of browser settings files
  * No collection for Safari, most of its interesting settings are locked away

### June 21, 2019

* Fixed persistence module bug
  * The persistence module was only outputting data for root agents/daemons from launchctl list. It is now showing both root agents/daemons and agents for the current user.