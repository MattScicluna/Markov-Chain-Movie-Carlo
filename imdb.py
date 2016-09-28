import urllib.request
from bs4 import BeautifulSoup
import csv
import time
import random
import re

from math import log
from math import ceil

#Starting movie
#movie = 'http://www.imdb.com/title/tt1832382/?ref_=nv_sr_1'
movie = 'http://www.imdb.com/title/tt0102926/?ref_=nv_sr_1'

# Weights with which to choose actors
WEIGHTS = [0.50, 0.25, 0.125, 0.075, 0.05]

# PDF to choose movies is exponential with mean = mu
def choose_movie(mu):
  val = -log(random.random())*mu
  return ceil(val)


def choose_weights(weights):
  '''weights is a list of probability values that sum to 1.
  Randomly choose a weight and return the index of that weight.
  '''
  import random
  running = []
  total = 0
  for weight in weights:
    running.append(total)
    total = total + weight

  rand = random.random() # number between 0 and 1
  for i in range(len(weights) - 1, -1, -1):
    if rand >= running[i]:
      return i
      

movie_stack = []
movie_stack.append(movie)
all_movies = []

f = open('imdb.csv', 'w', newline='', buffering=1)
f_csv = csv.writer(f)

# Write column headers as the first line
f_csv.writerow(["index", "title", "year", "budget", "gross", "country", "Genre", "keyword #1", "keyword #2", "keyword #3"])

# change the number to get more movies
MAX_MOVIES = 50

progress = 0
index = 0
while index < MAX_MOVIES:
    urllines = urllib.request.urlopen(movie)
    pagedat = urllines.read()
    urllines.close()
    soup = BeautifulSoup(pagedat)

# The [:-7] removes the " - IMDB" after the title
    title=soup.title.text[:-7]
    year = title[-5:-1]
    if not year.isdigit(): year = '' # movie not released
    # find more movie details
    budget = ''
    country = ''
    gross = ''
    keywords = ''
    genre = ''
    try:
        details = soup.find('h2', text=re.compile('Details')).parent
        storyline = soup.find('h2', text=re.compile('Storyline')).parent
        try:
            budget = details.find(text='Budget:').parent.next_sibling.strip()
        except Exception:
            print('No budget')
    
        country = ''
        try:
            country = details.find(text='Country:').parent.next_sibling.next_sibling.get_text().strip()
        except Exception:
            print('No country')

        try:
            if 'USA' in details.find(text='Gross:').parent.next_sibling.next_sibling.get_text().strip():
              gross = details.find(text='Gross:').parent.next_sibling.strip()

        except Exception:
            print('No gross')

        try:
           genre = storyline.find(text="Genres:").find_next().get_text().lstrip()

        except Exception:
            print('No genre')

        try:
           keywordsl = storyline.find(text="Plot Keywords:").parent.find_next_siblings()
           keywords1 = keywordsl[0].get_text().lstrip()
           keywords2 = keywordsl[2].get_text().lstrip()
           keywords3 = keywordsl[4].get_text().lstrip()
                       
        except Exception:
            print('No keywords')
    
            pass    
    except Exception:
        pass    
    
    if title not in all_movies:
        all_movies.append(title)
        f_csv.writerow([str(index), title, year, budget, gross, country, genre, keywords1, keywords2, keywords3,])
        index = index + 1
        progress = 0
    else:
        progress = progress + 1
        if progress > 0 and progress % 10 == 0:
            
            print('No progress for a while. Backing up...')
            for unwind in range(progress // 10):
                if movie_stack: movie = movie_stack.pop()
            continue    

    # Get the table of the cast list
    cast = soup.find('table', class_='cast_list') 
    if not cast:
        print('No cast table. Backing up...')
        movie = movie_stack.pop()
        continue
    
    # Movie is OK
    short = movie[:movie.find('?')]
    if short not in movie_stack:
        movie_stack.append(short)
    allrows = cast.find_all('tr')
    # collect actor links
    actor_links = []
    actor_fnames = []
    actor_lnames = []
    for row in allrows[1:]:
        if 'castlist_label' in row.td.get('class'):
            break # no more actors
        links=row.find_all('a')
        link=links[1].get('href')
        actor=row.get_text()
        href = 'http://www.imdb.com/filmosearch?explore=title_type&role='+link[6:15]+'&ref_=filmo_vw_smp&sort=year,desc&mode=simple&page=1&title_type=movie'
        actor_links.append(href)
    print('{} actors.'.format(len(actor_links)))
    # There might be fewer than five actors
    if len(actor_links) < 5:
        choose = random.randint(0, len(actor_links) -1)
    else:
        choose = choose_weights(WEIGHTS)
        href= actor_links[choose]
    try:
        print('Film Title: {0}, Actor Name: {1}'.format(title, actor))
    except Exception:
        pass # some titles have strange characters
    urllines = urllib.request.urlopen(href)
    pagedat = urllines.read()
    urllines.close()
    soup = BeautifulSoup(pagedat)
    links=soup.find_all('a')
    movies=[]
    for i in range(1,len(links)):
        if 'title' in str(links[i]):
            if 'film' in str(links[i]):
                movies.append('http://www.imdb.com' + links[i].get('href'))
    if len(movies) <= 1: continue
    if len(movies) < 5:
        choose2 = random.randint(0, len(movies) -1)
    else:
        choose2 = min(choose_movie(ceil(len(movies)/4)),len(movies)-1)
    movie = movies[choose2]
    
    print(movie)
    