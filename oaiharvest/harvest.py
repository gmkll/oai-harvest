# encoding: utf-8
"""Harvest records from an OAI-PMH provider.

positional arguments:
  provider              OAI-PMH Provider from which to harvest.

optional arguments:
  -h, --help            show this help message and exit
  -p METADATAPREFIX, --metadataPrefix METADATAPREFIX
                        where to output files for harvested records. default
                        is current working path
  -f YYYY-MM-DD, --from YYYY-MM-DD
                        harvest only records added/modified after this date.
  -u YYYY-MM-DD, --until YYYY-MM-DD
                        harvest only records added/modified up to this date.
  -d DIR, --dir DIR     where to output files for harvested records.default:
                        current working path

Copyright © 2013, the University of Liverpool <http://www.liv.ac.uk>.
All rights reserved.

Distributed under the terms of the BSD 3-clause License
<http://opensource.org/licenses/BSD-3-Clause>.
"""

import sys
import os

from argparse import ArgumentParser

from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

from metadata import DefaultingMetadataRegistry, XMLMetadataReader

class OAIHarvester(object):

    def __init__(self, mdRegistry):
        self._mdRegistry = mdRegistry
    
    def _listRecords(self, baseUrl, metadataPrefix="oai_dc", **kwargs):
        # Add metatdataPrefix to args
        kwargs['metadataPrefix'] = metadataPrefix
        client = Client(baseUrl, metadata_registry)
        for record in client.listRecords(**kwargs):
            yield record

    def harvest(self, baseUrl, metadataPrefix, **kwargs):
        "Harvest records"
        raise NotImplementedError("{0.__class__.__name__} must be sub-classed")


class DirectoryOAIHarvester(OAIHarvester):
    
    def __init__(self, mdRegistry, directory):
        OAIHarvester.__init__(self, mdRegistry)
        self._dir = directory

    def harvest(self, baseUrl, metadataPrefix, **kwargs):
        
        for header, metadata, about in self._listRecords(
                 baseUrl,
                 metadataPrefix=metadataPrefix,
                 **kwargs):
            fp =  os.path.join(self._dir,
                               "{0}.xml".format(header.identifier())
                               )
            with open(fp, 'w') as fh:
                fh.write(metadata)


def main(argv=None):
    '''Command line options.'''
    global argparser, metadata_registry
    if argv is None:
        args = argparser.parse_args()
    else:
        args = argparser.parse_args(argv)
    if args.dir:
        harvester = DirectoryOAIHarvester(metadata_registry,
                                          os.path.abspath(args.dir))
    for provider in args.provider:
        mdp = args.metadataPrefix
        if not provider.startswith('http://'):
            # Fetch configuration from persistent storage
            # Allow over-ride of default metadataPrefix
            raise NotImplementedError
        else:
            baseUrl = provider
            from_ = args.from_

        if mdp is None:
            mdp = 'oai_dc'
        harvester.harvest(baseUrl,
                          mdp,
                          from_=from_,
                          until=args.until
                          )


# Set up argument parser
docbits = __doc__.split('\n\n')

argparser = ArgumentParser("harvest(.py)",
                           description=docbits[0],
                           epilog='\n\n'.join(docbits[-2:]))
argparser.add_argument('provider',
                       action='store',
                       nargs='+',
                       help="OAI-PMH Provider from which to harvest."
                       )
argparser.add_argument('-p', '--metadataPrefix',
                       action='store', dest='metadataPrefix',
                       default=None,
                       help=("where to output files for harvested records. "
                             "default is current working path")
                       )
argparser.add_argument("-f", "--from", dest="from_",
                       default=None,
                       metavar="YYYY-MM-DD",
                       help=("harvest only records added/modified after this "
                             "date.")
                       )
argparser.add_argument("-u", "--until", dest="until",
                       default=None,
                       metavar="YYYY-MM-DD",
                       help=("harvest only records added/modified up to this "
                             "date.")
                       )

group = argparser.add_mutually_exclusive_group()
group.add_argument('-d', '--dir',
                   action='store', dest='dir',
                   default='.',
                   help=("where to output files for harvested records."
                         "default: current working path")
                   )

# Set up metadata registry
xmlReader = XMLMetadataReader()
metadata_registry = DefaultingMetadataRegistry(defaultReader=xmlReader)


if __name__ == "__main__":
    sys.exit(main())