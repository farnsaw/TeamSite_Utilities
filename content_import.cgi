#!/usr/iw-home/iw-perl/bin/iwperl

######################################################################
#
# Syntax: content_import.cgi
#
#
# Andy Farnsworth - farnsaw@stonedoor.com
#
#
$VERSION = "1.2";
#
######################################################################

use CGI qw/:standard/;
use CGI::Carp qw/fatalsToBrowser/;
use TeamSite::Config;
use File::Path;

my $iwhome  = TeamSite::Config::iwgethome();
my $iwmount = TeamSite::Config::iwgetmount();

my %permittedActions;
   $permittedActions{default}			= 1;
   $permittedActions{upload_file}		= 1;
   $permittedActions{upload_expand_zip}	= 1;
   $permittedActions{delete_file}		= 1;
   $permittedActions{set_metadata}		= 1;
   $permittedActions{show_code}			= 1;
   $permittedActions{debug}				= 1;

my %passwordList;
   $passwordList{"/default/main/www/fidelitypensions/docs_reports/WORKAREA/content"} = '/dFt0MZjxDWZI';

my $logfilename = "";

#
# Initialization
#
init();

#
# Get the current action or set action to "default" if there is no action set.
#
unless ($action = param('action')) { $action = "default"; }

#
# Check for permitted Actions.
#

reportStatus(-1, "Invalid or missing 'action' parameter. ($action)") unless ($permittedActions{$action});

#
# Call the function named the same as the action.
#

&$action;

print LOGFILE "[", scalar localtime(), "] End $logfilename.cgi LOG\n";
close LOGFILE;
exit;

#
#	----------------------------------------------------------------------------------------------------
#
#		The following subroutines represent the various states the program is run in.
#		Note that they do not require an "exit" command as the code will only execute
#		the one function that is appropriate.
#
#		To add an action to your CGI_Task, you just need to add the appropriate subroutine
#		and a way for it to be called by adding the action hidden variable to one of the
#		other subroutines with a value equal to that of the name of your new subroutine.
#
#	----------------------------------------------------------------------------------------------------
#

sub default
{
	show_form();
}

sub show_form
{
#
#	The "show_form" action that displays the initial form for the user to fill in and manipulate.
#	This is the action that is executed whenever there is no other action and therefor, it is displayed first.
#

	print <<END_HTML;
<html>
	<head>
		<title>Upload File</title>
	</head>
	<body>
		<center>
END_HTML

	print $cgi->start_multipart_form(-method=>"POST", -action=>$FORM_ACTION);
	print $cgi->hidden('action','upload_file');
	print "<table border='1'>\n";
	print "<tr><th colspan='2' align='center'>File Management <font size='-1'>v$VERSION</font></th></tr>\n";
	print "<tr><th>File to Upload</th><td>", $cgi->filefield(	-name=>'upload_file', -default=>'starting value', -size=>80, -maxlength=>800), "</td></tr>\n";

	print "<tr><th>Workarea Path</th><td>", textfield(-name=>'workarea', -default=>'/default/main/www/fidelitypensions/docs_reports/WORKAREA/content', -size=>100, -maxlength=>100), "</td></tr>\n";
	print "<tr><th>Password</th><td>", password_field(-name=>'password',-value=>'fidelitypensions_docs_reports',-size=>80,-maxlength=>80), "</td></tr>\n";
	print "<tr><th>Destination Path</th><td>", textfield(-name=>'dest_path', -default=>'/Reports/Client_1/QIR', -size=>80, -maxlength=>80), "</td></tr>\n";
	print "<tr><th>Filename</th><td>", textfield(-name=>'filename', -default=>'filename', -size=>80, -maxlength=>80), "</td></tr>\n";

	print "<tr><th>Metadata Key</th><td>", textfield(-name=>'metadatakey', -default=>'Key 1', -size=>80, -maxlength=>80), "</td></tr>\n";
	print "<tr><th>Metadata Value</th><td>", textfield(-name=>'metadatavalue', -default=>'Value 1', -size=>80, -maxlength=>80), "</td></tr>\n";
	print "<tr><th>Metadata Key</th><td>", textfield(-name=>'metadatakey', -default=>'Key 2', -size=>80, -maxlength=>80), "</td></tr>\n";
	print "<tr><th>Metadata Value</th><td>", textfield(-name=>'metadatavalue', -default=>'Value 2', -size=>80, -maxlength=>80), "</td></tr>\n";
	print "<tr><th>Overwrite</th><td>", radio_group(-name=>'overwrite', -values=>['TRUE','FALSE'], -default=>'FALSE'), "</td></tr>\n";

	print "<tr><td colspan='2' align='center'>", $cgi->submit(-name=>'Submit', -value=>'Submit'), "</td></tr>\n";
	print "</table>\n";
	print $cgi->endform;

print <<END_HTML;
		</center>
	</body>
</html>
END_HTML
}

