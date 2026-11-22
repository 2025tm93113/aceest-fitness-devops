# ACEest Fitness & Gym - Flask and DevOps CI/CD

**Student:** Yadav Suraj Gayaprasad  
**BITS ID:** 2025TM93113  
**Course:** Introduction to DevOps (CSIZG514 / SEZG514)  
**GitHub Repository:** https://github.com/2025tm93113/aceest-fitness-devops  
**Docker Hub Repository:** https://hub.docker.com/r/2025tm93113/aceest-fitness  
**Live Minikube Endpoint:** `http://127.0.0.1:59189/`

## Baseline adaptation & incremental releases

This application adapts the supplied `Aceestver-1.0.py` Tkinter desktop
application to Flask and evolves it across incremental Git-tagged releases
(`v1.0`, `v2.0`, `v3.0`). All ten instructor-provided desktop reference versions
(`Aceestver-1.0.py` through `Aceestver-3.2.4.py`) are preserved unchanged in
`original/`. Baseline program names, workout text, diet text, colors, and site
metrics are preserved. Tkinter widgets are replaced by a browser form and HTML
display, extended with JSON APIs for health checks, version reporting, calorie
estimation, BMI categorization, and AI-style program recommendations.

A test parses `original/Aceestver-1.0.py` with Python AST (without launching
Tkinter) and compares its complete program dictionary with `programs.py`. The
capacity of 150 users and break-even of 250 members are separate baseline
reference metrics; the application displays both without attempting to
reinterpret them. This project displays instructor-provided diet plans; it does
not provide personalized medical or nutrition advice.

## Project structure

- `app.py`: application factory, HTTP routes, calorie/BMI/recommendation logic (`v3.0`).
- `programs.py`: baseline program data and site metrics.
- `templates/index.html`: responsive dark/gold web interface.
- `original/`: unchanged instructor reference versions (`Aceestver-1.0.py` to `Aceestver-3.2.4.py`).
- `tests/`: logic, HTTP, UI-content, API, and baseline-fidelity tests (34 tests).
- `Dockerfile`: non-root multi-stage testing and runtime images.
- `.github/workflows/main.yml`: push/PR CI pipeline.
- `Jenkinsfile`, `jenkins/`: 7-stage automated Jenkins CI/CD pipeline and local Docker Compose setup.
- `sonar-project.properties`: SonarQube static analysis configuration.
- `reports/sonarqube-report.json`: exported SonarQube Quality Gate metrics report.
- `k8s/`: Kubernetes manifests for Rolling Update, Blue-Green, Canary, Shadow, and A/B Testing.

## Prerequisites and local execution

Install Python 3.12+, Git, Docker with Linux containers, Docker Compose v2,
Minikube, and `kubectl`. Run all commands from the repository root.

