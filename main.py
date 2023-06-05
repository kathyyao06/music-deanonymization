from bs4 import BeautifulSoup
import urllib
import pandas as pd
import json
from functools import reduce
import statistics
import os

def getArtists(newSoup):
#outputs a dictionary which includes artist and listeningCount for a single user
    listenedTo = {}
    song = newSoup.find_all('li')
    for s in song:
        songName = s.a.text
        listeningCount = (s.text.split("has been listened to ")[1]).split(" times.")[0]
        listeningCount = int("".join(i for i in listeningCount if i.isdigit()))
        listenedTo[songName] = listeningCount
    return listenedTo

def simFunction(webName, webArtists, lastFmName, lastFmArtists):
#calculates similarity between two people in terms of their listening Count for artists
    allArtists = reduce(lambda x, y: x.union(y.keys()), [webArtists, lastFmArtists], set())
    numerator = 0
    denominator = len(allArtists)
    maxListenCount = max(webArtists.values())
    for artist in allArtists:
        if artist in webArtists and artist in lastFmArtists:
            smallerWeight = min(webArtists[artist], lastFmArtists[artist])
            largerWeight = max(webArtists[artist], lastFmArtists[artist])
            similarity = smallerWeight / largerWeight
            if (largerWeight/maxListenCount) > .8 and similarity >= .90:
                numerator += 1.5
            elif largerWeight <= 20 and similarity >= .5:
                numerator += 1
            elif largerWeight <= 100 and similarity >= .7:
                numerator += 1 
            elif similarity >= .75:
                numerator += 1
    return numerator/denominator

def eccentricity(bestSim, secondBestSim, standardDeviation, e):
#calculates if bestSim is significantly greater than secondBestSim
    if ((bestSim - secondBestSim) / standardDeviation) < e:
        return False
    else:
        return True
            
def main():
    webData = {}
    lastFmData = {}
    matches = {}

    #reads in LastFm data into Pandas dataframe
    #artistsDf = pd.read_table(os.path.join(os.path.dirname(__file__), "../deanonymization/lastfm-data/data.csv"))
    artistsDf = pd.read_table("../deanonymization/lastfm-data/artists.dat", usecols = [0, 1])
    artistsDf.rename(columns = {"id" : "artistID", "name" : "artistName"}, inplace = True)
    userArtistsDf = pd.read_table("../deanonymization/lastfm-data/user_artists.dat")
    lastFmDf = userArtistsDf.merge(artistsDf, how = 'left', on = 'artistID')

    #converts lastFm data from dataframe to dictionary
    curID = 2
    for index, row in lastFmDf.iterrows():
        curUser = row['userID']
        if curUser in lastFmData.keys():
            lastFmData[curUser][row['artistName']] = row['weight']
        else:
            lastFmData[curUser] = {row['artistName']: row['weight']}

    #initiative webscraper to url
    url = "https://aifairness.tech/"
    req = urllib.request.urlopen(url)
    soup = BeautifulSoup(req, "lxml")

    #finds all names on the website
    names = soup.find_all('li')
    allNames = []
    for name in names:
        allNames.append(name.a.text)
    
    #creates a dictionary for the website that includes all users and their listening activity
    for name in allNames:
        newReq = urllib.request.urlopen(url + name + ".html")
        newSoup = BeautifulSoup(newReq, "lxml")
        webData[name] = getArtists(newSoup)
    
    maxsim = 0
    secondMaxSim = 0
    bestUser = None
    allSims = []
    ecc = True
    #loops through every user in webData with every user in lastFmData, calculating similarity
    #score and seeing if there is a match
    for webName, webArtists in webData.items():
        for lastFmName, lastFmArtists in lastFmData.items():
            val = simFunction(webName, webArtists, lastFmName, lastFmArtists)
            allSims.append(val)
            if val > maxsim:
                secondMaxSim = maxsim
                maxsim = val                
                bestUser = lastFmName   
        standardDeviation = statistics.stdev(allSims)
        if standardDeviation > 0:
            ecc = eccentricity(maxsim, secondMaxSim, standardDeviation, 5)   
        if maxsim > .7 and ecc:
            matches[webName] = bestUser
        maxsim = 0
        bestUser = None
        secondMaxSim = 0
        allSims = []

    #outputs matches to json file
    jsonString = json.dumps(matches, indent = 4)
    jsonFile = open("matches.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()
  
if __name__== "__main__":
    main()

