# Curated, Flask App, July 2024
# Written by Agamjot Sodhi

# Imports:
from flask import Flask, render_template, redirect, session, g, flash, request, url_for, jsonify
from forms import UserAddForm, UserEditForm, LoginForm, SearchForm, ArtworkTypeForm, ColorForm # WTForms inputs from forms.py
from models import User, Artwork, Favorite, SearchHistory, Type, db, connect_db     # SQLA table inputs from models.py
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import cast, func
from sqlalchemy.types import Integer
import json
from api import get_artwork_by_ids, fetch_artworks_batches, fetch_artworks_by_query, get_suggested_artworks
from flask_debugtoolbar import DebugToolbarExtension

# Connection to sql database - curated:
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://curated_r101_user:YV6Det6FqmMUPUSlSCWoh38ASv2XS4d3@dpg-creumaaj1k6c73dgi6c0-a/curated_r101'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_picasso_101'


app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False  # Prevent toolbar from intercepting redirects
app.debug = False  # Enable debugging mode

# Initialize the Debug Toolbar
# toolbar = DebugToolbarExtension(app)


connect_db(app)

# Global Variables
CURR_USER_KEY = "curr_user"

# User Functions ##########################################################################################################################

@app.before_request
def add_user_to_g():
    """ If we're logged in, add curr user to Flask global. """
    
    g.user = User.query.get(session[CURR_USER_KEY]) if CURR_USER_KEY in session else None

def do_login(user):
    """ Log in user, add to session. """
    
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Log out user, delete from session."""
    
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

# User Routes ##############################################################################################################################

@app.route('/')
def homepage():
    """Redirect to the dashboard if logged in otherwise home.html to login/signup."""
    
    if g.user:
        return redirect(url_for('dashboard'))
    else:
        return render_template('home.html')
      
@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle New User Signup."""
    
    # Log out any current user
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    # Call user signup form from forms.py
    form = UserAddForm()
    
    if form.validate_on_submit():
        try:
            # Create a new user
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()  # Handle duplicate username/email error
            flash("Username or email already taken, please try again!", 'danger')
            return render_template('users/signup.html', form=form)
        
        do_login(user)  # Log in the new user
        return redirect("/dashboard")
    
    return render_template('users/signup.html', form=form)  # Display signup form if not submitted or invalid

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle User Login."""
    
    # Call login form from forms.py
    form = LoginForm()
    
    if form.validate_on_submit():
        # User.authenticate class method from models.py
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            flash(f"Hello, {user.first_name}!", "success")
            return redirect("/dashboard")
        flash("Invalid credentials.", 'danger') # Handle incorrect credentials error
        
    return render_template('users/login.html', form=form)  # Display login form if not submitted or invalid


@app.route('/logout')
def logout():
    """Handle logout of user."""
    
    do_logout()
    flash("You have successfully logged out.", 'success')
    return redirect("/login")

# Artwork Routes ##############################################################################################################################


""" 
Route: /dashboard

This route handles the user dashboard page, providing search functionality for artworks. Users can search by query, category, or color. 

