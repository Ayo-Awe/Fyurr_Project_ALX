#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import json
import dateutil.parser
import sys
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from models import Venue,Artist,Show
from flask_moment import Moment
from models import db, db_setup
import logging
from logging import Formatter, FileHandler
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)

moment = Moment(app)
app.config.from_object('config')
db_setup(app)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#



    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
  return babel.dates.format_datetime(date, format, locale='en')


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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  city_states = {(venue.city,venue.state) for venue in venues}
  def City_State_Serializer(city_state):
    city = city_state[0]
    state = city_state[1]
    response = {
      "city": city,
      "state":state,
      "venues":[]
    }
    for venue in venues:
      if(venue.city == city and venue.state == state):
        d = {
          "id":venue.id,
          "name":venue.name,
          "num_upcoming_shows": Show.query.filter(Show.venue_id==venue.id,Show.start_time>datetime.today()).count()
        }
        response['venues'].append(d)
    return response
  
  data= [City_State_Serializer(city_state) for city_state in city_states]
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  def serialize(venue):
    num_upcoming_shows = Show.query.filter(Show.start_time>datetime.today(),Show.venue_id==venue.id).count()
    data = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    }
    print(data)
    return data

  response={
    "count": Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).count(),
    "data": [serialize(venue) for venue in venues]
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  if venue == None:
    abort(404)
  
  def ShowSerialzer(row):
    show = row[0]
    artist = row[1]
    data = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    }
    return data
  past_shows = db.session.query(Show,Artist).join(Artist).filter(Show.start_time<=datetime.today(),Show.venue_id==venue_id).all()
  upcoming_shows = db.session.query(Show,Artist).join(Artist).filter(Show.start_time>datetime.today(),Show.venue_id==venue_id).all()
  past_shows_count = Show.query.filter(Show.start_time<=datetime.today(),Show.venue_id==venue_id).count()
  upcoming_shows_count = Show.query.filter(Show.start_time>datetime.today(),Show.venue_id==venue_id).count()
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link":venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [ShowSerialzer(show) for show in past_shows],
    "upcoming_shows": [ShowSerialzer(show) for show in upcoming_shows],
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  
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
  form = VenueForm()
  try:

    # create a new venue using form data
    venue = Venue(
          name = form.name.data,
          city = form.city.data,
          state = form.state.data,
          address = form.address.data,
          phone = form.phone.data,
          image_link = form.image_link.data,
          genres = form.genres.data,
          facebook_link = form.facebook_link.data,
          website = form.website_link.data,
          seeking_description = form.seeking_description.data,
          seeking_talent = form.seeking_talent.data
        )

    # add new venue to session and commit changes
    db.session.add(venue)
    db.session.commit()

    # Flash success on successful db insert
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.',category='error')
    print(sys.exc_info())
    db.session.rollback()

  finally:
    db.session.close()
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
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
  artists = Artist.query.all()
  data=[{"id":artist.id,"name":artist.name} for artist in artists]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get("search_term", "")
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  count = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).count()

  # modifies the data received to conform to the modelled data
  def serialize(artist):
    num_upcoming_shows = 0
    for show in artist.shows:
      if show.start_time > datetime.today():
        num_upcoming_shows+=1


    d = {
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows
    }
    return d

  response={
    "count": count,
    "data": [serialize(artist) for artist in artists]
  }
  print(response)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  def ShowSerialzer(row):
    show = row[0]
    venue = row[1]
    data = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(show.start_time)
    }
    return data

  artist = Artist.query.get(artist_id)
  past_shows = db.session.query(Show,Venue).join(Venue).filter(Show.start_time<=datetime.today(),Show.artist_id==artist_id).all()
  upcoming_shows = db.session.query(Show,Venue).join(Venue).filter(Show.start_time>datetime.today(),Show.artist_id==artist_id).all()
  past_shows_count = Show.query.filter(Show.start_time<=datetime.today(),Show.artist_id==artist_id).count()
  upcoming_shows_count = Show.query.filter(Show.start_time>datetime.today(),Show.artist_id==artist_id).count()
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website":artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": [ShowSerialzer(show) for show in past_shows],
    "upcoming_shows": [ShowSerialzer(show) for show in upcoming_shows],
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count
  }

  if artist == None:
    abort(404)
  return render_template('pages/show_artist.html', artist=data)



#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website
  form.genres.data = artist.genres
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website_link.data
    artist.genres = form.genres.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()
  venue= Venue.query.get(venue_id)
  form.name.data = venue.name
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.genres.data = venue.genres
  form.seeking_description.data = venue.seeking_description
  form.seeking_talent.data = venue.seeking_talent
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  try:
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data 
    venue.address = form.address.data 
    venue.city = form.city.data
    venue.state = form.state.data 
    venue.website = form.website_link.data
    venue.facebook_link = form.facebook_link.data  
    venue.genres = form.genres.data 
    venue.seeking_description = form.seeking_description.data 
    venue.seeking_talent = form.seeking_talent.data 
    venue.phone = form.phone.data 
    venue.image_link = form.image_link.data 
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # venue record with ID <venue_id> using the new attributes
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
  form = ArtistForm()
  data = form.data
  try:
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website = form.website_link.data,
      genres = form.genres.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data,
    )

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
  finally:
    db.session.close()

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
def formatShows(result):
  artist = result[0]
  venue = result[1]
  show = result[2]
  data = {
    "venue_id": venue.id,
    "venue_name": venue.name,
    "artist_id": artist.id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time": str(show.start_time)
  }
  return (data)

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  results = db.session.query(Artist,Venue,Show).join(Artist).join(Venue).all()
  data = [formatShows(show) for show in results]
  
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
    form = ShowForm()
    show = Show(
      venue_id = form.venue_id.data,
      artist_id = form.artist_id.data,
      start_time = form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
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
