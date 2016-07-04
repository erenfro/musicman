import os
import base64

try:
	import mutagen
	import mutagen.id3
	import mutagen.mp3
	import mutagen.mp4
	import mutagen.asf
	import mutagen.flac
	import mutagen.apev2
	import mutagen.musepack
	import mutagen.oggvorbis
	NO_TAGS = False
except ImportError:
	NO_TAGS = True

from musicman.utils.tagmap import tags as tagmap

class MetaTag(object):
	"""
	handles tag extraction and insertion into and/or from audio files
	"""

	__tag_mapping = tagmap.copy()
	exts = __tag_mapping.keys()
	
	if not NO_TAGS:
		__id3_mapping = {
			'artist'		: mutagen.id3.TPE1,
			'album'			: mutagen.id3.TALB, 
			'title'			: mutagen.id3.TIT2, 
			'genre'			: mutagen.id3.TCON, 
			'year'		  	: mutagen.id3.TDRC, 
			'tracknumber'   : mutagen.id3.TRCK,
			'totaltracks'	: mutagen.id3.TRCK,
			'composer'		: mutagen.id3.TCOM,
			'lyrics'		: mutagen.id3.USLT,
			'disc'			: mutagen.id3.TPOS,
			'discnumber'	: mutagen.id3.TPOS,
		}
		__opener = {
			'.mp3'			: mutagen.mp3.Open,
			'.wma'			: mutagen.asf.Open,
			'.m4a'			: mutagen.mp4.Open,
			'.flac'			: mutagen.flac.Open,
			'.wv'			: mutagen.apev2.APEv2,
			'.mpc'			: mutagen.musepack.Open,
			'.ogg'			: mutagen.oggvorbis.Open,
		}
	else:
		__id3_mapping = {}
		__opener	  = {}

	def __init__(self, input_file):
		self.input_file = input_file
		self.tags = {key: None for key in self.__id3_mapping}
		self.extract()

	def extract(self):
		"""
		extracts metadata tags from the audio file
		"""
		ext = os.path.splitext(self.input_file)[1].lower()
		if ext in self.exts:
			tags = mutagen.File(self.input_file)
			#for tag, key in self.__tag_mapping[ext].iteritems():
			for tag, key in self.__tag_mapping[ext].items():
				if tag == 'albumart':
					try:
						self._extract_album_art(ext, tags)
					except:
						continue
				elif key in tags:
					#print "tag: %s, key: %s" % (tag, key)
					self.tags[tag] = tags[key][0]
				elif tag == 'lyrics' and key == 'USLT':
					self.tags.update({tag: tags[id3tag].text for id3tag in tags if id3tag.startswith(key)})

	def _extract_album_art(self, ext, tags):
		tag = self.__tag_mapping[ext].get('albumart')
		if tag is None:
			return
		if tag in tags:
			self.coverart['ext'] = ext
			if ext == '.mp3':
				apic = tags[tag]
				self.coverart['mime'] = apic.mime
				self.coverart['data'] = apic.data
			elif ext == '.m4a':
				self.coverart['data'] = tags[tag][0]
			elif ext in ('.ogg', '.flac'):
				encoded_image = tags[tag][0]
				image = mutagen.flac.Picture(base64.b64decode(encoded_image))
				self.coverart['data'] = image.data
				self.coverart['mime'] = image.mime
		elif ext == '.mp3':
			for key in tags:
				if key.startswith(tag):
					apic = tags[key]
					self.coverart['mime'] = apic.mime
					self.coverart['data'] = apic.data

