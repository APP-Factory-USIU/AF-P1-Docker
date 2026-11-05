# Instructor answer key

The three files here are the completed destination of the exercises. They are
not automatically active: the main checkout deliberately starts without Docker
configuration at its root. Have students attempt the lab before opening these.

## Preflight or demonstration

Use a fresh clone, or save your student-written files elsewhere first. Copy the
reference files **to the repository root**; these commands overwrite files with
those names if they already exist. Run from that root:

```sh
cp solutions/Dockerfile Dockerfile
cp solutions/.dockerignore .dockerignore
cp solutions/compose.yaml compose.yaml
docker compose up -d --build
docker compose ps
```

`cp` copies source to destination. In PowerShell, use `Copy-Item` in place of `cp`
with the same two arguments. Do not run Compose from inside `solutions/`: its
build context is designed to be the repository root after copying.

Wait for both services to be healthy. Open http://localhost:8000 and use Add one.
The reference has a web health check, Redis readiness check, dependency ordering,
and an AOF-backed named volume. In the lab, students add these progressively.

## Verify

With the reference running and otherwise idle:

```sh
python3 tests/smoke.py
```

`python3` executes the test script; it checks the health endpoint, page, POST,
redirect and Redis count, incrementing it once. Python 3 is needed on the host
only for this optional smoke script.

Run isolated unit tests with the image's installed dependencies (POSIX shell):

```sh
docker compose run --rm --no-deps -v "$PWD:/workspace:ro" -w /workspace web python -m unittest discover -s tests -v
```

On PowerShell use `${PWD}` instead of `$PWD`. Every option is explained in
[the command guide](../docs/commands.md). GitHub Actions first copies the answer
key into its disposable checkout, then builds and runs both checks. Students'
root files are never silently created in their local checkout by CI.

Stop with `docker compose down`; the named volume remains. For a **deliberate
reset of this demo's count**, use `docker compose down --volumes`. Redis uses
`--appendfsync always` for predictable persistence at classroom scale, trading
write throughput for synchronous writes.
