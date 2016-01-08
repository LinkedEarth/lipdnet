# ![LiPD Logo](https://www.dropbox.com/s/tnt1d10vwx4zlla/lipd_rm_trans.png?raw=1) LiPD

Summary
------

The LiPD package contains different tools that automate the conversion of data formats. Since this package is diverse, there are specific README files for each tool. Please reference the README file for the tool you would like to use for more detailed information.

Overview
------

###### Excel to LPD
>Convert Microsoft Excel (.xslx) format to LPD (.lpd) format.

###### LPD to NOAA
>Convert LPD (.lpd) format to NOAA text (.txt) format.

###### LPD DOI Resolver
>Uses Digital Object Identifier (DOI) name to fetch the most current online data for your record and updates your local copy.


Installation
------
These programs, external modules, and libraries were all tested and built with Python 3.4. Functionality cannot be guaranteed with other versions of Python.

There is not a dedicated installer package currently.

Modules
------
An internal set of modules is used for miscellaneous functions that are used throughout each program. For this reason, keep the modules directory intact for uninterrupted use. 
```
modules
  | bag.py
  | directory.py
  | loggers.py
  | zips.py
```

External Packages
------
###### [XLRD](https://github.com/python-excel/xlrd)
Version:  0.9.3
"Library for developers to extract data from Microsoft Excel (tm) spreadsheet files"

###### [bagit](http://libraryofcongress.github.io/bagit-python/)
Version: 1.5.4
"BagIt is a minimalist packaging format for digital preservation."

Bug Reports
------
If you happen to run into a bug with any of the tools, please feel free to contact us through the LiPD website. Provide a short description of the problem, and a way for us to access the file(s) that caused the error. We'll do our best to get a fix pushed quickly!

Contributors
------
The LiPD team. More information on the LiPD project can be found on the [LiPD website](www.lipd.net).