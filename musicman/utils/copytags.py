import os
import os.path
import sys
import re
#import logging

from mutagen import File as MusicFile
from mutagen.aac import AACError

try:
    from collections import MutableMapping
except ImportError:
    from UserDict import DictMixin as MutableMapping
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs):
        return iterable

# Set up logging
#logFormatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
#logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)
#logger.handlers = []
#logger.addHandler(logging.StreamHandler())
#for handler in logger.handlers:
#    handler.setFormatter(logFormatter)

class AudioFile(MutableMapping):
    """A simple class just for tag editing.

    No internal mutagen tags are exposed, or filenames or anything. So
    calling clear() won't destroy the filename field or things like
    that. Use it like a dict, then .write() it to commit the changes.
    When saving, tags that cannot be saved by the file format will be
    skipped with a debug message, since this is a common occurrance
    with MP3/M4A.

    Optional argument blacklist is a list of regexps matching
    non-transferrable tags. They will effectively be hidden, nether
    settable nor gettable.

    Or grab the actual underlying mutagen format object from the
    .data field and get your hands dirty.

    """
    def __init__(self, filename, blacklist=[], easy=True):
        self.filename = filename
        self.data = MusicFile(self.filename, easy=easy)
        if self.data is None:
            raise ValueError("Unable to identify %s as a music file" % (repr(filename)))
        # Also exclude mutagen's internal tags
        self.blacklist = [ re.compile("^~") ] + blacklist
    def __getitem__(self, item):
        if self.blacklisted(item):
            #logger.debug("Attempted to get blacklisted key: %s." % repr(item))
            return
        else:
            return self.data.__getitem__(item)
    def __setitem__(self, item, value):
        if self.blacklisted(item):
            #logger.debug("Attempted to set blacklisted key: %s." % repr(item))
            #print("DEBUG: Attempted to set blacklisted key: %s." % repr(item))
            return
        else:
            try:
                return self.data.__setitem__(item, value)
            except KeyError:
                #print("Skipping unsupported tag {0} for file type {0}".format(item, type(self.data)))
                pass
                #logger.debug("Skipping unsupported tag %s for file type %s",
                #             item, type(self.data))
    def __delitem__(self, item):
        if self.blacklisted(item):
            #logger.debug("Attempted to del blacklisted key: %s." % repr(item))
            return
        else:
            return self.data.__delitem__(item)
    def __len__(self):
        return len(self.keys())
    def __iter__(self):
        return iter(self.keys())

    def blacklisted(self, item):
        """Return True if tag is blacklisted.

        Blacklist automatically includes internal mutagen tags (those
        beginning with a tilde)."""
        for regex in self.blacklist:
            if re.search(regex, item):
                return True
        else:
            return False
    def keys(self):
        return [ key for key in self.data.keys() if not self.blacklisted(key) ]
    def write(self):
        return self.data.save()

def copy_tags (src, dest):
    """Replace tags of dest file with those of src.

    Excludes format-specific tags and replaygain info, which does not
    carry across formats."""

    # A list of regexps matching non-transferrable tags, like file format
    # info and replaygain info. This will not be transferred from source,
    # nor deleted from destination.
    blacklist_regexes = [ re.compile(s) for s in (
        'encoded',
        'replaygain',
    ) ]
    
    try:
        m_src = AudioFile(src, blacklist = blacklist_regexes, easy=True)
        m_dest = AudioFile(dest, blacklist = m_src.blacklist, easy=True)
        m_dest.clear()
        #logging.debug("Adding tags from source file:\n%s",
        #              "\n".join("%s: %s" % (k, repr(m_src[k])) for k in sorted(m_src.keys())))
        m_dest.update(m_src)
        #logger.debug("Added tags to dest file:\n%s",
        #             "\n".join("%s: %s" % (k, repr(m_dest[k])) for k in sorted(m_dest.keys())))
        m_dest.write()
    except AACError:
        #logger.warn("No tags copied because output format does not support tags: %s", repr(type(m_dest.data)))
        print("WARN: no tags copied because output format does not support tags: {0}".format(repr(type(m_dest.data))))
