# PICT - Post-Infection Collection Toolkit
## Version history

### July 2, 2019

* Added collection of extensions.json from Firefox profiles

### June 29, 2019, part 2

* Added collection of more data
	* [optional] OpenBSM audit log artifacts (which can be viewed with praudit)
	* en0 and en1 config information (so you have a record of the collected machine's IP address!)

### June 29, 2019

* Fixed issue with creation dates collected by fileinfo.py
	* It turns out os.stat().st_ctime cannot be relied on to give the correct creation time on macOS. Instead, os.stat().st_birthtime must be used.

### June 27, 2019

* Added support for log collection
	* Collects system logs, ASL logs, and unified logs. See comments in the logs.py module for details.

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