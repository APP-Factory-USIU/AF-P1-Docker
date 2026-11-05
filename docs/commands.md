# The commands, decoded

The everyday workflow is **up → ps → logs → exec → down**. Use `build` and
`pull` when you want to see those steps separately. These are common commands
for local Compose development, not a ranking based on usage statistics.

## How to read a command

```text
docker compose logs -f --tail 20 web
│      │       │    │  │      │  └─ service argument
│      │       │    │  └──────┴──── option + its value
│      │       │    └───────────── flag
│      │       └────────────────── subcommand
│      └────────────────────────── Compose plugin
└───────────────────────────────── Docker CLI
```

A **command** asks for an action. An **option/flag** changes that action; some
options take a value. An **argument** identifies a target or input. An image
**tag** selects an image version or variant; it is not a command-line flag.
Commands below run from the repository root, where Compose finds `compose.yaml`.
`web` and `redis` are the **service names in that file**, not image tags or fixed
container IDs. Omitting an optional service argument usually targets all services
relevant to that command.

## Start and inspect

| Command | Every part after `docker compose` |
| --- | --- |
| `up` | `up` creates/starts the app and attaches the terminal to combined logs. Ctrl+C stops this attached app. |
| `up -d --build` | `up` creates/starts services; `-d` = `--detach`, leave them running in the background; `--build` builds configured custom images before starting. It does not mean “download every newer image.” |
| `ps` | `ps` lists running service containers, published ports and status. Look for health status, not just “running.” |
| `ps -a` | `-a` = `--all`, also include stopped containers. |
| `logs web` | `logs` shows container output; `web` selects only the web service. `logs redis web` selects both. |
| `logs -f --tail 20 web` | `-f` = `--follow`, continue showing new output; `--tail` takes `20`, the initial number of recent lines per container; `web` is the service. Ctrl+C exits this log viewer without stopping detached services. |
| `images` | `images` lists the images used by the created service containers. |
| `config` | `config` validates and prints the resolved Compose configuration. It does not start services. `config --quiet` validates without printing it; useful in CI. |

`docker compose up --build --wait` is the automated-check variant used in CI:
`--build` builds first; `--wait` waits for running/healthy status and implies
detached mode. It is useful for scripts but is not required for the student
workflow. With `up -d --build`, run `ps` and wait for both services to be healthy
before opening the page.

## Build, pull and look inside

| Command | Every part after `docker compose` |
| --- | --- |
| `build web` | `build` builds an image from a configured Dockerfile; `web` selects our custom service. It does not start or replace a running container. |
| `pull redis` | `pull` downloads the image configured for `redis`. It does not start or replace the running container. |
| `exec web sh` | `exec` runs a process in an **existing running** container; `web` selects the service; `sh` is the shell program inside it. Compose supplies an interactive terminal by default. Type `exit` to leave the shell; the web server keeps running. |
| `exec redis redis-cli GET visits` | `exec` selects an existing container; `redis` is the service; `redis-cli` is the Redis client program; `GET` is its Redis command; `visits` is the key to read. A missing key returns nil. |

In the shell opened by `exec web sh`, `pwd` prints the working directory;
`printenv REDIS_HOST` prints the environment variable named `REDIS_HOST`; `exit`
ends that shell. You are now running these programs inside web, not on your laptop.

After editing the HTML, run `docker compose up -d --build` again. It rebuilds
as needed and recreates the service when its image changes. `restart` does not
build source changes into an image. To fetch a newer Redis image deliberately:
`docker compose pull redis`, then `docker compose up -d`. `-d` still means detach.

## Stop, restart or remove

