# Privacidad, seguridad y ética

## 1. Clasificación de los datos
Documentación técnica interna (guías de despliegue, APIs, infraestructura). Sensibilidad: **media**. Puede contener nombres de servicios, URLs internas o detalles de infraestructura, pero no datos personales.

## 2. API comercial vs. modelo local
| Criterio | API comercial | Modelo local |
|---|---|---|
| Calidad de respuesta | | |
| Privacidad (los datos salen de la empresa) | | |
| Coste | | |
| Latencia / recursos | | |

**Decisión del equipo:** _pendiente_

## 3. Riesgos de fuga de información (Data Leakage)
- Fragmentos de documentos enviados a un proveedor externo en el prompt.
- Claves API o secretos presentes en la documentación indexada.
- Registros (logs) que almacenen preguntas o contexto.

## 4. Medidas
- Secretos solo en `.env` (ignorado por Git).
- Revisión de los documentos antes de indexar (no indexar credenciales).
- Acceso a la base vectorial restringido.

## 5. Linaje del dato y explicabilidad
Cada respuesta devuelve las fuentes (`source`, `section`, texto original), lo que permite auditar de dónde proviene la información.

## 6. Reflexión ética
_Sesgos, uso responsable, límites del sistema y supervisión humana._
