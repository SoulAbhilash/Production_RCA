# Kubernetes manifests

Apply order (lab):

1. `kubectl apply -f deploy/k8s/app/namespace.yaml`
2. `kubectl apply -f deploy/k8s/app/rbac.yaml`
3. `kubectl apply -f deploy/k8s/app/configmap.yaml`
4. Create DB secret (see `deploy/k8s/app/secret.yaml.example`):  
   `kubectl -n poc create secret generic demo-app-db --from-literal=DATABASE_URL='...'`  
   Or copy `secret.yaml.example` to a **local** untracked `secret.yaml`, edit values, then apply.
5. Edit `deployment.yaml` image to your ECR URL, then:  
   `kubectl apply -f deploy/k8s/app/deployment.yaml`  
   `kubectl apply -f deploy/k8s/app/service.yaml`
6. Agent: `kubectl apply -f deploy/k8s/agent/`

Dry-run (no cluster required for client-side validation):

```bash
kubectl apply -f deploy/k8s/app/ --dry-run=client
kubectl apply -f deploy/k8s/agent/ --dry-run=client
```

**Note:** Do not commit real `secret.yaml` with credentials.
