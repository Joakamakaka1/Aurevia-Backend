# MODELS AUREVIA

## Descripcion TODO

Crear entidades:

- Crear Friendship
- Crear Comment
- Crear City

Relacionar entidades

- User con friendship
- User con comment
- Trip con comment
- Country con city

Decidir atributos

- Friendship

  - id
  - user_id
  - friend_id
    ...

- Comment

  - id
  - user_id
  - trip_id
  - content
    ...

- City
  - id
  - name
  - country_id
  - latitude
  - longitude
    ...

!! -- City y Country deben de usar atributos de las APIS publicas ( REST Countries y GeoNames )
