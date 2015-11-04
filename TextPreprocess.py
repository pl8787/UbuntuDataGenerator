#! author: pl8787
#! coding: utf-8

import re
import os
import time
import nltk
from twokenize import tokenize

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

def is_url(s):
    return s.startswith('http://') or s.startswith('https://') or s.startswith('ftp://') \
            or s.startswith('ftps://') or s.startswith('smb://')


def diff_times_in_seconds(t1,t2,date1,date2):
  """
  Returns the difference in time (in seconds) between two dates
  """
  t1 = t1.split(':')
  t2 = t2.split(':')
  date1 = date1.split('-')
  date2 = date2.split('-')
  if len(t1)<2 or len(t2)<2 or len(date1)<3 or len(date2)<3:
    return 60*60*24 #return 1 day if something goes wrong
  if not is_number(t1[0]) or not is_number(t1[1]) or not is_number(t2[0]) or not is_number(t2[1]):
    return 60*60*24
  if not is_number(date1[0]) or not is_number(date1[1]) or not is_number(date1[2]) or not is_number(date2[0]) \
          or not is_number(date2[1]) or not is_number(date2[2]):
    return 60*60*24
  h1,m1,s1 = int(t1[0]),int(t1[1]),0
  h2,m2,s2 = int(t2[0]),int(t2[1]),0
  d1,mo1,yr1 = int(date1[2]),int(date1[1]),int(date1[0])
  d2,mo2,yr2 = int(date2[2]),int(date2[1]),int(date2[0])
  t1_secs = s1 + 60*(m1 + 60*(h1 + 24*(d1+ 30*(mo1+12*yr1))))
  t2_secs = s2 + 60*(m2 + 60*(h2 + 24*(d2+ 30*(mo2+12*yr2))))
  return t2_secs - t1_secs


def clean_str(string, TREC=False):
    """
    Tokenization/string cleaning for all datasets except for SST.
    Every dataset is lower cased except for TREC
    """
    string = re.sub(r"\'m", " am", string) 
    string = re.sub(r"\'s", " is", string) 
    string = re.sub(r"\'ve", " have", string) 
    string = re.sub(r"n\'t", " not", string) 
    string = re.sub(r"\'re", " are", string) 
    string = re.sub(r"\'d", " would", string) 
    string = re.sub(r"\'ll", " will", string) 
    string = re.sub(r"`", " ` ", string)
    string = re.sub(r",", " , ", string) 
    return string.strip() 

def process_token(c, word):
    """
    Use NLTK to replace named entities with generic tags.
    Also replace URLs, numbers, and paths.
    """
    #nodelist = ['PERSON', 'ORGANIZATION', 'GPE', 'LOCATION', 'FACILITY', 'GSP']
    #if hasattr(c, 'label'):
    #    if c.label() in nodelist:
    #                return "__%s__" % c.label()
    if is_url(word):
        return "__url__"
    elif is_number(word):
        return "__number__"
    elif os.path.isabs(word):
        return "__path__"
    return word

def process_line(s, clean_string=True):
    """
    Processes a line by iteratively calling process_token.
    """
    if clean_string:
            s = clean_str(s)
    tokens = tokenize(s)
    #sent = nltk.pos_tag(tokens)
    #chunks = nltk.ne_chunk(sent, binary=False)
    #return [process_token(c,token).lower().encode('UTF-8') for c,token in map(None, chunks, tokens)]
    return [process_token(None,token).lower().encode('UTF-8') for token in tokens]



