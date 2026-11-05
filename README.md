# Docker: works on our machines

A first Docker workshop for university students. Build one image, pull another,
and run a web app with persistent data. No local Python or Redis installation needed.

## Before class

Install Git and either Docker Desktop or Docker Engine with Compose.
Follow [the installation guide](docs/installation.md), then run its sanity checks.
Allow time and internet access for the first image downloads.

## Run the app

```sh
git clone https://github.com/APP-Factory-USIU/AF-P1-Docker.git
cd AF-P1-Docker
docker compose up -d --build
docker compose ps
```

`up` creates/starts the services; `-d` keeps them in the background; `--build`
builds the custom web image first. `ps` shows status: wait for both services to
be healthy, then open **http://localhost:8000**. Click **Add one**, then refresh: a refresh only
reads the count. The button sends a POST that increments Redis atomically.

```sh
docker compose ps
docker compose logs --tail 20 web
docker compose exec redis redis-cli GET visits
```

## Two services

| Service | Image source | Responsibility |
| --- | --- | --- |
| `web` | Built from our `Dockerfile` using `python:3.13-slim` | Flask page served by Gunicorn on port 8000 |
| `redis` | Pulled unchanged: `redis:7.4-alpine` | Counter storage on port 6379 inside the Compose network |

The browser connects to the published loopback port `127.0.0.1:8000`.
The web container reaches Redis by service name `redis:6379`; `localhost` inside
the web container means the web container itself. Redis has no published host port.
Compose creates a network and a named `counter-data` volume automatically.
Health checks wait for Redis before starting the web service.

## Learn by changing things

Work through [the student lab](docs/lab.md). Present with
[the deck](slides/docker-introduction.pptx) and use
[the facilitator guide](docs/teaching-guide.md) for timing, answers, and preparation.
The editable slide content and speaker notes are also in [slides/lesson.json](slides/lesson.json).
The [command guide](docs/commands.md) explains every command, option, argument,
image tag, Dockerfile instruction, and Compose setting used here. The web app
also has an expandable guide to the everyday Compose workflow.

## Stop or reset

```sh
docker compose down
docker compose up -d
```

The count survives because Redis writes to a named volume. To deliberately erase
**this project's counter**, stop the project and remove its volume:

```sh
docker compose down --volumes
```

Do not use `--volumes` if you want to keep the count. There is no need to prune
all of Docker to clean up this workshop.

## Check the project

With the app running, test the full HTTP-to-Redis path (Python 3 required only for this check):

```sh
python3 tests/smoke.py
```

Run unit tests with the image's installed dependencies (POSIX shell):

```sh
docker compose run --rm --no-deps -v "$PWD:/workspace:ro" -w /workspace web python -m unittest discover -s tests -v
```

On PowerShell use `${PWD}` in place of `$PWD`. GitHub Actions runs both checks.

## Teaching scope

This is a local classroom demo: no accounts, authentication, or production deployment.
Redis is unauthenticated within the project network. Keep the loopback binding.
The direct Python requirements are pinned; image tags and transitive dependencies
can change. For repeatable assessed labs, record image digests and lock the full
dependency set. Redis uses synchronous AOF writes here to make the persistence
exercise predictable at classroom scale, at the expense of write throughput.

Sources and installation links are in [docs/installation.md](docs/installation.md)
and the deck's speaker notes. Existing MIT license retained for this repository's code.
