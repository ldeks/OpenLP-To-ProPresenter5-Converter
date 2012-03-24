#!/usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                            #
## OpenLP to ProPresentor Converter                                           #
## (C) 2012 Daniel Fairhead, OMNIvision                                       #
##                                                                            #
## This program is free to use, and public domain,                            #
## please consider a donation to OMNIvision if you find it useful. :-)        #
##                                                                            # 
###############################################################################

# Configuration Options:

OPENLP_DATABASE = "~/Library/Application Support/openlp/Data/songs/songs.sqlite"
OUTPUT_DIRECTORY = "/tmp/"

DEFAULT_FONT = "Helvetica"
DEFAULT_COLOR = (255,255,255) # RGB, white.
BACKGROUND_COLOR = '0 0 0 1' # RGBA black.

MAX_LINES = 4

OPEN_DIR_ON_EXIT = True # If you want to open the dir of new files...

# Options you probably don't need to edit, but can easily enough:

VERSE_COLORS = ['0 0 1 1',   # 0 = Blue 
                '0 1 0 1',   # 1 = Green
                '1 0.5 0 1', # 2 = Orange
                '1 0 1 1',   # 3 = Purple
                '0 1 1 1',   # 4 = Yellow
                '0.5 1 0 1', # ...
                '1 1 0.5 1', 
                '0 0 1 1',
                '0 1 0 1',
                '1 0.5 0 1',
                '1 0 1 1',
                '0 1 1 1',
                '0.5 1 0 1',
                '1 1 0.5 1']

VERBOSE_NAMES = {'c':'Chorus',
                 'v':'Verse',
                 'b':'Bridge',
                 'e':'Ending',
                 'p':'Pre-Chorus'}

# Cramming everything into this one file as opposed to separating it out 
# into modules may be rather messy and bad practice.  I do apologise.
# My intention is to have this as a stand alone python script, to make 
# it as easy as possible to distribute.

import sqlite3 as sql            # To import from OpenLP
import os                        # File loading stuff.
import sys                       # For UTF-8 settings.
reload(sys)                      # Stupid hack to re-apply UTF-8 if it
                                 #    wasn't loaded originally.
sys.setdefaultencoding('utf-8')  #    Oh for Py3k everywhere.

import re                        # For regexy stuff.
import xml.dom.minidom           # OpenLP lyric data stored as XML.
from xml.dom.minidom import Node 

from base64 import b64encode     # For ProPresenter RTF Data blobs
from uuid import uuid4           # For ProPresenter Slide UUIDs
from datetime import datetime    # Guess.

# Short generic(ish) useful functions:

def uni(x):
    """ Turns 'None' from empty sqlite columns into an empty string, 
        or else returns the original string. """
    return x if x != None else ''

def xml_tag_clean(text):
    return re.sub('[<>\n"]',' ',uni(text)).replace('&','&amp;')

def make_uuid():
    return uuid4().__str__().upper()

def Verbose_names(key):
    # Could use a collections.defaultdict, but I can't be bothered right now.
    if key in VERBOSE_NAMES:
        return VERBOSE_NAMES[key]
    else:
        return key

# Stupid BLASTED RTF.  This took me a *very* long time to figure out, 
# and I'm not sure it's in any way anything like bullet proof now anyway.
# At least it works for our database, currently.
# I *never* want to work with RTF again.

def AntiUnicode(text):

    def escape_u(t):
        """ turns a '\u####' type hexadecimal unicode escape char into 
            it's RTF '\uxxxx' decimal.
            For use in a re.sub function as the callback. """
        return r'\u'+unicode(int(t.group()[2:],16)) + ' '

    return re.sub(r"\\x..",   escape_u, 
               re.sub(r"\\u....", escape_u, 
                   text.encode('unicode-escape'))).replace(r'\n','\\\n')

def MakeRTFBlob(text):
    return b64encode('{\\rtf1\\ansi\\ansicpg1252\\cocoartf1038\\cocoasubrtf360\n{\\fonttbl\\f0\\fswiss\\fcharset0 '+DEFAULT_FONT+';}\n'
                    +'{\\colortbl;\\red'+str(DEFAULT_COLOR[0])+'\\green'+str(DEFAULT_COLOR[1])+'\\blue'+str(DEFAULT_COLOR[2])+';}\n'
                    +'\\pard\\tx560\\tx1120\\tx1680\\tx2240\\tx2800\\tx3360\\tx3920\\tx4480\\tx5040\\tx5600\\tx6160\\tx6720\\qc\\pardirnatural\n\n'
                    +'\\f0\\fs102\\fsmilli51200 \\cf1 \\expnd0\\expndtw0\\kerning0\n\\outl0\\strokewidth-20 \\strokec0 \\uc0 ' + AntiUnicode(text) + '}')

