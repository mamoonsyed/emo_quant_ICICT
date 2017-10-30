# -*- coding: utf-8 -*-
"""
Created on Sat Jul 29 21:25:41 2017
@author: transmatter
this file takes data from input_path and retrieves the articles using csv reader
and goose, then it cleans the data. using regex.
"""

import csv
import os.path
from goose import Goose
import re
import winsound
#from multiprocessing.dummy import Pool as ThreadPool
#import urllib2 # imported for cookie manipulation

# rows of csv file to process in one run
# this provision is given so that hanginng problem can be solved
# hanging problem may be because of some library.
START_ROW = 0
END_ROW = 114

#   i'm using csv for input data instead of excel (hoping that this will be faster).
# don't use '-' in the filename it will give an IO error.
# don't use the line continuer '\' to divide the path line into two. it won't work.
INPUT_FILE='E:/Google Drive/research/emo_quant_ICICT/input_data/data_2017_10_28.csv'

# text data will be saved in the below mentioned path.
TXT_PATH='E:/Google Drive/research/emo_quant_ICICT/txt_data'

def write_file(r, c, title_body_rating, data):
#    print "inside write_file function"
    file_name = os.path.join(TXT_PATH,
                             str(r)+
                             '_'+str(c)+
                             '_'+title_body_rating+
                             '.txt')
    with open(file_name, 'w+') as f:
        f.write(data)
    f.closed

def clean_current(current_string):
#    print "inside clean_current function"
    rx = re.compile('\W+')
    clean_string = rx.sub(' ', current_string).strip()
    return clean_string

def extract_article (row, row_index):
#    print "inside extract_article function"
    rating = row[4]
    write_file (row_index, 0, 'rating', rating)
    
    g = Goose()
#    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    url_array = row[6:]
#    print "url_array: "
#    print url_array
    for url_index, url in enumerate(url_array):
        if url == "":
            break
        event_url = 'event: ' + str(row_index) + " | url: " + str(url_index)
        print event_url
        article = g.extract(url)
        
#        title_present = article.title != ""
#        body_present = article.cleanedtext != ""
            
        clean_title = clean_current(article.title)
        write_file (row_index, url_index, 'title', clean_title)
        clean_body = clean_current(article.cleaned_text)
        write_file (row_index, url_index, 'body', clean_body)
        
         # following loop was abolished because there seemed to be no use to
         # loop in the cases where something was missing. looping didn't 
         # make it any better
         
#        # following loop is used to make sure that if the article is not extracted
#        # the first time, 3 attempts are made to retrieve the article.
#        for i in range (0,3,1):
#            print event_url+" attempt: "+ str(i)
##            response = opener.open(url)
##            raw_html = response.read()
##            article = g.extract(raw_html=raw_html)
#            if (article.title != "" and article.cleaned_text != ""):
#                clean_title = clean_current(article.title)
#                write_file (row_index, url_index, 'title', clean_title)
#                clean_body = clean_current(article.cleaned_text)
#                write_file (row_index, url_index, 'body', clean_body)
#                break
#            else:
#                continue
    
def play_sound():
    duration = 1500  # millisecond
    freq = 999  # Hz
    winsound.Beep(freq, duration)
    
#opening the input_data file
with open (INPUT_FILE, 'rb') as f:
    reader = csv.reader(f)
    for row_index, row in enumerate(reader):
#        if row_index == CURRENT_ROW:
        if row_index >= START_ROW and row_index < END_ROW:
            extract_article(row, row_index)
            print "------------------" # line separating each event
        elif row_index == END_ROW:
            break
        else:
            continue
play_sound()        