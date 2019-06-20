# PICT - Post-Infection Collection Toolkit

This set of scripts is designed to collect a variety of data from an endpoint thought to be infected, to facilitate the incident response process. This data should not be considered to be a full forensic data collection, but does capture a _lot_ of useful forensic information.

If you want true forensic data, you should really capture a full memory dump and image the entire drive. That is not within the scope of this toolkit.


## How to use

The script must be run on a live system, not on an image or other forensic data store. It does not strictly _require_ root permissions to run, but it will be unable to collect much of the intended data without.

Data will be collected in two forms. First is in the form of summary files, containing output of shell commands, data extracted from databases, and the like. For example, the `browser` module will output a `browser_extensions.txt` file with a summary of all the browser extensions installed for Safari, Chrome, and Firefox.

The second are complete files collected from the filesystem. These are stored in an `artifacts` subfolder inside the collection folder.


### Syntax

The script is very simple to run. It takes only one parameter, which is required, to pass in a configuration script in JSON format:

`./pict.py -c /path/to/config.json`

The configuration script describes what the script will collect, and how. It should look something like this:

```
{
	"collection_dest" : "~/Desktop/",
	"all_users" : true,
	
	"collectors" : {
		"browser" : "BrowserExtCollector",
		"persist" : "PersistenceCollector",
		"suspicious" : "SuspiciousBehaviorCollector",
		"browserhist" : "BrowserHistoryCollector",
		"bash_config" : "BashConfigCollector",
		"bash_hist" : "BashHistoryCollector",
		"processes" : "ProcessCollector",
		"network_config" : "NetworkConfigCollector",
		"profiles" : "ProfileCollector",
		"certs" : "TrustedCertCollector"
	},
	
	"settings" : {
		"keepLSData" : true,
		"zipIt" : true
	},
	
	"moduleSettings" : {
		"browser" : {
			"collectArtifacts" : true
		}
	},
	
	"unused" : {
		"installs" : "InstallationCollector"
	}
}
```

#### collection_dest

This specifies the path to store the collected data in. It can be an absolute path or a path relative to the user's home folder (by starting with a tilde). The default path, if not specified, is `/Users/Shared`.

Data will be collected in a folder created in this location. That folder will have a name in the form `PICT-computername-YYYY-MM-DD`, where the computer name is the name of the machine specified in *System Preferences* > *Sharing* and date is the date of collection.

#### all_users

If true, collects data from all users on the machine whenever possible. If false, collects data only for the user running the script. If not specified, this value defaults to true.

#### collectors

PICT is modular, and can easily be expanded or reduced in scope, simply by changing what Collector modules are used.

The `collectors` data is a dictionary where the key is the name of a module to load (the name of the Python file without the `.py` extension) and the value is the name of the Collector subclass found in that module. You can add additional entries for custom modules (see [Writing your own modules](#writing-your-own-modules)), or can remove entries to prevent those modules from running. One easy way to remove modules, without having to look up the exact names later if you want to add them again, is to move them into a top-level dictionary named `unused`.

#### settings

This dictionary provides global settings.

`keepLSData` specifies whether the `lsregister.txt` file - which can be quite large - should be kept. (This file is generated automatically and is used to build output by some other modules. It contains a wealth of useful information, but can be well over 100 MB in size. If you don't need all that data, or don't want to deal with that much data, set this to false and it will be deleted when collection is finished.)

`zipIt` specifies whether to automatically generate a zip file with the contents of the collection folder. Note that the process of zipping and unzipping the data will change some attributes, such as file ownership.

#### moduleSettings

This dictionary specifies module-specific settings. Not all modules have their own settings, but if a module does allow for its own settings, you can provide them here. In the above example, you can see a boolean setting named `collectArtifacts` being used with the `browser` module.

There are also global module settings that are maintained by the Collector class, and that can be set individually for each module.

`collectArtifacts` specifies whether to collect the file artifacts that would normally be collected by the module. If false, all artifacts will be omitted for that module. This may be needed in cases where storage space is a consideration, and the collected artifacts are large, or in cases where the collected artifacts may represent a privacy issue for the user whose system is being analyzed.


## Writing your own modules

Modules must consist of a file containing a class that is subclassed from Collector (defined in `collectors/collector.py`), and they must be placed in the `collectors` folder. A new Collector module can be easily created by duplicating the `collectors/template.py` file and customizing it for your own use.

### `def __init__(self, collectionPath, allUsers)`

This method can be overridden if necessary, but the super Collector.__init__() **must** be called in such a case, preferably before your custom code executes. This gives the object the chance to get its properties set up before your code tries to use them.

### `def printStartInfo(self)`

This is a very simple method that will be called when this module's collection begins. Its intent is to print a message to stdout to give the user a sense of progress, by providing feedback about what is happening.

### `def applySettings(self, settingsDict)`

This gives the module the chance to apply any custom settings. Each module can have its own self-defined settings, but the settingsDict should also be passed to the super, so that the Collection class can handle any settings that it defines.

### `def collect(self)`

This method is the core of the module. This is called when it is time for the module to begin collection. It can write as many files as it needs to, but should confine this activity to files within the path `self.collectionPath`, and should use filenames that are not already taken by other modules.

If you wish to collect artifacts, don't try to do this on your own. Simply add paths to the `self.pathsToCollect` array, and the Collector class will take care of copying those into the appropriate subpaths in the `artifacts` folder, and maintaining the metadata (permissions, extended attributes, flags, etc) on the artifacts.

When the method finishes, be sure to call the super (`Collector.collect(self)`) to give the Collector class the chance to handle its responsibilities, such as collecting artifacts.

Your `collect` method can use any data collected in the `basic_info.txt` or `lsregister.txt` files found at `self.collectionPath`. These are collected at the beginning by the `pict.py` script, and can be assumed to be available for use by any other modules. However, you should not rely on output from any other modules, as there is no guarantee that the files will be available when your module runs. Modules may not run in the order they appear in your configuration JSON, since Python dictionaries are unordered.


## Credits

Thanks to Greg Neagle for [FoundationPlist.py](https://github.com/munki/munki/blob/master/code/client/munkilib/FoundationPlist.py), which solved lots of problems with reading binary plists, plists containing date data types, etc.