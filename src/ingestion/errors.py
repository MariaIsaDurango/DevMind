"""Excepciones propias del módulo de ingesta.

P3 debe capturar IngestionError en /upload y devolver 400 con str(error).
Cualquier otra excepción no capturada aquí (bug real) debe seguir subiendo
como 500, así que NO se atrapa todo con un except genérico en el backend.
"""


class IngestionError(Exception):
    """Error esperable al procesar un archivo: formato inválido, archivo
    corrupto, extensión no soportada, etc. Seguro de mostrar al usuario."""
