# AegisOps — Infrastructure Monitoring & Incident Response API

AegisOps is a lightweight, cross-platform infrastructure monitoring and incident-management API built with Python and FastAPI. It monitors system resources, checks network and web service availability, records probe history, manages incidents, and simulates remediation actions safely.

The project demonstrates practical backend engineering, REST API development, persistence, API-key authentication, automated testing, and Linux/Windows compatibility.

## Features

- **System Metrics** — Monitor CPU, memory, and disk usage.
- **TCP Connectivity Checks** — Test whether a host and port are reachable.
- **DNS Resolution Checks** — Verify hostname resolution.
- **HTTP Health Probes** — Check web endpoint availability and response status.
- **TLS Certificate Monitoring** — Inspect TLS certificates and certificate expiry information.
- **Probe History** — Store monitoring results in a database using SQLAlchemy.
- **Incident Management** — Create incidents from failed probes, prevent duplicate open incidents, and resolve existing incidents.
- **API-Key Authentication** — Protect API routes with an `X-API-Key` header.
- **Safe Remediation Simulation** — Test remediation workflows without modifying the host system.
- **Automated Testing** — Validate core functionality with pytest.
- **Code Quality** — Enforce Python linting with Ruff.
- **Cross-Platform Support** — Develop and validate on Windows and Linux/WSL.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| FastAPI | REST API framework |
| SQLAlchemy | Database access and ORM |
| SQLite | Lightweight local persistence |
| Pydantic Settings | Environment-based configuration |
| psutil | System resource metrics |
| httpx | HTTP health checks |
| socket / ssl | TCP, DNS, and TLS diagnostics |
| pytest | Automated testing |
| Ruff | Linting and code quality |
| GitHub Actions | Continuous integration |

## Architecture

```text
                 Monitoring Clients
                         |
                         v
                 FastAPI Application
                         |
                 API-Key Authentication
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
        System Metrics  Network     Web Probes
                        Probes      HTTP / TLS
             |           |           |
             +-----------+-----------+
                         |
                         v
                  Probe History
                         |
                         v
                     Database
                         |
                         v
                 Incident Manager
                         |
                         v
                Remediation Simulator
```

## Project Structure

```text
AegisOps/
├── aegisops/
│   ├── api/
│   │   └── routes.py
│   ├── services/
│   │   ├── incident_manager.py
│   │   ├── network_probes.py
│   │   ├── probe_history.py
│   │   ├── remediation.py
│   │   ├── system_metrics.py
│   │   └── web_probes.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── security.py
├── tests/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

*The tree represents the intended project layout; adjust it to match the files actually present in your repository.*

## Getting Started

### Prerequisites

- Python 3.10 or later, subject to dependency compatibility.
- Git.
- Windows, Linux, or WSL Ubuntu.

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AegisOps
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / WSL Ubuntu**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and configure your local development settings.

Example configuration:

```dotenv
APP_NAME=AegisOps
ENVIRONMENT=development
DATABASE_URL=sqlite:///./aegisops.db
AEGISOPS_API_KEY=replace-with-a-private-local-development-key
```

Use a unique, private API key for your environment. Never commit `.env` or real credentials to GitHub.

### 5. Start the API

```bash
python -m uvicorn aegisops.main:app --reload
```

The service will normally be available at:

- **Interactive API documentation:** `http://127.0.0.1:8000/docs`
- **OpenAPI schema:** `http://127.0.0.1:8000/openapi.json`
- **Root endpoint:** `http://127.0.0.1:8000/`
- **Health endpoint:** `http://127.0.0.1:8000/health`

Confirm the health endpoint path against your current application if it differs.

## API Usage

Protected endpoints require the `X-API-Key` request header.

### Check API status

```bash
curl http://127.0.0.1:8000/api/v1/status \
  -H "X-API-Key: YOUR_LOCAL_API_KEY"
```

### Check system metrics

```bash
curl http://127.0.0.1:8000/api/v1/system/metrics \
  -H "X-API-Key: YOUR_LOCAL_API_KEY"
```

### Test TCP connectivity

```bash
curl -X POST http://127.0.0.1:8000/api/v1/probes/tcp \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_LOCAL_API_KEY" \
  -d '{"host":"example.com","port":443}'
```

### Test DNS resolution

```bash
curl -X POST http://127.0.0.1:8000/api/v1/probes/dns \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_LOCAL_API_KEY" \
  -d '{"hostname":"example.com"}'
```

Use the interactive documentation at `/docs` to inspect the exact request schemas and available endpoints.

## Incident Management

AegisOps records failed probes and can create incidents associated with monitoring failures. Repeated failures can reuse an existing open incident rather than creating duplicate incidents. Resolved incidents record their resolution status and timestamp.

Probe history and incidents can be inspected through the protected API routes.

## Remediation Safety

AegisOps includes simulated remediation actions for workflows such as:

- Simulated DNS cache clearing.
- Simulated service restart.
- Simulated probe retry.

These actions are simulations only. They do not modify the operating system or restart actual services.

## Testing

Run the automated tests:

```bash
python -m pytest -v
```

Run Ruff:

```bash
python -m ruff check aegisops tests
```

The project previously passed **23 tests in WSL Ubuntu**. Run the commands above on the latest revision to verify the current results.

## Continuous Integration

The GitHub Actions workflow in `.github/workflows/ci.yml` can run linting and automated tests on pushes and pull requests.

Check the **Actions** tab of your GitHub repository to verify that the workflow completes successfully.

## Security Notes

- Keep API keys and other credentials out of source control.
- Use `.env` for local secrets and commit only `.env.example`.
- Use authorized hosts and endpoints when running probes.
- Avoid exposing the development server directly to the public internet.
- Review dependency versions and security updates before production deployment.

## Future Improvements

- Configurable monitoring schedules.
- Alert integrations for incident notifications.
- Additional database backends.
- Dashboard for metrics and incident history.
- Structured logging and application tracing.
- Performance benchmarks and load testing.
- Containerized deployment, if needed.

## Author

**Yash Kalbhile**

Python Backend Development · FastAPI · SQLAlchemy · Monitoring · API Security · Automated Testing

## License

Add a `LICENSE` file with your chosen license before distributing the project for reuse.
