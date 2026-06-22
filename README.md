# Jenkins + SonarQube + Argo CD Setup

This repository includes a combined local developer setup:
- Jenkins on Docker Compose (`localhost:8080`)
- SonarQube on Docker Compose (`localhost:9000`)
- Argo CD installed into Kubernetes via a local Helm chart copy

## Prerequisites

- Docker Desktop installed and running
- Kubernetes enabled in Docker Desktop
- `kubectl` installed and configured for `docker-desktop`
- `helm` installed and available in PowerShell
- `git` installed and configured with your repository

## Project overview

This repository contains a lightweight Python-based DevOps demo app that includes:

- A Flask ML backend in `flask-app/`
- Redis for cache/state management
- MongoDB for storing training and ingestion data
- Kafka and Zookeeper for event ingestion
- A Helm chart for deploying the Flask backend in Kubernetes (`k8s/flask-app`)
- Kubernetes manifests for Redis, MongoDB, Kafka, and Zookeeper (`k8s/dependencies/`)
- A Jenkins pipeline (`Jenkinsfile`) for building, pushing, and promoting the container image
- An Argo CD application manifest (`k8s/argocd-app.yaml`) for GitOps deployment

## Git workflow

Use the repository history and Git remote to trigger CI/CD from Jenkins and Argo CD.

From `d:\cicd`:

```powershell
git init
git add .
git commit -m "Initial Flask ML backend with Jenkins + Argo CD"
git remote add origin https://github.com/<your-org>/<your-repo>.git
git push -u origin main
```

After the repository is pushed, Jenkins can track changes and automatically deploy via Argo CD.

## CI/CD pipeline

This repo includes a `Jenkinsfile` that builds the Flask app image, pushes it to Docker Hub, and triggers an Argo CD sync.

- Jenkins builds the app from `flask-app/Dockerfile`
- Image name is configured in `Jenkinsfile` via `DOCKER_HUB_REPO`
- Argo CD deployment is defined in `k8s/argocd-app.yaml`
- The Helm chart source is `k8s/flask-app`

### Jenkins setup

1. Open Jenkins at `http://localhost:8080`
2. Create credentials for:
   - `docker-hub-username`
   - `docker-hub-password`
   - `argocd-password`
3. Create a pipeline job and point it to this repository.
4. Use the repository branch (`main` or `master`) containing this `Jenkinsfile`.

### Argo CD setup

1. Install Argo CD with the local chart from `k8s/argocd-chart/argocd-chart-local`.
2. Update `k8s/argocd-app.yaml` with your Git repository URL and branch.
3. Apply the Argo CD application manifest:

```powershell
kubectl apply -f d:\cicd\k8s\argocd-app.yaml
```

4. In the Argo CD UI, sync the `flask-app` application or allow automated sync.

> If your Kubernetes cluster cannot pull the local Docker image, push it to Docker Hub and update `k8s/flask-app/values.dockerhub.yaml` with your repository path.

## Start Jenkins and SonarQube

From `d:\cicd`:

```powershell
docker compose up -d
```

Wait until both services are healthy, then open:

- Jenkins: `http://localhost:8080`
- SonarQube: `http://localhost:9000`

If Jenkins cannot reach SonarQube from inside its container, use this SonarQube URL in Jenkins configuration:

- `http://host.docker.internal:9000`

## Use the local Argo CD Helm chart

A local chart copy is stored at:

- `d:\cicd\k8s\argocd-chart\argocd-chart-local`

### Install from the local chart

```powershell
cd d:\cicd\k8s\argocd-chart\argocd-chart-local
helm dependency update
helm upgrade --install argocd . --namespace argocd --create-namespace
```

### Verify Argo CD deployment

```powershell
kubectl -n argocd get pods
kubectl -n argocd get svc
```

You should see `argocd-server`, `argocd-repo-server`, `argocd-redis`, `argocd-application-controller`, and `argocd-dex-server` services.

## Access Argo CD UI

Run this port-forward command and keep it running in a separate terminal:

```powershell
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

Open:

- `https://localhost:8080`

### Get the default admin password

```powershell
$secret = kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}'
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secret))
```

Login user: `admin`

## Create a second Argo CD user

To add a local Argo CD user, update the secret and RBAC config:

1. Generate a bcrypt password hash and encode it in base64.
2. Patch the Argo CD secret:

