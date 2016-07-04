#!/usr/bin/env python3

from __future__ import division, absolute_import, print_function, unicode_literals

import os
import signal
import sys
#import mutagen
import time
#from path import path

import musicman

#from musicman.utils.constants import (
#	VERSION,
#	NO_TAGS
#)
#from musicman.utils import (
#	parse_args,
#	load_config
#)
#from musicman.utils.metadata import MetaTag

def spinning_cursor():
	while True:
		for cursor in '|/-\\':
			yield cursor

spinner = spinning_cursor()

def supports_color():
	"""
	Returns True if the running system's terminal supports color, and False
	otherwise.
	"""
	plat = sys.platform
	supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
	                                          'ANSICON' in os.environ)
	# isatty is not always implemented, #6223.
	is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
	if not supported_platform or not is_a_tty:
		return False
	return True

def clearLine():
	if supports_color():
		sys.stdout.write('\033[K')
		sys.stdout.flush()

def sanitize(text):
	newtext = text
	newtext = newtext.replace('<', '').replace('>', '').replace(':', '').replace('"', '').replace('|', '').replace('?', '').replace('*', '')
	newtext = newtext.replace('/', '-')
	newtext = newtext.strip()
	#if newtext != text:
	#	clearLine()
	#	print("text:", text)
	#	print(" new:", newtext)
	return newtext

def getLibrary(path, excludeDirs=[]):
	if os.path.isdir(path):
		for root, directories, filenames in sorted(os.walk(path)):
			if root not in excludeDirs:
				for filename in filenames:
					yield os.path.join(root, filename)
	
# 	files=[]
# 	
# 	if os.path.isdir(path):
# 		for libraryDir, artists, dummy in os.walk(path):
# 			for artist in sorted(artists):
# 				for artistDir, albums, dummy in os.walk(os.path.join(libraryDir, artist)):
# 					if artistDir in excludeDirs:
# 						#clearLine()
# 						#print("Excluding:", artistDir)
# 						#print()
# 						continue
# 					for album in sorted(albums):
# 						for albumDir, dummy, songs in os.walk(os.path.join(artistDir, album)):
# 							if albumDir in excludeDirs:
# 								#clearLine()
# 								#print("Excluding:", albumDir)
# 								#print()
# 								continue
# 							#print("AlbumDir:", albumDir)
# 							#print("  Artist:", artist)
# 							#print("   Album:", album)
# 							for song in songs:
# 								print("Scanning", path, next(spinner), end="\r")
# 								files.append(os.path.join(albumDir, song))
# 									#print("Path:", os.path.join(albumDir, song))
# 		clearLine()
# 		print("Scan complete!")
# 		return files

def getEmptyDirs(path, excludeDirs=[]):
	if os.path.isdir(path):
		for root, directories, filenames in sorted(os.walk(path)):
			if root not in excludeDirs:
				if not directories and not filenames:
					yield root