```sh
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate on macOS/Linux:

```sh
source .venv/bin/activate
```

After activation:

```sh
python -m pip install -r requirements-dev.txt
python app.py
```

Open http://localhost:5000. Choose Fat Loss, Muscle Gain, or Beginner and
select View Plan. The workout and nutrition panels display the original content.
Stop with Ctrl+C. Flask's development server is for local use only.

## API

| Method | Endpoint | Release | Result |
| --- | --- | --- | --- |
| GET | `/` | v1.0 | HTML program-selection interface |
| GET | `/?program=Beginner%20%28BG%29` | v1.0 | Selected program in HTML |
| GET | `/health` | v1.0+ | Health and version JSON |
| GET | `/api/programs` | v1.0 | All original program data |
| GET | `/api/program?name=Beginner%20%28BG%29` | v1.0 | One program |
| GET | `/api/metrics` | v1.0 | Original site metrics |
| GET | `/api/version` | v2.0 | Application name and active version |
| POST | `/api/calories` | v2.0 | Daily calorie estimate (`program`, `weight`) |
| POST | `/api/bmi` | v2.0 | BMI score and category (`weight`, `height`) |
| POST | `/api/recommend` | v3.0 | AI-style program recommendation (`goal`) |

Missing or invalid parameters return 400; unknown API programs and unknown
routes return JSON 404.

## Manual tests and lint

```sh
python -m compileall -q app.py programs.py tests
ruff check app.py programs.py tests
python -m pytest -v --junitxml=reports/junit.xml --cov-report=xml:reports/coverage.xml
```

Pytest uses fresh Flask test-client fixtures. All **34 tests** verify preserved
source data, all three selections, HTML content, API responses, calorie/BMI/recommendation
endpoints, missing/unknown inputs, metrics, invalid methods, unknown routes,
application configuration, and protection against mutation of lookup results.
Coverage includes branches and reaches **100.0%** across `app.py` and `programs.py`
(threshold: 90%).

## Docker and Docker Hub

```sh
docker build --target test -t aceest:test .
docker run --rm aceest:test python -m pytest -v
docker build --target runtime -t 2025tm93113/aceest-fitness:v3.0 .
docker run -d --name aceest-app -p 127.0.0.1:5000:5000 2025tm93113/aceest-fitness:v3.0
docker logs aceest-app
docker exec aceest-app id
docker inspect --format="{{.State.Health.Status}}" aceest-app
```

Stop the local Flask server first. Wait about 30 seconds for health status.
Open http://localhost:5000. The application runs as non-root UID 10001 under
Gunicorn.

```sh
docker rm -f aceest-app
```

All incremental application versions are published to Docker Hub at
`2025tm93113/aceest-fitness` with tags `v1.0`, `v2.0`, `v3.0`, `latest`, and
Jenkins build tags (`build-3`).

## Static code quality with SonarQube

SonarQube analyzes `app.py` and `programs.py` using `sonar-project.properties`
(excluding legacy desktop scripts in `original/` and infrastructure folders) and
ingests `reports/coverage.xml`.

```powershell
docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community
docker run --rm -e SONAR_HOST_URL="[http://host.docker.internal:9000](http://host.docker.internal:9000)" -e SONAR_TOKEN="<TOKEN>" -v "${PWD}:/usr/src" sonarsource/sonar-scanner-cli
```

Verified SonarQube Quality Gate (`reports/sonarqube-report.json`):
- **Quality Gate:** `OK` (PASSED)
- **Bugs:** `0`
- **Vulnerabilities:** `0`
- **Duplicated Lines:** `0.0%`
- **Coverage:** `100.0%`
- **Code Smells:** `1`

## GitHub Actions

Every push and pull request triggers `.github/workflows/main.yml`; a manual
trigger is also provided. It checks out source, installs validation tools,
compiles Python, runs Ruff, builds runtime and test images, executes Pytest
inside the test container, exports JUnit and coverage XML artifacts, and
smoke-tests the runtime health endpoint.

## Jenkins CI/CD installation and configuration

This local setup uses a non-root Jenkins controller with a separate TLS-enabled
Docker-in-Docker daemon.

```sh
docker compose -f jenkins/compose.yml up -d --build
docker compose -f jenkins/compose.yml exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open http://localhost:8080, unlock Jenkins, install suggested plugins, and add
two Global Credentials:
1. `sonar-token` (Secret text): SonarQube analysis token.
2. `dockerhub-creds` (Username with password): Docker Hub credentials (`2025tm93113`).

Create a Pipeline job called `ACEest-CICD`:

1. Set Definition to **Pipeline script from SCM**.
2. Choose **Git** and enter `https://github.com/2025tm93113/aceest-fitness-devops.git`.
3. Leave credentials blank for the public repository.
4. Set Branch Specifier to `*/main`.
5. Set Script Path to `Jenkinsfile`.
6. Save and select **Build Now**.

The 7-stage `Jenkinsfile` runs with `pollSCM('H/2 * * * *')`:
1. **Clean checkout** from `main`
2. **Clean Docker build** (`--pull --no-cache --target test`)
3. **Build and lint** (`compileall` + `ruff`)
4. **Runtime image** (`--target runtime`)
5. **Containerized tests** (Pytest with JUnit & coverage XML archival)
6. **SonarQube Analysis** (containerized `sonar-scanner-cli`)
7. **Push to Docker Hub** (tags & pushes `v3.0`, `latest`, and `build-${BUILD_NUMBER}`)

