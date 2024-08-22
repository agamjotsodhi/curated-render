"""  API.py
    
    - all API call functions helper functions to get and post data from the Chicago Art Institue API
    - imports SQL table models from models.py, 
    - sets up functions that will be used in app.py """
    
# Imports:
import requests
from models import Artwork, Type, db, Favorite
from sqlalchemy.sql import func

#Chicago Art Institute API Base URL:
API_URL = "https://api.artic.edu/api/v1/artworks"


""" 
    get_artwork_by_ids:
    Fetch detailed information for multiple artworks by their IDs from the Chicago Art Institute API.
    This function saves the retrieved artwork data to the database and returns the data. """
    
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

"""
    Fetch artworks in batches between specified start and end IDs, retrieving data in batches to reduce API load.
    The function saves each batch of artworks to the database and returns all fetched artworks. """
   
def fetch_artworks_batches(start_id, end_id, batch_size):
    """Fetch artworks in batches and save to the database."""
    all_artworks = []
    for i in range(start_id, end_id, batch_size):
        batch_ids = range(i, min(i + batch_size, end_id))
        artworks = get_artwork_by_ids(batch_ids)
        all_artworks.extend(artworks)
    return all_artworks

"""
    Fetch artworks based on search query or theme. This function saves the retrived artwork to the database and returns
    search results. """
    
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
    if not data.get('data', []):
        print("No artworks found for the given query.")
    for artwork_data in data.get('data', []):
        Artwork.add_new_artwork(artwork_data)
    return data.get('data', [])

""" Helper function: Get suggested artworks for a user based on their favorited artworks. 
    The function returns artworks by the same artists or in the same categories as the user's favorites; 
    if the user has no favorites, random artworks are returned. """
    
def get_suggested_artworks(user, limit=8):
    """Get suggested artworks based on a user's favorites or randomly if no favorites."""
    favorites = Favorite.query.filter_by(user_id=user.id).join(Artwork).all()

    if favorites:
        favorite_artwork_ids = [fav.artwork_id for fav in favorites]
        favorite_artists = {fav.artwork.artist_display for fav in favorites}
        favorite_types = {fav.artwork.artwork_type_title for fav in favorites}

        suggested_artworks = Artwork.query.filter(
            (Artwork.artist_display.in_(favorite_artists)) | 
            (Artwork.artwork_type_title.in_(favorite_types)),
            Artwork.id.notin_(favorite_artwork_ids)
        ).order_by(func.random()).limit(limit).all()
    else:
        suggested_artworks = Artwork.query.order_by(func.random()).limit(limit).all()

    return suggested_artworks