# XML sections. 

# This is messy, and there is no way to help it, 
# besides having a separate template file.

def VerseBlock(block_name, block_type, text_sections, color='0 0 0 0'):
    
    #def splitmap ( split_func, list_to_split ):
    #    current_list = []
    #    for item in list_to_split:
    #        current_list += 
    #    return

    def list_split_substrings_by_lines(max_lines, oldlist):
        # Very imperative, I know.  There's probably a better 
        # (functional/pythonic) way to do this...
        new_list = []
        for raw_item in oldlist:
            x = 1
            new_item = ''
            for line in raw_item.splitlines():
                if x < max_lines:
                    new_item += line + '\n'
                    x += 1
                else:
                    new_item += line
                    new_list.append(new_item)
                    new_item = ''
                    x = 1
            if new_item != '':
                new_list.append(new_item)

        new_list.reverse()# Not sure why reverse is needed...
        return new_list 

    
    def list_split_substrings(split_by, oldlist):
        newlist = []
        for item in oldlist:
            newlist += item.split(split_by)
        return newlist


    all_sections = map(unicode.strip,
                       list_split_substrings_by_lines(MAX_LINES,  
                           list_split_substrings('\n\n', 
                               list_split_substrings ('[---]', 
                                   text_sections))))

    return ('<RVSlideGrouping name="' + block_name + '" uuid="'+ make_uuid() +
            '" color="' + color + '" serialization-array-index="0"><slides containerClass="NSMutableArray">' + 
            ''.join(map(SlideBlock, all_sections)) + '</slides></RVSlideGrouping>')



def SlideBlock(text):
    return '<RVDisplaySlide backgroundColor="' + BACKGROUND_COLOR + '" enabled="1" highlightColor="0 0 0 0" hotKey="" label="" notes="" slideType="1" sort_index="0" UUID="' + make_uuid() + '" drawingBackgroundColor="0" chordChartPath="" serialization-array-index="0"><cues containerClass="NSMutableArray"></cues><displayElements containerClass="NSMutableArray"><RVTextElement displayDelay="0" displayName="Default" locked="0" persistent="0" typeID="0" fromTemplate="1" bezelRadius="0" drawingFill="0" drawingShadow="1" drawingStroke="0" fillColor="0 0 0 0" rotation="0" source="" adjustsHeightToFit="0" verticalAlignment="0" RTFData="' + MakeRTFBlob(text) + '" revealType="0" serialization-array-index="0"><_-RVRect3D-_position x="30" y="30" z="0" width="964" height="708"></_-RVRect3D-_position><_-D-_serializedShadow containerClass="NSMutableDictionary"><NSNumber serialization-native-value="4" serialization-dictionary-key="shadowBlurRadius"></NSNumber><NSColor serialization-native-value="0 0 0 1" serialization-dictionary-key="shadowColor"></NSColor><NSMutableString serialization-native-value="{2.82843, -2.82843}" serialization-dictionary-key="shadowOffset"></NSMutableString></_-D-_serializedShadow><stroke containerClass="NSMutableDictionary"><NSColor serialization-native-value="0 0 0 0" serialization-dictionary-key="RVShapeElementStrokeColorKey"></NSColor><NSNumber serialization-native-value="0" serialization-dictionary-key="RVShapeElementStrokeWidthKey"></NSNumber></stroke></RVTextElement></displayElements><_-RVProTransitionObject-_transitionObject transitionType="-1" transitionDuration="1" motionEnabled="0" motionDuration="20" motionSpeed="100"></_-RVProTransitionObject-_transitionObject></RVDisplaySlide>'

