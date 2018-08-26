import os
#import tempfile

from musicman.utils.constants import SUPPORTED_FORMATS, VERSION

def parse_args():
	import argparse
	#parser = optparse.OptionParser(usage="%prog [options] [files]",
	#			       version=VERSION)
	#parser = argparse.ArgumentParser(description="Media Library Management Tools",
	#								 usage="%(prog)s [command] [options]")
	parser = argparse.ArgumentParser(description="Media Library Management Tools")
	#subparsers = parser.add_subparsers(help="sub-command-help")
	
	#parser.add_argument('-b', '--base', help="Origin Directory for Library (overrides config)", type=str, dest="originDir")
	#parser.add_argument('-t', '--target', help="Target Directory for Library (overrides config)", type=str, dest="targetDir")
	
	parser.add_argument('--version', help="show version information and exit", action="version", version='%(prog)s '+VERSION)
	parser.add_argument('-v', help='Increase verbosity of processing', dest='verbose', action='count')
	
	subparsers = parser.add_subparsers(title="Command Modes", dest="mode")
	
	clean = subparsers.add_parser('clean', help='Clean Mode', description='Library cleanup operations. Allows you to remove empty directories.')
	clean_lib = clean.add_argument_group('Library Options')
	clean_lib.add_argument('-o', '--origin', help="Origin Directory for Library (overrides config)", metavar="DIR", type=str, dest="originDir")
	clean_lib.add_argument('-t', '--target', help="Target Directory for Library (overrides config)", metavar="DIR", type=str, dest="targetDir")
	clean_lib.add_argument('-w', '--work', help="Working Directory for new processed files (overrides config)", metavar="DIR", type=str, dest="workingDir")
	clean_lib.add_argument('-e', '--exclude', help="Exclude Directory from origin (can be used multiple times)", metavar="DIR", dest='excludeDirs', action='append')
	clean_lib.add_argument('-i', '--include', help="Include Directory from origin (can be used multiple times)", metavar="DIR", dest='includeDirs', action='append')
	clean_act = clean.add_argument_group('Action Options')
	clean_act.add_argument('-g', '--go', help="Clean up library (default just shows what would be done)", dest="act", action='store_true')
	clean.set_defaults(act=False)
	
	convert = subparsers.add_parser('convert', help='Convert Mode', description='Conversion mode scans for media in the origin library, and converts them into the target format. Conversion depends on a fully tagged library, including MusicBrainz metadata. This insures that the data provide is accurate as it uses that metadata for the destination artist/album/song.')
	convert_lib = convert.add_argument_group('Library Options')
	convert_lib.add_argument('-o', '--origin', help="Origin Directory for Library (overrides config)", metavar="DIR", type=str, dest="originDir")
	convert_lib.add_argument('-t', '--target', help="Target Directory for Library (overrides config)", metavar="DIR", type=str, dest="targetDir")
	convert_lib.add_argument('-w', '--work', help="Working Directory for new processed files (overrides config)", metavar="DIR", type=str, dest="workingDir")
	convert_lib.add_argument('--format', help="Target directory library format", metavar="FORMAT", type=str, dest="targetFormat")
	convert_lib.add_argument('-e', '--exclude', help="Exclude Directory from origin (can be used multiple times)", metavar="DIR", dest='excludeDirs', action='append')
	convert_lib.add_argument('-i', '--include', help="Include Directory from origin (can be used multiple times)", metavar="DIR", dest='includeDirs', action='append')
	convert_act = convert.add_argument_group('Action Options')
	convert_act.add_argument('-g', '--go', help="Convert media (default just shows new items)", dest="act", action='store_true')
	convert.set_defaults(act=False)
	
	info = subparsers.add_parser('info', help='Info Mode', description='Displays file and metadata information about specified files and files within specified directories.')
	info.add_argument('paths', help="Show information about files, or all files in directory.", metavar="PATH", nargs='+')

	rename = subparsers.add_parser('rename', help='Rename Mode', description='Library rename tool renames media into their respective Artist/Album/[Disc-][Track-]Title in relation to their metadata.')
	rename_lib = rename.add_argument_group('Library Options')
	rename_lib.add_argument('-o', '--origin', help="Origin Directory for Library (overrides config)", metavar="DIR", type=str, dest="originDir")
	rename_lib.add_argument('-f', '--format', help="Origin Format (flac, m4a, mp3, ...) (overrides config)", metavar="FMT", type=str, dest="origFormat")
	rename_lib.add_argument('-e', '--exclude', help="Exclude Directory from origin (can be used multiple times)", metavar="DIR", dest='excludeDirs', action='append')
	rename_lib.add_argument('-i', '--include', help="Include Directory from origin (can be used multiple times)", metavar="DIR", dest='includeDirs', action='append')
	rename_act = rename.add_argument_group('Action Options')
	rename_act.add_argument('-g', '--go', help="Process renaming (default just shows what would be done", dest="act", action='store_true')
	rename.set_defaults(act=False)
	
	scan = subparsers.add_parser('scan', help='Scan Mode', description='Scan library for various different operational purposes.')
	scan_lib = scan.add_argument_group('Library Options')
	scan_lib.add_argument('-o', '--origin', help="Origin Directory for Library (overrides config)", metavar="DIR", type=str, dest="originDir")
	scan_lib.add_argument('-t', '--target', help="Target Directory for Library (overrides config)", metavar="DIR", type=str, dest="targetDir")
	scan_lib.add_argument('-w', '--work', help="Working Directory for new processed files (overrides config)", metavar="DIR", type=str, dest="workingDir")
	scan_lib.add_argument('--format', help="Target directory library format", metavar="FORMAT", type=str, dest="targetFormat")
	scan_lib.add_argument('-e', '--exclude', help="Exclude Directory from origin (can be used multiple times)", metavar="DIR", dest='excludeDirs', action='append')
	scan_lib.add_argument('-i', '--include', help="Include Directory from origin (can be used multiple times)", metavar="DIR", dest='includeDirs', action='append')
	scan_subparsers = scan.add_subparsers(title='Scan Modes', dest='scanMode')
	scan_untagged = scan_subparsers.add_parser('untagged', help='Find untagged media', description='Scans for untagged or insufficiently tagged media in the library.')
	scan_new = scan_subparsers.add_parser('new', help='Find new unconverted media', description='Scans for new media that is not in the target library for conversion.')

	sync = subparsers.add_parser('sync', help='Sync Mode', description='Moves media from working DIR into target DIR')
	sync_lib = sync.add_argument_group('Library Options')
	#sync_lib.add_argument('-o', '--origin', help="Origin Directory for Library (overrides config)", metavar="DIR", type=str, dest="originDir")
	sync_lib.add_argument('-t', '--target', help="Target Directory for Library (overrides config)", metavar="DIR", type=str, dest="targetDir")
	sync_lib.add_argument('-w', '--work', help="Working Directory for new processed files (overrides config)", metavar="DIR", type=str, dest="workingDir")
	sync_lib.add_argument('-e', '--exclude', help="Exclude Directory from origin (can be used multiple times)", metavar="DIR", dest='excludeDirs', action='append')
	sync_lib.add_argument('-i', '--include', help="Include Directory from origin (can be used multiple times)", metavar="DIR", dest='includeDirs', action='append')
	sync_act = sync.add_argument_group('Action Options')
	sync_act.add_argument('-g', '--go', help="Move media (default just what would be done)", dest="act", action='store_true')
	
	parser.set_defaults(verbose=0)

	return parser.parse_args()

def load_config():
	import configparser
	config = configparser.ConfigParser()
	config.read('musicman.ini')

	try:
		#print("Test1:", config.get('lossless', 'test'))
		config.get('origin', 'path')
		config.get('origin', 'format')
		config.get('target', 'path')
		config.get('target', 'format')
		config.get('working', 'path')
	except configparser.NoOptionError as err:
		print("ERROR: Configuration of required settings are missing:", err)
		sys.exit(1)

	return config
