# SQUEMAS AUREVIA

## Descripcion TODO

Crear esquemas:

- Crear Friendship
- Crear Comment
- Crear City

(Posible cambio en el futuro para mejorar la flexibilidad del esquema en User, Trip y Country)

Ejemplos:

## Usuario:

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "4YH0T@example.com",
  "trips": {
    "name": "Trip to Paris",
    "description": "Visit the Eiffel Tower and the Louvre Museum",
    "start_date": "2022-01-01",
    "end_date": "2022-01-05",
    "country": {
      "name": "France",
      "cities": []
    }
  },
  "friendships": [],
  "comments": []
}
```

## Trip:

```json
{
  "id": 1,
  "name": "Trip to Paris",
  "description": "Visit the Eiffel Tower and the Louvre Museum",
  "start_date": "2022-01-01",
  "end_date": "2022-01-05",
  "user_id": 1,
  "user": {
    "username": "johndoe",
    "email": "4YH0T@example.com"
  },
  "country_id": 1,
  "country": {
    "name": "France",
    "cities": []
  },
  "comments": []
}
```

## Country:

```json
{
  "id": 1,
  "name": "France",
  "cities": []
}
```

## Friendship:

```json
{
  "id": 1,
  "user_id": 1,
  "friend_id": 2
}
```

## Comment:

```json
{
  "id": 1,
  "content": "Great trip!",
  "user_id": 1,
  "user": {
    "username": "johndoe",
    "email": "4YH0T@example.com"
  },
  "trip_id": 1,
  "trip": {
    "name": "Trip to Paris",
    "description": "Visit the Eiffel Tower and the Louvre Museum",
    "start_date": "2022-01-01",
    "end_date": "2022-01-05",
    "country": {
      "name": "France",
      "cities": []
    }
  }
}
```

## City:

```json
{
  "id": 1,
  "name": "Paris",
  "country_id": 1,
  "latitude": 48.8566,
  "longitude": 2.3522
}
```
