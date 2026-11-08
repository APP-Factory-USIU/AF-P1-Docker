# Docker: works on our machines

This workshop turns an existing Python web app into a two-service application:
our custom web image plus an official Redis image. The counter and UI are ready;
the root `Dockerfile`, `.dockerignore`, and `compose.yaml` are intentionally absent.
You will create them during the lab.

## Start here

1. Install Git and Docker using [the setup guide](docs/installation.md).
2. Clone the repository and open it in your editor:

   ```sh
   git clone https://github.com/APP-Factory-USIU/AF-P1-Docker.git
   cd AF-P1-Docker
   ```

3. Follow [the hands-on lab](docs/lab.md). Each stage has a scaffold, hints,
   a command to try, and an observable checkpoint.

## What you will build

| Stage | You create | You prove |
| --- | --- | --- |
| 1 | An understanding of the app's runtime and dependencies | Identify Python, the HTTP port, Redis, and its configuration. |
| 2 | `Dockerfile` | Build a tagged custom image, then run its web process. |
| 3 | `.dockerignore` | Keep source dependencies in the build context and local/private files out. |
| 4 | `compose.yaml` | Build web, pull Redis, publish one port, and connect the services. |
| 5 | Redis persistence and health checks | The count survives recreation and startup waits for readiness. |
| 6 | A change and a failure you can explain | Rebuild after an edit; diagnose and recover from a Redis outage. |

The image tag, port mapping, working directory and startup command are decisions
you make from the application's requirements. A successful build is only one checkpoint.

## Repository layout

```text
app/                 Working Flask app, templates and static assets
pyproject.toml       Python project metadata and direct dependencies
uv.lock              Locked Python dependencies (managed by uv)
README.md            Workshop entry point
docs/lab.md          Student exercises and checkpoints
docs/commands.md     Commands, arguments, flags and image tags explained
docs/installation.md Docker setup plus an optional native baseline
solutions/           Instructor answer key; open after attempting the exercises
slides/              Presentation and editable lesson content
tests/               Unit tests and an HTTP-to-Redis smoke check
```

Your completed files belong in the **repository root**, alongside `pyproject.toml` and `uv.lock`.
No branches, reset script or file-deletion command is required to begin.

## Learning resources

- [Student lab](docs/lab.md): the main workshop path.
- [Command guide](docs/commands.md): use when a token in a command is unfamiliar.
- [Slide deck](slides/docker-introduction.pptx): concepts and practical prompts.

## Scope

This is a local teaching app, without accounts or authentication. Keep web bound
to host loopback and Redis unpublished. Each laptop has its own counter.
Python dependencies, including transitive dependencies, are pinned in `uv.lock`.
Commit both `pyproject.toml` and `uv.lock` when changing dependencies with `uv add`
or `uv lock`. Image tags can still change; freeze image digests for an assessed
lab requiring identical image contents. The reference uses Redis AOF storage on
a named volume; persistence is not a backup.
