507_final_project
Morgan Durow (mdurow)

Data sources used: Spotify API (OAuth) and Wikipedia (web scraping)
  I used my own personal Spotify data and had to authorize its use. 
  See https://developer.spotify.com/documentation/general/guides/authorization-guide/ for details.
  
  For my second data source, I scraped pages of Wikipedia to get basic article information

Other info:
  My program requires secret key and credentials to access user's Spotify data
  It uses plotly to display graphics https://plot.ly/python/getting-started/

Brief description:
  My code is organized into three main areas:
  1) getting and caching the user's Spotify song data
  2) creating a database and populating tables within
  3) data processing and interactive command interface
  
  Two significant data processing functions are:
  
  get_aggregates(feature)
    This function aggregates data across all 500 songs for the feature input as a parameter
    The data returned is then later used in plotly to graph features of my music
  
  get_top_artists()
    This function queries the database and selects the artists that I have the most songs by



Brief description of how your code is structured, including the names of significant data processing functions (just the 2-3 most important functions--not a complete list) and class definitions. If there are large data structures (e.g., lists, dictionaries) that you create to organize your data for presentation, briefly describe them.

User Guide:
  run python3 final_proj.py in terminal
  The program will ask you to authorize use of your Spotify data if you have not already
  It collects your 500 most recently saved songs and gets the audio features for each as well as scrapes Wikipedia for artist   info
  
  An interaction user interface will appear
    - enter 'help' to see list of command options
    - enter 'exit' to quit the program
    - enter 'artists' to get your top 15 artists
    - enter 'get info <#>' to get more information about selected artist
    - enter 'plot <feature>' to launch a plotly histogram of that audio feature
      options: danceability, acoustiness, tempo, speechiness