```sh
docker compose -f jenkins/compose.yml down
```

Do not append `-v` unless intentionally deleting Jenkins configuration.

## Kubernetes deployment strategies (Minikube)

Five progressive delivery manifests are stored under `k8s/` and deployed to
Minikube using the versioned Docker Hub images (`v2.0` and `v3.0`):

| Manifest | Strategy | Service & Port |
| --- | --- | --- |
| `k8s/01-rolling-update.yaml` | Rolling Update (`maxSurge: 1`, `maxUnavailable: 0`) + Rollback | `aceest-rolling-svc` (NodePort `30001`) |
| `k8s/02-blue-green.yaml` | Blue-Green Deployment (`slot: blue` → `slot: green`) | `aceest-bluegreen-svc` (NodePort `30002`) |
| `k8s/03-canary.yaml` | Canary Release (3 stable `v2.0` + 1 canary `v3.0`, 75/25 split) | `aceest-canary-svc` (NodePort `30003`) |
| `k8s/04-shadow.yaml` | Shadow Deployment (NGINX `mirror` from `v2.0` to `v3.0`) | `aceest-shadow-svc` (NodePort `30004`) |
| `k8s/05-ab-testing.yaml` | A/B Testing (NGINX routes `X-Version: B` to `v3.0`, default `v2.0`) | `aceest-ab-svc` (NodePort `30005`) |

```powershell
minikube start
kubectl apply -f k8s/
kubectl get pods,svc

# Rolling update (v2.0 -> v3.0) and rollback (v3.0 -> v2.0)
kubectl set image deployment/aceest-rolling aceest=2025tm93113/aceest-fitness:v3.0
kubectl rollout status deployment/aceest-rolling
kubectl rollout undo deployment/aceest-rolling

# Blue-Green zero-downtime switch (blue -> green)
kubectl patch svc aceest-bluegreen-svc -p '{\"spec\":{\"selector\":{\"app\":\"aceest-bg\",\"slot\":\"green\"}}}'

# Expose live cluster endpoint on Windows
minikube service aceest-bluegreen-svc --url
```

## Integration architecture

```text
Local development -> Git commits & tags (v1.0–v3.0) -> GitHub (main)
                                                        |-> GitHub Actions (CI validation)
                                                        |-> Jenkins (pollSCM)
                                                              |-> Docker Build + Ruff + Pytest
                                                              |-> SonarQube Quality Gate
                                                              |-> Docker Hub Push (v1.0–v3.0, latest)
                                                                    |-> Minikube / Kubernetes
                                                                        (Rolling, Blue-Green, Canary, Shadow, A/B)
```

## Verified outcomes

- **Git tags:** `v1.0`, `v2.0`, `v3.0` on public repository `https://github.com/2025tm93113/aceest-fitness-devops`
- **Pytest:** `34/34` passing, `100.0%` coverage
- **SonarQube:** Quality Gate `OK` (`0` bugs, `0` vulnerabilities, `0.0%` duplication, `100.0%` coverage)
- **Jenkins:** Build `#3` `SUCCESS` with archived `junit.xml`, `coverage.xml`, and Docker Hub push
- **Docker Hub:** `2025tm93113/aceest-fitness` (`v1.0`, `v2.0`, `v3.0`, `latest`, `build-3`)
- **Kubernetes:** All 5 strategies active on Minikube (`http://127.0.0.1:59189/`)

## Troubleshooting

- Docker unavailable: start Docker Desktop and use Linux containers.
- Port 5000 busy: stop Flask or map `127.0.0.1:5001:5000` instead.
- Port 8080 busy: change compose's host port to 8081.
- Jenkins TLS connection fails: wait for the daemon startup, inspect compose service logs, and retry.
- Jenkins branch not found (`master`): ensure Branch Specifier is set to `*/main`.
- SonarQube API `403 Forbidden` when exporting metrics: use admin credentials for REST API queries; reserve the Global Analysis Token for `sonar-scanner-cli`.
- Test cannot find original file: run tests from the repository root and retain `original/Aceestver-1.0.py`.