sub upload_file
{
	my $upload_file		= $cgi->param('upload_file');

	my $workarea		= $cgi->param('workarea');		$workarea  =~ s|^\s+||go;	$workarea  =~ s|\s+$||go;
	my $password		= $cgi->param('password');		$password  =~ s|^\s+||go;	$password  =~ s|\s+$||go;
	my $dest_path		= $cgi->param('dest_path');		$dest_path =~ s|^\s+||go;	$dest_path =~ s|\s+$||go;
	my $filename		= $cgi->param('filename');		$filename  =~ s|^\s+||go;	$filename  =~ s|\s+$||go;
	my @metadatakeys	= $cgi->param('metadatakey');
	my @metadatavalues	= $cgi->param('metadatavalue');
	my $overwrite		= $cgi->param('overwrite');		$overwrite  =~ s|^\s+||go;	$overwrite  =~ s|\s+$||go;

	print LOGFILE "Call: upload_file\n";
	print LOGFILE "------------------\n";
	print LOGFILE "[",scalar localtime(),"]\n";
	print LOGFILE "------------------\n";
	print LOGFILE "\taction = $action\n";
	print LOGFILE "\tworkarea = $workarea\n";
	print LOGFILE "\tpassword = $password\n";
	print LOGFILE "\tdest_path = $dest_path\n";
	print LOGFILE "\tfilename = $filename\n";
	print LOGFILE "\toverwrite = $overwrite\n";
	print LOGFILE "\tmetadatakeys = ", join(' | ', @metadatakeys), "\n";
	print LOGFILE "\tmetadatavalues = ", join(' | ', @metadatavalues), "\n";

	unless (length $workarea)
	{
		reportStatus(-9, "Invalid or missing workarea parameter. ($workarea)");
	}

	unless ( (exists $passwordList{$workarea}) && ($passwordList{$workarea} eq crypt($password,$passwordList{$workarea})) )
	{
		print LOGFILE $passwordList{$workarea}, " eq ", crypt($password,$passwordList{$workarea});
		reportStatus(-2, "Incorrect password");
	}

	$dest_path =~ s|^/||o;
	$dest_path =~ s|/$||o;
	$dest_path = '/' . $dest_path if (length $dest_path);

	#$filename =~ s|\s+|_|go;
	$filename =~ s|^/||o;
	$filename = '/' . $filename if (length $filename);

	my $fullpath = $iwmount . $workarea . $dest_path . $filename;
	my $dest_dir = $iwmount . $workarea . $dest_path;

	print LOGFILE "fullpath = $fullpath\n";
	print LOGFILE "dest_dir = $dest_dir\n";

	$overwrite = lc $overwrite;
	reportStatus(-3, "File already exists, use overwrite flag to overwrite this file: $fullpath") if ( (-f $fullpath) && ('true' ne $overwrite) );

	if (-d $dest_dir)
	{
		print LOGFILE "Directory exists: $dest_dir\n";
	}
	else
	{
		print LOGFILE "mkpath($dest_dir)\n" unless (-d $dest_dir);
		eval { mkpath($dest_dir) unless (-d $dest_dir); };
	}

	open OUTFILE, ">$fullpath" or reportStatus(-4, "Could not open file for writing. $!\n");
	while ($bytesread=read($upload_file,$buffer,1024))
	{
		print OUTFILE $buffer;
	}
	close OUTFILE;

	unless ((stat($fullpath))[7])
	{
		reportStatus(-10, "Uploaded file has ZERO length. ($filename)");
		return();
	}

	my $loopcount = 0;
	push @metadatakeys, "TeamSite/Metadata/timestamp";
	push @metadatavalues, scalar localtime();
	foreach $metadatakey (@metadatakeys)
	{
		my $metadatavalue = $metadatavalues[$loopcount++];
		next if (0 == length $metadatakey);
		my $cmd = qq|$iwhome/bin/iwextattr -S "$metadatakey=$metadatavalue" "$fullpath"|;
		my $rv = `$cmd 2>&1`;
		print LOGFILE "cmd: $cmd\n";
		print LOGFILE "rv : $rv\n";
	}
	iwsubmit($fullpath, "File uploaded and metadata attached by content_import[$action]");
	reportStatus(0, "The file has been uploaded to: $fullpath");
}

