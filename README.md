# Curated, centralized art database to discover, search, and save artwork

This project is a web-based art discovery engine designed to help users discover, search, and save artwork to their accounts. The application utilizes a PostgreSQL database to manage and store artworks, user information, and search history, enabling a suggestion-based model for personalized recommendations. It is built with Flask, leveraging Python for backend development, while JavaScript, HTML, and CSS power the front end. The project integrates the Art Institute of Chicago API to retrieve artwork data in JSON format, providing a  diverse collection of international artworks. The user interface features a sleek, modern design with carefully crafted elements to enhance the user experience.

## Visit the Site
Feel free to check out the website here!

## Features

## Installation

## 


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
