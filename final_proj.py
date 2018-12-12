import sys
import final_proj_secrets
import sqlite3
from bs4 import BeautifulSoup
import json
import requests
import spotipy
import spotipy.util as util 
import wikipedia
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

# set up authorization Plotly
PLOTLY_USERNAME = final_proj_secrets.PLOTLY_USERNAME
PLOTLY_API_KEY = final_proj_secrets.PLOTLY_API_KEY
plotly.tools.set_credentials_file(username=PLOTLY_USERNAME, api_key=PLOTLY_API_KEY)

# set up authorization for Spotify
username = final_proj_secrets.S_USERNAME
S_CLIENT_ID = final_proj_secrets.S_CLIENT_ID
S_CLIENT_SECRET = final_proj_secrets.S_CLIENT_SECRET
scope = "user-library-read"
redirect_uri = "https://accounts.spotify.com/authorize?" #this will become the URL your app landing page

token = util.prompt_for_user_token(username, scope, client_id=S_CLIENT_ID,client_secret=S_CLIENT_SECRET,redirect_uri=redirect_uri)

if token:
	print("Token good!")
	sp = spotipy.Spotify(auth=token)
else:
	print("Unable to access")

# set up cache files for data collection

SONGS_CACHE_FNAME = "spotify_cache.json"
AUDIO_FEATURES_CACHE_FNAME = "audio_features_cache.json"
WIKI_CACHE_FNAME = 'wikiepdia.json'
WIKI_RESULTS_CACHE_FNAME = 'wiki_artists.json'