sub upload_expand_zip
{
	my $upload_file		= $cgi->param('upload_file');

	my $workarea		= $cgi->param('workarea');		$workarea  =~ s|^\s+||go;	$workarea  =~ s|\s+$||go;
	my $password		= $cgi->param('password');		$password  =~ s|^\s+||go;	$password  =~ s|\s+$||go;
	my $dest_path		= $cgi->param('dest_path');		$dest_path =~ s|^\s+||go;	$dest_path =~ s|\s+$||go;
	my $filename		= $cgi->param('filename');		$filename  =~ s|^\s+||go;	$filename  =~ s|\s+$||go;
	my @metadatakeys	= $cgi->param('metadatakey');
	my @metadatavalues	= $cgi->param('metadatavalue');
	my $overwrite		= $cgi->param('overwrite');		$overwrite  =~ s|^\s+||go;	$overwrite  =~ s|\s+$||go;

	print LOGFILE "Call: upload_expand_zip\n";
	print LOGFILE "------------------\n";
	print LOGFILE "[",scalar localtime(),"]\n";
	print LOGFILE "------------------\n";
	print LOGFILE "\taction = $action\n";
	print LOGFILE "\tworkarea = $workarea\n";
	print LOGFILE "\tpassword = $password\n";
	print LOGFILE "\tdest_path = $dest_path\n";
	print LOGFILE "\tfilename = $filename\n";
	print LOGFILE "\toverwrite = $overwrite\n";
	print LOGFILE "\tmetadatakeys = ", join(' | ', @metadatakeys), "\n";
	print LOGFILE "\tmetadatavalues = ", join(' | ', @metadatavalues), "\n";

	unless (length $workarea)
	{
		reportStatus(-9, "Invalid or missing workarea parameter. ($workarea)");
	}

	unless ( (exists $passwordList{$workarea}) && ($passwordList{$workarea} eq crypt($password,$passwordList{$workarea})) )
	{
		print LOGFILE $passwordList{$workarea}, " eq ", crypt($password,$passwordList{$workarea});
		reportStatus(-2, "Incorrect password");
	}

	$dest_path =~ s|^/||o;
	$dest_path =~ s|/$||o;
	$dest_path = '/' . $dest_path if (length $dest_path);

	#$filename =~ s|\s+|_|go;
	$filename =~ s|^/||o;
	$filename = '/' . $filename if (length $filename);

	my $fullpath = $iwmount . $workarea . $dest_path . $filename;
	my $tmp_path = "/tmp" . $filename;
	my $dest_dir = $iwmount . $workarea . $dest_path;

	print LOGFILE "fullpath = $fullpath\n";
	print LOGFILE "tmp_path = $tmp_path\n";
	print LOGFILE "dest_dir = $dest_dir\n";

	if (-d $dest_dir)
	{
		print LOGFILE "Directory exists so remove contents: $dest_dir\n";
		
		print LOGFILE "cleanup($dest_dir)\n";
		cleanup($dest_dir);
		iwsubmit($dest_dir, "File deleted by content_import[$action]");
	}

	print LOGFILE "mkpath($dest_dir)\n" unless (-d $dest_dir);
	eval { mkpath($dest_dir) unless (-d $dest_dir); };

	open OUTFILE, ">$tmp_path" or reportStatus(-8, "Could not open temp file for writing. $!\n");
	while ($bytesread=read($upload_file,$buffer,1024))
	{
		print OUTFILE $buffer;
	}
	close OUTFILE;

	unless ((stat($tmp_path))[7])
	{
		reportStatus(-10, "Uploaded zip file has ZERO length. ($filename)");
		return();
	}

	unzip($tmp_path, $dest_dir);
	unlink $tmp_path;

#	my $loopcount = 0;
#	foreach $metadatakey (@metadatakeys)
#	{
#		my $metadatavalue = $metadatavalues[$loopcount++];
#		my $cmd = qq|$iwhome/bin/iwextattr -S "$metadatakey=$metadatavalue" "$fullpath"|;
#		my $rv = `$cmd 2>&1`;
#		print LOGFILE "cmd: $cmd\n";
#		print LOGFILE "rv : $rv\n";
#	}
	iwsubmit($dest_dir, "Zip File uploaded and expanded by content_import[$action]");
	reportStatus(0, "The file has been expanded into: $dest_dir");
}

