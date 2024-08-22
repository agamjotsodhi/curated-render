# Forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length


class UserAddForm(FlaskForm):
    """ User sign-up form - form for adding users. """

    username = StringField('Username', validators=[DataRequired()],render_kw={"placeholder": "Enter your username"})
    email = StringField('E-mail', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email address"})
    password = PasswordField('Password', validators=[Length(min=6)], render_kw={"placeholder": "Create a password"}) # Will hold Bcrypt hashed password, min. 6 characters
    first_name = StringField('First Name', render_kw={"placeholder": "Enter your first name"})
    image_url = StringField('(Optional) Image URL', render_kw={"placeholder": "Enter an image URL (optional)"}) 


class UserEditForm(FlaskForm):
    """ Edit account information Form """

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    first_name = StringField('First Name')
    image_url = StringField('(Optional) Image URL')
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """ Login form """

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class SearchForm(FlaskForm):
    """ Artwork query search bar form """
    
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')
    
class ArtworkTypeForm(FlaskForm):
    """ Search for artwork by catergory type - drop down menu """
    
    artwork_type = SelectField('Artwork Type', validators=[DataRequired()], choices=[])
    submit = SubmitField('Search')    
    
class ColorForm(FlaskForm):
    """ Search for artwork by color - color picker form """
    
    color = StringField('Color', validators=[DataRequired()])
    submit = SubmitField('Search')
       
    