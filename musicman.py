#!/usr/bin/env python3

from __future__ import division, absolute_import, print_function, unicode_literals

import os
import signal
import sys
#import mutagen
import time
#from path import path

import musicman
import mutagen

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
	newtext = newtext.replace('<', '').replace('>', '').replace(':', '').replace('"', '').replace('|', '').replace('?', '').replace('*', '').replace('$', '')
	newtext = newtext.replace('/', '-')
	newtext = newtext.strip()
	#if newtext != text:
	#	clearLine()
	#	print("text:", text)
	#	print(" new:", newtext)
	return newtext

def escape(text):
	newtext = text
	newtext = newtext.replace('$', '\$')
	return newtext

def getLibrary(path, libFormat=None, excludeDirs=[], includeDirs=[]):
	#print("DEBUG: libFormat={0}".format(libFormat)) 
	global originFormat;
	if os.path.isdir(path):
		for root, directories, filenames in sorted(os.walk(path)):
			if root not in excludeDirs:
				#if any(root in s for s in includeDirs):
				#if [s for s in [root] if any (xs in s for xs in includeDirs)] or len(includeDirs) == 0:
				#	print("DEBUG: Matched: {0}".format(root))
				#print("DEBUG: Found: {0}".format(root))
				#if any(root in s for s in includeDirs) or len(includeDirs) == 0:
				if [s for s in [root] if any (xs in s for xs in includeDirs)] or len(includeDirs) == 0:
					for filename in filenames:
						#print("DEBUG: filename: {0}".format(filename))
						if filename.endswith(libFormat):
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

def ensure_dir(file_path):
	directory = os.path.dirname(file_path)
	if not os.path.exists(directory):
		os.makedirs(directory)

def copy_file(src, dest):
	from shutil import copyfile
	ensure_dir(dest)
	copyfile(src, dest)

def getEmptyDirs(path, excludeDirs=[]):
	if os.path.isdir(path):
		for root, directories, filenames in sorted(os.walk(path)):
			if root not in excludeDirs:
				if not directories and not filenames:
					yield root

def getSong(file, orgDir=None, tmpDir=None, dstDir=None):
	from musicman.utils.metadata import MetaTag
	from musicman.utils.constants import INTERNAL_FORMATS
	global config
	global originDir
	global workingDir
	global targetDir
	global targetFormat
	
	song = {}
	orgDir = originDir if orgDir is None else orgDir
	tmpDir = workingDir if tmpDir is None else tmpDir
	dstDir = targetDir if dstDir is None else dstDir
	
	
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
				song['outFile'] = '{0:d}-{1:02d}-{2}'.format(song['discnumber'], song['tracknumber'], song['titleName'])
			else:
				if metadata.tags.get("tracknumber") is not None:
					song['outPath'] = os.path.join(song['artistName'], song['albumName'])
					song['outFile'] = '{0:d}-{1:02d}-{2}'.format(song['discnumber'], song['tracknumber'], song['titleName']) 
				else:
					song['outPath'] = os.path.join(song['artistName'], song['albumName'])
					outFile = '{0}'.format(song['titleName'])
			
			song['originFile'] = os.path.join(orgDir, song['outPath'], song['outFile'])
			song['workingFile'] = os.path.join(tmpDir, song['outPath'], song['outFile'])
			song['targetFile'] = os.path.join(dstDir, song['outPath'], song['outFile'])
			song['originExt'] = os.path.splitext(file)[1]
			song['targetExt'] = '.' + targetFormat
			song['targetDir'] = targetDir
			
			return song
	else:
		clearLine()
		print("FATAL: File extension \"{0}\" is not supported.".format(os.path.splitext(file)[1]))
		print("       Supported:", ", ".join(INTERNAL_FORMATS))
		sys.exit(2)

def cleanLibrary(rootDir, excludeDirs=[], act=False, verbose=0):
	global config
	
	if excludeDirs is None:
		excludeDirs=[]
	
	print("Clean Dirs:", rootDir)

	#while getEmptyDirs(rootDir, excludeDirs) != [] and act == True and tries > 0:
	
	if act:
		try:
			while getEmptyDirs(rootDir, excludeDirs).__next__():
				for path in getEmptyDirs(rootDir, excludeDirs):
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
		for path in getEmptyDirs(rootDir, excludeDirs):
			print("Empty:", path)
	
	#print("Processing Complete!")
	
def renameLibrary(rootDir, libFormat, excludeDirs=[], includeDirs=[], act=False, verbose=0):
	global config
	
	if excludeDirs is None:
		excludeDirs=[]
	if includeDirs is None:
		includeDirs=[]
	
	print("Renaming:", rootDir)
	for file in getLibrary(rootDir, libFormat, excludeDirs, includeDirs):
		if (os.path.isdir(os.path.dirname(file)) and os.path.isfile(file)):
			clearLine()
			print("Processing:", os.path.dirname(os.path.dirname(file)), next(spinner), end="\r")
			
			song = getSong(file, rootDir)
			
			if song['metadata'] is None:
				if verbose > 2:
					clearLine()
					print("Skipping: {0} due to lack of metadata".format(file))
			else:
				if not os.path.isfile(song['originFile'] + song['originExt']):
					clearLine()
					print("Found:", file)
					if verbose > 0:
						print("  New:", song['originFile'] + song['originExt'])
					
					if (act):
						if verbose > 1:
							print("Renaming: \"{0}\" -> \"{1}\"".format(file, song['originFile'] + song['originExt']))
						try:
							os.renames(file, song['originFile'] + song['originExt'])
						except OSError as err:
							print("ERROR: Failed to move:", err)
							sys.exit(5)
	
	clearLine()
	#print("Processing Complete!")

