import os
import spotipy
import spotipy.util as util
from dotenv import load_dotenv

load_dotenv()

def spotipy_login():
    SPOTIFY_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_USERNAME = os.environ.get('SPOTIFY_USER')
    scope = 'playlist-modify-private, user-read-recently-played, playlist-modify-public, playlist-read-private, user-follow-read, user-read-private'
    token = util.prompt_for_user_token(username=SPOTIFY_USERNAME, scope=scope, client_id=SPOTIFY_ID,
                                       client_secret=SPOTIFY_SECRET, redirect_uri='http://whatagoodbot.com/test-callback')
    sp = spotipy.Spotify(auth=token, requests_timeout=10, retries=10)
    return sp

def getGenre(trackId):
    sp = spotipy_login()
    spotifyTrack = sp.track(trackId)
    return sp.artist(spotifyTrack['artists'][0]['uri'])

def getAvailableMarkets(trackId):
    sp = spotipy_login()
    spotifyTrack = sp.track(trackId)
    return spotifyTrack['available_markets']

# Below need to be connected up to work
def spin_track(ws ,room_details, bot):
    '''
    Plays a song from room_details['playlist'].
    If the playlist is empty, it takes the last 5 songs from the rooms history
    and uses them as seeds for recommendations from spotify.
    '''
    get_next_track = '''42["getNextTrack",{"roomId":"59efa6f39c05e3009e4da397","user":{"username":"-doopbot-","id":"doopbot","_id":"doopbot","uri":"spotify:user:doopbotwhaaa","image":"https://jqbx.s3.amazonaws.com/hantyumi-1611935649567.jpg","thumbsUpImage":"https://jqbx.s3.amazonaws.com/hantyumi-1611935649567.jpg","thumbsDownImage":"https://jqbx.s3.amazonaws.com/doopfuckedupbigtime13-1556310031703.gif","djImage":"https://jqbx.s3.amazonaws.com/Pizzagif-1610135519252.webp","device":"desktop","status":"active","country":"US","socketId":"FCpv7sEI5uLRJ6V-AB-T"}}]'''
    get_next_track = json.loads(get_next_track[2:])
    get_next_track[1]['roomId'] = bot['roomId']
    get_next_track[1]['user'] = bot['user']
    sp = spotipy_login()
    if room_details['quick_themes'] == True:
        track = sp.track('spotify:track:5nKe9PgCtEhqdnvXAQIBhF')
        get_next_track[1]['track'] = reduce_track(track)
        ws.send(f'42{json.dumps(get_next_track)}')
        return room_details
    print(f"the playlist is {room_details['playlist']}")
    if len(room_details['playlist']) == 0:
        seed_tracks = [i['uri'] for i in room_details['tracks'][-5:]]
        print('the seed tracks are:')
        print(seed_tracks)
        recommendations = sp.recommendations(seed_tracks=seed_tracks)
        playlist_uris = [i['uri'] for i in recommendations['tracks']]
        room_details['playlist'] = playlist_uris[:5]
        print(room_details['playlist'])
    track_uri = room_details['playlist'].pop()
    track = sp.track(track_uri)
    get_next_track[1]['track'] = reduce_track(track)
    ws.send(f'42{json.dumps(get_next_track)}')
    return room_details

def doopbot_spotify_login():
    print('attempting to login')
    SPOTIFY_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_USERNAME = os.environ.get('SPOTIFY_USER')
    print(SPOTIFY_ID)
    print(SPOTIFY_SECRET)
    print(SPOTIFY_USERNAME)
    scope = 'playlist-modify-private, user-read-recently-played, playlist-modify-public, playlist-read-private, user-follow-read, user-read-private'
    token = util.prompt_for_user_token(username=SPOTIFY_USERNAME, scope=scope, client_id=SPOTIFY_ID,
                                       client_secret=SPOTIFY_SECRET, redirect_uri="http://localhost:8080/callback")
    #spotipy will create a .cache-username file.
    #If you need to do the spotify redirect thing again to use a new user, delete that file beforehand.
    sp = spotipy.Spotify(auth=token)
    return sp

def theme_playlist_dictionary():
    '''
    returns a dictionary of themes and their corresponding playlist. Adds new playlists if new themes are discovered.
    '''
    with open(r'quick_themes_playlists.yml') as file:
        theme_playlists = yaml.load(file, Loader=yaml.FullLoader)
    with open('qt_themes') as file:
        qt_themes = file.readlines()
    themes = qt_themes
    format_themes = [i.lower().rstrip() for i in themes]
    sp = doopbot_spotify_login()
    for i in format_themes:
        if not theme_playlists.get(i):
            print(f'Adding {i} theme playlist')
            playlist = sp.user_playlist_create('9lmdbr25slw401t2mmq86y2sd', i, public=True, collaborative=False, description='')
            #playlist['external_urls']['spotify']
            theme_playlists[i] = {'uri': playlist['uri'], 'link': playlist['external_urls']['spotify']}
    write_playlists_config(theme_playlists)
    return theme_playlists

def create_theme_playlist(room_details, title):
    print('trying to build playlists')
    print('trying to build playlists')
    print('trying to build playlists')
    print('trying to build playlists')
    print('trying to build playlists')
    title = title.lower().strip()
    format_theme = title.lower().strip()
    sp = doopbot_spotify_login()
    print(f'Adding {format_theme} theme playlist')
    playlist = sp.user_playlist_create('9lmdbr25slw401t2mmq86y2sd', title, public=True, collaborative=False, description='')
    room_details['qt_playlists'][format_theme] = {'uri': playlist['uri'], 'link': playlist['external_urls']['spotify']}
    write_playlists_config(room_details['qt_playlists'])

def quick_themes_add(room_details):
    ''' Adds the track to the correct theme playlist'''
    sp = doopbot_spotify_login() #doopbots account has the mass of theme playlists..
    theme = room_details['theme'].lower().strip()
    playlist = room_details['qt_playlists'].get(theme)
    track = room_details['nextTrack']['uri']
    if playlist != None:
        sp.user_playlist_add_tracks('9lmdbr25slw401t2mmq86y2sd', playlist['uri'], [track], position=0)
    else:
        print('cannot find that playlist')

def build_spotify_playlist(track):
    sp = spotipy_login()

    if track['stars'] >= 2 and track['room'] == '59efa6f39c05e3009e4da397':
        #add track to pizza/beer >2 star playlist
        sp.user_playlist_add_tracks('boncora', 'spotify:playlist:4sXChbEoPWTiyKf0lOLPj2', [track['uri']], position=0)

    if track['stars'] >= 3 and track['room'] == '59efa6f39c05e3009e4da397':
        #add track to pizza/beer >3 star playlist
        sp.user_playlist_add_tracks('boncora', 'spotify:playlist:5c8SYbTytW5Ly9OJX4Oxkc', [track['uri']], position=0)

    if track['userUri'] == 'spotify:user:keithkenez':
        #CPAs the coolest! Save those spins!
        sp.user_playlist_add_tracks('boncora', 'spotify:playlist:6taMJihC5mqEFTmL46jUxz', [track['uri']], position=0)
