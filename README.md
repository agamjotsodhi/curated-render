# READ ME 

## API used for this project: Art institute of Chicago API
## API docs link: https://api.artic.edu/docs/#introduction
## Base API link: https://api.artic.edu/api/v1/artworks

# DESIGN FLOW based on routes:


Routes Based on Design Flow:
Home Page (/):


Show homepage with hero image and search bar.
Allows user to search for artworks by title, artist, or style.
User Dashboard (/dashboard):


Show user's dashboard with personal collection and recommendations.
Search Page (/search):


Allow users to search for artworks using filters.
Artwork Detail Page (/artwork/<int:artwork_id>):


Show detailed information about selected artwork.
Save to Favorites (/artwork/<int:artwork_id>/favorite):


Option to save artwork to user's favorites.
Personal Collection (/favorites):


Show user's favorite artworks.
Recommendations (/recommendations):


Show recommendations based on user's preferences.