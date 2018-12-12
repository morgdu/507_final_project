import unittest
from final_proj import *

class TestDatabase(unittest.TestCase):

    def test_song_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT TrackName from Songs'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Candid',), result_list) # checks that one of my most recent saved songs is included
        self.assertEqual(len(result_list), 500) # checks that 500 songs were fetched

        sql = '''
            SELECT TrackName from Songs where Popularity > 90
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 3) # checks that there are 3 songs with popularity score > 90
        self.assertEqual(result_list[0][0], 'Happier') # checks that Happier is the first result

        conn.close()

    def test_audio_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT IdNumber FROM AudioFeatures WHERE Tempo > 100
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('0mgtiiVldf7Owx7p4MinC2',), result_list) # checks that a song is present in the results
        self.assertEqual(len(result_list), 373)  # checks that selects correct number based on criteria

        sql = '''
            SELECT COUNT(*)
            FROM AudioFeatures
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count == 500) # checks that there are 500 records for audio features

        conn.close()

    def test_artists_table(self):  
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Distinct Name FROM Artists
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('The 1975',), result_list) # checks that an artist is present in the results
        self.assertEqual(len(result_list), 294)  # checks that selects correct number based on criteria

        sql = '''
            SELECT COUNT(*)
            FROM Artists
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count == 500) # checks that there are 500 records for artists

class TestAggregates(unittest.TestCase):

    def test_aggregates(self):
        results = get_aggregates('danceability')
        self.assertEqual(len(results), 500)

        results = get_aggregates('tempo')
        self.assertEqual(len(results), 500)

        results = get_aggregates('speechiness')
        self.assertEqual(len(results), 500)

        results = get_aggregates('acousticness')
        self.assertEqual(len(results), 500)

class TestMapping(unittest.TestCase):

    # we can't test to see if the maps are correct, but we can test that
    # the functions don't return an error!
    def test_show_state_map(self):
        try:
            plot('danceability')
            plot('acousticness')
            plot('tempo')
            plot('speechiness')
        except:
            self.fail()


unittest.main()