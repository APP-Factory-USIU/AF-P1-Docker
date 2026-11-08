# Facilitator guide

This is a **containerization workshop**, starting with application source and
ending with files students wrote. The root Dockerfile, dockerignore and Compose
file are deliberately absent. `solutions/` holds the answer key; CI copies it
into a disposable checkout to keep the reference tested.

Keep the two-service scope: custom Python web image plus pulled Redis image.
The lab follows the scaffold/hints/checkpoint style of the
[former App Factory practical](https://github.com/APP-Factory-USIU/docker-workshop/blob/main/docs/DOCKER_PRACTICAL.md).
Do not hand out the completed reference as the opening activity.

## Preparation

- Send `docs/installation.md` before class. Git, Docker, Buildx and Compose should
  pass their checks before the session; local Python/Redis are optional.
- Allow 120–150 minutes for theory plus the 60–90-minute practical. The theory
  and command slides are references: interleave them with students' typing.
- On a fresh instructor clone, follow `solutions/README.md` to copy and run the
  answer key. Verify Wi-Fi/registry access, browser, projection and image downloads.
- Keep a clean starter clone ready to demonstrate creating files. A checkout in
  which you already copied the answer key is not a student starting point.
- Stop an older workshop stack before class if it occupies port 8000, preserving
  its volume unless you deliberately want to erase it.

## Teaching sequence

| Block | Activity | Evidence before moving on |
| --- | --- | --- |
| 30–40 min | Environment drift, VMs, containers and Docker | Students identify the shared-kernel distinction. |
| 5–10 min | Inspect source; optionally show a native run | Identify runtime, dependencies, HTTP port and Redis hostname. |
| 10 min | Write Dockerfile from the scaffold | Explain FROM, WORKDIR, COPY, RUN, USER, EXPOSE and CMD. |
| 10 min | Write dockerignore, build and run one image | Tagged image exists; standalone web deliberately returns 503. |
| 15 min | Write the two-service Compose file | Web and Redis connect; counter works. |
| 10 min | Observe lost state, then add persistence | Before/after recreation demonstrates why the volume matters. |
| 10 min | Add health checks and startup dependency | Both services healthy; readiness differs from a running process. |
| 10 min | Rebuild and break/recover a dependency | Diagnose with ps/logs; explain restart versus rebuild. |
| 5–10 min | Compare files, explain, clean up | Students explain their own three artifacts without the answer key. |

If time is short, keep persistence and readiness as the next lab rather than
skipping Dockerfile authoring. The main learning outcome is creating the files.

## Checkpoint answers and common mistakes

1. **Runtime:** Flask, Redis client and Gunicorn are declared in pyproject.toml
   and pinned with their transitive dependencies in uv.lock. The
   image supplies Python 3.13 slim. A local native run defaults to localhost for
   Redis; Compose must explicitly set REDIS_HOST to the Redis service name.
2. **Paths:** after WORKDIR /app, COPY app/ . puts app.py, templates and static
   together. Copying into /app/app accidentally changes the module path. The
   Gunicorn target app:app is module : object, not repository : image tag.
3. **Caching:** copy pyproject.toml and uv.lock and run uv sync before copying
   source. A template edit can then reuse the dependency layer. uv's --no-cache
   controls its download cache; it does not disable Docker build-layer caching.
   Add /app/.venv/bin to PATH so the non-root process uses uv's environment.
4. **Context:** docker build's final dot selects files available to COPY. It is
   independent of WORKDIR. The dockerignore allowlist excludes credentials and
   unrelated repository files, then includes pyproject.toml, uv.lock and the app tree.
5. **Single-container test:** Gunicorn should start and serve HTTP, but health
   returns 503 because Redis is missing from that container's network. Treat a
   startup crash or import error as a different failure, not a passing checkpoint.
6. **Compose networking:** redis resolves by service name on the default network.
   localhost inside web is web itself. Publish only web on host loopback.
7. **Persistence:** before a named volume is attached, down/up should reset the
   counter. Redis's default anonymous volume isn't automatically reattached. Once
   counter-data is mounted at /data and AOF is enabled, count survives recreation.
   Lost earlier state cannot be recovered. A volume is not a backup.
8. **Readiness:** depends_on with service_healthy waits initially; it does not
   prevent later outages. The app returns 503 if Redis stops and reconnects when
   Redis returns. Its health route tests the actual dependency.
9. **Rebuild:** source is copied into the image. restart reuses the same image;
   up -d --build incorporates the edit and recreates web when its image changes.

Use the reference only after students attempt a stage. Accept equivalent valid
files that meet the requirements; formatting need not match the answer key.

## Command vocabulary

Every command/flag used is decoded in `docs/commands.md` or the native-baseline
section of `docs/installation.md`. Teach standard Compose commands after students
have written compose.yaml. Before then, demonstrate build -t and attached run -p.

Distinguish these contexts explicitly:

- classroom-web:workshop is repository : image tag.
- redis:6379 is host : network port.
- app:app is Python module : application object.
- -t labels an image in docker build; other commands may use -t differently.
- -v means a volume in Compose run, but verbose in Python unittest.
- Ctrl+C stops attached docker run/up, but merely exits logs -f for a detached app.

## Assessment and exit questions

Ask pairs to submit their root Dockerfile, .dockerignore and compose.yaml, then
show a successful build, working counter, persistence, and outage recovery.

1. Which files does the build context contain, and which files reach the image?
2. What happens at build time versus container startup?
3. Why did the standalone web container return 503?
4. Why did you build web but pull Redis?
5. Which configuration change made the count survive container removal?
6. Which kernel does a Linux container use on a Mac?

Answers: context follows dockerignore, COPY selects image files; RUN versus CMD;
missing Redis dependency; custom application versus reusable official image;
named volume plus Redis persistence; Linux kernel supplied by Desktop's VM/environment.

Finish with docker compose down, preserving the count. --volumes is an explicit,
destructive reset of this project's declared volume and should be labelled before typing.
