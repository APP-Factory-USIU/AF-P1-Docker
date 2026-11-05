# Student lab: two services, one counter

Work in pairs. One person types, the other predicts the result. Swap halfway.
Run commands from the repository root. Complete the installation checks first.
Keep [the command guide](commands.md) open: it decodes every flag, argument,
image tag, Dockerfile instruction, and Compose setting used in this workshop.

## 1. Build and pull (5 minutes)

Read `Dockerfile` and `compose.yaml`. Which service has `build:`? Which has `image:`?

```sh
docker compose pull redis
docker compose build web
docker compose up -d
docker compose ps
docker compose images
```

`pull redis` downloads the image for the Redis service. `build web` builds our
custom image. `up -d` creates/starts the app in the background (`-d` = detach).
`ps` shows container/health status; wait for both services to be healthy.
`images` lists the images used by those containers.

For everyday work, combine building and starting: `docker compose up -d --build`.
`--build` builds configured images first; it is not an image tag.

Open http://localhost:8000, click Add one twice, and refresh. Explain why refresh
does not increase the count. Notice that building web also pulls a Python base image.

## 2. Follow a request (5 minutes)

```sh
docker compose logs --tail 20 web
docker compose exec redis redis-cli GET visits
docker compose exec web sh
```

`logs` reads output, `--tail 20` selects the last 20 lines per container, and
`web` selects the service. Try `docker compose logs -f --tail 20 web` in a second
terminal: `-f` follows new logs; Ctrl+C leaves the log viewer while services keep running.

`exec` runs a program inside an existing container. In the Redis example, the
service is `redis`, the program is `redis-cli`, its command is `GET`, and its
key argument is `visits`. In the last example, the program is the shell `sh`.
Inside that shell run `pwd` (show the working directory), then
`printenv REDIS_HOST` (show that environment variable), then `exit` (leave the shell).

Explain each hop: browser → published host port → web → `redis:6379`.
Why would `REDIS_HOST=localhost` fail inside the web container?
Why can the browser use port 8000 but not the Redis port on the host?

## 3. Recreate without losing data (5 minutes)

Record the count, then predict what each command does:

```sh
docker compose restart web
docker compose down
docker compose up -d
docker compose exec redis redis-cli GET visits
```

`restart web` stops and starts the existing web container; it does not rebuild.
`down` removes the service containers and network, keeping our named volume.
`up -d` recreates them and reuses the saved volume.

The count should remain. Find `counter-data` in the Compose file.
What would happen without that mount when the Redis container is removed?

## 4. Change the image (5 minutes)

Change the heading in `app/templates/index.html`. Refresh first: why is it unchanged?

```sh
docker compose up -d --build
```

Refresh again. Which build layers were reused? Why copy requirements before the app?
Explain why an image and a running container are different things.
`--build` reads the changed source into a new image before `up` recreates web.
Running only `restart web` would keep using the old image.

## 5. Break a dependency (5 minutes)

```sh
docker compose stop redis
```

Refresh the page. It should return HTTP 503 with a useful message, not an
invented count. Inspect `docker compose logs --tail 20 web` and `docker compose ps --all`.
`stop redis` halts Redis without removing its container. `ps --all` (also `ps -a`)
includes stopped containers, so you can see what happened.

```sh
docker compose start redis
```

`start redis` starts the already-existing stopped Redis container. Use `up`
instead when containers need to be created.

Wait a few seconds and refresh. Does the original count return? Explain why
startup ordering alone cannot prevent a dependency failing later.

## 6. Explain and clean up (5 minutes)

Explain to your partner: Dockerfile, image, container, registry, network, volume.
Then stop your project while preserving its data:

```sh
docker compose down
```

Optional destructive experiment, **only for this workshop's disposable count**:

```sh
docker compose down --volumes
docker compose up -d
```

The counter starts at zero. Why? Finish with `docker compose down`.
`--volumes` means delete this project's declared named volumes too. It is the
destructive difference from plain `down`.
