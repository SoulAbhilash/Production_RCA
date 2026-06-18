# Kubernetes manifests

The **demo-app** Deployment runs **Postgres 16 as a sidecar** in the same pod as the API. The app uses **`DATABASE_URL` → `127.0.0.1:5432`** (see `deploy/k8s/app/secret.yaml.example`). Keep **`replicas: 1`** if you use the **ReadWriteOnce** PVC.

Apply order (lab):

1. `kubectl apply -f deploy/k8s/app/namespace.yaml`
2. `kubectl apply -f deploy/k8s/app/rbac.yaml`
3. `kubectl apply -f deploy/k8s/app/configmap.yaml`
4. `kubectl apply -f deploy/k8s/app/postgres-pvc.yaml`  
   - Requires a **default StorageClass** (typical on EKS). If you skip persistence, see **Ephemeral Postgres** below instead of this step.
5. Create DB secret (see `deploy/k8s/app/secret.yaml.example`) — must include **`POSTGRES_PASSWORD`** and **`DATABASE_URL`** with the **same** password and host **`127.0.0.1`**:  
   `kubectl -n poc create secret generic demo-app-db \`  
   `  --from-literal=POSTGRES_PASSWORD='...' \`  
   `  --from-literal=DATABASE_URL='postgresql+psycopg://app:...@127.0.0.1:5432/app'`  
   Or copy `secret.yaml.example` to a **local** untracked `secret.yaml`, edit values, then apply.
6. Edit `deployment.yaml` image to your ECR URL (or use the GitHub deploy workflow `sed`), then:  
   `kubectl apply -f deploy/k8s/app/deployment.yaml`  
   `kubectl apply -f deploy/k8s/app/service.yaml`
7. Agent: `kubectl apply -f deploy/k8s/agent/`

Dry-run (no cluster required for client-side validation):

```bash
kubectl apply -f deploy/k8s/app/ --dry-run=client
kubectl apply -f deploy/k8s/agent/ --dry-run=client
```

**Note:** Do not commit real `secret.yaml` with credentials.

## Ephemeral Postgres (no PVC)

If you have **no StorageClass** or want a **throwaway** DB (data lost when the pod is deleted):

1. Do **not** apply `postgres-pvc.yaml`.
2. In `deployment.yaml`, replace the `postgres-data` volume with:

```yaml
      volumes:
        - name: postgres-data
          emptyDir: {}
```

3. Keep the **postgres** container `PGDATA` as in the default `deployment.yaml` (data under `/var/lib/postgresql/data/pgdata` on the volume).
