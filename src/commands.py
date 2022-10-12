import json
from spotify import getAvailableMarkets, getGenre

def diffMap(diff):
  return diff['name']

def relink(trackId, meta):
  availableMarkets = getAvailableMarkets(trackId)
  if len(availableMarkets) == 0:
    print('No Info')
  else:
    with open('src/config/spotifyMarkets.json') as marketsFile:
      spotifyMarkets = json.load(marketsFile)

    filteredMarkets = [spotifyMarket for spotifyMarket in spotifyMarkets if spotifyMarket['include']]
    differences = [filteredMarket for filteredMarket in filteredMarkets if filteredMarket['code'] not in availableMarkets]
    if len(differences):
      if len(differences) > len(availableMarkets):
        differencesPositive = [filteredMarket for filteredMarket in filteredMarkets if filteredMarket['code'] in availableMarkets]
        marketString = ', '.join(list(map(diffMap, differencesPositive)))
        return  { 'response': { 'message': f'This song is only available in {marketString}' }, 'meta': meta }
      else:
        marketString = ', '.join(list(map(diffMap, differences)))
        return  { 'response': { 'message': f'This song isn\'t available in {marketString}' }, 'meta': meta }
    else:
        return  { 'response': { 'message': 'This song should be available for everyone in the room.' }, 'meta': meta }

def genre(trackId, meta):
  artistInfo = getGenre(trackId)
  return  { 'response': { 'message': f"Spotify describes {artistInfo['name']} as {', '.join(artistInfo['genres'])}" }, 'meta': meta }
