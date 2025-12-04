import random
import string
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.country import Country
from app.db.models.city import City
from app.db.models.trip import Trip
from app.db.models.comment import Comment
from app.auth.security import hash_password # Assuming this exists, otherwise I'll use a placeholder or check imports

# Helper to generate random strings
def random_string(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def seed_db(db: Session):
    print("----- SEEDING DATABASE -----")
    
    # 1. Clean old data (Order matters because of Foreign Keys)
    print("Cleaning old data...")
    db.query(Comment).delete()
    db.query(Trip).delete()
    db.query(City).delete()
    db.query(Country).delete()
    db.query(User).delete()
    db.commit()

    # 2. Seed Users
    print("Seeding Users...")
    users = []
    for i in range(5):
        username = f"user_{random_string(5)}"
        email = f"{username}@example.com"
        # Using a simple hash or placeholder if get_password_hash isn't easily available, 
        # but better to try to find the real one. 
        # I'll assume a simple string for now if I can't find the auth util, 
        # but based on file list 'app.core' exists.
        # Let's use a dummy hash for simplicity and speed unless strict auth is needed.
        hashed_password = "hashed_password_secret" 
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        db.add(user)
        users.append(user)
    db.commit()
    
    # Refresh users to get IDs
    for user in users:
        db.refresh(user)

    # 3. Seed Locations (Countries and Cities)
    print("Seeding Locations...")
    countries = []
    country_names = ["Spain", "France", "Italy", "Japan", "USA"]
    
    for name in country_names:
        country = Country(name=name)
        db.add(country)
        countries.append(country)
        
    db.commit()
    
    for country in countries:
        db.refresh(country)
        # Add cities for this country
        for _ in range(2):
            city = City(
                name=f"City_{random_string(5)}",
                country_id=country.id,
                latitude=random.uniform(-90, 90),
                longitude=random.uniform(-180, 180)
            )
            db.add(city)
    db.commit()

    # 4. Seed Trips
    print("Seeding Trips...")
    trips = []
    for user in users:
        # Create 2 trips per user
        for _ in range(2):
            country = random.choice(countries)
            trip = Trip(
                name=f"Trip to {country.name}",
                description=f"A wonderful trip to {country.name} with lots of fun.",
                start_date="2023-01-01",
                end_date="2023-01-10",
                user_id=user.id,
                country_id=country.id
            )
            db.add(trip)
            trips.append(trip)
    db.commit()
    
    for trip in trips:
        db.refresh(trip)

    # 5. Seed Comments
    print("Seeding Comments...")
    for trip in trips:
        # 3 comments per trip
        for _ in range(3):
            commenter = random.choice(users)
            comment = Comment(
                content=f"Amazing trip! {random_string(10)}",
                user_id=commenter.id,
                trip_id=trip.id
            )
            db.add(comment)
    db.commit()

    print("----- DATABASE SEEDED SUCCESSFULLY -----")