| Command | Effect and arguments |
| --- | --- |
| `docker compose stop redis` | `stop` halts the existing `redis` service container and leaves it present. |
| `docker compose start redis` | `start` starts that stopped container. It requires the container to exist already; it does not build or create one. |
| `docker compose restart web` | `restart` stops then starts the existing `web` service. No image rebuild and no application of changed Compose environment settings. |
| `docker compose down` | `down` stops/removes this project's containers and network. Our named volume stays. |
| `docker compose down --volumes` | `--volumes` (short form `-v` here) also removes the project's declared named volume and attached anonymous volumes. **Deletes this lab's saved count.** External volumes are not removed. |

No host-wide prune command is needed. `stop` preserves containers; `down`
removes them. An image and a named volume are separate from a container.

## Image names and tags

```text
redis:7.4-alpine
───── ──────────
name      tag
```

- `redis` is the image repository. With no registry or namespace written, this
  official image resolves to `docker.io/library/redis`.
- `:` separates the repository from its tag. `7.4-alpine` is **one whole tag**:
  the Redis 7.4 version line packaged on an Alpine Linux base.
- `python:3.13-slim` selects the Python 3.13 version line with a smaller Debian
  user-space image variant. `slim` and `alpine` are different base-image choices;
  they are not Docker commands.
- `hello-world` without a tag defaults to `hello-world:latest`. `latest` is a
  conventional label, not a guarantee of the newest release.
- Tags can move. A `name@sha256:…` reference pins image content by digest.
- `redis:6379` **in a connection address** is host + port, not an image tag.
  The context tells you which meaning applies.

## The Compose file, decoded

| Configuration | Meaning |
| --- | --- |
| `services:` | Defines the application's services. `web:` and `redis:` name ours. |
| `build: .` | Build from the current project directory; `.` is the build context containing the default `Dockerfile`. |
| `image: redis:7.4-alpine` | Use that named/tagged image for Redis. |
| `ports: ["127.0.0.1:8000:8000"]` | Host IP : host port : container port. Bind only to laptop loopback, forwarding port 8000 into web's port 8000. |
| `REDIS_HOST: redis` | Set an environment variable in web; `redis` resolves via Compose's network. |
| `depends_on` + `condition: service_healthy` | Wait for Redis's health check before initially starting web. This is not supervision of later outages. |
| `counter-data:/data` | Mount the named volume `counter-data` at Redis's container directory `/data`. The bottom-level `volumes:` declares it. |
| `command: [...]` | Override the image's default command arguments. Here `redis-server` starts Redis; `--appendonly yes` enables its append-only persistence log; `--appendfsync always` synchronizes each write for this small demo. |
| `healthcheck.test: ["CMD", ...]` | Execute the named program directly, without a shell. Redis runs `redis-cli ping`: `ping` requests a PONG response. Web runs `python -c` followed by inline Python that requests `/health` with a two-second timeout. |
| `interval`, `timeout`, `retries` | How often to probe, how long each probe may take, and how many consecutive failures mark it unhealthy. `s` in `5s` means seconds. |

## The Dockerfile, decoded

| Instruction | Meaning |
| --- | --- |
| `FROM python:3.13-slim` | Choose the base image. `python` is the repository; `3.13-slim` is the tag. |
| `WORKDIR /app` | Create/use `/app` as the working directory for following instructions and the default process. |
| `COPY requirements.txt .` | Copy the requirements file from the build context into the working directory. The final dot is the destination. |
| `RUN pip install --no-cache-dir -r requirements.txt` | During the build, run `pip install`; `--no-cache-dir` avoids retaining pip's download cache; `-r` reads package requirements from the following filename. `==` in the file pins a direct dependency version. |
| `COPY app/ .` | Copy the application directory contents into `/app`. Editing this source requires a rebuild. |
| `USER 10001:10001` | Run later instructions/default process as numeric user ID 10001 and group ID 10001. This is a user/group pair, not an image tag. |
| `EXPOSE 8000` | Document the intended container port; it does not publish a host port. |
| `CMD [...]` | Default startup command in exec form: each JSON string is one argument, without shell parsing. |

