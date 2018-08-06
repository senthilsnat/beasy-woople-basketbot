#!/usr/bin/env python
# -*- coding: utf-8 -*-
# install and include python-Levenshtein
import fuzzywuzzy.fuzz as fuzz
import tweepy
import time as timer
from datetime import datetime, timedelta


####################################
# Initialize Authentication Tokens
####################################
consumer_key = '[insert your key here]'
consumer_secret = '[insert your token here]'
access_token = '[insert your key here]'
access_token_secret = '[insert your token here]'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


###########
# Helpers
###########
# A probably non-comprehensive mapping of team and city nicknames to official city names
teams_map = {"Hawks": "Atlanta", "Celtics": "Boston", "Nets": "Brooklyn", "Hornets": "Charlotte", "Bulls": "Chicago",
             "Cavaliers": "Cleveland", "Mavericks": "Dallas", "Nuggets": "Denver", "Pistons": "Detroit",
             "Warriors": "Golden State", "Rockets": "Houston", "Pacers": "Indiana", "Clippers": "Los Angeles",
             "Lakers": "Los Angeles", "Grizzlies": "Memphis", "Heat": "Miami", "Bucks": "Milwaukee",
             "Timberwolves": "Minnesota", "Pelicans": "New Orleans", "Knicks": "New York", "Thunder": "Oklahoma City",
             "OKC": "Oklahoma City", "Magic": "Orlando", "LA": "Los Angeles", "76ers": "Philadelphia",
             "Suns": "Phoenix", "Trailblazers": "Portland", "Trail blazers": "Portland", "Trail Blazers": "Portland",
             "Blazers": "Portland", "NOLA": "New Orleans", "Kings": "Sacramento", "Spurs": "San Antonio",
             "SA": "San Antonio", "Raptors": "Toronto", "Raps": "Toronto", "Jazz": "Utah", "Wizards": "Washington",
             "Wiz": "Washington", "Clips": "Los Angeles", "ATL": "Atlanta", "BOS": "Boston", "BKN": "Brooklyn",
             "CHA": "Charlotte", "CHO": "Charlotte", "CHI": "Chicago", "CLE": "Cleveland", "DAL": "Dallas",
             "DEN": "Denver", "DET": "Detroit", "GSW": "Golden State", "HOU": "Houston", "IND": "Indiana",
             "LAC": "Los Angeles", "LAL": "Los Angeles", "MEM": "Memphis", "MIA": "Miami", "MIL": "Milwaukee",
             "MIN": "Minnesota", "NOP": "New Orleans", "NO": "New Orleans", "NY": "New York", "NYK": "New York",
             "ORL": "Orlando", "PHI": "Philadelphia", "PHO": "Phoenix", "PHX": "Phoenix", "POR": "Portland",
             "PDX": "Portland", "SAC": "Sacramento", "TOR": "Toronto", "UTA": "Utah", "WAS": "Washington",
             "Sixers": "Philadelphia", "Philly": "Philadelphia"}

# Specify duration/refresh interval to check back on
d = datetime.today() - timedelta(hours=3)


####################################
# Shams-Woj Similarity Competition
####################################
# Helper function for stripping artificially similar language
def content_stripper(s):
    # Permutations of "league sources say..."
    if "League sources tell" in s:
        s = s.replace("League sources tell", "")
    if "league sources tell" in s:
        s = s.replace("league sources tell", "")
    if "League source tells" in s:
        s = s.replace("League source tells", "")
    if "league source tells" in s:
        s = s.replace("league source tells", "")
    if "league sources said" in s:
        s = s.replace("league sources said", "")
    if "sources: " in s:
        s = s.replace("sources: ", " ")
    if "Sources: " in s:
        s = s.replace("Sources: ", " ")
    if "sources" in s:
        s = s.replace("sources", "")
    if "Sources" in s:
        s = s.replace("Sources", "")

    # Permutations of certain deal type parameters
    if "free agent" in s:
        s = s.replace("free agent", "")
    if "Free agent" in s:
        s = s.replace("Free agent", "")
    if "trade" in s:
        s = s.replace("trade", "")
    if "agreed" in s:
        s = s.replace("agreed", "")
    if "deal" in s:
        s = s.replace("deal", "")

    return s


