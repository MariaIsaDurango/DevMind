# Guía de despliegue CI/CD

Repositorio: backend-core
Tecnología: GitLab CI

## Entornos de Staging

Para desplegar el servicio en staging se hace push a la rama `develop`. El pipeline de GitLab CI se ejecuta automáticamente con las etapas build, test y deploy-staging.

Comando:

```bash
git push origin develop
```

El despliegue a staging no requiere aprobación manual. Tras finalizar, verificar el endpoint `/health` del servicio en el entorno de staging.

## Entornos de Producción

El despliegue a producción se hace desde la rama `main`. La etapa `deploy-production` es manual y requiere la aprobación de un miembro del equipo de DevOps.

## Rollback

Para revertir un despliegue, ejecutar manualmente el job `rollback` del último pipeline exitoso. El rollback restaura la imagen Docker anterior en menos de cinco minutos.
