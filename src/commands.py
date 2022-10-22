import json
from spotify import getAvailableMarkets, getGenre, getRecommendations, addToPlaylist


def diffMap(diff):
    return diff['name']


def relink(payload):
    availableMarkets = getAvailableMarkets(payload['nowPlaying']['id'])
    if len(availableMarkets) == 0:
        print('No Info')
    else:
        with open('src/config/spotifyMarkets.json') as marketsFile:
            spotifyMarkets = json.load(marketsFile)

        filteredMarkets = [spotifyMarket for spotifyMarket in spotifyMarkets if spotifyMarket['include']]
        differences = [filteredMarket for filteredMarket in filteredMarkets if filteredMarket['code'] not in availableMarkets]
        if len(differences):
            if len(differences) > len(availableMarkets):
                differencesPositive = [filteredMarket for filteredMarket in filteredMarkets
                                       if filteredMarket['code'] in availableMarkets]
                marketString = ', '.join(list(map(diffMap, differencesPositive)))
                payload['message'] = f"This song is only available in {marketString}"
            else:
                marketString = ', '.join(list(map(diffMap, differences)))
                payload['message'] = f"This song isn't available in {marketString}"
        else:
            payload['message'] = "This song should be available for everyone in the room."
        return payload


def genre(payload):
    artistInfo = getGenre(payload['nowPlaying']['id'])
    payload['message'] = f"Spotify describes {artistInfo['name']} as {', '.join(artistInfo['genres'])}"
    return payload

def getPlaylist(seed_tracks):
    recommendations = getRecommendations(seed_tracks)
    return recommendations['tracks']


def addTrackToPlaylist(payload):
    if payload['reaction'] == 'star':
        if payload['nowPlaying']['provider'] == 'spotify':
            if payload['room']['spotify']:
                if payload['room']['spotify']['enabled'] and payload['room']['spotify']['starredPlaylist']:
                    addToPlaylist(payload['room']['spotify']['starredPlaylist'], payload['nowPlaying']['id'])
