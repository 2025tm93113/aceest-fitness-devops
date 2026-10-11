# ACEest Fitness & Gym - Flask and DevOps

## Baseline adaptation

This application adapts the supplied `Aceestver-1.0.py` Tkinter desktop
application to Flask. The original is preserved unchanged in `original/`.
Program names, workout text, diet text, colors, and site metrics are preserved.
Tkinter widgets are replaced by a browser form and HTML display, with additional
JSON APIs and a health endpoint for automated validation.

A test parses the original file with Python AST (without launching Tkinter) and
compares its complete program dictionary with `programs.py`. The capacity of
150 users and break-even of 250 members are separate baseline reference metrics;
the application displays both without attempting to reinterpret them.
This project displays instructor-provided diet plans; it does not provide
personalized medical or nutrition advice.

## Project structure

- `app.py`: application factory, HTTP routes, and lookup logic.
- `programs.py`: baseline program data and site metrics.
- `templates/index.html`: responsive dark/gold web interface.
- `original/Aceestver-1.0.py`: unchanged instructor reference.
- `tests/`: logic, HTTP, UI-content, and baseline-fidelity tests.
- `Dockerfile`: non-root multi-stage testing and runtime images.
- `.github/workflows/main.yml`: push/PR CI pipeline.
- `Jenkinsfile`, `jenkins/`: automated Jenkins build and local setup.

## Prerequisites and local execution

Install Python 3.12, Git, Docker with Linux containers, and Docker Compose v2.
Run all commands from the repository root.

```sh
python -m venv .venv
```

Activate on Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Activate on macOS/Linux:

```sh
source .venv/bin/activate
```

Use `python3` to create the virtual environment if required by your OS.
After activation:

```sh
python -m pip install -r requirements-dev.txt
python app.py
```

Open http://localhost:5000. Choose Fat Loss, Muscle Gain, or Beginner and
select View Plan. The workout and nutrition panels display the original content.
Stop with Ctrl+C. Flask's development server is for local use only.

## API

| Method | Endpoint | Result |
| --- | --- | --- |
| GET | `/` | HTML program-selection interface |
| GET | `/?program=Beginner%20%28BG%29` | Selected program in HTML |
| GET | `/health` | Health JSON |
| GET | `/api/programs` | All original program data |
| GET | `/api/program?name=Beginner%20%28BG%29` | One program |
| GET | `/api/metrics` | Original site metrics |

Missing API name returns 400; unknown API program returns 404; unknown web
selection returns 400. Unknown routes return JSON 404. API endpoints are read-only.
There is no workout logging or pricing feature because version 1.0 does not
contain those features. No persistent database is needed for these static plans.

## Manual tests and lint

```sh
python -m compileall -q app.py programs.py tests
ruff check app.py programs.py tests
python -m pytest -v
```

Pytest uses fresh Flask test-client fixtures. Tests check preserved source data,
all three selections, HTML content, API responses, missing/unknown inputs,
metrics, invalid methods, unknown routes, application configuration, and
protection against mutation of lookup results. Coverage includes branches and
must reach 90% across app and program modules. HTML-template line coverage is
not measured by Python coverage; content behavior is tested through responses.

## Docker

```sh
docker build --target test -t aceest:test .
docker run --rm aceest:test python -m pytest -v
docker build --target runtime -t aceest:runtime .
docker run -d --name aceest-app -p 127.0.0.1:5000:5000 aceest:runtime
docker logs aceest-app
docker exec aceest-app id
docker inspect --format="{{.State.Health.Status}}" aceest-app
```

Stop the local Flask server first. Wait about 30 seconds for health status.
Open http://localhost:5000. The application uses non-root UID 10001 and Gunicorn.

```sh
docker rm -f aceest-app
```

The slim base, dependency-layer caching, excluded build context, and separated
test/runtime stages reduce unnecessary runtime contents. The runtime image
omits tests, the Tkinter original, and development tools. Direct dependency
versions are pinned; stricter production reproducibility would also lock
transitive dependencies and container-image digests.

## GitHub Actions

Every push and pull request triggers `.github/workflows/main.yml`; a manual
trigger is also provided. It checks out source, installs validation tools,
compiles Python, runs Ruff, builds runtime and test images, then executes Pytest
inside the test container. It exports JUnit and coverage XML artifacts and
smoke-tests the runtime health endpoint. Build, lint, test, coverage, and smoke
test failures fail the job. Compilation checks Python syntax; it is not native
binary compilation. Read-only repository permissions are sufficient.

## Jenkins installation and configuration

This local educational setup uses a non-root Jenkins controller with a separate
TLS-enabled Docker-in-Docker daemon. The daemon is privileged: use only trusted
code and do not expose the services publicly. Production should use isolated,
hardened build agents rather than building on the controller.

```sh
docker compose -f jenkins/compose.yml up -d --build
docker compose -f jenkins/compose.yml logs jenkins
docker compose -f jenkins/compose.yml exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open http://localhost:8080. Unlock Jenkins, install suggested plugins, and
create an administrator account. Never commit the password.

Create a Pipeline job called `aceest-fitness-build`:

1. Set Definition to Pipeline script from SCM.
2. Choose Git and enter the public repository HTTPS clone URL.
3. Leave credentials blank for the public repository.
4. Set Branch Specifier to `*/main`.
5. Set Script Path to `Jenkinsfile`.
6. Save and select Build Now for the initial build.

The Jenkinsfile deletes the workspace, checks out GitHub, builds a clean test
image with `--pull --no-cache`, compiles/lints, builds the runtime image, and
runs containerized Pytest with the coverage gate. Test and coverage reports are
copied from the test container and archived. Nonzero exits fail the pipeline.

The first run loads the polling trigger. Then Jenkins checks main approximately
every two minutes through `pollSCM('H/2 * * * *')`. Keep Jenkins running, push a
real change to main, and verify an SCM-triggered successful build. This avoids
requiring an internet-accessible webhook for localhost.

```sh
docker compose -f jenkins/compose.yml down
```

Do not append `-v` unless intentionally deleting Jenkins configuration.

## Integration boundary

```text
Local development -> Git commits -> GitHub
                                    |-> Actions on pushes and PRs
                                    |-> Jenkins polls main for changes
```

Both pipelines validate the same code and Dockerfile independently. Actions
does not trigger Jenkins. This assignment implements automated builds, tests,
and executable container packaging. It does not publish images to a registry
or claim automatic production deployment.

## Version control and evidence

Use genuine application, testing, and infrastructure branches with descriptive
commits and a reviewed infrastructure PR. Keep the original reference unchanged.
Add actual screenshots in `evidence/`: UI with a selected plan, local Pytest
coverage, Docker health/non-root user, successful Actions run, successful
Jenkins stages, automatic SCM build cause, and PR/commit history.

Before submission, record the actual test count, coverage, successful run/build
numbers, and tested commit SHA here. This template does not claim that pipelines
have already been executed. The repository must be public.

## Troubleshooting

- Docker unavailable: start Docker Desktop and use Linux containers.
- Port 5000 busy: stop Flask or map `127.0.0.1:5001:5000` instead.
- Port 8080 busy: change compose's host port to 8081.
- Jenkins TLS connection fails: wait for the daemon startup, inspect compose
  service logs, and retry; do not disable TLS merely to hide a setup issue.
- Jenkinsfile missing: ensure it is committed on main with the correct path.
- Test cannot find original file: run tests from the repository root and retain
  `original/Aceestver-1.0.py`.
- Test or lint failure: correct the reported issue instead of bypassing checks.