sub unzip
{
	my ($tmp_path, $dest_dir) = @_;
# UnZip 5.32 of 3 November 1997, by Info-ZIP.  Maintained by Greg Roelofs.  Send
# bug reports to the authors at Zip-Bugs@lists.wku.edu; see README for details.
#
# Usage: unzip [-Z] [-opts[modifiers]] file[.zip] [list] [-x xlist] [-d exdir]
#   Default action is to extract files in list, except those in xlist, to exdir;
#   file[.zip] may be a wildcard.  -Z => ZipInfo mode ("unzip -Z" for usage).
#
#   -p  extract files to pipe, no messages     -l  list files (short format)
#   -f  freshen existing files, create none    -t  test compressed archive data
#   -u  update files, create if necessary      -z  display archive comment
#   -x  exclude files that follow (in xlist)   -d  extract files into exdir
#
# modifiers:                                   -q  quiet mode (-qq => quieter)
#   -n  never overwrite existing files         -a  auto-convert any text files
#   -o  overwrite files WITHOUT prompting      -aa treat ALL files as text
#   -j  junk paths (do not make directories)   -v  be verbose/print version info
#   -C  match filenames case-insensitively     -L  make (some) names lowercase
#   -X  restore UID/GID info                   -V  retain VMS version numbers
#                                              -M  pipe through "more" pager
# Examples (see unzip.doc for more info):
#   unzip data1 -x joe   => extract all files except joe from zipfile data1.zip
#   unzip -p foo | more  => send contents of foo.zip via pipe into program more
#   unzip -fo foo ReadMe => quietly replace existing ReadMe if archive file newer

	my $cmd = qq|/usr/bin/unzip -o -qq "$tmp_path" -d "$dest_dir"|;
	my $rv  = qx|$cmd 2>&1|;
	print LOGFILE "cmd: $cmd\n";
	print LOGFILE "rv : $rv\n";
	
	# if the return value is empty then the extraction was completely successful, otherwise it failed
	# and the contents should be deleted
	if ($rv ne "") {
		print LOGFILE "Error extracting zip so deleting directory contents\n";
		print LOGFILE "cleanup($dest_dir)\n";
		cleanup($dest_dir);
		iwsubmit($dest_dir, "File deleted by content_import[$action]");
		
		reportStatus(-11, "Extraction of uploaded zip file has failed. Error: $rv");
	}
	
	return();
}

