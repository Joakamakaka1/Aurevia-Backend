# SERVICE AUREVIA

## Descripcion TODO

Crear nuevos servicios:

- Crear Friendship
- Crear Comment
- Crear City

(Posibles cambios en el futuro para mejorar la flexibilidad del servicio en User, Trip y Country)

Controlar errores en los servicios

- User

  - Email ya registrado
  - Username ya registrado
  - User no encontrado
  - Password incorrecta
  - Username demasiado corto
  - Email no valido
  - Password demasiado corto
  - Password no coincide
  - Rol no valido
  - Rol sin permiso de admin
    ...

- Trip

  - Trip no encontrado
  - Viaje ya existente por la fecha de inicio y el usuario
  - Fecha de inicio posterior a la de fin
  - Viaje no encontrado por el nombre
  - Viaje no encontrado por la fecha de inicio

- Country

  - Pais no encontrado
  - Pais duplicado

- Friendship

  - Amigo no encontrado
  - Amigo duplicado

- Comment

  - Comentario no encontrado
  - Comentario duplicado
  - Comentario demasido corto
  - Comentario demasido largo

- City

  - Ciudad no encontrada
  - Ciudad duplicada
