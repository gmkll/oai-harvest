# -*- coding: utf-8 -*-
"""Document directory_store here."""
import codecs
import logging
import os
import platform

from six import string_types
from six.moves.urllib import parse as urllib

from oaiharvest.record import Record

from bs4 import BeautifulSoup
#from html.parser import HTMLParser

class DirectoryRecordStore(object):
    def __init__(self, directory, createSubDirs=False, resolveEntities=True):
        self.directory = directory
        self.createSubDirs = createSubDirs
        self.resolveEntities = resolveEntities
        self.logger = logging.getLogger(__name__).getChild(self.__class__.__name__)

    def write(self, record: Record, metadataPrefix: str):
        fp = self._get_output_filepath(record.header, metadataPrefix)
        self._ensure_dir_exists(fp)
        self.logger.debug("Writing to file {0}".format(fp))
        if (record.metadata is None):
            self.logger.info("*** No metadata for {0}.{1}".format(record.header.identifier(), metadataPrefix) )
            return
        if self.resolveEntities:
            result = BeautifulSoup(str(record.metadata),"html.parser")
            result = str(result)
        else:
            result = record.metadata
            
        with open( fp, 'w', encoding="utf8", newline='\n') as fh: 
            fh.write( result )

    def delete(self, record: Record, metadataPrefix: str):
        fp = self._get_output_filepath(record.header, metadataPrefix)
        try:
            os.remove(fp)
        except OSError:
            # File probably does't exist in destination directory
            # No further action needed
            self.logger.debug("")
            pass

    def _get_output_filepath(self, header, metadataPrefix):
        filename = "{0}.{1}.xml".format(header.identifier(), metadataPrefix)

        protected = []
        if platform.system() != "Windows":
            protected.append(":")

        if self.createSubDirs:
            if isinstance(self.createSubDirs, string_types):
                # Replace specified character with platform path separator
                filename = filename.replace(self.createSubDirs, os.path.sep)

            # Do not escape path separators, so that sub-directories
            # can be created
            protected.append(os.path.sep)

        filename = urllib.quote(filename, "".join(protected))
        fp = os.path.join(self.directory, filename)
        return fp

    def _ensure_dir_exists(self, fp):
        if not os.path.isdir(os.path.dirname(fp)):
            # Missing base directory or sub-directory
            self.logger.debug("Creating target directory {0}".format(self.directory))
            os.makedirs(os.path.dirname(fp))
