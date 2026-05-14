# ModelServe

> MLOps with Cloud Season 2 — Capstone Exam

ModelServe is an MLflow-powered fraud detection model serving platform that provides a REST API for real-time credit card fraud predictions. The system uses Feast for feature retrieval, Redis for caching, and includes full observability with Prometheus metrics and Grafana dashboards.

## Prerequisites

- **Docker** & Docker Compose
- **Python 3.10+**
- **AWS CLI** (for ECR push/pull)
- **Pulumi** (for infrastructure provisioning)

## Quick Start (Local Development)

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/MLOps-S2-Exam1-modelserve-capstone-starter.git
cd MLOps-S2-Exam1-modelserve-capstone-starter

# Start all services
docker compose up -d

# Access services
# - FastAPI:    http://localhost:8000
# - MLflow:     http://localhost:5000
# - Prometheus: http://localhost:9090
# - Grafana:    http://localhost:3000 (admin / admin123)
```

## REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Returns service status and model version |
| POST | `/predict` | Accepts `entity_id`, returns fraud prediction with probability |
| GET | `/predict/<id>?explain=true` | Returns prediction with feature values |
| GET | `/metrics` | Prometheus metrics endpoint |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MLFLOW_TRACKING_URI` | MLflow server URL | `http://mlflow:5000` |
| `REDIS_HOST` | Redis cache host | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `POSTGRES_HOST` | PostgreSQL host | `postgres` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | PostgreSQL user | `mlflow` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `mlflow_password` |
| `POSTGRES_DB` | PostgreSQL database | `mlflow` |
| `GF_SECURITY_ADMIN_USER` | Grafana admin username | `admin` |
| `GF_SECURITY_ADMIN_PASSWORD` | Grafana admin password | `admin123` |

## GitHub Secrets

| Secret | Purpose |
|--------|---------|
| `AWS_ACCESS_KEY_ID` | AWS credentials for ECR and EC2 access |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for ECR and EC2 access |
| `EC2_SSH_KEY` | Private SSH key for EC2 instance access |
| `EC2_HOST` | EC2 instance hostname or IP address |
| `EC2_USERNAME` | SSH username for EC2 (e.g., `ubuntu`) |

## Engineering Documentation

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full architecture documentation, ADRs, runbook, and known limitations.

## Dataset

[Credit Card Transactions Fraud Detection](https://www.kaggle.com/datasets/kartik2112/fraud-detection) — Simulated credit card transactions generated using Sparkov. Use `fraudTrain.csv` (~1.3M rows, 22 features). Entity key: `cc_num`.

---

*MLOps with Cloud Season 2 — Capstone: ModelServe | Poridhi.io*