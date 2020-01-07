# Creates and adds the initial data to the database
from app import db, Venue, Artist, Show
from datetime import date

# import time

# state_cities = set()

# for x in db.session.query(Venue.state, Venue.city).all():
#     state_cities.add(x)

# state_cities = sorted(list(state_cities))

# for data in db.session.query(Venue.id, Venue.name).filter(Venue.city==state_cities[0][1]):
#     venue_id, venue_name = data
#     upcoming_shows = db.session.query(Show).filter(Show.venue_id==venue_id, Show.start_time > date.today()).count()
#     print(venue_id, venue_name, upcoming_shows)

#     # filter by show time aswell 

# num_up_coming_shows = {}

# x = db.session.query(Artist).filter(Artist.id==4).one()
# print(x.__dict__

artist = Artist.query.filter(Artist.id==4).first()

vals = {"name": "Guns N Petals"}

print(artist.__dict__)

for key in vals:
    setattr(artist, key, vals[key])

db.session.commit()
print(artist.__dict__)    

# z = db.session.query(Venue).filter(Venue.id==1)
# print(z)
# print(z[0])
# data = z[0].__dict__
# print(data["genres"].split(","))