# songs cache
try:
    fobj = open(SONGS_CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    SONGS_CACHE_DICTION = json.loads(cache_contents)
    fobj.close()
except:
    SONGS_CACHE_DICTION = {}

# audio features cache
try: 
	fobj = open(AUDIO_FEATURES_CACHE_FNAME, 'r')
	cache_contents = cache_file.read()
	AUDIO_FEATURES_CACHE_DICTION = json.loads(cache_contents)
	fobj.close()
except:
	AUDIO_FEATURES_CACHE_DICTION = {}

# wiki html cache
try:
    cache_file = open(WIKI_CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    WIKI_CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    WIKI_CACHE_DICTION = {}

# wiki artists results cache
try:
    cache_file = open(WIKI_RESULTS_CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    WIKI_RESULTS_CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    WIKI_RESULTS_CACHE_DICTION = {}

# a helper function that returns url (to be used in caching later)
def get_unique_key(url):
  return url 

# song class that takes in a diciontary as input and then assigns instance variables by parsing
class Song():
	def __init__(self, song_dict):
		self.name = song_dict['track']['name']
		self.artist = song_dict['track']['artists'][0]['name']
		self.duration = song_dict['track']['duration_ms']
		self.id = song_dict['track']['id']
		self.popularity = song_dict['track']['popularity']
		self.dict = song_dict
	def __str__(self):
		return "{} by {}".format(self.name, self.arist)

# function to get most recently saved 500 songs from user's library
def get_song_ids():

	# get song results - the max limit is 50
	results = sp.current_user_saved_tracks(limit=50)

	# accumulate track_ids for each song in the initial 50 results
	track_ids = []
	for item in results['items']:
		id = item['track']['id']
		s = Song(item)

		# append to accumulator list if the song id is not already in the list - ensures not duplicates
		if id not in track_ids:
			track_ids.append(id)

		# write to cache
		SONGS_CACHE_DICTION[id] = item['track']
		dumped_json_cache = json.dumps(SONGS_CACHE_DICTION)
		fw = open(SONGS_CACHE_FNAME, "w")
		fw.write(dumped_json_cache)
		fw.close()

	# paging to get the full 500 songs
	next_page = sp.next(results)
	while len(track_ids) < 500:
		for item in next_page['items']:
			id = item['track']['id']
			if id not in track_ids:
				track_ids.append(id)

			SONGS_CACHE_DICTION[id] = item['track']
			dumped_json_cache = json.dumps(SONGS_CACHE_DICTION)
			fw = open(SONGS_CACHE_FNAME, "w")
			fw.write(dumped_json_cache)
			fw.close()
		next_page = sp.next(next_page)
	
	return track_ids

# function to get audio features given a song's id
def get_song_info(song_id):

	# load cache
	fobj = open(AUDIO_FEATURES_CACHE_FNAME, 'r')
	cache_contents = fobj.read()
	AUDIO_FEATURES_CACHE_DICTION = json.loads(cache_contents)
	fobj.close()

	# if the song is in the cache file, get its info from cache
	if song_id in list(AUDIO_FEATURES_CACHE_DICTION.keys()):
		return AUDIO_FEATURES_CACHE_DICTION[song_id]
	else:
		# get audio features for song and write to cache
		audio_features_dict = sp.audio_features(song_id)
		AUDIO_FEATURES_CACHE_DICTION[song_id] = audio_features_dict
		dumped_json_cache = json.dumps(AUDIO_FEATURES_CACHE_DICTION)
		fw = open(AUDIO_FEATURES_CACHE_FNAME, "w")
		fw.write(dumped_json_cache)
		fw.close()

		return audio_features_dict

def get_and_cache_all_audio_features(song_id_lst):
	for song_id in song_id_lst:
		get_song_info(song_id)

# set up database tables

DBNAME = 'songs.db'

def create_tables():

    # try to conenct to database and create tables
    try:
	    conn = sqlite3.connect(DBNAME)
	    cur = conn.cursor()

	    # Drop tables 
	    statement = '''DROP TABLE IF EXISTS 'Songs';'''
	    cur.execute(statement)

	    statement = '''DROP TABLE IF EXISTS 'AudioFeatures';'''
	    cur.execute(statement)

	    statement = '''DROP TABLE IF EXISTS 'Artists';'''
	    cur.execute(statement)

	    conn.commit()

	    # set fields
	    statement = '''
	        CREATE TABLE 'Songs' (
	        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
	        'TrackName' TEXT NOT NULL,
	        'Artist' INTEGER,
	        'Album' TEXT NOT NULL,
	        'Duration' INTEGER,
	        'IdNum' TEXT NOT NULL,
	        'Popularity' INTEGER
	        );
	    '''
	    cur.execute(statement)

	    statement = '''
	        CREATE TABLE 'AudioFeatures' (
	        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
	        'Danceability' REAL,
	        'Energy' REAL,
	        'Key' INTEGER,
	        'Loudness' REAL,
	        'Speechiness' REAL,
	        'Acousticness' REAL,
	        'Liveness' REAL,
	        'Valence' REAL,
	        'Tempo' REAL,
	        'IdNumber' TEXT NOT NULL
	        );
	    '''
	    cur.execute(statement)

	    statement = '''
	        CREATE TABLE 'Artists' (
	        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
	        'Name' TEXT NOT NULL,
	        'YearsActive' TEXT NOT NULL,
	        'Website' TEXT NOT NULL,
	        'WikiURL' TEXT NOT NULL,
	        'Summary' TEXT NOT NULL
	        );
	    '''
	    cur.execute(statement)

	    conn.commit()
	    conn.close()
	   
    except:
        print("Could not create tables.")

# populate songs table
def populate_songs():
	
	# try to connect to database and populate tables with data from cache
	try:
	    conn = sqlite3.connect(DBNAME)
	    cur = conn.cursor()

	    # open countries file and make it a python object
	    f = open(SONGS_CACHE_FNAME)
	    content = f.read()
	    songs_py_obj = json.loads(content)

	    # populate table and update Artist foreign key columns referencing Artists table
	    for track in list(songs_py_obj.keys()):
	    	name = songs_py_obj[track]['artists'][0]['name']
	    	cur.execute("INSERT INTO 'Songs' (TrackName, Artist, Album, Duration, IdNum, Popularity) VALUES (?, ?, ?, ?, ?, ?)", (songs_py_obj[track]['name'], songs_py_obj[track]['artists'][0]['name'], songs_py_obj[track]['album']['name'], songs_py_obj[track]['duration_ms'], songs_py_obj[track]['id'], songs_py_obj[track]['popularity']))

	    f.close()

	    conn.commit()
	    conn.close()
	except:
		print("Could not populate songs table.")


# populate audio features table
def populate_audio_features():
	try:
	    conn = sqlite3.connect(DBNAME)
	    cur = conn.cursor()

	    # open countries file and make it a python object
	    f = open(AUDIO_FEATURES_CACHE_FNAME)
	    content = f.read()
	    af_py_obj = json.loads(content)

	    # populate table and update Bars foreign key columns referencing Countries table
	    for track in list(af_py_obj.keys()):
	        cur.execute("INSERT INTO 'AudioFeatures' (Danceability, Energy, Key, Loudness, Speechiness, Acousticness, Liveness, Valence, Tempo, IdNumber) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (af_py_obj[track][0]['danceability'], af_py_obj[track][0]['energy'], af_py_obj[track][0]['key'], af_py_obj[track][0]['loudness'], af_py_obj[track][0]['speechiness'], af_py_obj[track][0]['acousticness'], af_py_obj[track][0]['liveness'], af_py_obj[track][0]['valence'], af_py_obj[track][0]['tempo'], af_py_obj[track][0]['id']))

	    f.close()

	    conn.commit()
	    conn.close()
	except:
		print("Could not populate audio features table.")


# funciton to get the html for a wikipedia page
# looks in cache for url+params combo and returns that stored html text
# if not in cache, makes new request 
def make_wiki_request_using_cache(artist_name):
	artist_name = artist_name.replace(" ", "_") # encode for URL
	url = "https://en.wikipedia.org/wiki/" + artist_name
	unique_ident = get_unique_key(url)

	# first, look in the cache to see if we already have this data
	if unique_ident in WIKI_CACHE_DICTION:
		return WIKI_CACHE_DICTION[unique_ident]
	else:
		# get data
		resp = requests.get(url)
		WIKI_CACHE_DICTION[unique_ident] = resp.text

		# write to cache
		dumped_json_cache = json.dumps(WIKI_CACHE_DICTION)
		fw = open(WIKI_CACHE_FNAME, "w")
		fw.write(dumped_json_cache)
		fw.close()

		return WIKI_CACHE_DICTION[unique_ident]

# function that scrapes a wikipedia page for an artist and creates a dictionary of info about them
def scrape_wiki(artist_name):

	# first, look in the cache to see if we already have this data
	try:
		f = open(WIKI_RESULTS_CACHE_FNAME, "r")
		cache_contents = f.read()
		WIKI_RESULTS_CACHE_DICTION = json.loads(cache_contents)
		f.close()

		return WIKI_RESULTS_CACHE_DICTION[artist_name]

	# otherwise get new data and write it to cache
	except:

		# get html data and soupify
		html = make_wiki_request_using_cache(artist_name)
		soup = BeautifulSoup(html, features='html.parser')

		# create empty dictionary to populate with artist info
		artist_dict = {}

		# add wikipedia url key and value
		artist_name = artist_name.replace(" ", "_")
		wikiurl = "https://en.wikipedia.org/wiki/" + artist_name
		artist_dict["wiki_url"] = wikiurl

		# add title key and value of wikipedia page if firstHeading idea present
		try:
			title = soup.find(id="firstHeading")
			title = title.text
			artist_dict['title'] = title
		except:
			artist_dict['title'] = "n/a"

		# add website key and value if it is present in the table of info
		try:
			table = soup.find(class_="infobox vcard plainlist")
			rows = table.find_all('tr')

			for row in rows:
				if "Website" in str(row):
					link = str(row).split('href="')
					link = link[1].split('"')
					link = link[0]
					artist_dict['website'] = link
		except:
			artist_dict['website'] = 'n/a'

		# add years active key and value if it is present in the table of info
		try:
			table = soup.find(class_="infobox vcard plainlist")
			rows = table.find_all('tr')

			for row in rows:
				if "Years active" in str(row):
					years = str(row).split('</th><td>')
					years = years[1].split('</td></tr>')
					years = years[0]
					artist_dict['years_active'] = years
		except:
			artist_dict['years_active'] = 'n/a'

		# add one senetence summary key and value using wikipedia package
		try:
			summary = wikipedia.summary(artist_name, sentences=1)
			artist_dict["summary"] = summary
		except:
			artist_dict['summary'] = 'n/a'

		# populate years_active and website keys with null values
		# not sure why this isn't handled by try/except above but it's needed
		if 'years_active' not in list(artist_dict.keys()):
			artist_dict['years_active'] = 'n/a'
		if 'website' not in list(artist_dict.keys()):
			artist_dict['website'] = 'n/a'

		# write to cache
		f = open(WIKI_RESULTS_CACHE_FNAME, "r")
		cache_contents = f.read()
		WIKI_RESULTS_CACHE_DICTION = json.loads(cache_contents)
		f.close()

		WIKI_RESULTS_CACHE_DICTION[artist_name] = artist_dict
		dumped_json_cache = json.dumps(WIKI_RESULTS_CACHE_DICTION)
		fw = open(WIKI_RESULTS_CACHE_FNAME, "w")
		fw.write(dumped_json_cache)
		fw.close()

		return artist_dict

# populate artist table
def populate_artist():
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()

	# open cache of songs
	f = open(SONGS_CACHE_FNAME)
	contents = f.read()
	py_obj = json.loads(contents)

	# get ids of all songs
	songs = get_song_ids()

	# get list of artist names from songs
	artist_names = []
	for id in songs:
		artist_names.append(py_obj[id]['artists'][0]['name'])

	# get wikipedia data and scrape page for each artist
	for artist in artist_names:
		artist_dict = scrape_wiki(artist)
		#print(artist_dict)
		cur.execute("INSERT INTO 'Artists' (Name, YearsActive, Website, WikiURL, Summary) VALUES (?, ?, ?, ?, ?)", (artist, artist_dict['years_active'], artist_dict['website'], artist_dict['wiki_url'], artist_dict['summary']))
	f.close()

	conn.commit()
	conn.close()

def update_songs_foreign_key():
	try:
	    conn = sqlite3.connect(DBNAME)
	    cur = conn.cursor()

	    # open countries file and make it a python object
	    f = open(SONGS_CACHE_FNAME)
	    content = f.read()
	    songs_py_obj = json.loads(content)

	    # populate table and update Artist foreign key columns referencing Artists table
	    for track in list(songs_py_obj.keys()):
	    	name = songs_py_obj[track]['artists'][0]['name']
	    	print(name)
	    	try:
	    		artist_id = cur.execute("SELECT id FROM 'Artists' WHERE Name=?", (name,)).fetchone()[0]
	    		print(artist_id)
	    		statement = "UPDATE Songs SET Artist = ? WHERE Artist = ?"
	    		cur.execute(statement,(artist_id, name))	
	    	except:
	    		continue    	
	    f.close()

	    conn.commit()
	    conn.close()
	except:
		print("Could not update songs table with foreign keys.")

#create_tables()
#populate_songs()
#populate_audio_features()
#populate_artist()
#update_songs_foreign_key()

# set up cache to store aggregate data
AGGREGATES_CACHE_FNAME = 'aggregates.json'

try:
    fobj = open(AGGREGATES_CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    AGGREGATES_CACHE_DICTION = json.loads(cache_contents)
    fobj.close()
except:
    AGGREGATES_CACHE_DICTION = {}

# function that takes a feature as input and collects the # value of that feature for all 500 songs
def get_aggregates(feature):
	if feature in list(AGGREGATES_CACHE_DICTION.keys()):
		return AGGREGATES_CACHE_DICTION[feature]
	else:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
		statement = "SELECT " + feature + " FROM AudioFeatures"
		results = cur.execute(statement)
		results = cur.fetchall()

		agg_lst = []
		for r in results:
			agg_lst.append(float(r[0]))

		AGGREGATES_CACHE_DICTION[feature] = agg_lst
		dumped_json_cache = json.dumps(AGGREGATES_CACHE_DICTION)
		fw = open(AGGREGATES_CACHE_FNAME, "w")
		fw.write(dumped_json_cache)
		fw.close()

		return AGGREGATES_CACHE_DICTION[feature]

#d = get_aggregates('danceability')
#s = get_aggregates('speechiness')
#t = get_aggregates('tempo')
#a = get_aggregates('acousticness')

# gets top 15 artists by song count
def get_top_artists():
	conn = sqlite3.connect(DBNAME)
	cur = conn.cursor()
	statement = "SELECT Artists.Name FROM Artists JOIN Songs ON Artists.Id = Songs.Artist GROUP BY Songs.Artist HAVING COUNT(*) > 1 ORDER BY COUNT (*) DESC LIMIT 15"
	results = cur.execute(statement)
	results = cur.fetchall()

	artists = []
	for r in results:
		artists.append(r[0])
	return artists

# display artist info
def get_artist_info(artist_name):
	artist_dict = scrape_wiki(artist_name)

	info = '''
	Name: {}
	Summary: {}
	Years Active: {}
	Website: {}
	Wikipedia: {}
	'''.format(artist_name, artist_dict['summary'], artist_dict['years_active'], artist_dict['website'], artist_dict['wiki_url'])

	print(info)

# plot histogram for audio features data
def plot(feature):

	x = get_aggregates(feature)
	data = [go.Histogram(x=x)]
	py.plot(data, filename='basic histogram')

# interaction command prompt
def interactive_prompt():
	print("Enter a command or enter 'help' to see options \n")
	help_f = open('help.txt')
	help_text = help_f.read()
	help_f.close()

	# get user response and continue looping
	response = ''
	while response != 'exit':
		response = input('Enter a command: ')

		# break on exit
		if response == 'exit':
			print("Bye")
			break

		# get help text info and loop again
		elif response == 'help':
			print(help_text)
			continue

		# display top artists
		elif response == 'artists':
			print("Your top artists are ...")
			counter = 1
			artists = get_top_artists()
			for artist in artists:
				print(str(counter) + " " + artist)
				counter += 1

		# display info about selected artist
		elif "get info" in response:
			artists = get_top_artists()
			choice = int(response.split()[2])

			artist = artists[choice - 1]
			get_artist_info(artist)

		# plots
		elif "danceability" in response:
			print("Launching your data in plotly...")
			plot("danceability")
		elif "acousticness" in response:
			print("Launching your data in plotly...")
			plot("acousticness")
		elif "tempo" in response:
			print("Launching your data in plotly...")
			plot("tempo")
		elif "speechiness" in response:
			print("Launching your data in plotly...")
			plot("speechiness")
		# error handling
		else:
			print("Command not recognized: " + response)

if __name__=="__main__":
    interactive_prompt()