def getSong(file):
	from musicman.utils.metadata import MetaTag
	from musicman.utils.constants import INTERNAL_FORMATS
	global config
	song = {}
	
	#if file.endswith(INTERNAL_FORMATS):
	if (os.path.splitext(file)[1][1:] in INTERNAL_FORMATS):
		metadata = MetaTag(file)

		if metadata.tags.get("artist") is None or len(metadata.tags.get("artist")) < 1:
			return {'metadata': None}
		elif metadata.tags.get("albumartist") is None or len(metadata.tags.get("albumartist")) < 1:
			return {'metadata': None}
		elif metadata.tags.get('album') is None or len(metadata.tags.get("album")) < 1:
			return {'metadata': None}
		elif metadata.tags.get("musicbrainz_albumid") is None or len(metadata.tags.get("musicbrainz_albumid")) < 5:
			return {'metadata': None}
		else:
			song['metadata'] = metadata
			song['artistName'] = sanitize(metadata.tags["albumartist"]) 
			song['albumName'] = sanitize(metadata.tags["album"])
			song['titleName'] = sanitize(metadata.tags["title"])
			if isinstance(metadata.tags.get("totaldiscs", 0), tuple):
				song['discnumber'] = int(metadata.tags.get('totaldiscs', 0)[0])
				song['totaldiscs'] = int(metadata.tags.get("totaldiscs", 0)[1])
			else:
				song['discnumber'] = int(metadata.tags.get('discnumber', 0))
				song['totaldiscs'] = int(metadata.tags.get("totaldiscs", 0))
			if isinstance(metadata.tags.get('totaltracks', 0), tuple):
				song['tracknumber'] = int(metadata.tags.get('totaltracks', 0)[0])
				song['totaltracks'] = int(metadata.tags.get('totaltracks', 0)[1])
			else:
				song['tracknumber'] = int(metadata.tags.get('tracknumber', 0))
				song['totaltracks'] = int(metadata.tags.get('totaltracks', 0))
			
			if song['totaldiscs'] > 1:
				song['outPath'] = os.path.join(song['artistName'], song['albumName'])
				song['outFile'] = '{0:d}-{1:02d}-{2}'.format(song['discnumber'],
																song['tracknumber'],
																song['titleName'])
			else:
				if metadata.tags.get("tracknumber") is not None:
					song['outPath'] = os.path.join(song['artistName'], song['albumName'])
					song['outFile'] = '{0:02d}-{1}'.format(song['tracknumber'], song['titleName']) 
				else:
					song['outPath'] = os.path.join(song['artistName'], song['albumName'])
					outFile = '{0}'.format(song['titleName'])
			
			return song
	else:
		clearLine()
		print("FATAL: File extension \"{0}\" is not supported.".format(os.path.splitext(file)[1]))
		print("       Supported:", ", ".join(INTERNAL_FORMATS))
		sys.exit(2)

def getSongPaths(song):
	global originDir
	global workingDir
	global targetDir
	
	print("DEBUG:", originDir)
	print("DEBUG:", workingDir)
	print("DEBUG:", targetDir)
	
	sys.exit(0)

def cleanLibrary(originDir, excludeDirs=[], act=False, verbose=0):
	global config
	
	if excludeDirs is None:
		excludeDirs=[]
	
	print("Clean Dirs")

	#while getEmptyDirs(originDir, excludeDirs) != [] and act == True and tries > 0:
	
	if act:
		try:
			while getEmptyDirs(originDir, excludeDirs).__next__():
				for path in getEmptyDirs(originDir, excludeDirs):
					print("Removing:", path)
					
					if act:
						try:
							os.rmdir(path)
						except OSError as err:
							print("ERROR: Failed to remove directory:", err)
							sys.exit(5)
		except StopIteration:
			pass
	else:
		for path in getEmptyDirs(originDir, excludeDirs):
			print("Empty:", path)
	
	print("Processing Complete!")
	
def renameLibrary(originDir, excludeDirs=[], act=False, verbose=0):
	global config
	
	if excludeDirs is None:
		excludeDirs=[]
	
	print("Rename")
	for file in getLibrary(originDir, excludeDirs):
		#print("File:", file)
		if (os.path.isdir(os.path.dirname(file)) and os.path.isfile(file)):
			clearLine()
			print("Processing:", os.path.dirname(os.path.dirname(file)), next(spinner), end="\r")
			
			song = getSong(file)
			
			#print("song", song)
			if song['metadata'] is None:
				if verbose > 2:
					clearLine()
					print("Skipping: {0} due to lack of metadata".format(file))
			else:
				filename = os.path.basename(file)
				file_ext = os.path.splitext(filename)[1]
				
				if not os.path.isfile(os.path.join(originDir, song['outPath'], song['outFile'] + file_ext)):
					clearLine()
					print("Found:", file)
					if verbose > 0:
						print("  New:", os.path.join(originDir, song['outPath'], song['outFile'] + file_ext))
					
					if (act):
						if verbose > 1:
							print("Renaming: \"{0}\" -> \"{1}\"".format(file, os.path.join(originDir, song['outPath'], song['outFile'] + file_ext)))
						try:
							os.renames(file,
									os.path.join(originDir,
												song['outPath'],
												song['outFile'] + file_ext))
						except OSError as err:
							print("ERROR: Failed to move:", err)
							sys.exit(5)
	
	clearLine()
	print("Processing Complete!")

