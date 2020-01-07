#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import date
from utils import get_num_upcoming_shows_at_venue, get_num_upcoming_shows_for_artist
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database
# Create the database automatically if it doesn't exist
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from config import SQLALCHEMY_DATABASE_URI
engine = create_engine(SQLALCHEMY_DATABASE_URI)
if not database_exists(engine.url):
    create_database(engine.url)

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from flask_migrate import Migrate

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    website = db.Column(db.String(120))

    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.String(120), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False) 
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False) 


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  state_cities = set()

  for x in db.session.query(Venue.state, Venue.city).all():
      state_cities.add(x)

  state_cities = sorted(list(state_cities))
  data = []
  for (state, city) in state_cities:
    data.append({})
    data[-1]["city"] = city
    data[-1]["state"] = state
    data[-1]["venues"] = []

    for venue_id, venue_name in db.session.query(Venue.id, Venue.name).filter(Venue.city==city):
      upcoming_shows = get_num_upcoming_shows_at_venue(db, venue_id, Show)
      venue_details = {}
      venue_details["id"] = venue_id
      venue_details["name"] = venue_name
      venue_details["num_upcoming_shows"] = upcoming_shows
      data[-1]["venues"].append(venue_details)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = db.session.query(Venue.id, Venue.name).all()
  response = {"count": 0, "data": []}

  for venue_id, venue_name in venues: 
    # venue_id, venue_name = venue_ids[ix], venue_names[ix]
    if search_term.lower() in venue_name.lower() or venue_name.lower() in search_term.lower():
      response["count"] += 1
      upcoming_shows = get_num_upcoming_shows_at_venue(db, venue_id, Show)
      venue_info = {"id": venue_id, "name": venue_name, "num_upcoming_shows": upcoming_shows}
      response["data"].append(venue_info)
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  result = db.session.query(Venue).filter(Venue.id==venue_id)[0]
  data = result.__dict__
  data["genres"] =  data["genres"].split(",")

  data["past_shows"] = []
  data["upcoming_shows"] = []
  for show in db.session.query(Show).filter(Show.venue_id==venue_id).all():
      show_info = {}
      format="EE MM, dd, y h:mma"
      show_info["start_time"] =  babel.dates.format_datetime(show.start_time, format)
      artist_info = db.session.query(Artist.id, Artist.name, Artist.image_link).filter(Artist.id==show.artist_id)[0]
      show_info["artist_id"] = artist_info.id
      show_info["artist_name"] = artist_info.name
      show_info["artist_image_link"] = artist_info.image_link

      if show.start_time <= date.today():
          data["past_shows"].append(show_info)
      else:
          data["upcoming_shows"].append(show_info)


  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])

  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  try:
    venue = Venue()
    venue.name = request.form["name"]
    venue.genres = request.form["genres"] 
    venue.city = request.form["city"]
    venue.state = request.form["state"]
    venue.address = request.form["address"]
    venue.phone = request.form["phone"]
    venue.facebook_link = request.form["facebook_link"]
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form["name"] + ' could not be listed.')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.filter_by(venue_id==venue_id).one()
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue_id + ' was successfully delete!')
  
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
  
  finally:
    db.session.close()


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  results = db.session.query(Artist.id, Artist.name).all()
  data = []
  for result in results:
    info = {"id": result.id, "name": result.name}
    data.append(info)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = db.session.query(Artist.id, Artist.name).all()
  response = {"count": 0, "data": []}
  for artist_id, artist_name in artists: 
    if search_term.lower() in artist_name.lower() or artist_name.lower() in search_term.lower():
      response["count"] += 1
      upcoming_shows = get_num_upcoming_shows_for_artist(db, artist_id, Show)
      artist_info = {"id": artist_id, "name": artist_name, "num_upcoming_shows": upcoming_shows}
      response["data"].append(artist_info)
  return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  time_format="EE MM, dd, y h:mma"
  result = db.session.query(Artist).filter(Artist.id==artist_id)[0]
  data = result.__dict__
  data["genres"] =  data["genres"].split(",")

  data["past_shows"] = []
  data["upcoming_shows"] = []
  for show in db.session.query(Show).filter(Show.artist_id==artist_id).all():
      show_info = {}      
      show_info["start_time"] =  babel.dates.format_datetime(show.start_time, time_format)
      venue_info = db.session.query(Venue.id, Venue.name, Venue.image_link).filter(Venue.id==show.venue_id)[0]
      show_info["venue_id"] = venue_info.id
      show_info["venue_name"] = venue_info.name
      show_info["venue_image_link"] = venue_info.image_link

      if show.start_time <= date.today():
          data["past_shows"].append(show_info)
      else:
          data["upcoming_shows"].append(show_info)


  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = db.session.query(Artist).filter(Artist.id==artist_id).one().__dict__
  artist = {key: artist[key] for key in artist.keys() if key != "_sa_instance_state"}
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try: 
    artist = Artist.query.filter(Artist.id==artist_id).first()
    new_info = request.form.__dict__

    for key in new_info.keys():
        setattr(artist, key, new_info[key])
    
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter(Venue.id==venue_id).one().__dict__
  venue = {key: venue[key] for key in venue.keys() if key != "_sa_instance_state"}  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try: 
    venue = Venue.query.filter(Venue.id==venue_id).first()
    new_info = request.form.__dict__

    for key in new_info.keys():
        setattr(venue, key, new_info[key])    
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    artist = Artist()
    artist.name = request.form["name"]
    artist.genres = request.form["genres"] 
    artist.city = request.form["city"]
    artist.state = request.form["state"]
    artist.phone = request.form["phone"]
    artist.facebook_link = request.form["facebook_link"]
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form["name"] + ' could not be listed.')

  finally:
    db.session.close()
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  time_format="EE MM, dd, y h:mma"
  shows = db.session.query(Show).all()
  data = []
  for show in shows:
    result = {"venue_id": show.venue_id, "venue_name": show.venue.name, "artist_id": show.artist_id,
              "artist_image_link": show.artist.image_link, "start_time": babel.dates.format_datetime(show.start_time, time_format)}
    data.append(result)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    show = Show()
    show.artist_id = request.form["artist_id"]
    show.venue_id = request.form["venue_id"] 
    show.start_time = request.form["start_time"]
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Show not listed')

  finally:
    db.session.close()
  


  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