- All API handling functions and there descriptions can be found in api.py in the project directory
- The Chicago Art where the art records obtain from have a 100 artworks per call limit
- start-id, end-id and batch size help fetch artwork in batches to meet limits """


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    """Show user dashboard with search functionality."""
    
    # Error handling
    if not g.user:
        flash("Access unauthorized. Please log in or create an account.", "danger")
        return redirect("/home")

    # Initialize forms
    search_form = SearchForm()
    type_form = ArtworkTypeForm()
    color_form = ColorForm()
    
    # Populate the artwork type dropdown with category names
    type_form.artwork_type.choices = [(type.name, type.name) for type in Type.query.all()]

    # To hold search results
    search_results = []

    # Handle Search by Query
    if search_form.validate_on_submit() and search_form.submit.data:
        query = search_form.query.data.strip()

        if query:
            search_results = fetch_artworks_by_query(query=query) # API function from api.py
            
        # Fetch artworks in batches to help meet API limits 
        else:
            start_id = 1
            end_id = 100
            batch_size = 50
            search_results = fetch_artworks_batches(start_id, end_id, batch_size)

        # Saves search results/user search terms - will be used for suggested artworks section
        if search_results:
            SearchHistory.save_history(g.user.id, query)
            search_result = SearchHistory(user_id=g.user.id, search_term=json.dumps(search_results))
            db.session.add(search_result)
            db.session.commit()
            session['search_result_id'] = search_result.search_id
            return redirect(url_for('results'))
        else:
            # If no artworks are found error handling
            flash("No artworks found for the given query.", "danger")
            return redirect(url_for('dashboard'))

    # Handle Search by Category - drop down menu
    if type_form.validate_on_submit() and type_form.submit.data:
        
        # Get user selected artwork type from form
        artwork_type = type_form.artwork_type.data
        # Query database to find type instance matching user selected artwork type 
        type_instance = Type.query.filter_by(name=artwork_type).first()

        # If found return results/artwork ids in that artwork type
        if type_instance:
            artwork_ids = type_instance.get_artwork_ids()
            search_results = [Artwork.query.get(artwork_id) for artwork_id in artwork_ids] 

            if search_results:
                return render_template('art/results.html', search_results=search_results)
            
            # Error handling for no/invalid results
            else:
                flash("No artworks found for the selected category.", "danger")
                return redirect(url_for('dashboard'))
        else:
            flash("Invalid artwork type selected.", "danger")
            return redirect(url_for('dashboard'))

    # Handle Search by Color
    if color_form.validate_on_submit() and color_form.submit.data:
        print("Color Form Submitted")
        try:
            # Parse selected color from form data
            selected_color = json.loads(color_form.color.data)
        except json.JSONDecodeError:
            flash("Invalid color data.", "danger")
            return redirect(url_for('dashboard'))

        # Range for color matching - will color match to HSL color codes per artwork within a +/- exception of 50 
        color_range = 60

        # Filter artworks by matching color attributes within the color range   
        search_results = Artwork.query.filter(
            cast(func.jsonb_extract_path_text(Artwork.color, 'h'), Integer).between(selected_color['h'] - color_range, selected_color['h'] + color_range),
            cast(func.jsonb_extract_path_text(Artwork.color, 's'), Integer).between(selected_color['s'] - color_range, selected_color['s'] + color_range),
            cast(func.jsonb_extract_path_text(Artwork.color, 'l'), Integer).between(selected_color['l'] - color_range, selected_color['l'] + color_range)
        ).all()

        if search_results:
            return render_template('art/results.html', search_results=search_results)
        else:
            flash("No artworks found for the selected color.", "danger")
            return redirect(url_for('dashboard'))

    # Get 4 suggested artworks using the helper function
    suggested_artworks = get_suggested_artworks(g.user, limit=4)
    
    # Fetch 4 random artworks for display on the dashboard
    random_artworks = Artwork.query.order_by(func.random()).limit(4).all()
        
    
    return render_template('art/dashboard.html', search_form=search_form, type_form=type_form, color_form=color_form, random_artworks=random_artworks, suggested_artworks=suggested_artworks )

 
""" Route: /results
Returns all results from search bar/ drop down menu and color picker, displays each artwork from the user request. """

@app.route('/results')
def results():
    """Show search results."""
    
    query = request.args.get('query')  # Get the query from the search bar in the navbar
    
    if query:
        search_results = fetch_artworks_by_query(query=query) # Display results
        if not search_results:
            flash("No artworks found for the given query.", 'danger')
            return redirect(url_for('dashboard'))
    else:
        search_result_id = session.get('search_result_id')
        if not search_result_id:
            flash("No search results found.", 'danger')
            return redirect(url_for('dashboard'))

        search_result = SearchHistory.query.get_or_404(search_result_id)
        search_results = json.loads(search_result.search_term)

    return render_template('art/results.html', search_results=search_results)

 
""" Route: /artwork/<int:artwork_id
Fetch and display details of a specific artwork by its ID. If the artwork is not found in the database, 
it fetches the data from an external API and saves it. """

@app.route('/artwork/<int:artwork_id>')
def artwork(artwork_id):
    """Show details of a specific artwork."""
    
    artwork = Artwork.query.get(artwork_id)
    if not artwork:
        # Fetch the artwork data using get_artwork_by_ids function from api.py
        data = get_artwork_by_ids([artwork_id])
        if not data:
            flash("Artwork not found.", 'danger')
            return redirect(url_for('results'))

        # Save the artwork data to the database using add_new_artwork method from models.py
        Artwork.add_new_artwork(data[0])

        # Retrieve newly added artwork
        artwork = Artwork.query.get(artwork_id)

    return render_template('art/artwork_details.html', artwork=artwork)

""" Route: /explore
Displays a page with 36 random artworks and includes a refresh button to load more. """
@app.route('/explore')
def explore():
    """Display 36 new artworks and a refresh button at the bottom"""
    random_artworks = Artwork.query.order_by(func.random()).limit(36).all()
    
    return render_template('art/explore.html', random_artworks=random_artworks)

""" Route: /favorites
Displays all the artworks favorited by user. Redirects to the homepage if the user is not logged in."""
@app.route('/favorites')
def favorites():
    """Show all favorited artworks by the user."""
    
    if not g.user:
        flash("Access unauthorized. Please log in or create an account.", "danger")
        return redirect("/")

    # Query all artworks favorited by the user
    favorited_artworks = Artwork.query.join(Favorite).filter(Favorite.user_id == g.user.id).all()

    return render_template('art/favorites.html', favorited_artworks=favorited_artworks)


""" Route: /artwork/<int:artwork_id>/favorite (POST)
Toggles the favorite status of an artwork for the logged-in user. 
Returns a JSON response if artwork was favorited or unfavorited."""
@app.route('/artwork/<int:artwork_id>/favorite', methods=['POST'])
def favorite_artwork(artwork_id):
    """Toggle favorite status of an artwork asynchronously."""
    
    if not g.user:
        return jsonify({"message": "Unauthorized"}), 401

    # Check if already favorited
    favorite = Favorite.query.filter_by(user_id=g.user.id, artwork_id=artwork_id).first()
    
    if favorite:
        # If it is already favorited, unfavorite it
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Artwork unfavorited successfully!", "liked": False}), 200
    else:
        # Otherwise, add to favorites
        db.session.add(Favorite(user_id=g.user.id, artwork_id=artwork_id))
        db.session.commit()
        return jsonify({"message": "Artwork favorited successfully!", "liked": True}), 200


"""Route: /profile
Displays the user's profile page, including suggested artworks and a preview of their favorited artworks. """
@app.route('/profile')
def profile():
    """Show profile page."""
    
    if not g.user:
        flash("Access unauthorized. Please log in or create an account.", "danger")
        return redirect("/")
    # Get 4 suggested artworks using the helper function
    suggested_artworks = get_suggested_artworks(g.user, limit=8)
    
    # Fetch 4 random favorited artworks for the user
    favorites = Favorite.query.filter_by(user_id=g.user.id).join(Artwork).order_by(func.random()).limit(4).all()


    return render_template('profile/profile.html', user=g.user, suggested_artworks=suggested_artworks, favorites=favorites)

"""Route: /profile/edit
Allows the user to edit their profile information, including username, email, first name, and profile image."""
@app.route('/profile/edit', methods=["GET", "POST"])
def edit_profile():
    """Edit user's profile."""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = UserEditForm(obj=g.user)

    if form.validate_on_submit():
        g.user.username = form.username.data
        g.user.email = form.email.data
        g.user.first_name = form.first_name.data
        g.user.image_url = form.image_url.data or User.image_url.default.arg
        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('profile'))

    return render_template('profile/edit.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure all tables are created
        # Example of fetching the first 100 artworks on startup
        fetch_artworks_batches(start_id=1, end_id=101, batch_size=100)
    app.run()
