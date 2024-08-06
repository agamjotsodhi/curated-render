# Curated, Flask App
# Written by Agamjot Sodhi

# Imports:
from flask import Flask, render_template, redirect, session, g, flash, request, url_for
from forms import UserAddForm, LoginForm, SearchForm # WTForms inputs from forms.py
from models import User, Artwork, Favorite, SearchHistory, Type, db, connect_db     # SQLA table inputs from models.py
from sqlalchemy.exc import IntegrityError
import json
from api import get_artwork_by_ids, fetch_artworks_batches, fetch_artworks_by_query

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///curated'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

connect_db(app)

# Global Variables
CURR_USER_KEY = "curr_user"

# User Functions ##########################################################################################################################
@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    g.user = User.query.get(session[CURR_USER_KEY]) if CURR_USER_KEY in session else None

def do_login(user):
    """Log in user, add to session."""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Log out user, delete from session."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

# User Routes ##############################################################################################################################

@app.route('/')
def homepage():
    """Show initial landing page with login/sign up."""
    return render_template('home.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle New User Signup."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = UserAddForm()
    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username or email already taken, please try again!", 'danger')
            return render_template('users/signup.html', form=form)
        do_login(user)
        return redirect("/dashboard")
    return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle User Login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            flash(f"Hello, {user.first_name}!", "success")
            return redirect("/dashboard")
        flash("Invalid credentials.", 'danger')
    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have successfully logged out.", 'success')
    return redirect("/login")

# Artwork Routes ##############################################################################################################################

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    """Show user dashboard with search functionality"""
    if not g.user:
        flash("Access unauthorized. Please log in or create an account.", "danger")
        return redirect("/entry")

    form = SearchForm()

    if form.validate_on_submit():
        query = form.query.data.strip()

        search_results = []
        if query:
            search_results = fetch_artworks_by_query(query=query)
        else:
            start_id = 1
            end_id = 100
            batch_size = 50
            search_results = fetch_artworks_batches(start_id, end_id, batch_size)
            
        SearchHistory.save_history(g.user.id, query)

        # Store search results as JSON in the database
        search_result = SearchHistory(user_id=g.user.id, search_term=json.dumps(search_results))
        db.session.add(search_result)
        db.session.commit()

        # Store only the search result ID in the session
        session['search_result_id'] = search_result.search_id
        return redirect(url_for('results'))

    return render_template('art/dashboard.html', form=form)

@app.route('/results')
def results():
    """Show search results."""
    search_result_id = session.get('search_result_id')
    if not search_result_id:
        flash("No search results found.", 'danger')
        return redirect(url_for('dashboard'))

    search_result = SearchHistory.query.get_or_404(search_result_id)
    search_results = json.loads(search_result.search_term)
    
    
    return render_template('art/results.html', search_results=search_results)

@app.route('/artwork/<int:artwork_id>')
def artwork(artwork_id):
    """Show details of a specific artwork."""
    artwork = Artwork.query.get(artwork_id)
    if not artwork:
        # Fetch the artwork data from the API
        data = get_artwork_by_ids([artwork_id])
        if not data:
            flash("Artwork not found.", 'danger')
            return redirect(url_for('results'))

        # Save the artwork data to the database using add_new_artwork method
        Artwork.add_new_artwork(data[0])

        # Retrieve the newly added artwork
        artwork = Artwork.query.get(artwork_id)

    return render_template('art/artwork_details.html', artwork=artwork)

@app.route('/explore')
def explore():
    """Show explore page."""
    return render_template('art/explore.html')

@app.route('/favorites')
def favorites():
    """Show favorites page."""
    return render_template('art/favorites.html')

@app.route('/profile')
def profile():
    """Show profile page."""
    return render_template('profile/profile.html')

if __name__ == '__main__':
    app.run(debug=True)
