#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys;
import BeautifulSoup;
import re ;
import sqlite3 as lite ;
import matplotlib.pyplot as plt
import numpy

# from decimal import *
# getcontext().prec = 3

headers=["Team", "FG%", "FT%", "PTM3", "PTS", "REB", "AST", "ST", "BLK", "TO", "Score"]

conn = None
try :
    conn = lite.connect('nba_fantasy_2013_14.db')
    curs = conn.cursor()

    curs.execute('SELECT SQLITE_VERSION()')
    data = curs.fetchone()
    print "SQLite version: %s" % data

    curs.execute('SELECT * FROM games_info WHERE Team IS "Red-Yellow Wolves"')
    # curs.execute('SELECT * FROM games_info WHERE Team IS "Roma-1"')
    data = curs.fetchall()
    array_stat=[0]*len(headers)
    
    # for games in data :
    #     print(games)
    Team=data[0][2]
    for i in range(1,9) :
        temp_array=map(lambda x: float(x[i+2]), data)    
        # print(temp_array)
    
        print("%.3f"%numpy.mean(temp_array))
        print("%.3f"%numpy.std(temp_array))
    #   print("")
    # #  print(y)
    # #  print(range(1,len(y)+1))
        fig=plt.figure()
        ax=fig.add_subplot(111)
        plt.plot(range(1,len(temp_array)+1),temp_array)
        plt.axhline(y=numpy.mean(temp_array), xmin=0, xmax=len(temp_array)+1)
        # plt.text(0.5,0.5,"%.3f"%numpy.mean(temp_array))
        plt.text(0.95, 0.95,"Avg.: %.3f"%numpy.mean(temp_array), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        plt.text(0.95, 0.90,"Std.: %.3f"%numpy.std(temp_array), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)        
        for k,l in zip(range(1,len(temp_array)+1),temp_array):
            plt.annotate(str(temp_array[k-1]),xy=(k+0.1,l+0.1))
        plt.gca().set_ylim(bottom=0)
        plt.ylabel(headers[i])
        plt.xlabel('weeks')
        plt.gca().xaxis.set_major_locator(plt.MultipleLocator(1))
        plt.gca().yaxis.set_minor_locator(plt.IndexLocator(1,1))
        plt.grid(True)
        plt.title(Team+ " "+headers[i])
        plt.savefig(headers[i] + '.png')
        plt.close()


    #     for category in (categories[0]).split(',') :
    #         # print(category)
    #         array_stat[int(category)]+=1
    # print(array_stat)
    # temp_array=sorted(array_stat)[-5:]
    # print temp_array
    # temp_array=sorted(range(len(array_stat)), key=lambda k: array_stat[k])[-5:]
    # print temp_array
    # temp_array=[headers[i] for i in sorted(range(len(array_stat)), key=lambda k: array_stat[k])[-5:]]
    # print temp_array


except lite.Error, e :
    print("Error %s:" % e.args[0])
    sys.exit(1)
finally:
    if conn:
        conn.close()