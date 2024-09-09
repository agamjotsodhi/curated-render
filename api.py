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
            # Assuming `Artwork.add_new_artwork` returns an instance of `Artwork` or None if fails
            artwork = Artwork.add_new_artwork(artwork_data)
            if artwork:
                db.session.add(artwork)  # Explicitly add artwork
                db.session.commit()  # Commit after each addition
                logger.info(f"Added artwork {artwork.id} - {artwork.title} to the database.")
            else:
                logger.warning(f"Invalid artwork data: {artwork_data}")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"SQLAlchemyError when adding artwork {artwork_data.get('id')}: {e}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error: {e}")

    return data
