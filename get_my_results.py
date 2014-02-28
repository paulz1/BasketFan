#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from sitescraper import sitescraper
from pylab import *
import numpy

ss = sitescraper()

#url='http://basketball.fantasysports.yahoo.com/nba/86110/matchup?week=1&module=matchup'
url='http://basketball.fantasysports.yahoo.com/nba/86110/?matchup_week=2&module=matchupsmack&matchupsmacktab=m'

#data = [".451 ",".793","16","271","151","109","35","15"," 56",'<td  class="stat"><strong>47</strong></td>',"7"]
data=[["FG%","FT%","3PTM","PTS","REB","AST","ST","BLK","TO","Score"], [".473 ",".716","44","441","210","105","34","20"," 88","6"]]

ss.add(url, data)
cur_week=ss.scrape('http://basketball.fantasysports.yahoo.com/nba/86110/matchup?week=2')

print cur_week
sys.exit(0)

#print(ss.scrape('http://basketball.fantasysports.yahoo.com/nba/87421/matchup?week=3&mid1=18&mid2=1'))
weeks=[]
for week_num in range(2,5) :
#for week_num in range(2,21) :
  print week_num
  cur_week=ss.scrape('http://basketball.fantasysports.yahoo.com/nba/86110/matchup?week='+str(week_num)+'&mid1=18&mid2=1')
  weeks.append(cur_week[1])
#  print(cur_week[1])

#print(weeks)
for cat in range(0,len(data[0])):
  category=data[0][cat]
  print(category)
  y=[float(data[1][cat])]
  for i in range(0,len(weeks)):
    y.append(float(weeks[i][cat]))
    print(weeks[i][cat]),
  print("")
  print("%.3f"%numpy.mean(y))
  print("%.3f"%numpy.std(y))
  print("")
#  print(y)
#  print(range(1,len(y)+1))
  plot(range(1,len(y)+1),y)
  axhline(y=numpy.mean(y), xmin=0, xmax=len(y)+1)
  for k,l in zip(range(1,len(y)+1),y):
    annotate(str(y[k-1]),xy=(k+0.1,l+0.1))
  gca().set_ylim(bottom=0)
  ylabel(category)
  xlabel('weeks')
  title(category)
  gca().xaxis.set_major_locator(MultipleLocator(1))
  #gca().yaxis.set_minor_locator(IndexLocator(1,1))
  grid(True)
  savefig(category+'.png')
  close()
#  show()