def findUntagged(originDir, excludeDirs=[], verbose=0):
	global config
	
	if excludeDirs is None:
		excludeDirs=[]
	
	print("Find Untagged")
	for file in getLibrary(originDir, excludeDirs):
		if (os.path.isdir(os.path.dirname(file)) and os.path.isfile(file)):
			clearLine()
			print("Processing:", os.path.dirname(os.path.dirname(file)), next(spinner), end="\r")
			
			song = getSong(file)
			
			if song['metadata'] is None:
				clearLine()
				print("Untagged: {0}".format(file))
	clearLine()
	print("Processing Complete!")

def findNew(originDir, workingDir, targetDir, targetFormat, excludeDirs=[], verbose=0):
	global config
	
	if excludeDirs is None:
		excludeDirs=[]
	
	print("Find New Media")
	for file in getLibrary(originDir, excludeDirs):
		if (os.path.isdir(os.path.dirname(file)) and os.path.isfile(file)):
			clearLine()
			print("Processing:", os.path.dirname(os.path.dirname(file)), next(spinner), end="\r")
			
			song = getSong(file)
			
			getSongPaths(song)
			
			if song['metadata'] is None:
				if verbose > 2:
					clearLine()
					print("Skipping: {0} due to lack of metadata".format(file))
			else:
				filename = os.path.basename(file)
				file_ext = os.path.splitext(filename)[1]
				
				if not (os.path.isfile(os.path.join(workingDir, song['outPath'], song['outFile'] + '.' + config['target']['format'])) or
					os.path.isfile(os.path.join(targetDir, song['outPath'], song['outFile'] + '.' + config['target']['format']))):
					print("New:", file)
					if verbose > 0:
						if not os.path.isfile(os.path.join(targetDir, song['outPath'], song['outFile'] + '.' + config['target']['format'])):
							print(" No:", os.path.join(targetDir, song['outPath'], song['outFile'] + '.' + config['target']['format']))
						elif not os.path.isfile(os.path.join(workingDir, song['outPath'], song['outFile'] + '.' + config['target']['format'])):
							print(" No:", os.path.join(workingDir, song['outPath'], song['outFile'] + '.' + config['target']['format']))
				#if not os.path.isfile(os.path.join(originDir, song['outPath'], song['outFile'] + file_ext)):
				#	clearLine()
				#	print("New:", file)
	
	clearLine()
	print("Processing Complete!")

def syncWorking(workingDir, targetDir, excludeDirs=[], act=False, verbose=0):
	global config
	
	if excludeDirs is None:
		excludeDirs=[]
	
	print("Sync Target Media")
	
	for file in getLibrary(workingDir, excludeDirs):
		if (os.path.isdir(os.path.dirname(file)) and os.path.isfile(file)):
			clearLine()
			#print("Checking:", file)
			print("Processing:", os.path.dirname(os.path.dirname(file)), next(spinner), end="\r")
			
			song = getSong(file)
			
			if song['metadata'] is None:
				if verbose > 2:
					clearLine()
					print("Skipping: {0} due to lack of metadata".format(file))
			else:
				filename = os.path.basename(file)
				file_ext = os.path.splitext(filename)[1]
				
				if not os.path.isfile(os.path.join(targetDir, song['outPath'], song['outFile'] + file_ext)):
					print("Sync:", file)
					if verbose > 0:
						print("  To:", os.path.join(targetDir, song['outPath'], song['outFile'] + file_ext))
					
					if act:
						print("would've acted")
	
	clearLine()
	print("Processing Complete!")