def findUntagged(rootDir, libFormat, excludeDirs=[], includeDirs=[], verbose=0):
	global config
	
	if excludeDirs is None:
		excludeDirs=[]
	if includeDirs is None:
		includeDirs=[]
	
	print("Find Untagged:", rootDir)
	for file in getLibrary(rootDir, libFormat, excludeDirs, includeDirs):
		if (os.path.isdir(os.path.dirname(file)) and os.path.isfile(file)):
			clearLine()
			print("Processing:", os.path.dirname(os.path.dirname(file)), next(spinner), end="\r")
			
			song = getSong(file)
			
			if song['metadata'] is None:
				clearLine()
				print("Untagged: {0}".format(file))
	
	clearLine()
	#print("Processing Complete!")

def findNew(rootDir, libFormat, tmpDir, dstDir, dstFormat, excludeDirs=[], includeDirs=[], verbose=0):
	global config
	
	if excludeDirs is None:
		excludeDirs=[]
	if includeDirs is None:
		includeDirs=[]
	
	print("Find New Media")
	for file in getLibrary(rootDir, libFormat, excludeDirs, includeDirs):
		if (os.path.isdir(os.path.dirname(file)) and os.path.isfile(file)):
			clearLine()
			print("Processing:", os.path.dirname(os.path.dirname(file)), next(spinner), end="\r")
			
			song = getSong(file)
			
			if song['metadata'] is None:
				if verbose > 2:
					clearLine()
					print("Skipping: {0} due to lack of metadata".format(file))
			else:
				if not (os.path.isfile(song['workingFile'] + song['targetExt']) or
						os.path.isfile(song['targetFile'] + song['targetExt'])):
					clearLine()
					print("New:", file)
					if verbose > 0:
						if not os.path.isfile(os.path.isfile(song['workingFile'] + song['targetExt'])):
							print(" No:", song['workingFile'] + song['targetExt'])
						elif not os.path.isfile(os.path.isfile(song['targetFile'] + song['targetExt'])):
							print(" No:", song['targetFile'] + song['targetExt'])
	
	#clearLine()
	#print("Processing Complete!")

def syncWorking(tmpDir, libFormat, excludeDirs=[], includeDirs=[], act=False, verbose=0):
	global config
	
	if excludeDirs is None:
		excludeDirs=[]
	if includeDirs is None:
		includeDirs=[]
	
	print("Sync Target Media")
	
	for file in getLibrary(tmpDir, libFormat, excludeDirs, includeDirs):
		if (os.path.isdir(os.path.dirname(file)) and os.path.isfile(file)):
			clearLine()
			print("Processing:", os.path.dirname(os.path.dirname(file)), next(spinner), end="\r")
			
			song = getSong(file)
			
			if song['metadata'] is None:
				if verbose > 2:
					clearLine()
					print("Skipping: {0} due to lack of metadata".format(file))
			else:
				filename = os.path.basename(file)
				file_ext = os.path.splitext(filename)[1]
				
				if not os.path.isfile(song['targetFile'] + song['originExt']):
					print("Sync:", file)
					if verbose > 0:
						print("  To:", song['targetFile'] + song['originExt'])
					
					if act:
						copy_file(file, song['targetFile'] + song['originExt'])
						#print("would've acted")
					
					
				#if not os.path.isfile(os.path.join(destDir, song['outPath'], song['outFile'] + file_ext)):
				#	print("Sync:", file)
				#	if verbose > 0:
				#		print("  To:", os.path.join(destDir, song['outPath'], song['outFile'] + file_ext))
				#	
				#	if act:
				#		print("would've acted")
	
	#clearLine()
	#print("Processing Complete!")

