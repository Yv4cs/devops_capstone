# DevOps Capstone — End-to-End CI/CD Pipeline

A learning project that takes a small web app through the full DevOps lifecycle:
**Docker → CI (GitHub Actions) → Kubernetes → GitOps → Terraform/Ansible/AWS → Prometheus & Grafana.**

This repository currently implements **Phase 1: the application + containerization.**

## What's here (Phase 1)
A simple "Notes" web app:
- **Backend:** Python (Flask) REST API, served by gunicorn
- **Database:** PostgreSQL
- **Frontend:** a single HTML page

## Architecture (Phase 1)
```
Browser ──► Flask app (port 5000) ──► PostgreSQL
```

## Run it locally
Requires Docker.
```bash
docker compose up --build
```
Then open http://localhost:5000

To stop and remove everything:
```bash
docker compose down -v
```

## Endpoints
| Method | Path | Description |
|---|---|---|
| GET  | `/`          | Web UI |
| GET  | `/health`    | Health check (used later by Kubernetes probes) |
| GET  | `/api/notes` | List notes |
| POST | `/api/notes` | Create a note — body: `{"content": "..."}` |

## Project structure
```
.
├── app/
│   ├── app.py            # Flask application
│   ├── requirements.txt  # Python dependencies
│   ├── Dockerfile        # Container image definition
│   └── templates/
│       └── index.html    # Frontend
├── docker-compose.yml    # Runs app + database locally
└── README.md
```

## Roadmap
- [x] Phase 1 — App + Docker
- [ ] Phase 2 — CI with GitHub Actions (build, test, security scan, push image)
- [ ] Phase 3 — Deploy to Kubernetes (kind / minikube)
- [ ] Phase 4 — GitOps with Argo CD
- [ ] Phase 5 — Terraform + Ansible + AWS
- [ ] Phase 6 — Monitoring with Prometheus & Grafana
