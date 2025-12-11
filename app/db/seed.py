# import random
# import string
# from sqlalchemy.orm import Session
# from app.db.models.user import User
# from app.db.models.country import Country  # Used to link trips
# # from app.db.models.city import City  # Ya no se usa en seed
# from app.db.models.trip import Trip
# from app.db.models.comment import Comment
# from app.auth.security import hash_password

# def random_string(length=10):
#     '''Genera strings aleatorios para nombres de prueba.'''
#     letters = string.ascii_letters
#     return ''.join(random.choice(letters) for i in range(length))

# def seed_db(db: Session):
#     '''
#     Puebla la base de datos con datos de prueba SOLO si está vacía.
    
#     Verifica la existencia de usuarios antes de insertar.
#     Esto evita duplicar datos en cada reinicio de la aplicación.
    
#     NOTA IMPORTANTE:
#     - Los países (Country) y ciudades (City) NO se insertan aquí
#     - Deben poblarse usando las APIs externas (REST Countries y GeoNames)
#     - Usa los endpoints /v1/country/populate y /v1/city/populate
    
#     Datos generados:
#     - 5 usuarios (1 admin, 4 regulares) con password: 'password123'
#     - 2 viajes por usuario (SIN país asignado, ya que no hay países en seed)
#     - 3 comentarios por viaje
#     '''
#     print("----- CHECKING DATABASE STATUS -----")
    
#     # Verificar si ya existen datos en la base de datos
#     existing_users = db.query(User).count()
    
#     if existing_users > 0:
#         print(f"✓ Database already has data:")
#         print(f"  - Users: {existing_users}")
#         print(f"  - Trips: {db.query(Trip).count()}")
#         print(f"  - Comments: {db.query(Comment).count()}")
#         print("----- SKIPPING SEED (Database already populated) -----")
#         return
    
#     print("✓ Database is empty, proceeding with seeding...")
#     print("----- SEEDING DATABASE -----")
    
#     # 2. Seed Users
#     print("Seeding Users...")
#     users = []
#     for i in range(5):
#         username = f"user_{random_string(5)}"
#         email = f"{username}@example.com"
#         # Hashear contraseña usando la función de seguridad
#         plain_password = "password123"
#         hashed_password = hash_password(plain_password)
#         # Asignar role (por defecto 'user', pero podríamos hacer uno admin)
#         role = "admin" if i == 0 else "user"  # Primer usuario es admin
        
#         user = User(
#             username=username,
#             email=email,
#             hashed_password=hashed_password,
#             role=role
#         )
#         db.add(user)
#         users.append(user)
#     db.commit()
    
#     # Refresh users to get IDs
#     for user in users:
#         db.refresh(user)
    
#     print(f"Created {len(users)} users (1 admin, {len(users)-1} regular users)")

#     # 3. Get existing Countries
#     countries = db.query(Country).all()
    
#     trips = [] # Initialize trips list
#     comments_count = 0 # Initialize comments count

#     if not countries:
#         print("WARNING: No countries found in DB. Trips cannot be seeded without countries.")
#         print("Please run POST /v1/country/populate first, then reset DB and re-seed.")
#     else:
#         print(f"Found {len(countries)} existing countries. Proceeding to seed Trips...")

#         # 4. Seed Trips
#         for user in users:
#             # Create 2 trips per user
#             for i in range(2):
#                 # Select a random country
#                 random_country = random.choice(countries)
                
#                 trip = Trip(
#                     name=f"Trip {i+1} by {user.username}",
#                     description=f"A wonderful trip planned by {user.username} to {random_country.name}.",
#                     start_date="2023-01-01",
#                     end_date="2023-01-10",
#                     user_id=user.id,
#                     country_id=random_country.id
#                 )
#                 db.add(trip)
#                 trips.append(trip)
#         db.commit()
        
#         for trip in trips:
#             db.refresh(trip)
            
#         print(f"Created {len(trips)} trips.")

#         # 5. Seed Comments
#         print("Seeding Comments...")
#         for trip in trips:
#             # 3 comments per trip
#             for _ in range(3):
#                 commenter = random.choice(users)
#                 comment = Comment(
#                     content=f"Amazing trip! {random_string(10)}",
#                     user_id=commenter.id,
#                     trip_id=trip.id
#                 )
#                 db.add(comment)
#                 comments_count += 1
#         db.commit()
#         print(f"Created {comments_count} comments for trips.")

#     print("----- DATABASE SEEDED SUCCESSFULLY -----")
#     print(f"Summary:")
#     print(f"  - Users: {len(users)}")
#     print(f"  - Countries: {len(countries)} (populate via API)")
#     print(f"  - Cities: 0 (populate via API)")
#     print(f"  - Trips: {len(trips)}")
#     print(f"  - Comments: {comments_count}")
#     print(f"  - Default password for all users: 'password123'")
#     print("")
#     print("⚠️  NEXT STEPS:")
#     print("   1. Populate countries: POST /v1/country/populate")
#     print("   2. Populate cities: POST /v1/city/populate")