sub set_metadata
{
	my $workarea		= $cgi->param('workarea');		$workarea  =~ s|^\s+||go;	$workarea  =~ s|\s+$||go;
	my $password		= $cgi->param('password');		$password  =~ s|^\s+||go;	$password  =~ s|\s+$||go;
	my $dest_path		= $cgi->param('dest_path');		$dest_path =~ s|^\s+||go;	$dest_path =~ s|\s+$||go;
	my $filename		= $cgi->param('filename');		$filename  =~ s|^\s+||go;	$filename  =~ s|\s+$||go;
	my @metadatakeys	= $cgi->param('metadatakey');
	my @metadatavalues	= $cgi->param('metadatavalue');
	my $overwrite		= $cgi->param('overwrite');		$overwrite  =~ s|^\s+||go;	$overwrite  =~ s|\s+$||go;

	print LOGFILE "Call: set_metadata\n";
	print LOGFILE "------------------\n";
	print LOGFILE "[",scalar localtime(),"]\n";
	print LOGFILE "------------------\n";
	print LOGFILE "\taction = $action\n";
	print LOGFILE "\tworkarea = $workarea\n";
	print LOGFILE "\tpassword = $password\n";
	print LOGFILE "\tdest_path = $dest_path\n";
	print LOGFILE "\tfilename = $filename\n";
	print LOGFILE "\toverwrite = $overwrite\n";
	print LOGFILE "\tmetadatakeys = ", join(' | ', @metadatakeys), "\n";
	print LOGFILE "\tmetadatavalues = ", join(' | ', @metadatavalues), "\n";

	unless (length $workarea)
	{
		reportStatus(-9, "Invalid or missing workarea parameter. ($workarea)");
	}

	reportStatus(-2, "Incorrect password") unless ( (exists $passwordList{$workarea}) && ($passwordList{$workarea} eq crypt($password,$passwordList{$workarea})) );

	$dest_path =~ s|^/||o;
	$dest_path =~ s|/$||o;
	$dest_path = '/' . $dest_path if (length $dest_path);

	#$filename =~ s|\s+|_|go;
	$filename =~ s|^/||o;
	$filename = '/' . $filename if (length $filename);

	my $fullpath = $iwmount . $workarea . $dest_path . $filename;
	my $dest_dir = $iwmount . $workarea . $dest_path;

	print LOGFILE "fullpath = $fullpath\n";
	print LOGFILE "dest_dir = $dest_dir\n";
	reportStatus(-5, "Cannot set metadata on file. File does not exist. $fullpath") unless (-f $fullpath);

	my $loopcount = 0;
	foreach $metadatakey (@metadatakeys)
	{
		my $metadatavalue = $metadatavalues[$loopcount++];
		my $cmd = qq|$iwhome/bin/iwextattr -S "$metadatakey=$metadatavalue" "$fullpath"|;
		my $rv = `$cmd 2>&1`;
		print LOGFILE "cmd: $cmd\n";
		print LOGFILE "rv : $rv\n";
	}
	iwsubmit($fullpath, "File metadata attached by content_import[$action]");
	reportStatus(0, "Metadata[$loopcount] has been set on the file: $fullpath");
}

