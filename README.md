507_final_project
Morgan Durow (mdurow)

# Data sources used: Spotify API (OAuth) and Wikipedia (web scraping)
  I used my own personal Spotify data and had to authorize its use. <br>
  See https://developer.spotify.com/documentation/general/guides/authorization-guide/ for details.<br>
  
  For my second data source, I scraped pages of Wikipedia to get basic article information

# Other info:
  Requires username, key, and credentials to access user's Spotify data
  Requires username, key to use plotly to display graphics https://plot.ly/python/getting-started/
  See requirements.txt for full list of necessary modules

# Brief description:
  My code is structured into a main python program final_proj.py and a unittest program final_proj_test.py
  
  Parts of the main python program include:
  1) getting and caching the user's Spotify song data
  2) creating a database and populating tables within
  3) data processing and interactive command interface
  
  Significant data processing functions are:
  
  get_songs_ids():
    This function loops through the results of the request and collects the unique ids of each song (total 500)
    These will be later used to search for audio features for that specific song id
  
  get_aggregates(feature)
    This function aggregates data across all 500 songs for the feature input as a parameter
    The data returned is then later used in plotly to graph features of my music
  
  get_top_artists()
    This function queries the database and selects the artists that I have the most songs by

# class definition
  class Song(): accepts API dictionary result and assigns instance variables for track name, id, artist, duration, popularity

# User Guide:
  1. run python3 final_proj.py in terminal
  2. The program will ask you to authorize use of your Spotify data if you have not already
  3. It collects 500 most recently saved songs and gets audio features for each as well as scrapes Wikipedia for artist info
  4. Populates database - with empty cache, this can take ~5 minutes
  5. run user interface
  
  An interactiove user interface will appear
    - enter 'help' to see list of command options
    - enter 'exit' to quit the program
    - enter 'artists' to get your top 15 artists
    - enter 'get info <#>' to get more information about selected artist
    - enter 'plot <feature>' to launch a plotly histogram of frequency of that audio feature in browser
      options: danceability, acoustiness, tempo, speechiness
 
  6. run python3 final_proj_test.py in terminal to test program