if __name__ == '__main__':
	global opt
	global config
	global originPath, targetPath, targetFormat, workPath
	import configparser
	#opt, files = parse_args()
	opt = musicman.utils.parse_args()
	config = musicman.utils.load_config()
	
	print("opt:", opt)
	
	try:
		originDir = config['origin']['path'] if opt.originDir is None else opt.originDir
	except AttributeError:
		originDir = config['origin']['path']
	
	try:
		targetDir = config['target']['path'] if opt.targetDir is None else opt.targetDir
	except AttributeError:
		targetDir = config['target']['path']
	
	try:
		targetFormat = config['target']['format'] if opt.targetFormat is None else opt.targetFormat
	except AttributeError:
		targetFormat = config['target']['format']
	
	try:
		workingDir = config['working']['path'] if opt.workingDir is None else opt.workingDir
	except AttributeError:
		workingDir = config['working']['path']

	if opt.mode is None:
		print("ERROR: No command provided.")
		sys.exit(1)
	
	
	try:
		if opt.mode == 'clean':
			cleanLibrary(originDir, opt.excludeDirs, opt.act, opt.verbose)
		
		elif opt.mode == 'rename':
			renameLibrary(originDir, opt.excludeDirs, opt.act, opt.verbose)
		
		elif opt.mode == 'scan':
			if opt.scanMode is None:
				print("ERROR: Subcommand for scan not provided.")
				sys.exit(1)
			elif opt.scanMode == 'untagged':
				findUntagged(originDir, opt.excludeDirs, opt.verbose)
			elif opt.scanMode == 'new':
				findNew(originDir, workingDir, targetDir, targetFormat, opt.excludeDirs, opt.verbose)
		elif opt.mode == 'sync':
			syncWorking(workingDir, targetDir, opt.excludeDirs, opt.act, opt.verbose)
	except KeyboardInterrupt:
		clearLine()
		print(end='\r')
		print("Aborted by user")
	
	
	
	#for file in getLibrary(config['origin']['path']):
	#	#print("File:", file)
	#	if (os.path.isdir(os.path.dirname(file)) and os.path.isfile(file)):
	#		clearLine()
	#		print("Processing:", os.path.dirname(os.path.dirname(file)), next(spinner), end="\r")
	#		#time.sleep(0.01)
	#		
	#		#print("Path:", os.path.dirname(file))
	#		#print("File:", os.path.basename(file))
	#clearLine()
	#print("Processing Complete!")
	
	sys.exit(0)
	#config = configparser.ConfigParser()
	#config.read('library.ini')
	
	#print(config.sections())
	#print(config["lossless"]["Path"])
	
	#try:
	#	#print("Test1:", config.get('lossless', 'test'))
	#	config.get('lossless', 'path')
	#	config.get('lossless', 'format')
	#	config.get('converted', 'path')
	#	config.get('converted', 'format')
	#except configparser.NoOptionError as err:
	#	print("ERROR: Configuration of required settings are missing:", err)
	#	sys.exit(1)
		
	LosslessLibraryRoot = '/srv/public/Music-Lossless'
	#LosslessLibraryRoot = '/srv/public/Music-iTunes'
	iTunesLibraryRoot = '/srv/public/Music-iTunes'

	#artistWalker = os.walk(LosslessLibraryRoot)
	#dest_dir, artists, files = artistWalker.next()

	#print "dest_dir: %s" % dest_dir
	#print "artists: %s" % artists
	#print "files: %s" % files

	#for artist in artists:
	#	print "Artist: %s" % artist

	#	albumWalker = os.walk(os.path.join(dest_dir, artist))
	#	artist_dir, albums, artist_files = albumWalker.next()

	#	print "Albums: %s" % albums
	#	print "Album Dir: %s" % artist_dir

	#	for album in albums:
	#		songWalker = os.walk(os.path.join(artist_dir, album)
	#		album_dir, dummy, songs = songWalker.next()

	for libraryDir, artists, dummy in os.walk(config['origin']['path']):
		for artist in sorted(artists):
			for artistDir, albums, dummy in os.walk(os.path.join(libraryDir, artist)):
				for album in sorted(albums):
					for albumDir, dummy, songs in os.walk(os.path.join(artistDir, album)):
						#print("AlbumDir:", albumDir)
						#print("  Artist:", artist)
						#print("   Album:", album)
						for song in songs:
							if song.endswith('.flac'):
								#print "    Song: %s" % song
								metadata = MetaTag(os.path.join(albumDir, song))
								#if os.path.isfile(os.path.join()
								#print "MetaData: %s" % metadata.tags
								#os.path.join(iTunesLibraryRoot, [metadata.tags["artist"], metadata.tags["album"]])
								#print("\033[KArtist:", metadata.tags["artist"], end="\r")
								
								clearLine()
								print("Scanning", artistDir, next(spinner), end="\r")
								
								#if int(metadata.tags["totaldiscs"]) > 1:
								if metadata.tags.get("artist") is None:
									continue
								if metadata.tags.get("albumartist") is None:
									continue
								if metadata.tags.get('album') is None:
									continue
								if metadata.tags.get("musicbrainz_albumid") is None or len(metadata.tags.get("musicbrainz_albumid")) < 5:
									clearLine()
									print("Skipping:", os.path.join(albumDir, song))
									continue
								
								#if 'Centennial' in song:
								#	print
								#	print
								#	print("DEBUG")
								#	print("Path:", artistDir)
								#	print("Song:", song)
								#	print("musicbrainz_albumid:", metadata.tags.get("musicbrainz_albumid"))
								#	print(type(metadata.tags.get("musicbrainz_albumid")))
								#	sys.exit(0)
								
								artistName = sanitize(metadata.tags["albumartist"]) 
								albumName = sanitize(metadata.tags["album"])
								titleName = sanitize(metadata.tags["title"])
								outPath = ''
								outFile = ''
								
								if int(metadata.tags.get("totaldiscs", 0)) > 1:
									outPath = os.path.join(config['converted']['path'],
														artistName,
														albumName)
									outFile = '{0:d}-{1:02d}-{2}.{3}'.format(int(metadata.tags["discnumber"]),
																			int(metadata.tags["tracknumber"]),
																			titleName,
																			'm4a')
									#print("iTunes:", os.path.join(iTunesLibraryRoot,
									#								metadata.tags["artist"],
									#								metadata.tags["album"],
									#								'{0:d}-{1:02d}-{2}.{3}'.format(int(metadata.tags["discnumber"]),
									#															int(metadata.tags["tracknumber"]),
									#															metadata.tags["title"],
									#															'm4a')))
									#								#int(metadata.tags["discnumber"]) + '-' + '{0:02d}'.format(int(metadata.tags["tracknumber"])) + '-' + metadata.tags["title"] + ".m4a")
								else:
									if metadata.tags.get("tracknumber") is not None:
										outPath = os.path.join(config['converted']['path'],
															artistName,
															albumName)
										outFile = '{0:02d}-{1}.{2}'.format(int(metadata.tags["tracknumber"]), titleName, 'm4a') 
										#print("iTunes:", os.path.join(iTunesLibraryRoot,
										#								metadata.tags["artist"],
										#								metadata.tags["album"],
										#								'{0:02d}'.format(int(metadata.tags["tracknumber"])) + '-' + metadata.tags["title"] + ".m4a"))
									else:
										outPath = os.path.join(config['converted']['path'],
															artistName,
															albumName)
										outFile = '{0}.{1}'.format(titleName, 'm4a')
										#print("iTunes:", os.path.join(iTunesLibraryRoot,
										#								metadata.tags["artist"],
										#								metadata.tags["album"],
										#								metadata.tags["title"] + ".m4a"))
								#print "iTunes: %s" % os.path.join(iTunesLibraryRoot, metadata.tags["artist"], metadata.tags["album"])
								if not os.path.isfile(os.path.join(outPath, outFile)):
									print("NEW:", os.path.join(outPath, outFile))
							if song.endswith('.m4a'):
								#print "    Song: %s" % song
								metadata = MetaTag(os.path.join(albumDir, song))
								#print "MetaData: %s" % metadata.tags
	clearLine()
	print()
		

#LosslessLibraryRoot = '/srv/public/Music-Lossless'
#
#for subdir, dirs, files in os.walk(LosslessLibraryRoot):
#	print subdir
#
#	for file in files:
#		if file.endswith('.flac'):
#			audio = mutagen.File(os.path.join(subdir, file))
#			print file
#			#print audio.tags.pprint()
#			print "Artist: %s" % audio['ARTIST'][0]
#			print "Album:  %s" % audio['ALBUM'][0]
#			print "Title:  %s" % audio['TITLE'][0]
#
#	#for file in files:
#	#	print os.path.join(subdir, file)