def HeaderBlock(Name='New Song', 
                Authors='', 
                Artist='', 
                CCLICopyRightInfo='', 
                CCLILicenceNumber='', 
                Publisher='',
                Notes=''):
    return '<RVPresentationDocument height="768" width="1024" versionNumber="500" docType="0" creatorCode="1349676880" lastDateUsed="' + datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '" usedCount="0" category="Song" resourcesDirectory="" backgroundColor="0 0 0 1" drawingBackgroundColor="0" notes="' + Notes + '" artist="' + Artist + '" author="'+ Authors +'" album="" CCLIDisplay="0" CCLIArtistCredits="" CCLISongTitle="' + Name + '" CCLIPublisher="' + Publisher + '" CCLICopyrightInfo="' + CCLICopyRightInfo + '" CCLILicenseNumber="' + CCLILicenceNumber + '" chordChartPath=""><timeline timeOffSet="0" selectedMediaTrackIndex="0" unitOfMeasure="60" duration="0" loop="0"><timeCues containerClass="NSMutableArray"></timeCues><mediaTracks containerClass="NSMutableArray"></mediaTracks></timeline><bibleReference containerClass="NSMutableDictionary"></bibleReference><_-RVProTransitionObject-_transitionObject transitionType="-1" transitionDuration="1" motionEnabled="0" motionDuration="20" motionSpeed="100"></_-RVProTransitionObject-_transitionObject><groups containerClass="NSMutableArray">'

def FooterBlock():
    return '</groups><arrangements containerClass="NSMutableArray"></arrangements></RVPresentationDocument>' 


# Database functions:

def filterbyfield(id,table,field='id'):
    return filter(lambda x: x[field]==id, table)


###################################################
#
# Actually do stuff:
#
###################################################


# First load the data from the OpenLP database:

try:
    con = None

    ## Fetch all the data first. Gets it in memory to use, rather than loads of SQLlite queries.

    print ("OpenLP to Pro-Presenter 5 converter.\n")
    print ("Loading Database:\n  " + os.path.expanduser(OPENLP_DATABASE) + "\n")

    con = sql.connect(os.path.expanduser(OPENLP_DATABASE))
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute('SELECT id, title, ccli_number, song_number, copyright, comments, lyrics FROM songs')
    songs = cur.fetchall()

    cur.execute('SELECT id, display_name FROM authors')
    authors = cur.fetchall()

    cur.execute('SELECT song_id, author_id FROM authors_songs')
    authors_songs = cur.fetchall()

    # Database helper functions:

    def get_authorname(id):
        names = filterbyfield(id,authors)
        if len(names) == 0:
            return ''
        else:
            return xml_tag_clean(names[0]['display_name'])

    def get_song_authors(song_id):
        return filterbyfield(song_id,authors_songs,'song_id')


    def get_song_authornames(song_id):
        return ' &amp; '.join(map (get_authorname, map (lambda x: x['author_id'], get_song_authors(song_id))))

except:

    print ("Sorry - There was a problem loading the OpenLP Database.\n"\
          +"(" + OPENLP_DATABASE + ")\n"\
          +"Maybe OpenLP isn't set up on this user?\n\n"\
          +"If you know where the database is, you can edit the path at the top of this script\n"\
          +"And set it manually.")
    exit()


# Now go through songs and output the files.

print ("And writing the new files to\n  " + OUTPUT_DIRECTORY + "\n")

for song_raw in songs:

    # Clean out non-XML happy characters...

    song = {} 
    for field in ['title','ccli_number','song_number','copyright', 'comments']:
        song[field] = xml_tag_clean(song_raw[field])

    song_lyrics = xml.dom.minidom.parseString(song_raw['lyrics'])

    song_authors = get_song_authornames(song_raw['id'])

    # Find the copyright year (this is so much briefer in perl...)

    get_year = re.match(r'^\d\d\d\d', song['copyright'])

    if get_year != None:
        copyright_year = get_year.group()
        song['copyright'] = song['copyright'][4:].strip()
    else:
        copyright_year = ''

    # Open the appropriate file:

    f = open(OUTPUT_DIRECTORY + song['title'].replace('/','') + '.pro5','w')

    # Write the header

    f.write ( HeaderBlock(Name=uni(song['title']),
                          CCLILicenceNumber=uni(song['ccli_number']),
                          Notes=uni(song['comments']),
                          CCLICopyRightInfo=uni(copyright_year),
                          Publisher=uni(song['copyright']),
                          Authors=song_authors) )

    # Write the verses (slides)

    song_sections = song_lyrics.getElementsByTagName('verse')
    song_sections.reverse()

    for verse in song_sections:
        f.write ( VerseBlock( Verbose_names(verse.getAttribute('type')) + ' ' + verse.getAttribute('label'),
                              verse.getAttribute('type'),
                              map(lambda x: x.nodeValue, verse.childNodes) ,
                              color = '1 0 0 1' if verse.getAttribute('type') == 'c' else VERSE_COLORS[int(verse.getAttribute('label'))]  ) )

    # And the footer, and close.

    f.write ( FooterBlock() )
    f.close()

print ("Finished.")
if OPEN_DIR_ON_EXIT: 
    os.system('open "' + OUTPUT_DIRECTORY + '"')