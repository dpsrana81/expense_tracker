# Deployment Guide (AWS, Docker, Kubernetes, CI/CD)

This expands on README section 7 with concrete commands, mirroring `DEVELOPMENT_GUIDE.md` phases 6-12 from the original project guide.

## Phase 6 — Containerize with Docker

```bash
cd backend
docker build -t expense-tracker-backend .
docker run -p 5000:5000 --env-file .env expense-tracker-backend
```

Or bring up the full stack (MySQL + backend + Nginx):

```bash
docker compose up --build -d
docker compose logs -f backend
```

## Phase 7 — Deploy to AWS EC2 with RDS

1. Launch a MySQL 8 RDS instance (`db.t3.micro` is enough for a demo). Note the endpoint, username, password.
2. Launch an EC2 instance (Ubuntu 22.04, `t3.small`+), open inbound ports 80/443/22 in its security group, and allow EC2 → RDS on port 3306 in the RDS security group.
3. On the EC2 instance:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-plugin
   git clone <your-repo-url> /opt/expense-tracker
   cd /opt/expense-tracker
   cp backend/.env.example backend/.env
   # edit backend/.env: DATABASE_URL -> your RDS endpoint, real SECRET_KEY/JWT_SECRET_KEY
   sudo docker compose up --build -d
   ```
4. Visit `http://<ec2-public-ip>`.

## Phase 8 — Nginx + HTTPS

Nginx config is already at `nginx/nginx.conf` and wired into `docker-compose.yml`. To add HTTPS once you have a domain pointed at the EC2 IP:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Phase 9 — CI/CD

**GitHub Actions** (`.github/workflows/ci-cd.yml`): on every push to `main` it installs dependencies, runs tests, builds and pushes the Docker image to Docker Hub, then SSHes into EC2 to pull and restart. Required repo secrets:

- `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`
- `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`

**Jenkins** (`Jenkinsfile`): equivalent pipeline (checkout → test → build → push → deploy) for teams using a self-hosted Jenkins server. Configure the `dockerhub-credentials` and `ec2-ssh-key` credentials in Jenkins first.

## Phase 10 — Kubernetes (optional, instead of a single EC2 box)

```bash
kubectl apply -f kubernetes/secrets-and-ingress.yaml   # edit real values first
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl get pods -w
```

This gives you 3 replicas behind a `ClusterIP` Service, a `HorizontalPodAutoscaler` (2-6 pods on 70% CPU), and an `Ingress` for TLS termination via cert-manager. MySQL itself is expected to be RDS, not run inside the cluster.

## Phase 11 — Monitoring (Prometheus + Grafana + CloudWatch)

```bash
docker compose -f docker-compose.yml -f monitoring/docker-compose.monitoring.yml up -d
```

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (default login `admin` / `admin`, change immediately)

To scrape real Flask metrics, add `prometheus-flask-exporter` to `requirements.txt` and 2 lines to `app/__init__.py` (see the comment at the bottom of `monitoring/prometheus.yml`). For AWS-native monitoring, install the CloudWatch Agent on the EC2 instance to ship CPU/memory/disk metrics and container logs.

## Phase 12 — Documentation & Presentation

- `README.md` — overview, setup, structure
- `docs/API.md` — full endpoint reference
- `docs/DEPLOYMENT.md` — this file
- Resume bullet points are listed in the original `README.md` "Resume Highlights" section — all of them are now backed by real, working code in this repo (JWT auth, Dockerized services, CI/CD pipeline, Kubernetes manifests, Prometheus/Grafana monitoring).