sub delete_file
{
	my $workarea		= $cgi->param('workarea');		$workarea  =~ s|^\s+||go;	$workarea  =~ s|\s+$||go;
	my $password		= $cgi->param('password');		$password  =~ s|^\s+||go;	$password  =~ s|\s+$||go;
	my $dest_path		= $cgi->param('dest_path');		$dest_path =~ s|^\s+||go;	$dest_path =~ s|\s+$||go;
	my $filename		= $cgi->param('filename');		$filename  =~ s|^\s+||go;	$filename  =~ s|\s+$||go;

	print LOGFILE "Call: delete_file\n";
	print LOGFILE "------------------\n";
	print LOGFILE "[",scalar localtime(),"]\n";
	print LOGFILE "------------------\n";
	print LOGFILE "\taction = $action\n";
	print LOGFILE "\tworkarea = $workarea\n";
	print LOGFILE "\tpassword = $password\n";
	print LOGFILE "\tdest_path = $dest_path\n";
	print LOGFILE "\tfilename = $filename\n";

	unless (length $workarea)
	{
		reportStatus(-9, "Invalid or missing workarea parameter. ($workarea)");
	}

	reportStatus(-2, "Incorrect password") unless ( (exists $passwordList{$workarea}) && ($passwordList{$workarea} eq crypt($password,$passwordList{$workarea})) );

	$dest_path =~ s|^/||o;
	$dest_path =~ s|/$||o;
	$dest_path = '/' . $dest_path if (length $dest_path);

	#$filename =~ s|\s+|_|go;
	$filename =~ s|^/||o;
	$filename = '/' . $filename if (length $dest_path);

	my $fullpath = $iwmount . $workarea . $dest_path . $filename;
	my $dest_dir = $iwmount . $workarea . $dest_path;

	print LOGFILE "fullpath = $fullpath\n";
	print LOGFILE "dest_dir = $dest_dir\n";
	reportStatus(-6, "Cannot delete the file. File does not exist. $fullpath") unless (-f $fullpath);

	unless (unlink $fullpath)
	{
		reportStatus(-7, "Cannot delete the file.\t$fullpath\t$!") unless (-f $fullpath);
	}

	#
	#	Note: When submitting a deleted file, you MUST use a vpath and not a full path.
	#	NO  : /iwmnt/default/main/www/...
	#   YES : /default/main/www/...
	#
	$fullpath =~ s|^/\.?iwmnt||o;
	print LOGFILE "vpath for submit = $fullpath\n";
	iwsubmit($fullpath, "File deleted by content_import[$action]");

	reportStatus(0, "The file has been deleted: $fullpath");
}

sub show_code
{
	my $workarea		= $cgi->param('workarea');		$workarea  =~ s|^\s+||go;	$workarea  =~ s|\s+$||go;
	my $password		= $cgi->param('password');		$password  =~ s|^\s+||go;	$password  =~ s|\s+$||go;

	unless (length $workarea)
	{
		reportStatus(-9, "Invalid or missing workarea parameter. ($workarea)");
	}

	reportStatus(-2, "Incorrect password") unless ( (exists $passwordList{$workarea}) && ($passwordList{$workarea} eq crypt($password,$passwordList{$workarea})) );

	open CODE, "<$0" or reportStatus(-99, "Show code failed, could not open source code file: $0");
	my @codelisting = <CODE>;
	close CODE;

	my $list = join "", @codelisting;
	$list =~ s|&|&amp;|go;
	$list =~ s|<|&lt;|go;
	$list =~ s|>|&gt;|go;

	print "<HTML><BODY>CODE (showcode)<hr>\n<pre>$list</pre></body></html>";
}

#
#	----------------------------------------------------------------------------------------------------
#
#		The following subroutines are support routines for the system.
#
#	----------------------------------------------------------------------------------------------------
#

sub iwsubmit
{
	my ($fullpath, $comment) = @_;
	my $cmd = qq|$iwhome/bin/iwsubmit -x -u "$fullpath" "$comment"|;
	my $rv = `$cmd 2>&1`;
	print LOGFILE "cmd = $cmd\n";
	print LOGFILE "rv = $rv\n";
}


