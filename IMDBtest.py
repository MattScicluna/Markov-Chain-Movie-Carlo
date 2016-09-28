import urllib.request
from bs4 import BeautifulSoup
import csv
import time
import random

#Starting movie
nextmovie='http://www.imdb.com/title/tt1832382/?ref_=nv_sr_1'

f = csv.writer(open("IMDB Data" + ".csv", "w", newline=''), dialect='excel')

# Write column headers as the first line
f.writerow(["Movie", "Year", "First Name", "Last Name", "Link"])

for i in range(1,10):
    urllines = urllib.request.urlopen(nextmovie)
    pagedat = urllines.read()
    urllines.close()
    soup = BeautifulSoup(pagedat)
    Title=soup.find_all('title')
    Title=str(Title)
    Title=Title[8:-16]
    allrows = soup.find_all("tr")
    index=random.randint(3,10)
    row=allrows[index]
    try:
        links=row.find_all('a')
        link=links[1].get('href')
        actor=row.get_text()
        actor=actor.split()
        FirstName=actor[0]
        LastName=actor[1]
        nextactor='http://www.imdb.com/filmosearch?explore=title_type&role='+link[6:15]+'&ref_=filmo_vw_smp&sort=year,desc&mode=simple&page=1&title_type=movie'
        print('Film Title: {0}, First Name: {1}, Last Name: {2}'.format(Title, FirstName, LastName))

    except Exception:
        print("there was an exception")
    urllines = urllib.request.urlopen(nextactor)
    pagedat = urllines.read()
    urllines.close()
    soup = BeautifulSoup(pagedat)
    links=soup.find_all('a')
    movies=list()
    for i in range(1,len(links)):
        if 'title' in str(links[i]):
            if 'film' in str(links[i]):
                movies.append(links[i].get('href'))
    index=random.randint(1,len(movies)-1)
    nextmovie='http://www.imdb.com/'+movies[index]
