import argparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
import pandas as pd
import json
from datetime import date
from tqdm import tqdm
import math

"""
SAMPLE USAGE:

python retrieve_user_data.py -p parameters.json
"""

def get_parameters(fname: str) -> dict:
    """
    Retrieve parameters from the JSON file

    Args:
        fname (str): filepath containing parameters

    Returns:
        dict: dictionary containing parameters
    """
    with open(fname, 'r') as j:
        param = json.loads(j.read())

    return param

def get_library() -> pd.DataFrame:
    """
    Pulls song ids and added on dates from user's liked songs
    
    Returns:
        pd.DataFrame: dataframe of user's liked songs
    """    
    
    userlib = {'added_on': [], 'id': []}

    # User saved tracks has 50 song limit per call
    for offset in tqdm(range(0, 100000, 50), desc = "Pulling songs from library", total = math.ceil(5000/50)):
                
        results = sp.current_user_saved_tracks(limit = 50, offset = offset)

        if len(results['items'])==0:
            break
        else:
            userlib['added_on'].extend(x['added_at'] for x in results['items'])
            tracks = [x['track'] for x in results['items']]
            userlib['id'].extend(x['id'] for x in tracks)

    libdf = pd.DataFrame(userlib)

    return libdf

def get_track_info(ids: iter) -> pd.DataFrame:
    """
    Pulls track info (e.g. artist, song name, album) for a set of ids

    Args:
        ids (iter): song ids

    Returns:
        pd.DataFrame: dataframe containing track info
    """
    trackdf = pd.DataFrame()

    # Tracks function has 50 song limit per call
    for i in tqdm(range(0, len(ids), 50), desc = "Pulling track info", total = math.ceil(len(ids)/50)):
        track_info = sp.tracks(ids[i:i+50])
        trackdf = pd.concat([trackdf, pd.json_normalize(track_info, record_path = ['tracks'])])
    
    # Parse artist fields
    artdf = pd.DataFrame()

    for idx, row in trackdf.iterrows():
        mydict = {key: [artist[key] for artist in row.artists] for key in row.artists[0].keys()}
        tmpdf = pd.json_normalize(mydict)
        tmpdf = tmpdf.rename(columns = {'external_urls':'artist.external_urls', 
                            'href': 'artist.href', 
                            'name': 'artist.name', 
                            'type': 'artist.type', 
                            'uri':'artist.uri'})
        tmpdf['id'] = row.id
        artdf = pd.concat([artdf,tmpdf])

    # Merge artists back in with track info
    trackdf = pd.merge(trackdf, artdf, on='id')

    return trackdf

def get_track_features(ids: iter) -> pd.DataFrame:
    """
    Pulls track features (e.g. loudness) for a set of ids

    Args:
        ids (iter): song ids

    Returns:
        pd.DataFrame: dataframe containing track features
    """
    featdf = pd.DataFrame()

    # Features function has 100 song limit per call
    for i in tqdm(range(0, len(ids), 100), desc = "Pulling track features", total = math.ceil(len(ids)/100)):
        audio_feat = sp.audio_features(ids[i:i+100])
        
        if None in audio_feat:
            idx = [j for j,v in enumerate(audio_feat) if v!=None]
            featdf = pd.concat([featdf, pd.json_normalize([audio_feat[k] for k in idx])])
        else:
            featdf = pd.concat([featdf, pd.json_normalize(audio_feat)])

    return featdf

if __name__== '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--params', help='JSON filepath containing parameters', type=str, required=True, default='parameters.json')
    args = parser.parse_args()

    # Retrieve parameters, set up connection
    param = get_parameters(args.params)
    token = util.prompt_for_user_token(**param)
    sp = spotipy.Spotify(auth=token)

    # Retrieve saved songs for user
    libdf = get_library()

    # Retrieve track details
    trackdf = get_track_info(libdf['id'])
    outdf = pd.merge(libdf, trackdf, on = 'id')

    # Retrieve track features
    featdf = get_track_features(libdf['id'])
    outdf = pd.merge(outdf, featdf, on = 'id')
    outdf.drop(columns=['type_y', 'uri_y'], inplace = True)
    outdf.rename(columns={"type_x": "type", "uri_x": "uri"}, inplace = True)

    # Save to csv for posterity
    today = date.today().strftime('%Y-%m-%d')
    outdf.to_csv(f'{param["username"]}_{today}.csv', index = False)
    print(f'Saved {outdf.shape[0]} songs from {param["username"]}\'s library.')
    