sub init
{
	#
	# Since this code is running as a CGI, we need to turn on Auto Flush
	#
	$| = 1;

	#
	# Tell the browser what type of content to expect
	# If your form will return different types of content in addition to text/html
	# you will need to move this output into the action subroutines.
	#
	print "Content-type:  text/html\n\n";

	#
	# Create a CGI object and parse all the parameters passed to us.
	#
	$cgi = new CGI;

	#
	# Build the action for the action attribute to the form tag.
	#
	$FORM_ACTION = $0;
	$FORM_ACTION =~ s|.*/httpd||o;

#	my $logpath = "/var/adm/log";
	my $logpath = "/tmp/log";
	
	
	$logfilename = $0;
	$logfilename =~ s|\\|/|o;
	$logfilename =~ s|.*/(\w+)\..+|$1|o;
	my $logfilepath = $logpath . "/" . $logfilename . ".log";
	open LOGFILE, ">>$logfilepath";
	print LOGFILE "[", scalar localtime(), "] Begin $logfilename.cgi LOG\n";
	print LOGFILE "[", scalar localtime(), "] FORM_ACTION : $FORM_ACTION\n";
	print LOGFILE "\nCGI PARAMS\n----------\n";
	@names = param();
	foreach $name (@names)
	{
		my $value = param($name);
		print LOGFILE "[", scalar localtime(), "] $name = $value\n";
	}
	print LOGFILE "\n\n";

	return();
}

sub reportStatus
{
	my ($STATUS_CODE, $STATUS_MSG) = @_;

	print "STATUS_CODE:", $STATUS_CODE, "\n";
	print "STATUS_MSG:", $STATUS_MSG, "\n";
	print "VERSION:", $VERSION, "\n";

	print LOGFILE "[", scalar localtime(), "] STATUS_CODE:", $STATUS_CODE, "\n";
	print LOGFILE "[", scalar localtime(), "] STATUS_MSG:", $STATUS_MSG, "\n";
	print LOGFILE "[", scalar localtime(), "] VERSION:", $VERSION, "\n";

	if ($STATUS_CODE < 0)
	{
		print LOGFILE "[", scalar localtime(), "] End $logfilename.cgi LOG\n";
		close LOGFILE;
		exit;
	}
}

sub debuginfo
{	my $whoami = `/usr/ucb/whoami`;

	my $debug_info=<<END_DEBUG;
		<hr>
		<center>
		<table>
		<tr><th colspan='2'>DEBUG: Var list</th></tr>
		<tr><td>filename</td><td>$filename</td></tr>
		<tr><td>dest_path</td><td>$dest_path</td></tr>
		<tr><td>password</td><td>$password</td></tr>
		<tr><td>metadatakeys</td><td>@metadatakeys</td></tr>
		<tr><td>metadatavalues</td><td>@metadatavalues</td></tr>
		<tr><td>workarea</td><td>$workarea</td></tr>
		<tr><td>fullpath</td><td>$fullpath</td></tr>
		<tr><td>whoami</td><td>$whoami</td></tr>
		</table>
		</center>
		<hr>
END_DEBUG
}

sub cleanup {
	my $dir = shift;
	local *DIR;
	
	opendir DIR, $dir or die "opendir $dir: $!";
	my $found = 0;
	while ($_ = readdir DIR) {
		next if /^\.{1,2}$/;
		my $path = "$dir/$_";
		unlink $path if -f $path;
		cleanupinside($path) if -d $path;
	}
	closedir DIR;
}

sub cleanupinside {
	my $dir = shift;
	local *DIR;
	
	opendir DIR, $dir or die "opendir $dir: $!";
	my $found = 0;
	while ($_ = readdir DIR) {
		next if /^\.{1,2}$/;
		my $path = "$dir/$_";
		unlink $path if -f $path;
		cleanup($path) if -d $path;
	}
	closedir DIR;
	rmdir $dir or print "error - $!";
}