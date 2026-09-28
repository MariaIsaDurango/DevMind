# Referencia de API: Servicio de Usuarios

Repositorio: backend-core
Tecnología: FastAPI

## Autenticación

Todas las peticiones requieren la cabecera `Authorization: Bearer <token>`. Los tokens expiran a las 24 horas.

## Listar usuarios

Endpoint: `GET /api/v1/users`

Parámetros opcionales: `page` (por defecto 1) y `limit` (por defecto 20, máximo 100).

## Crear usuario

Endpoint: `POST /api/v1/users`

Cuerpo requerido: `email` y `name`. Devuelve `201` con el usuario creado, o `409` si el email ya existe.

## Límites de uso

Cada token permite 100 peticiones por minuto. Al superarlo, la API responde `429 Too Many Requests`.
