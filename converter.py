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

# Configuration Options:

OPENLP_DATABASE = "~/source/OpenLP-To-ProPresenter5-Converter/songs2.sqlite"
OUTPUT_DIRECTORY = "tmp/"


import OpenLP
import Pro5
import LifeVerse
import re                        # For regexy stuff.
import codecs

# Apparently it's faster / better to compile regex:
__re_year = re.compile(r'^\d\d\d\d')   # Year from Copyright String
__re_xml_attr = re.compile('[<>\n"]')  # Stuff to strip from XML attributes

def main():
    # First load the data from the OpenLP database:
    lp = OpenLP.OpenLPReader()
    if (not lp.load(OPENLP_DATABASE)):
        exit()

    # Now go through songs and output the files.

    print ("And writing the new files to\n  " + OUTPUT_DIRECTORY + "\n")

    for song in lp.songs:

        song_authors = lp.get_song_authornames(song['id'])

        # Find the copyright year (this would be briefer in perl...)

        get_year = re.match(__re_year, Pro5.xml_attr(song['copyright']))

        if get_year != None:
            copyright_year = get_year.group()
            copyright = song['copyright'][4:].strip()
        else:
            copyright_year = ''
            copyright = ''

        # pro5 = Pro5.Pro5Writer()
        # for v in lp.ParseLyric(song['lyrics']):
        #     pro5.addVerse(v)

        # if (not pro5.writeFile(OUTPUT_DIRECTORY, song['title'], song['ccli_number'], song['comments'],
        #                     copyright_year, copyright, song_authors)):
        #     exit()
        orderToTagName = dict()

        orderToTagName["v"] = "verse"
        orderToTagName["c"] = "chorus"
        orderToTagName["p"] = "pre-chorus"
        orderToTagName["e"] = "ending"
        orderToTagName["i"] = "intro"
        orderToTagName["b"] = "bridge"
        orderToTagName["o"] = "outro"
        orderToTagName["verse"] = "verse"
        orderToTagName["chorus"] = "chorus"
        orderToTagName["pre-chorus"] = "pre-chorus"
        orderToTagName["ending"] = "ending"
        orderToTagName["intro"] = "intro"
        orderToTagName["bridge"] = "bridge"
        orderToTagName["outro"] = "outro"

        song_authors = song_authors.replace("&amp;", "|")

        lyrics = lp.ParseLyric(song['lyrics'])
        lyrics.reverse()
        tags = []
        slides = []
        for l in lyrics:
            tags.append(orderToTagName[str(l['type']).lower()] + " " + str(l['label']))
            text = ""
            for i in range(len(l['text'])):
                text += str(codecs.decode(l['text'][i], 'utf-8'))
            slides.append(text)

        LifeVerse.writeFile(OUTPUT_DIRECTORY + song['title'].replace(' ', '-').replace('/', '-'), song['title'], song_authors, tags, slides)
        #print(tags)
        #print(slides)


    print ("Finished.")

if __name__ == "__main__":
    main()
