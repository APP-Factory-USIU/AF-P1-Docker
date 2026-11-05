# Docker: works on our machines

**You receive the application. You write its Docker configuration.**

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

**Do not start with `docker compose up`. There is no Compose file until you write one.**
If you have a previous version of this workshop running, stop it before the lab
so host port 8000 is available. Do not delete its volumes unless you want to lose its count.
After updating an older checkout to this starter, you can stop that existing
stack from the root with:

```sh
docker compose -f solutions/compose.yaml --project-directory . down
```

`-f` selects the moved configuration; `--project-directory .` keeps the original
root project name/path; `down` stops/removes its containers and network, keeping
the named volume. This is a migration cleanup command, not the way to start the
answer key; see [solutions/README.md](solutions/README.md) for that.

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
requirements.txt     Python dependencies
README.md            Workshop entry point
docs/lab.md          Student exercises and checkpoints
docs/commands.md     Commands, arguments, flags and image tags explained
docs/installation.md Docker setup plus an optional native baseline
solutions/           Instructor answer key; open after attempting the exercises
slides/              Presentation and editable lesson content
tests/               Unit tests and an HTTP-to-Redis smoke check
```

Your completed files belong in the **repository root**, alongside `requirements.txt`.
No branches, reset script or file-deletion command is required to begin.

## Learning resources

- [Student lab](docs/lab.md): the main workshop path.
- [Command guide](docs/commands.md): use when a token in a command is unfamiliar.
- [Slide deck](slides/docker-introduction.pptx): concepts and practical prompts.
- [Facilitator guide](docs/teaching-guide.md): timing, checkpoints and common mistakes.
- [Instructor solution](solutions/README.md): a completed reference and CI setup.

The practical structure follows the scaffold-and-checkpoint approach in the
[earlier App Factory workshop](https://github.com/APP-Factory-USIU/docker-workshop/blob/main/docs/DOCKER_PRACTICAL.md),
while retaining this workshop's two-service scope.

## Scope

This is a local teaching app, without accounts or authentication. Keep web bound
to host loopback and Redis unpublished. Each laptop has its own counter.
Image tags and transitive dependencies can change; freeze digests and a full lock
file for an assessed lab requiring identical dependency contents. The reference
uses Redis AOF storage on a named volume; persistence is not a backup.
