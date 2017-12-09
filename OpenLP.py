#!/usr/bin/python
# -*- coding: utf-8 -*-

#############################################################################
#                                                                           #
#                      OpenLP to ProPresentor Converter                     #
#                    (C) 2012 Daniel Fairhead, OMNIvision                   #
#                                                                           #
#---------------------------------------------------------------------------#
#                                                                           #
# This program is free to use, change, edit, do what you want with.         #
# Please consider a donation to OMNIvision if you find it useful. :-)       #
#                                                                           #
# http://www.omnivision.om.org/                                             #
#                                                                           #
# OMNIvision is the media & events team of Operation Mobilisation (OM)      #
#                                                                           #
# http://www.om.org/                                                        #
#                                                                           #
#############################################################################

import sqlite3 as sql            # To import from OpenLP
import os                        # File loading stuff.
import sys                       # For UTF-8 settings.
reload(sys)                      # Stupid hack to re-apply UTF-8 if it
                                 #    wasn't loaded originally.
sys.setdefaultencoding('utf-8')  #    Oh for Py3k everywhere.

import xml.parsers.expat         # For Parsing OpenLP Lyrics Data

class OpenLPReader:

    def __init__(self):
        self.songs = []
        self.authors = dict()
        self.authors_songs = []

    ###########
    #
    # (OpenLP) Lyrics XML Parsing
    #
    ###########

    def ParseLyric(self,text):
        current_verses = []

        def _element(name, attrs):
            if name == 'verse':
                current_verses.append(attrs)
                current_verses[-1]['text'] = []

        def _chardata(data):
            current_verses[-1]['text'].append(data)

        parser = xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = _element
        parser.CharacterDataHandler = _chardata
        parser.buffer_text = True

        parser.Parse(text,True)

        current_verses.reverse() #Not really sure why we need this...

        return current_verses

    #######
    #
    # Database functions:
    #
    #######

    def get_song_authornames(self, song_id):
        return ' &amp; '.join(
            [self.authors[id] for id in
                [row['author_id'] for row in self.authors_songs
                    if row['song_id'] == song_id]])

    def load(self, fname):
        # Load the data from the OpenLP database:

        success = True

        try:
            con = None

            # Fetch all the data first. Gets it in memory to use, rather than
            # loads of SQLlite queries. This seems to be faster, with a little
            # profiling.  If re-writing it as loads of sqlite queries
            # works better for you, I'm cool with that too.

            print ("OpenLP to Pro-Presenter 5 converter.\n")
            print ("Loading Database:\n  "
                    + os.path.expanduser(fname) + "\n")

            con = sql.connect(os.path.expanduser(fname))
            con.row_factory = sql.Row

            cur = con.cursor()
            cur.execute('SELECT id, title, ccli_number, copyright, comments, lyrics FROM songs')
            self.songs = cur.fetchall()

            cur.execute('SELECT id, display_name FROM authors')
            for author in cur.fetchall():
                self.authors[author['id']] = author['display_name']

            cur.execute('SELECT song_id, author_id FROM authors_songs')
            self.authors_songs = cur.fetchall()

            print ('  Cool.  ' + str(len(self.songs)) + ' songs loaded.\n' );

        except:

            print ("Sorry - There was a problem loading the OpenLP Database.\n" +
                  "(" + fname + ")\n" +
                  "Maybe OpenLP isn't set up on this user?\n\n" +
                  "If you know where the database is, you can edit the path at \n" +
                  "the top of this script and set it manually.")
            success = False

        return success