def convertMedia(rootDir, originFormat, tmpDir, dstDir, dstFormat, excludeDirs=[], includeDirs=[], act=False, verbose=0):
	import subprocess
	from musicman.utils.copytags import (
		copy_tags
	)
	
	if excludeDirs is None:
		excludeDirs=[]
	if includeDirs is None:
		includeDirs=[]
	
	print("Convert Library Media")

	for file in getLibrary(rootDir, originFormat, excludeDirs, includeDirs):
		if (os.path.isdir(os.path.dirname(file)) and os.path.isfile(file)):
			clearLine()
			print("Processing:", os.path.dirname(os.path.dirname(file)), next(spinner), end="\r")
			
			song = getSong(file, rootDir, tmpDir, targetDir)
			
			if song['metadata'] is None:
				if verbose > 2:
					clearLine()
					print("Skipping: {0} due to lack of metadata".format(file))
			else:
				if not (os.path.isfile(song['workingFile'] + song['targetExt']) or
						os.path.isfile(song['targetFile'] + song['targetExt'])):
					clearLine()
					print("New:", file)
					if verbose > 2:
						if not os.path.isfile(os.path.isfile(song['workingFile'] + song['targetExt'])):
							print(" No:", song['workingFile'] + song['targetExt'])
						elif not os.path.isfile(os.path.isfile(song['targetFile'] + song['targetExt'])):
							print(" No:", song['targetFile'] + song['targetExt'])
					
					if act:
						#print("would've acted")
						if not os.path.isdir(os.path.dirname(song['workingFile'])):
							os.makedirs(os.path.dirname(song['workingFile']))
						#subprocess.call("ffmpeg", "-loglevel", "quiet", "-stats", "-i", file, "-vn", "-c:a", "libfdk_aac", "-vbr", "5", "-nostdin", "-y", song['workingFile'] + song['targetExt'])
						try:
							#subprocess.call('/usr/bin/ffmpeg -loglevel quiet -stats -i "{0}" -vn -c:a libfdk_aac -vbr 5 -nostdin -y "{1}"'.format(file, song['workingFile'] + song['targetExt']), shell=True)
							#subprocess.call('/usr/bin/ffmpeg -i "{0}" -f caf - | /usr/bin/fdkaac -I -p 29 -m 5 -o "{1}" -'.format(file, song['workingFile'] + song['targetExt']), shell=True)
							subprocess.call('/usr/bin/ffmpeg -i "{0}" -f caf - | /usr/bin/fdkaac -I -p 2 -m 5 -o "{1}" -'.format(escape(file), escape(song['workingFile'] + song['targetExt'])), shell=True)
							#new = MetaData(song['workingFile'] + song['targetExt'])
							#new.update(song['metadata'])
							#new.save()
							
							#old = mutagen.File(file)
							#new = mutagen.File(song['workingFile'] + song['targetExt'])
							#new.update(old)
							#new.save()
							copy_tags(file, song['workingFile'] + song['targetExt'])
						except KeyboardInterrupt:
							if os.path.isfile(song['workingFile'] + song['targetExt']):
								os.remove(song['workingFile'] + song['targetExt'])
							clearLine()
							print(end='\r')
							print("Aborted by user")
							sys.exit(0)
							
	clearLine()

if __name__ == '__main__':
	global opt
	global config
	global originPath, originFormat, targetPath, targetFormat, workPath
	import configparser
	
	opt = musicman.utils.parse_args()
	config = musicman.utils.load_config()
	
	#print("opt:", opt)
	
	try:
		originDir = config['origin']['path'] if opt.originDir is None else opt.originDir
	except AttributeError:
		originDir = config['origin']['path']
	
	try:
		originFormat = config['origin']['format'] if opt.origFormat is None else opt.origFormat
	except AttributeError:
		originFormat = config['origin']['format']
	
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
			cleanLibrary(originDir, originFormat, opt.excludeDirs, opt.includeDirs, opt.act, opt.verbose)
			cleanLibrary(targetDir, targetFormat, opt.excludeDirs, opt.includeDirs, opt.act, opt.verbose)
			cleanLibrary(workingDir, targetFormat, opt.excludeDirs, opt.includeDirs, opt.act, opt.verbose)
		
		elif opt.mode == 'rename':
			renameLibrary(originDir, originFormat, opt.excludeDirs, opt.includeDirs, opt.act, opt.verbose)
			renameLibrary(targetDir, targetFormat, opt.excludeDirs, opt.includeDirs, opt.act, opt.verbose)
			renameLibrary(workingDir, targetFormat, opt.excludeDirs, opt.includeDirs, opt.act, opt.verbose)
		
		elif opt.mode == 'scan':
			if opt.scanMode is None:
				print("ERROR: Subcommand for scan not provided.")
				sys.exit(1)
			elif opt.scanMode == 'untagged':
				findUntagged(originDir, originFormat, opt.excludeDirs, opt.includeDirs, opt.verbose)
				findUntagged(targetDir, targetFormat, opt.excludeDirs, opt.includeDirs, opt.verbose)
				findUntagged(workingDir, targetFormat, opt.excludeDirs, opt.includeDirs, opt.verbose)
			elif opt.scanMode == 'new':
				findNew(originDir, originFormat, workingDir, targetDir, targetFormat, opt.excludeDirs, opt.includeDirs, opt.verbose)
		elif opt.mode == 'sync':
			syncWorking(workingDir, targetFormat, opt.excludeDirs, opt.includeDirs, opt.act, opt.verbose)
		
		elif opt.mode == 'convert':
			convertMedia(originDir, originFormat, workingDir, targetDir, targetFormat, opt.excludeDirs, opt.includeDirs, opt.act, opt.verbose)
	except KeyboardInterrupt:
		clearLine()
		print(end='\r')
		print("Aborted by user")
		sys.exit(0)
	
	clearLine()
	print("Processing Complete!")
