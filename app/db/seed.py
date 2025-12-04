import random
import string
from sqlalchemy.orm import Session
from app.db.models.user import User
from app.db.models.country import Country
from app.db.models.city import City
from app.db.models.trip import Trip
from app.db.models.comment import Comment
from app.auth.security import hash_password

# Helper to generate random strings
def random_string(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def seed_db(db: Session):
    """
    Seed the database with initial data only if it's empty.
    Checks if there are existing users before seeding.
    """
    print("----- CHECKING DATABASE STATUS -----")
    
    # Verificar si ya existen datos en la base de datos
    existing_users = db.query(User).count()
    existing_countries = db.query(Country).count()
    
    if existing_users > 0 or existing_countries > 0:
        print(f"✓ Database already has data:")
        print(f"  - Users: {existing_users}")
        print(f"  - Countries: {existing_countries}")
        print(f"  - Trips: {db.query(Trip).count()}")
        print(f"  - Cities: {db.query(City).count()}")
        print(f"  - Comments: {db.query(Comment).count()}")
        print("----- SKIPPING SEED (Database already populated) -----")
        return
    
    print("✓ Database is empty, proceeding with seeding...")
    print("----- SEEDING DATABASE -----")
    
    # 2. Seed Users
    print("Seeding Users...")
    users = []
    for i in range(5):
        username = f"user_{random_string(5)}"
        email = f"{username}@example.com"
        # Hashear contraseña usando la función de seguridad
        plain_password = "password123"
        hashed_password = hash_password(plain_password)
        # Asignar role (por defecto 'user', pero podríamos hacer uno admin)
        role = "admin" if i == 0 else "user"  # Primer usuario es admin
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        )
        db.add(user)
        users.append(user)
    db.commit()
    
    # Refresh users to get IDs
    for user in users:
        db.refresh(user)
    
    print(f"Created {len(users)} users (1 admin, {len(users)-1} regular users)")

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
    print(f"Summary:")
    print(f"  - Users: {len(users)}")
    print(f"  - Countries: {len(countries)}")
    print(f"  - Cities: {len(countries) * 2}")
    print(f"  - Trips: {len(trips)}")
    print(f"  - Comments: {len(trips) * 3}")
    print(f"  - Default password for all users: 'password123'")
