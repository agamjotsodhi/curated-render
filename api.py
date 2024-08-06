"""  API.py
    
    - all API functions to get and post data from the Chicago Art Institue API
    - imports SQL table models from models.py, 
    - sets up functions that will be used in app.py """
    
# Imports:
import requests
from models import Artwork, Type, db

#Chicago Art Institute API Base URL:
API_URL = "https://api.artic.edu/api/v1/artworks"



def get_artwork_by_ids(artwork_ids):
    """Fetch detailed info for multiple artworks by their IDs and save to the database."""
    params = {
        'ids': ','.join(map(str, artwork_ids)),
        'fields': 'id,title,alt_titles,artist_display,date_start,date_end,date_display,place_of_origin,classification_titles,edition,color,dimensions,description,image_id,artwork_type_title,api_link,medium_display'
    }
    response = requests.get(API_URL, params=params)
    if response.status_code != 200:
        print(f"API request failed, status code {response.status_code}")
        return []
    data = response.json().get('data', [])
    for artwork_data in data:
        Artwork.add_new_artwork(artwork_data)
    return data


def fetch_artworks_batches(start_id, end_id, batch_size):
    """Fetch artworks in batches and save to the database."""
    all_artworks = []
    for i in range(start_id, end_id, batch_size):
        batch_ids = range(i, min(i + batch_size, end_id))
        artworks = get_artwork_by_ids(batch_ids)
        all_artworks.extend(artworks)
    return all_artworks


def fetch_artworks_by_query(query=None, theme=None):
    """Fetch artworks by search query and save to the database."""
    params = {
        'fields': 'id,title,alt_titles,artist_display,date_start,date_end,date_display,place_of_origin,classification_titles,edition,color,dimensions,description,image_id,artwork_type_title,api_link,medium_display',
        'limit': 100
    }
    if query:
        params['q'] = query
   
    response = requests.get(f"{API_URL}/search", params=params)
    if response.status_code != 200:
        print(f"API request failed with status code: {response.status_code}")
        return []
    data = response.json()
    artworks = data.get('data', [])
    if not artworks:
        print("No artworks found for the given query.")
        return []
    for artwork_data in artworks:
        Artwork.add_new_artwork(artwork_data)
    return artworks