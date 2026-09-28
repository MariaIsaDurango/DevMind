# Runbook de infraestructura

Repositorio: infra-platform
Tecnología: Kubernetes

## Reinicio de un servicio

Para reiniciar un servicio en el clúster de Kubernetes:

```bash
kubectl rollout restart deployment/<nombre-servicio> -n <namespace>
```

Comprobar el estado con `kubectl rollout status deployment/<nombre-servicio> -n <namespace>`.

## Escalado manual

Para escalar un servicio manualmente:

```bash
kubectl scale deployment/<nombre-servicio> --replicas=<n> -n <namespace>
```

El máximo permitido en staging es de 3 réplicas.

## Consulta de logs

Para ver los logs de un pod: `kubectl logs <pod> -n <namespace> --tail=100`. Los logs históricos están disponibles en Grafana Loki con retención de 14 días.
