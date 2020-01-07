#Utility functions used elsewhere
from datetime import date


def get_num_upcoming_shows_at_venue(db, venue_id, Show):
    return db.session.query(Show).filter(Show.venue_id==venue_id, Show.start_time > date.today()).count()

def get_num_upcoming_shows_for_artist(db, artist_id, Show):
    return db.session.query(Show).filter(Show.artist_id==artist_id, Show.start_time > date.today()).count()

