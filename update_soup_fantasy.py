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

    def get_week(soup_week,nm):
        all_games={}        
        week_matchs=soup_week.findAll('li',{"class":"Linkable Listitem No-p"})
               
        for match_li in week_matchs :
            url_match="http://basketball.fantasysports.yahoo.com"+match_li['data-target']
            usock=urllib2.urlopen(url_match);
            data1=usock.read();
            usock.close();
            soup_match=BeautifulSoup.BeautifulSoup(data1);
            match_table=soup_match.find('table',{'class':re.compile(".*Datatable.*")})
            match_rows=match_table.findAll('tr')
            all_games[nm]={}
            all_games[nm]["Team1"]={}
            all_games[nm]["Team2"]={}

            all_points1=match_rows[1].findAll('td')
            all_points2=match_rows[2].findAll('td')
            
            all_games[nm]["Team1"]["Team"]=all_points1[0].findAll(text=True)[1]
            all_games[nm]["Team2"]["Team"]=all_points2[0].findAll(text=True)[1]
            i=0
            for category in match_rows[0].findAll('th') :
                if category.contents[0].string != "Team" :
                    if category.contents[0].string == "3PTM" :
                        cur_category="PTM3"
                    else :
                        cur_category=category.contents[0].string
                    all_games[nm]["Team1"][cur_category]=(all_points1[i].contents[0].find(text=True)).rstrip("*")
                    all_games[nm]["Team2"][cur_category]=(all_points2[i].contents[0].find(text=True)).rstrip("*")
                i+=1
            query="INSERT INTO games_id ('id','week','team1','score1','team2','score2') VALUES("+",".join(['?']*6)+")"
            curs.execute(query,(nm,cur_week_number,all_games[nm]["Team1"]["Team"],all_games[nm]["Team1"]["Score"],\
                all_games[nm]["Team2"]["Team"],all_games[nm]["Team2"]["Score"]))        

            array_cat_won=det_cat_won(sub_dict(all_games[nm]["Team1"],headers),sub_dict(all_games[nm]["Team2"],headers))
            query="INSERT INTO games_info ('game_id','" + "','".join(sub_dict(all_games[nm]["Team1"],headers).keys()) + \
                "','result','cat_won') VALUES("+",".join(['?']*(len(headers)+3))+")"
            curs.execute(query,([nm] + sub_dict(all_games[nm]["Team1"],headers).values() + \
                det_result(all_games[nm]["Team1"],all_games[nm]["Team2"])[:1]+\
                (det_cat_won(sub_dict(all_games[nm]["Team1"],headers),sub_dict(all_games[nm]["Team2"],headers))[:1])))
            curs.execute(query,([nm] + sub_dict(all_games[nm]["Team2"],headers).values() + \
                det_result(all_games[nm]["Team1"],all_games[nm]["Team2"])[1:]+\
                (det_cat_won(sub_dict(all_games[nm]["Team1"],headers),sub_dict(all_games[nm]["Team2"],headers))[1:])))
            conn.commit()
            nm+=1
        return nm

# End of functions

conn = None
try :
    conn = lite.connect('nba_fantasy_2013_14.db')
    curs = conn.cursor()

    curs.execute('SELECT max(week) FROM games_id GROUP BY week')
    data = curs.fetchall()
    start_week=max(map(lambda x: x[0], data))+1
    print("SQLite version: %s" % start_week)

    curs.execute('SELECT max(id) FROM games_id')
    data = curs.fetchall()
    nm=map(lambda x: x[0], data)[0]+1

    very_max_week=23

    url_base="http://basketball.fantasysports.yahoo.com/nba/86110?matchup_week="

    cur_week_number=start_week
    while cur_week_number<=very_max_week :
        # print(cur_week_number)
        url_main=url_base+str(cur_week_number)

        usock=urllib2.urlopen(url_main);
        data=usock.read();
        usock.close();        
        soup_week=BeautifulSoup.BeautifulSoup(data);
        week_status=soup_week.findAll('span',{"class":"Ta-c Fz-xxs Pbot-sm Grid-u"})
        if week_status!="Final Result" :
            max_week=cur_week_number
            break
        else :
            temp_nm=get_week(soup_week,nm)
            if temp_nm<=nm :
                print("Something got wrong. NM after inserting is little than before :" + temp_nm)
                break
        cur_week_number+=1
    print max_week


except lite.Error, e :
    print("Error %s:" % e.args[0])
    sys.exit(1)
finally:
    if conn:
        conn.close()

exit()
