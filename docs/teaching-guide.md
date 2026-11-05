# Facilitator guide

Audience: university students comfortable with a terminal, files, and a browser.
No Docker experience assumed. Plan for a 90-minute core session, with installation
completed before class. Allow up to 120 minutes if you explain every installation
and command example live. The five requested topics are sections, not a five-slide limit.

## Learning outcomes

Students can explain environment drift, distinguish a VM from a container,
describe five core Docker concepts, check their installation, and run/rebuild a
two-service app while explaining its network and persistent volume.

## Before the session

Send `docs/installation.md` and the GitHub clone URL. Ask students to bring a
laptop with Git and complete the sanity checks in the same terminal they will use.
Confirm campus Wi-Fi can reach Docker Hub and PyPI. On the teaching laptop, run
`docker compose pull redis` and `docker compose build web` before class. Test
the browser and projector; keep a built laptop available for pairs with setup issues.
The first build needs downloads; cached images make later exercises faster.
Run `python3 tests/smoke.py` after starting the app, then intentionally reset only
your workshop volume if you want to start at zero. Do not reset student data.

## Suggested timing

| Time | Activity |
| --- | --- |
| 0–8 min | “Works on my machine”: ask for examples of missing dependencies or mismatched versions. |
| 8–20 min | VMs: virtual hardware, hypervisor, separate guest kernel, examples, costs. |
| 20–32 min | Containers: isolated processes, shared kernel, images, limitations. |
| 32–40 min | VM comparison and using containers inside VMs. |
| 40–50 min | Docker, five concepts, image lifecycle, Compose. |
| 50–60 min | Installation routes and sanity checks; route difficult installs to paired work. |
| 60–85 min | Student lab, emphasizing predictions and explanations. |
| 85–90 min | Exit questions and cleanup. |

The slide notes include prompts, command breakdowns, and source links.
Use the command slides alongside the lab rather than presenting them all before
students type. Package-manager setup and advanced test options are reference
material in `docs/installation.md` and `docs/commands.md`.

## Command vocabulary

Use `docker compose up -d --build` for the main walkthrough. Explain the program,
plugin, action, flags, values, and service argument in that order. Pair each new
command with a prediction. `--wait` remains in CI, where waiting for health matters
to the next automated step; it is explained in the command guide.

Teach `ps`, `logs -f --tail 20 web`, `exec`, `build`, `pull`, `stop`, `start`,
`restart`, and `down` as the everyday toolkit. Explain `config` and `images` as
inspection tools. Show the different outcomes of Ctrl+C during attached `up`
versus Ctrl+C in `logs -f` for an already-detached app.

Point out that `redis:7.4-alpine` is an image reference, `redis:6379` is a network
address, and `app:app` is a Python module/object reference. The colon does not
have one universal meaning. Likewise, `-v` means volume in Compose `run`, but
verbose after Python's `unittest` arguments.

## Demo script and answers

1. Show the Dockerfile: `FROM` provides Python, `WORKDIR` sets a path, requirements
   are copied first for build caching, `RUN` installs dependencies, `COPY` adds
   source, `USER` avoids running the web process as root, `EXPOSE` documents a
   port, and `CMD` starts Gunicorn. `EXPOSE` alone publishes no host port.
2. Show Compose: `build` makes our image; `image` obtains Redis; the healthy
   dependency controls initial startup; `ports` publishes only web on loopback;
   environment config supplies the Redis hostname; the volume persists Redis files.
3. Click Add one. GET `/` reads; POST `/count` uses atomic Redis INCR and a 303
   redirect. Logs show both requests. A refresh doesn't cause a write.
4. `redis` resolves through Compose's network. A container's `localhost` refers
   to itself, not another container or the laptop. No fixed container IP is needed.
5. `down` removes project containers and network, but retains the named volume.
   Redis AOF lives there. `down --volumes` deletes that data deliberately.
   A volume is persistence, not a backup, and each student's machine has its own count.
6. A source edit requires a rebuild because there is no source bind mount.
   A runtime writable layer does not modify the underlying image.
7. Stopping Redis yields 503. The app creates fresh connections when it returns.
   The initial `depends_on` check does not supervise later availability.

## Concept checks

- “An Ubuntu container boots Ubuntu's kernel.” False: it normally supplies Ubuntu
  user-space files and uses the Linux host/VM kernel.
- “Containers replace VMs.” False: a VM can host many containers; Desktop runs
  this lab's Linux containers in a Linux environment on non-Linux hosts.
- “An image tag fixes the contents forever.” False: tags may move; digests identify contents.
- “A running process is always healthy.” False: health checks test readiness/availability.
- “Docker guarantees identical behavior everywhere.” False: architecture, kernel,
  config, external services, and resources still matter.

## Exit questions

1. Which kernel does this lab's container use on a Mac?
2. What is the difference between `build`, `pull`, and `up`?
3. Which file tells Docker how to build web? Which defines the whole app?
4. Why does the count survive container recreation?
5. What does the Server section in `docker version` prove?

Answers: Linux kernel in Desktop's VM; build an image / download an image /
create and start services; Dockerfile / compose.yaml; named volume with Redis
persistence; the client can contact the selected daemon.

## GitHub handoff

The existing origin is `git@github.com:APP-Factory-USIU/AF-P1-Docker.git`.
Review the local diff and slides, then commit and push with your usual workflow.
No remote push is necessary to run the class locally. The included GitHub Actions
workflow checks the app on pushes and pull requests once published.
