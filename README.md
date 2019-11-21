# TeamSite_Utilities
A set of utility scripts to run on TeamSite repository to perform tasks you cannot do via the normal interface.  Some of these are written to be integrated into the TeamSite interface via custom entried is drop downs.  Others are completely stand alone.

## Save_Extended_Attributes
A script to run on a TeamSite repository that will save all the extended attributes of the files stored within to a text file.  It will also run in reverse and assign the attributes in a text file to the files in the repository.  This is used to transfer files from one TeamSite instance to another.

## Make_it_a_DCR
A script to run against a file that will tag it with appropriate TeamSite extended attributes for TeamSite to recognize it as a DCR.  Note: DCR attributes are directly related to the file structure where they reside.  If the file does NOT exist in the correct location it will NOT be tagged and TeamSite will NOT recognize it as a DCR.

## Reset Microsoft Terminal Server
A CGI script that will reside on a Windows server and, when accessed, list the currently active MSTS client sessions and allow you to terminate one.  This is useful if the sessions are all taken and you need to get on the server.  Often people just disconnect (i.e. close the window) rather than end their session and this let you kick them off.

## Content Import CGI
A CGI script to allow you to upload individual files or a zip archive and have it store these in the TeamSite repository appropriately.
