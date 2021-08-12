"""
                                                                                      Hung Nguyen
Description: Parse information into a JSON, input the JSON into the database
ps: my json gives error when loading, hence I used my dict to put into the sql
"""
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
from collections import defaultdict
import pickle
import json
import sqlite3
from operator import itemgetter

def main():
    #gets the page and parse information
    testList = []
    movieDict = {}
    page = requests.get("https://editorial.rottentomatoes.com/article/most-anticipated-movies-of-2021/")
    soup = BeautifulSoup(page.content, "lxml")
    longestActors = 0
    data = soup.select("div.articleContentBody p")
    """
    for a in soup.select("div.articleContentBody p"):
        
        try:
            title = (a.find("strong").text).replace("\xa0"," ").split("(")
            print(title[0].strip())
        except:
            pass
        
        for b in a.find_all('strong'):
            print(b.text)
    """

    for a in soup.select("div.articleContentBody p"):
        try:
         
            if a.has_attr("style"):
                pass
            elif a.find("strong"):
                title = (a.find("strong").text).replace("\xa0"," ").split("(")
                
                if title[0] == "Directed by:":
                    title[0] = "tick, tick... BOOM!"
           
        
            b = a.find("strong")
            try:
                c = b.find('a')
                url = c['href']
            
            except TypeError:
                url = 'none'
         
            actor = (a.find('strong', string = re.compile('Starring:', re.I)))
            actor = str(actor.next_sibling).replace("\xa0","").strip().split(",")
        
            if (len(actor) >longestActors):
                longestActors = len(actor)
          

            directors = (a.find("strong", string = re.compile("Directed by:", re.I)))
            directors = str(directors.next_sibling).replace('\xa0', "").strip()
      

            date = (a.find("strong",string = re.compile("Opening on:", re.I)))
            date = str(date.next_sibling).strip().split(" ")
            if date[0] == '2021':
                date[0] = 'TBD'
            
        
        
            movie = {title[0].strip(): {'link':url, 'directors':directors, 'actors':actor, 'month':date[0].strip()}}
        
            movieDict.update(movie)
            testList.append(movie)
        
        except Exception as E:
            pass 
    print (movieDict)
    """ PS: this part gives me an index error whenever I try to load the file. It
    doesn't happen anywhere else. However, It creates a json but 
    with open("movies.json", 'w') as fh:
        json.dump(movieDict,fh)
    with open("movies.json",'r')as fh:
        d = json.loads(fh)
    """
    #A part2: creates a movie db that connects with a monthdb
    conn = sqlite3.connect('movies.db')
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS MoviesDB")      
    cur.execute('''CREATE TABLE MoviesDB(             
                       title STR NOT NULL PRIMARY KEY,
                       url STR,
                       directors STR,
                       monthKey INTEGER )''')
    cur.execute("DROP TABLE IF EXISTS MonthDB")     
    cur.execute('''CREATE TABLE MonthDB(             
                       monthKey INTEGER NOT NULL PRIMARY KEY,
                       month TEXT UNIQUE ON CONFLICT IGNORE )''')
    for i in range(longestActors):
            cur.execute(f'''ALTER TABLE MoviesDB ADD COLUMN {'actors' +str(i)} STR ''')
    conn.commit()
    for k, v in movieDict.items():
            cur.execute("""INSERT INTO MonthDB (month) VALUES (?)""", (v['month'],))
            cur.execute('SELECT monthKey FROM MonthDB WHERE month = ?', (v['month'],))
            monthId= cur.fetchone()[0]
        
            cur.execute("INSERT INTO MoviesDB (title, url,directors, monthKey) VALUES (?,?,?,?)", (k,v["link"], v['directors'], monthId,))
            
            for i in range(len(v['actors'])):
                try:  
                    cur.execute(f"UPDATE MoviesDB set {'actors' +str(i)} = ? WHERE title = ?", (v['actors'][i], k))
                except IndexError :
                    pass

    conn.commit()    

    

if __name__ == '__main__':
    main()
