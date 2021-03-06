import os
import requests
import json
import urllib.parse

from flask import Flask, request, render_template,  redirect, flash, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm
from models import db,  connect_db, User, Animal, Country, AnimalCountry
# from helper import how_many_pages_RL

#API
# from mb_Meschenmoser import callMovebankAPI

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///anitracker'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

################
#GLOBAL VARIABLES

RED_LIST_URL = 'http://apiv3.iucnredlist.org'
TOKEN = '9bb4facb6d23f48efbf424bb05c0c1ef1cf6f468393bc745d42179ac4aca5fee'


##############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")


################################################################################
#user routes


@app.route('/users/<int:user_id>')
def show_user_profile(user_id):
    """Show user profile pg"""
    user = User.query.get_or_404(user_id)
    return render_template('users/profile.html', user=user)

############################################################################
#Red List Routes
@app.route('/red_list')
def show_search_by():
    '''Shows search by options for the animals'''
    return render_template('red_list/search_by.html')

@app.route('/red_list/result')
def send_api_req():
    species = request.args["species"]
    country = request.args["country"]
    category = request.args["category"]

    res = requests.get(f'{RED_LIST_URL}/api/v3/species/category/{category}?token={TOKEN}')
    res=res.json()

    
    
    return render_template('red_list/search_result.html', species=species,country=country,category=category, result = res)

################################################################################
#Animals routes



@app.route('/animals/update')
def update_db():
    """get the info from RL API and add to the db"""


    #first  add the counties
    # res_countries = requests.get(f'{RED_LIST_URL}/api/v3/country/list?token={TOKEN}')
    # res_countries = res_countries.json()['results']

    # for country in res_countries:
    #     json_country = country
    #     country_to_db = Country.update_db(json_country['isocode'], 
    #                                       json_country['country'])
    #     db.session.commit()
    res_animals = requests.get(f'{RED_LIST_URL}/api/v3/species/page/17?token={TOKEN}')
    res_animals = res_animals.json()['result']

    for animal in res_animals:
        # species_name = animal['scientific_name'].replace(' ', '%20')
        # res_taxonomicnotes = requests.get(f'{RED_LIST_URL}/api/v3/species/narrative/{species_name}?token={TOKEN}')
        # res_taxonomicnotes = res_taxonomicnotes.json()['result']
        animal_to_db = Animal.update_db(
                                        family_name=animal['family_name'],
                                        scientific_name=animal['scientific_name'],
                                        main_common_name=animal['main_common_name'],
                                        category=animal['category'],
                                        # taxonomicnotes=res_taxonomicnotes[1]
        )
        db.session.commit()
        
    return render_template('animals/update.html')

@app.route('/animals/<species_name>')
def show_animal_details(species_name):
    """Sends a GET request to RI API, displays the result on the page """
    name_for_url = species_name.replace(' ', '%20')
    res = requests.get(f'{RED_LIST_URL}/api/v3/species/{species_name}?token={TOKEN}')
    narrative = requests.get(f'https://apiv3.iucnredlist.org/api/v3/species/narrative/{name_for_url}?token={TOKEN}')
    narrative_data = narrative.json()
    
    return render_template('animals/details.html', narrative_data = narrative_data, res = res.json()['result'][0])


@app.route('/animals/<species_name>/track')
def add_animal_to_db(species_name):
    """Saving the animal to the db"""
    
    return "Weeeee"


# request to hte db, ge as much as I can
# do i loop throught it?
# do i need to add everything to a dictionary? 

##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        return render_template('home.html')

    else:
        return render_template('home-anon.html')


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


    

