#!/bin/bash
set -e

COMMIT_SHA=$(git rev-parse --short HEAD)
IMAGE="demo-app:${COMMIT_SHA}"

echo "=== Step 1: Build image ==="
docker build -t ${IMAGE} ./app

echo "=== Step 2: Import to K3s ==="
sudo docker save ${IMAGE} | sudo k3s ctr images import -

echo "=== Step 3: Update staging deployment ==="
cd k8s/overlays/staging
kustomize edit set image demo-app=${IMAGE}
kustomize build . | kubectl apply -f -

echo "=== Step 4: Wait for rollout ==="
kubectl rollout status deployment/staging-demo-app -n staging

echo "=== Step 5: Verify ==="
kubectl get pods -n staging

echo "=== Done ==="