# Primary function for comparing Shams to Woj... Who will come out on top?
def shamwoj():
    # Aggregate all Woj tweets within last duration, but only if they're news hits
    woj_tweets = []
    for status in tweepy.Cursor(api.user_timeline, id="wojespn", tweet_mode="extended").items(100):
        if ("source" in status.full_text) or ("sources" in status.full_text) or ("Source" in status.full_text) or ("Sources" in status.full_text):
            if status.created_at >= d:
                woj_tweets.append(status)

    # Aggregate all Shams tweets within last duration, but only if they're news hits
    sham_tweets = []
    for status in tweepy.Cursor(api.user_timeline, id="ShamsCharania", tweet_mode="extended").items(100):
        if ("source" in status.full_text) or ("sources" in status.full_text) or ("Source" in status.full_text) or ("Sources" in status.full_text):
            if status.created_at >= d:
                sham_tweets.append(status)

    # Iterate through Shams/Woj tweets to find similar tweets
    for ss in sham_tweets:
        for ww in woj_tweets:
            # Get the content out of the tweet objects
            s = ss.full_text
            w = ww.full_text

            # remove punctuation that connects two words directly
            s = s.replace("-", " ")
            s = s.replace("/", " ")
            s = s.replace(".", " ")
            s = s.replace(",", " ")
            w = w.replace("-", " ")
            w = w.replace("/", " ")
            w = w.replace(".", " ")
            w = w.replace(",", " ")

            # standardize team names to cities
            for word in s.split(' '):
                if word in teams_map:
                    s = s.replace(word, teams_map[word])
            for word in w.split(' '):
                if word in teams_map:
                    w = w.replace(word, teams_map[word])

            # Clean the tweets by stripping out artificially similar language
            s = content_stripper(s)
            w = content_stripper(w)

            # Get similarity scores and establish similar tweets
            simtoken = 0
            if fuzz.token_set_ratio(s, w) > 50:
                # Similarity established beyond reproach
                if fuzz.token_set_ratio(s, w) >= 66:
                    simtoken = 1

                # If similarity score isn't high enough, check the proper nouns in the tweets
                elif fuzz.token_set_ratio(s, w) < 66:
                    # Initialize objects for keeping track of proper noun overlap
                    wupp = []
                    supp = []
                    strue = 1
                    wtrue = 1

                    # Insert all proper nouns into their respective lists
                    for www in w.split(' '):
                        if (www != 'ESPN') and (www != ''):
                            if www[0].isupper():
                                wupp.append(www)
                    for sss in s.split(' '):
                        if (sss != 'Yahoo') and (sss != ''):
                            if sss[0].isupper():
                                supp.append(sss)

                    # Once one of the proper nouns are not in the opposite list, no more overlap
                    for sss in supp:
                        if sss not in wupp:
                            strue = 0
                    for www in wupp:
                        if www not in supp:
                            wtrue = 0

                    # If there is a perfect subset, then similarity works
                    if (strue == 1) or (wtrue == 1):
                        simtoken = 1

            # If there is a similarity between the tweets found...
            if simtoken == 1:
                # Debug statements
                print "-s-", s
                print "+w+", w

                # Wrap final functionality into exception handler
                try:
                    # Shams got it first
                    if ss.created_at < ww.created_at:
                        diff = (ww.created_at - ss.created_at).total_seconds()

                        # A fairly non-elegant scorekeeper method
                        with open("shamwoj_tracker.txt", 'r') as myFile:
                            dataLines = myFile.readlines()
                        tracks = dataLines[0].split(' || ')
                        shamscore = float(tracks[0].split(',')[0])
                        wojscore = float(tracks[0].split(',')[1])
                        margin = float(tracks[1])
                        battles = float(tracks[2])

                        # Update the scorekeeper
                        shamscore += 1
                        margin += diff
                        battles += 1
                        with open("shamwoj_tracker.txt", 'w') as myFile:
                            myFile.write(str(shamscore) + "," + str(wojscore) + " || " + str(margin) + " || " + str(battles))

                        api.update_status("Shams got it first by " + str(int(diff)) + " seconds. \n" +
                                          "Scoreboard: Shams " + str(int(shamscore)) + " | Woj " + str(int(wojscore)) +
                                          "\n" + "Avg Margin: " + str(abs(int(margin/battles))) + " seconds" + "\n" +
                                          " https://twitter.com/ShamsCharania/status/" + str(ss.id))
                    # Woj got it first
                    elif ss.created_at > ww.created_at:
                        diff = (ss.created_at - ww.created_at).total_seconds()

                        # A fairly non-elegant scorekeeper method
                        with open("shamwoj_tracker.txt", 'r') as myFile:
                            dataLines = myFile.readlines()
                        tracks = dataLines[0].split(' || ')
                        shamscore = float(tracks[0].split(',')[0])
                        wojscore = float(tracks[0].split(',')[1])
                        margin = float(tracks[1])
                        battles = float(tracks[2])

                        # Update the scorekeeper
                        wojscore += 1
                        margin -= diff
                        battles += 1
                        with open("shamwoj_tracker.txt", 'w') as myFile:
                            myFile.write(str(shamscore) + "," + str(wojscore) + " || " + str(margin) + " || " + str(battles))

                        api.update_status("Woj got it first by " + str(int(diff)) + " seconds. \n" +
                                          "Scoreboard: Shams " + str(int(shamscore)) + " | Woj " + str(int(wojscore)) +
                                          "\n" + "Avg Margin: " + str(abs(int(margin/battles))) + " seconds" + "\n" +
                                          " https://twitter.com/wojespn/status/" + str(ww.id))

                    # They tied - what the hell
                    elif ss.created_at == ww.created_at:
                        api.update_status("By god, it's like they're the same person - a tie! \n" +
                                          " https://twitter.com/ShamsCharania/status/" + str(ss.id))

                    # Remove the tweet from the lists so we don't recheck them
                    sham_tweets.remove(ss)
                    woj_tweets.remove(ww)

                # Use exception handler to not re-post tweets or matches
                except tweepy.TweepError:
                    # Remove the tweets still, this just means we've already posted about them
                    sham_tweets.remove(ss)
                    woj_tweets.remove(ww)
                    pass


####################
# Execution block
####################
c = 0
while True:
    # functions to run
    shamwoj()

    # testers for now, will remove after a beta deploy period
    # c += 1
    # api.update_status("TESTING HEROKU" + str(c))
    
    # wake up to potentially tweet only once every 3 hours
    timer.sleep(10800)
