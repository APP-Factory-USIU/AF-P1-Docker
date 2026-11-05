# Student lab: write the Docker files

Work in pairs. One person types, one predicts and checks; swap after the first
image builds. The application is supplied. **You create `Dockerfile`,
`.dockerignore`, and `compose.yaml` at the repository root.**

Keep [commands.md](commands.md) nearby. The completed files in `solutions/` are
an answer key to compare with after your attempt, not the starting instructions.
Allow 60–90 minutes for the practical after the theory discussion.

## 1. Explore the application (5 minutes)

Open `app/app.py`, `requirements.txt`, and `app/templates/index.html`.

Before writing Docker configuration, answer:

1. Which runtime and Python packages must the web image contain?
2. Which route reads the counter? Which route changes it?
3. What environment variable selects the Redis hostname?
4. What must `/health` successfully contact before it reports success?
5. Which host and port should the HTTP server listen on inside a container?

The web process will use Gunicorn on container port **8000**. Redis listens on
**6379**. You can optionally run the native baseline in [installation.md](installation.md#optional-run-the-app-without-containerizing-it)
to experience the dependency setup Docker will package. Local Python and Redis
installation are not required for the container lab itself.

**Checkpoint:** explain the browser → Python → Redis request path to your partner.

## 2. Create the Dockerfile (10 minutes)

Create `Dockerfile` in the root, with no filename extension. Fill the blanks:

```dockerfile
FROM _____

WORKDIR _____
COPY _____ _____
RUN _____

COPY _____ _____
USER _____
EXPOSE _____
CMD ["_____", "_____", "_____", "_____", "_____", "_____", "_____", "_____"]
```

Constraints and hints:

- Use the official Python **3.13 slim** image. Identify repository and tag.
- Put the app in `/app`. Copy the requirements file there before the source.
- Install requirements with pip. Use `-r` for the file and avoid pip's download
  cache. Why should this `RUN` happen before copying application source?
- Copy the **contents** of `app/` into the image working directory. That places
  `app.py`, `templates/`, and `static/` together; do not introduce another `app/` nesting.
- Run as numeric user and group **10001:10001**. This app doesn't need root.
- Document container port **8000**. Does `EXPOSE` publish it on the laptop?
- For `CMD`, use Gunicorn. Its program plus seven arguments must: bind
  `0.0.0.0:8000`, use two workers, write access logs to `-` (stdout), and load
  `app:app`. Find those flags in [the Dockerfile command breakdown](commands.md#the-dockerfile-decoded).
- `RUN` happens during the build; `CMD` defines the default startup process.
  JSON exec form makes each string one argument. It does not invoke a shell.

**Checkpoint:** read each instruction aloud and identify its input and effect.
Do not build yet: first decide which local files the build should be allowed to see.

## 3. Create .dockerignore, then build and run (10 minutes)

Create `.dockerignore` beside the Dockerfile. This exercise uses an allowlist:
ignore everything, then include only the requirements file and application tree.
Complete:

```text
*
!_____
!_____/
!_____/**
**/__pycache__
**/*.pyc
```

`*` excludes paths; `!` makes an exception. Include the `app/` directory itself
before its contents. The final exclusions keep generated Python cache files out.
Git history, `.env` files, your virtual environment, and the slide deck do not
belong in the build context. What could go wrong if a credential file is copied
into an image?

Now build:

```sh
docker build -t classroom-web:workshop .
docker images classroom-web
```

`build` creates an image. `-t` names/tags it: repository `classroom-web`, tag
`workshop`. The final `.` is the current directory, the **build context**, not
the container working directory. `images classroom-web` lists matching local images.

**Checkpoint:** a successful build and an image listed with tag `workshop`.
A build failure belongs here: fix one instruction and rebuild, observing cached layers.

Start only the web container, attached to this terminal:

```sh
docker run --rm -p 127.0.0.1:8000:8000 classroom-web:workshop
```

`run` creates a container; `--rm` removes it after exit. `-p` publishes
host IP : host port : container port. The image name/tag is the final argument.
In another terminal:

```sh
curl -i http://localhost:8000/health
```

`curl` requests the URL; `-i` includes response headers. Use `curl.exe` in
PowerShell if curl is aliased. A browser also shows the response.

**Expected checkpoint: HTTP 503.** The web server runs, but we have not supplied
Redis in this container's network. This proves a running process is not the same
as a working application. `localhost` inside this container means itself.

Press **Ctrl+C in the attached run terminal**, then wait for the container to
exit and be removed. Free port 8000 before the next stage. If you see a Python
import error or no HTTP response, fix that first; those are not the expected 503.

## 4. Write the Compose file (15 minutes)

Create `compose.yaml` at the repository root. Fill this scaffold. YAML indentation
matters; use spaces. The service names are supplied, but you choose their configuration:

```yaml
services:
  web:
    build: _____
    ports:
      - "_____"
    environment:
      REDIS_HOST: _____

  redis:
    image: _____
```

Requirements:

- Build web using the Dockerfile you wrote in the root.
- Publish web on laptop loopback, host port 8000 → container port 8000.
- Pull **Redis 7.4 on Alpine Linux** using its official image tag.
- Make web connect to the **Redis service name**, not `localhost` or a fixed IP.
- Do not publish Redis's port to the host. Both services join Compose's default network.

Predict which service needs a build and which needs a pull. Then:

```sh
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs --tail 20 web
```

`config` validates/prints the resolved file; it does not start anything. `up`
creates/starts the app; `-d` detaches; `--build` builds custom images first. `ps`
shows state. `logs --tail 20 web` selects the last 20 log lines for web.

At this stage there are no health checks or startup ordering. Redis may take a
moment to become ready: refresh once it starts. You will improve that below.

Open http://localhost:8000. Click **Add one** twice, then refresh.

```sh
docker compose exec redis redis-cli GET visits
```

`exec` runs a process in an existing container. `redis` selects the service;
`redis-cli` is the program; `GET` is its command; `visits` is the key argument.

**Checkpoint:** the browser and Redis report the same count. Refresh doesn't increment it.

## 5. Add persistence yourself (10 minutes)

Record your count, then run:

```sh
docker compose down
docker compose up -d
```

`down` removes the containers/network; `up -d` recreates them in the background.
**Before your volume exists, the old count should be gone.** Redis's default
anonymous data volume is not automatically reattached to the replacement container.

Now edit your Compose file to:

1. Declare a named volume **`counter-data`** at the top-level `volumes:` key.
2. Mount that volume at Redis's **`/data`** directory.
3. Enable append-only persistence with Redis's startup command:
   `redis-server --appendonly yes --appendfsync always`.

Start the changed configuration with `docker compose up -d`, wait for Redis,
then click Add one and record the new count. Repeat `down` and `up -d`.

**Checkpoint:** the count now survives. Explain why both the mount and Redis's
persistence settings matter. `--appendonly yes` enables the append-only log;
`--appendfsync always` synchronizes every write for this small classroom experiment.
You cannot recover the count lost before persistent storage was configured.

## 6. Add readiness checks (10 minutes)

Improve the same Compose file; do not create a third service:

- Give Redis a health check running `redis-cli ping` using exec-form `CMD`.
  Use interval `2s`, timeout `1s`, and retries `10`.
- Add web's `depends_on` entry for Redis with `condition: service_healthy`.
- Give web a health check that uses the image's Python interpreter to request
  `http://localhost:8000/health` with urllib and a two-second request timeout.
  Use interval `5s`, timeout `3s`, and retries `5`.

Look at the health-check settings in [commands.md](commands.md#the-compose-file-decoded)
for syntax and meaning, then construct the YAML. The complete answer is available
in `solutions/compose.yaml` after your attempt.

```sh
docker compose config
docker compose up -d
docker compose ps
```

**Checkpoint:** both services show healthy, and web starts after Redis is healthy.
Can `depends_on` prevent a dependency from failing later?

## 7. Change, diagnose and explain (10 minutes)

- **Rebuild:** change the heading in `app/templates/index.html`. Run
  `docker compose restart web`, then refresh. Why is it still old? Run
  `docker compose up -d --build`, wait for healthy status, then refresh again.
- **Observe:** follow requests with `docker compose logs -f --tail 20 web`.
  `-f` follows new output; Ctrl+C leaves this log viewer without stopping detached services.
- **Break:** run `docker compose stop redis`. Refresh: HTTP 503. Inspect
  `docker compose ps -a` (`-a` includes stopped containers) and the logs.
- **Recover:** run `docker compose start redis`, wait for readiness, and refresh.
  The count returns. `stop`/`start` reuse an existing container; `restart` does
  not rebuild an image or apply changes to Compose configuration.

Finish with `docker compose down`, preserving your named volume. A deliberate
reset is `docker compose down --volumes`: **this deletes the project's saved count**.
Do not reset your partner's or an unrelated project's data.

## Your hand-in

Show your partner your three root files and demonstrate a working counter.
Explain the base image/tag, build context, build cache, port mapping, Redis
hostname, named volume, and health dependency without opening the answer key.
Compare with `solutions/` only after you have tried each checkpoint.