```powershell
$username = 'newuser'
$password = 'YourPassword123'
$hash = python -c "import bcrypt,sys; print(bcrypt.hashpw(sys.argv[1].encode(), bcrypt.gensalt()).decode())" $password
$hash_b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($hash))
kubectl -n argocd patch secret argocd-secret -p ("{`"data`":{`"accounts.$username.password`":`"$hash_b64`"}}")
```

3. Grant the new user a role in `argocd-rbac-cm`:

```powershell
kubectl -n argocd patch configmap argocd-rbac-cm --type merge -p @"
{"data":{"policy.csv":"p, role:admin, applications, *, */*\n g, user:$username, role:admin\n"}}
"@
```

4. Restart Argo CD server:

```powershell
kubectl -n argocd rollout restart deployment argocd-server
```

## Troubleshooting

- If `helm` is not found, restart PowerShell after installation or add the Helm binary path to your user PATH.
- If `helm dependency update` fails, make sure all `values.yaml` files in the chart are UTF-8 encoded and the chart dependencies exist under `charts/`.
- If Argo CD pods do not become ready, run:

```powershell
kubectl -n argocd get pods -o wide
kubectl -n argocd describe pod <pod-name>
```

- If the local chart directory is locked, close editors that have the chart files open before deleting or replacing files.

## Notes

- Use `host.docker.internal` inside Jenkins to reach SonarQube.
- The local Argo CD chart deploys the standard Argo CD components: `argocd-server`, `argocd-repo-server`, `argocd-application-controller`, `argocd-dex-server`, and `argocd-redis`.
- If Docker Desktop Kubernetes is broken, fix it first before installing Argo CD.

## Local Flask ML Backend

This repository now includes a lightweight Flask ML backend in `flask-app` plus local Kubernetes manifests for Redis, MongoDB, Zookeeper, and Kafka.

### Build and publish the app image

From `d:\cicd`:

```powershell
cd d:\cicd\flask-app
docker build -t rishiapp:latest .
```

If your Kubernetes cluster cannot access the local image, tag and push it to a Docker Hub repository:

```powershell
docker tag rishiapp:latest <your-dockerhub-username>/rishiapp:latest
docker push <your-dockerhub-username>/rishiapp:latest
```

Then update `k8s/flask-app/values.yaml` to use your Docker Hub repository if needed.

### Deploy dependencies to Kubernetes

```powershell
kubectl apply -f d:\cicd\k8s\dependencies\
```

### Install the Flask app Helm chart

```powershell
helm upgrade --install flask-app d:\cicd\k8s\flask-app --namespace devops-app --create-namespace
```

### Verify the Flask ML backend

```powershell
kubectl get pods,svc -n devops-app
```

Then access the backend routes using port-forwarding or a local ingress:

```powershell
kubectl -n devops-app port-forward svc/flask-app-flask-ml-backend 5000:5000
```

Available endpoints:

- `GET /health`
- `POST /ingest` to send event data into MongoDB and Kafka
- `POST /train` to train a model from MongoDB data
- `POST /predict` to request a prediction
- `GET /status` to inspect cached model state and last prediction

For a Docker Desktop local cluster, the local image `rishiapp:latest` is usually available directly in Kubernetes. If not, push it to Docker Hub or use a local registry.

## Install a specific Argo CD chart version and upgrade

You can install a specific chart version from the official Helm repo or pull a local copy.

From the Helm repo (recommended):

```powershell
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
# list available versions
helm search repo argo/argo-cd --versions
# install a specific version
helm upgrade --install argocd argo/argo-cd --version 3.4.1 --namespace argocd --create-namespace
```

From a local chart copy (keeps a repository-local copy you can modify):

```powershell
helm pull argo/argo-cd --untar --untardir d:\cicd\k8s\argocd-chart --version 3.4.1
Rename-Item d:\cicd\k8s\argocd-chart\argo-cd d:\cicd\k8s\argocd-chart\argocd-chart-local
cd d:\cicd\k8s\argocd-chart\argocd-chart-local
helm dependency update
helm upgrade --install argocd . --namespace argocd --create-namespace
```

To upgrade to a newer chart version from the repo:

```powershell
helm repo update
helm upgrade argocd argo/argo-cd --version 3.5.0 --namespace argocd
kubectl -n argocd rollout status deployment argocd-argocd --timeout=5m
```

Check release details:

```powershell
helm list -n argocd
helm status argocd -n argocd
```

Notes:
- Always run `helm dependency update` when using local charts if `Chart.yaml` declares dependencies.
- Keep `values.yaml` UTF-8 encoded; editors that save UTF-16 can break Helm parsing.
