507_final_project
Morgan Durow (mdurow)

# Data sources used: Spotify API (OAuth) and Wikipedia (web scraping)
  I used my own personal Spotify data and had to authorize its use. <br>
  See https://developer.spotify.com/documentation/general/guides/authorization-guide/ for details.<br>
  
  For my second data source, I scraped pages of Wikipedia to get basic article information

# Other info:
  Requires username, key, and credentials to access user's Spotify data<br>
  Requires username, key to use plotly to display graphics https://plot.ly/python/getting-started/<br>
  See requirements.txt for full list of necessary modules<br>

# Brief description:
  My code is structured into a main python program final_proj.py and a unittest program final_proj_test.py<br>
  
  Parts of the main python program include:<br>
  1) getting and caching the user's Spotify song data<br>
  2) creating a database and populating tables within<br>
  3) data processing and interactive command interface<br>
  
  Significant data processing functions are:<br>
  
  get_songs_ids()<br>
    This function loops through the results of the request and collects the unique ids of each song (total 500)<br>
    These will be later used to search for audio features for that specific song id<br>
  
  get_aggregates(feature)<br>
    This function aggregates data across all 500 songs for the feature input as a parameter<br>
    The data returned is then later used in plotly to graph features of my music<br>
  
  get_top_artists()<br>
    This function queries the database and selects the artists that I have the most songs by<br>

# class definition
  class Song(): accepts API dictionary result and assigns instance variables for track name, id, artist, duration, popularity

# User Guide:
  1. run python3 final_proj.py in terminal<br>
  2. The program will ask you to authorize use of your Spotify data if you have not already<br>
  3. It collects 500 most recently saved songs and gets audio features for each as well as scrapes Wikipedia for artist info<br>
  4. Populates database - with empty cache, this can take ~5 minutes<br>
  5. run user interface<br>
  
  An interactiove user interface will appear<br>
    - enter 'help' to see list of command options<br>
    - enter 'exit' to quit the program<br>
    - enter 'artists' to get your top 15 artists<br>
    - enter 'get info <#>' to get more information about selected artist<br>
    - enter 'plot <feature>' to launch a plotly histogram of frequency of that audio feature in browser<br>
      options: danceability, acoustiness, tempo, speechiness<br>
 
  6. run python3 final_proj_test.py in terminal to test program<br>
