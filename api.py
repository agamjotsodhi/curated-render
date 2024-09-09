import requests
import logging
from models import Artwork, db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "https://api.artic.edu/api/v1/artworks"

def get_artwork_by_ids(artwork_ids):
    """Fetch detailed info for multiple artworks by their IDs and save to the database."""
    params = {
        'ids': ','.join(map(str, artwork_ids)),
        'fields': 'id,title,alt_titles,artist_display,date_start,date_end,date_display,place_of_origin,classification_titles,edition,color,dimensions,description,image_id,artwork_type_title,api_link,medium_display'
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        return []

    data = response.json().get('data', [])
    logger.info(f"Fetched {len(data)} artworks from the API.")

    for artwork_data in data:
        try:
            artwork = Artwork.add_new_artwork(artwork_data)
            if artwork:
                db.session.add(artwork)  # Explicitly add the new artwork to the session
                db.session.commit()  # Commit after adding the artwork
                logger.info(f"Added artwork {artwork.id} - {artwork.title} to the database.")
            else:
                logger.warning(f"Artwork data invalid or could not be processed: {artwork_data}")
        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback in case of error
            logger.error(f"Error adding artwork {artwork_data.get('id')} to the database: {e}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error processing artwork {artwork_data.get('id')}: {e}")

    return data

def fetch_artworks_batches(start_id, end_id, batch_size):
    """Fetch artworks in batches and save to the database."""
    all_artworks = []
    for i in range(start_id, end_id, batch_size):
        batch_ids = range(i, min(i + batch_size, end_id))
        artworks = get_artwork_by_ids(batch_ids)
        all_artworks.extend(artworks)
        logger.info(f"Fetched batch {i} to {min(i + batch_size, end_id)}, total artworks: {len(all_artworks)}")
    return all_artworks

def fetch_artworks_by_query(query=None, theme=None):
    """Fetch artworks by search query and save to the database."""
    params = {
        'fields': 'id,title,alt_titles,artist_display,date_start,date_end,date_display,place_of_origin,classification_titles,edition,color,dimensions,description,image_id,artwork_type_title,api_link,medium_display',
        'limit': 100
    }
    if query:
        params['q'] = query
   
    try:
        response = requests.get(f"{API_URL}/search", params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        return []

    data = response.json().get('data', [])
    if not data:
        logger.info("No artworks found for the given query.")
    else:
        logger.info(f"Found {len(data)} artworks for the query '{query}'.")

    for artwork_data in data:
        try:
            artwork = Artwork.add_new_artwork(artwork_data)
            if artwork:
                db.session.add(artwork)
                db.session.commit()  # Commit after adding the artwork
                logger.info(f"Added artwork {artwork.id} - {artwork.title} to the database.")
            else:
                logger.warning(f"Artwork data invalid or could not be processed: {artwork_data}")
        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback in case of error
            logger.error(f"Error adding artwork {artwork_data.get('id')} to the database: {e}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error processing artwork {artwork_data.get('id')}: {e}")

    return data

def get_suggested_artworks(user, limit=8):
    """Get suggested artworks based on a user's favorites or randomly if no favorites."""
    try:
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

        logger.info(f"Suggested {len(suggested_artworks)} artworks for user {user.id}.")
        return suggested_artworks
    except SQLAlchemyError as e:
        logger.error(f"Error fetching suggested artworks: {e}")
        return []
