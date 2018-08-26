MusicMan
========

A music library and converter manager.
--------------------------------------

MusicMan is a media library management and orchistration tool to assist in
keeping a music library neat, tidy, and clean. It utilizes the music metadata
to organize files into their respective reasonable organizational structure:

Artist/Album/[disc#-][track#-]Song Title.ext

The tool was primarily designed to work from a lossless media format, such as
FLAC, and transcode into compressed formats, such as M4A for use on portable
devices such as an iPhone or Android device.

Metadata evaluation is dependant on the existance of MusicBrainz' fields to
help insure accuracy is maintained. Right now it's recommended to use 
MusicBrainz Picard, or similar, to tag your media and then use the tool to
organize it. Organization is kept on both media library formats so it remains
neat and clean.

This is work in progress, and currently only transcodes to M4A, but the idea
is to be able to support other formats to convert to.

Conversion to M4A requires FFmpeg with the fdk-aac codec support compiled in.

If you're interested in helping develop on this project, please feel free to,
all I ask is that you work off a feature or bug branch off the develop branch
and request your pull requests towards develop.

### Dependancies

- Python 3.3 and up.
- mutagen
- ffmpeg
- fdkaac

