#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2;
import sys;
import BeautifulSoup;
import re ;
import sqlite3 as lite ;

headers=["Team", "FG%", "FT%", "PTM3", "PTS", "REB", "AST", "ST", "BLK", "TO", "Score"]

def sub_dict(somedict, somekeys, default=None):
    return dict([ (k, somedict.get(k, default)) for k in somekeys ])
def det_result(score1,score2):
    if int(score1["Score"]) > int(score2["Score"]) :
        return ['W','L']
    elif int(score1["Score"]) < int(score2["Score"]) :
        return ['L','W']
    else :
        return ['D','D']
def det_cat_won(team1_results,team2_results):
    result1=[]
    result2=[]
    for cur_key in team1_results.keys() :
        if (cur_key=="TO") :
            if float(team1_results[cur_key]) < float(team2_results[cur_key]) :
                result1.append(str(headers.index(cur_key)))
            elif float(team1_results[cur_key]) > float(team2_results[cur_key]) :
                result2.append(str(headers.index(cur_key)))
        if ((cur_key!="Score") and (cur_key!="Team") and (cur_key!="TO")) :
            if float(team1_results[cur_key]) > float(team2_results[cur_key]) :
                result1.append(str(headers.index(cur_key)))
            elif float(team1_results[cur_key]) < float(team2_results[cur_key]) :
                result2.append(str(headers.index(cur_key)))
            # print(cur_key)
            # print(float(team1_results[cur_key]))
            # print(float(team2_results[cur_key]))
            # print(result2)
            # print("----")
    return [",".join(result1),",".join(result2)]

conn = None
try :
    conn = lite.connect('nba_fantasy_2013_14.db')
    curs = conn.cursor()

    curs.execute('SELECT SQLITE_VERSION()')
    data = curs.fetchone()
    print "SQLite version: %s" % data
    curs.execute("DROP TABLE IF EXISTS games_id")
    curs.execute("CREATE TABLE games_id(id INTEGER PRIMARY KEY, week INT, team1 TEXT, team2 TEXT, score1 INT, score2 INT)")
    curs.execute("DROP TABLE IF EXISTS games_info")
    curs.execute("CREATE TABLE games_info (id INTEGER PRIMARY KEY, game_id INTEGER, \
        Team TEXT, 'FG%' NUMERIC, 'FT%' NUMERIC, \
        PTM3 NUMERIC, PTS NUMERIC, REB NUMERIC, AST NUMERIC, \
        ST NUMERIC, BLK NUMERIC, 'TO' NUMERIC, Score NUMERIC, \
        result TEXT, cat_won TEXT)")


    url_base="http://basketball.fantasysports.yahoo.com/nba/86110?matchup_week="    

    # Numero of Match
    nm=0     

    for cur_week_number in range(1,18):
    #     print(cur_week_number)
    # exit()
        url_main=url_base+str(cur_week_number)

        usock=urllib2.urlopen(url_main);
            #data_iso=usock.read();
            #data=data_iso.decode('iso-8859-1').encode('utf-8');
        data=usock.read();
        usock.close();

        all_games={}

        soup_week=BeautifulSoup.BeautifulSoup(data);

        week_matchs=soup_week.findAll('li',{"class":"Linkable Listitem No-p"})
               
        for match_li in week_matchs :
            #print(match_li)    
            #print(match_li['data-target'])
            url_match="http://basketball.fantasysports.yahoo.com"+match_li['data-target']
            usock=urllib2.urlopen(url_match);
            data1=usock.read();
            usock.close();
            soup_match=BeautifulSoup.BeautifulSoup(data1);
            match_table=soup_match.find('table',{'class':re.compile(".*Datatable.*")})
            match_rows=match_table.findAll('tr')
            # print(match_rows)
            all_games[nm]={}
            all_games[nm]["Team1"]={}
            all_games[nm]["Team2"]={}

            all_points1=match_rows[1].findAll('td')
            all_points2=match_rows[2].findAll('td')
            
            all_games[nm]["Team1"]["Team"]=all_points1[0].findAll(text=True)[1]
            all_games[nm]["Team2"]["Team"]=all_points2[0].findAll(text=True)[1]
            i=0
            for category in match_rows[0].findAll('th') :
                # print(all_points1[i].contents[0])
                # print(all_points1[i].contents[0].find(text=True))
                if category.contents[0].string != "Team" :
                    if category.contents[0].string == "3PTM" :
                        cur_category="PTM3"
                    else :
                        cur_category=category.contents[0].string
                    all_games[nm]["Team1"][cur_category]=(all_points1[i].contents[0].find(text=True)).rstrip("*")
                    all_games[nm]["Team2"][cur_category]=(all_points2[i].contents[0].find(text=True)).rstrip("*")
                i+=1
            #Print team name of first team
            #print(all_games[nm]["Team1"]["Team"])

            query="INSERT INTO games_id ('id','week','team1','score1','team2','score2') VALUES("+",".join(['?']*6)+")"
            # print(query)        
            curs.execute(query,(nm,cur_week_number,all_games[nm]["Team1"]["Team"],all_games[nm]["Team1"]["Score"],\
                all_games[nm]["Team2"]["Team"],all_games[nm]["Team2"]["Score"]))        

            array_cat_won=det_cat_won(sub_dict(all_games[nm]["Team1"],headers),sub_dict(all_games[nm]["Team2"],headers))

            query="INSERT INTO games_info ('game_id','" + "','".join(sub_dict(all_games[nm]["Team1"],headers).keys()) + \
                "','result','cat_won') VALUES("+",".join(['?']*(len(headers)+3))+")"
            # print(sub_dict(all_games[nm]["Team1"],headers).values())
            # print(sub_dict(all_games[nm]["Team2"],headers).values())
            curs.execute(query,([nm] + sub_dict(all_games[nm]["Team1"],headers).values() + \
                det_result(all_games[nm]["Team1"],all_games[nm]["Team2"])[:1]+\
                (det_cat_won(sub_dict(all_games[nm]["Team1"],headers),sub_dict(all_games[nm]["Team2"],headers))[:1])))

            curs.execute(query,([nm] + sub_dict(all_games[nm]["Team2"],headers).values() + \
                det_result(all_games[nm]["Team1"],all_games[nm]["Team2"])[1:]+\
                (det_cat_won(sub_dict(all_games[nm]["Team1"],headers),sub_dict(all_games[nm]["Team2"],headers))[1:])))
            
            # print("-----------------")        

            conn.commit()
            # print(all_games)
            # for match_tr in match_table.findAll('tr') :
            #     print(match_tr.contents)
                        
            # break
            nm+=1

except lite.Error, e :
    print("Error %s:" % e.args[0])
    sys.exit(1)
finally:
    if conn:
        conn.close()