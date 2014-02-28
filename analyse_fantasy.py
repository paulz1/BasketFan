#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2;
import sys;
import BeautifulSoup;
import re ;
import sqlite3 as lite ;

headers=["Team", "FG%", "FT%", "PTM3", "PTS", "REB", "AST", "ST", "BLK", "TO", "Score"]

conn = None
try :
    conn = lite.connect('nba_fantasy_2013_14.db')
    curs = conn.cursor()

    curs.execute('SELECT SQLITE_VERSION()')
    data = curs.fetchone()
    print "SQLite version: %s" % data

    curs.execute('SELECT cat_won FROM games_info WHERE result IS "W"')
    data = curs.fetchall()
    array_stat=[0]*len(headers)

    for categories in data :    
        for category in (categories[0]).split(',') :
            # print(category)
            array_stat[int(category)]+=1
    print(array_stat)
    temp_array=sorted(array_stat)[-5:]
    print temp_array
    temp_array=sorted(range(len(array_stat)), key=lambda k: array_stat[k])[-5:]
    print temp_array
    temp_array=[headers[i] for i in sorted(range(len(array_stat)), key=lambda k: array_stat[k])[-5:]]
    print temp_array


except lite.Error, e :
    print("Error %s:" % e.args[0])
    sys.exit(1)
finally:
    if conn:
        conn.close()