The startup command is `gunicorn --bind 0.0.0.0:8000 --workers 2 --access-logfile - app:app`:
`gunicorn` is the server program; `--bind` takes the container listening address;
`0.0.0.0` accepts connections on all interfaces **inside the container**;
`--workers 2` starts two worker processes; `--access-logfile -` sends access logs
to standard output so Compose can show them; `app:app` means the `app` object
inside the Python module `app`, not an image tag.

## Checks and advanced test command

| Command | Meaning |
| --- | --- |
| `git clone https://github.com/APP-Factory-USIU/AF-P1-Docker.git` | `clone` downloads the repository at the URL into a new directory. |
| `cd AF-P1-Docker` | Shell builtin: change into that directory. |
| `git --version` | Print the Git CLI version. |
| `docker version` | Show Docker client and reachable server versions. |
| `docker info` | Show the selected engine's system information. |
| `docker context ls` | `context` manages engine connection settings; `ls` lists them and marks the active one. |
| `docker compose version` | Print the installed Compose plugin version. |
| `docker buildx version` | Print the installed Buildx plugin version. |
| `docker run --rm hello-world` | `run` creates/starts a standalone container; `--rm` removes it after exit; `hello-world` selects the image (default tag `latest`). This is Docker's run command, not Compose's. |
| `curl http://localhost:8000/health` | Request the URL and print its response body. `curl.exe` is the Windows executable spelling when PowerShell has an alias named curl. |
| `python3 tests/smoke.py` | Run that local Python script; it checks HTTP and increments the counter once. Run while the demo is otherwise idle. |

The optional unit-test command in the README is deliberately outside the main lab:

```sh
docker compose run --rm --no-deps -v "$PWD:/workspace:ro" -w /workspace web python -m unittest discover -s tests -v
```

- `run`: create a **new one-off container** using web's configuration and replace
  its default command. Unlike `exec`, it does not use the running web container;
  it also does not publish the service ports by default.
- `--rm`: remove that one-off container when its command finishes.
- `--no-deps`: do not start dependency services; these unit tests mock Redis.
- The first `-v`: `--volume`, a bind mount. `$PWD` expands to your current host
  directory; `/workspace` is the container destination; `ro` makes it read-only.
  Quotes keep paths with spaces together. PowerShell uses `${PWD}` here.
- `-w /workspace`: set the working directory inside the one-off container.
- `web`: choose the service configuration. Everything after it is the command
  **inside** the container, not more Compose options.
- `python -m unittest`: run Python's standard-library test module; `-m` selects a module.
- `discover -s tests`: find tests starting in the `tests` directory.
- The final `-v`: Python unittest's **verbose** flag. Same letter, different
  program/context from Compose's volume flag.
- In scripts, `exec -T ...` disables terminal allocation. It is useful for CI,
  whereas an interactive `exec web sh` normally wants a terminal.
- A Compose-wide `-p af-p1-docker-check` before the subcommand selects an isolated
  project name for local verification. It is not a port mapping.

## Sources

Checked against the official CLI references on 5 November 2026:
[Compose](https://docs.docker.com/reference/cli/docker/compose/),
[up](https://docs.docker.com/reference/cli/docker/compose/up/),
[ps](https://docs.docker.com/reference/cli/docker/compose/ps/),
[logs](https://docs.docker.com/reference/cli/docker/compose/logs/),
[exec](https://docs.docker.com/reference/cli/docker/compose/exec/),
[build](https://docs.docker.com/reference/cli/docker/compose/build/),
[pull](https://docs.docker.com/reference/cli/docker/compose/pull/),
[restart](https://docs.docker.com/reference/cli/docker/compose/restart/),
[down](https://docs.docker.com/reference/cli/docker/compose/down/),
[run](https://docs.docker.com/reference/cli/docker/compose/run/),
[image references](https://docs.docker.com/reference/cli/docker/image/tag/),
[Dockerfile](https://docs.docker.com/reference/dockerfile/).
