# Docker installation and sanity checks

Guidance checked against official documentation on 5 November 2026. Read the
linked OS requirements before class; supported releases and installer details change.
Choose **one** route for the workshop. You do not need Desktop plus a separate Engine.
For the Compose vocabulary, image tags, and sanity-check commands, use
[the command guide](commands.md). The setup-specific options are decoded below.

## Route A: Docker Desktop

Desktop bundles the Engine, CLI, Buildx, and Compose with a graphical dashboard.
Download the installer matching your OS and CPU architecture, install it, then
**launch Docker Desktop and wait until its engine is running**.

| OS | Steps and requirements |
| --- | --- |
| Windows | Follow [Windows installation](https://docs.docker.com/desktop/setup/install/windows-install/). Use its supported Windows/WSL versions, enable hardware virtualization, and select the WSL 2 backend with Linux containers for this lab. Check `wsl --version` and `wsl --status` in PowerShell; install/update WSL as the guide requires, then restart if prompted. If using an Ubuntu WSL terminal, enable integration for that distribution in Desktop settings. |
| macOS | Follow [Mac installation](https://docs.docker.com/desktop/setup/install/mac-install/). Choose Apple silicon or Intel correctly, open the DMG, drag Docker to Applications, and launch it. Check the supported macOS version and RAM requirements. |
| Linux | Follow [Linux installation](https://docs.docker.com/desktop/setup/install/linux/), then its distribution-specific package instructions. Desktop requires supported virtualization/KVM and runs its own VM; it uses a separate context and image store from native Engine. |

On macOS, installing only a Docker CLI with Homebrew does **not** provide a Linux
engine. Likewise, a Windows CLI alone does not run this lab. Desktop supplies a
Linux environment on these hosts. Avoid a second engine inside WSL when using
Desktop integration. Education is covered by Desktop's free-use terms; review
[current subscription terms](https://docs.docker.com/subscription/desktop-license/) for other use.

## Route B: individual packages on native Linux

The following commands are for **Ubuntu and Fedora respectively**, not every
Linux distribution. Check prerequisites and conflicting packages in the official
guide before installing. Existing users should inspect what is already installed
rather than blindly removing packages or replacing a working setup.

### Ubuntu: official apt repository

Use [Docker's Ubuntu guide](https://docs.docker.com/engine/install/ubuntu/) for a
supported Ubuntu installation. Register Docker's signing key and repository:

```sh
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker run --rm hello-world
```

### Fedora: official dnf repository

Follow [Docker's Fedora guide](https://docs.docker.com/engine/install/fedora/).
These commands use the current `dnf config-manager` syntax; use the guide for
your supported Fedora version if yours differs. Verify the repository signing
key fingerprint shown in that guide before accepting it.

```sh
sudo dnf install dnf-plugins-core
sudo dnf config-manager addrepo --from-repofile https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker run --rm hello-world
```

| Package | Job |
| --- | --- |
| `docker-ce` | Engine daemon, which manages containers |
| `docker-ce-cli` | `docker` command and API client |
| `containerd.io` | Lower-level runtime stack, including containerd and runc |
| `docker-buildx-plugin` | Build interface used for images |
| `docker-compose-plugin` | `docker compose` commands for multiple services |

For [Debian](https://docs.docker.com/engine/install/debian/) or other systems,
use their own official instructions; Ubuntu repository commands are not universal.

### Linux permissions

Initially use `sudo docker ...` on native Engine, including `sudo docker compose ...`.
All workshop examples otherwise assume your user can access Docker.
If this is your own development machine and you accept that the **docker group
grants root-level host access**, the standard optional setup is:

```sh
sudo groupadd --force docker
sudo usermod -aG docker "$USER"
```

Sign out completely and sign back in, then run the checks below. On shared
university machines, follow administrator policy. Do not make the Docker socket
world-writable. See [Linux postinstall](https://docs.docker.com/engine/install/linux-postinstall/)
and [rootless mode](https://docs.docker.com/engine/security/rootless/) for alternatives.

## Sanity checks: run in the terminal you will use in class

```sh
git --version
docker version
docker info
docker context ls
docker compose version
docker buildx version
docker run --rm hello-world
```

Success means `docker version` shows **Client and Server**, Compose and Buildx
report versions, and `hello-world` prints its greeting and exits successfully.
A client version alone does not prove an engine is reachable. `hello-world`
also tests pulling and running, but does not test builds, ports, or this app's network.

The starter checkout intentionally has no root Dockerfile or Compose file.
After these sanity checks, begin [the file-writing lab](lab.md), not `compose up`.
Once you have written those files, the completed workshop check is:

```sh
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

`up` creates/starts services, `-d` detaches, and `--build` builds our image first.
`ps` displays state; wait until both services are healthy. Open http://localhost:8000 and click Add one.
Optional: `curl http://localhost:8000/health` should return `{"status":"ok"}`.
Use `curl.exe` in PowerShell if `curl` is aliased. Stop with `docker compose down`.

## Troubleshooting

| Symptom | First check |
| --- | --- |
| Command not found | Installation and PATH; open a new terminal after installing. |
| Client only / cannot connect | Start Desktop, or inspect `sudo systemctl status docker` on native Linux. Check `docker context ls` for the intended engine. |
| Socket permission denied | Use sudo on native Linux or complete the group login steps above. |
| Images missing after switching engines | Desktop and native Engine have different contexts/stores. Use the context matching the route you chose. |
| Port 8000 already in use | Stop your conflicting app, or change only the host side to `127.0.0.1:8001:8000` and browse port 8001. The smoke script assumes 8000. |
| Pull/build timeout or rate limit | Check internet, campus proxy, registry access, and Docker Hub login if needed; pre-pull before class. |
| No matching manifest / exec format error | Verify CPU architecture and image support. Emulation can be slower. |
| Redis unavailable / HTTP 503 | `docker compose ps` and `docker compose logs redis web`; restore Redis with `docker compose start redis`. |
| Page edits do not appear | The app is copied into the image. Run `docker compose up -d --build`. |

## Installation commands and options, decoded

These commands change host system settings; they are setup steps rather than
Docker container commands. `sudo` runs the following program with administrator
privileges. URLs and paths are arguments, not flags. A line beginning with `#`
is a shell comment.

| Command or option | Meaning |
| --- | --- |
| `wsl --version` / `wsl --status` | Windows Subsystem for Linux: display the installed version / current configuration. |
| `apt update` | Refresh Ubuntu's package index; it does not upgrade installed software. |
| `apt install ...` | Install the named packages. `ca-certificates` supplies trusted certificate authorities; `curl` is the download/request tool. The Docker packages are explained above. |
| `install -m 0755 -d /etc/apt/keyrings` | Here `install` is a filesystem utility: `-d` creates a directory, and `-m 0755` sets owner read/write/execute and group/other read/execute permissions. This `-d` is not Compose's detach flag. |
| `curl -fsSL URL -o PATH` | `-f` fail on HTTP errors; `-s` quiet progress; `-S` still show errors; `-L` follow redirects. `-o` takes the destination file path. Here it downloads Docker's public signing key. |
| `chmod a+r PATH` | Give all users read permission on the public key file. `a+r` is the permission expression. |
| `tee PATH <<EOF ... EOF` | `tee` writes its input to the file and terminal. `<<EOF` is a shell here-document: feed the following lines until the matching `EOF`. It writes Docker's apt repository configuration. |
| `Types: deb` / `URIs:` / `Components: stable` | Repository file fields: Debian binary packages, repository URL, and the stable component. These are configuration, not shell commands. |
| `Suites:` | The Ubuntu release codename. `$(...)` runs a shell expression and substitutes its output. `. /etc/os-release` loads OS variables; `&&` runs the following command only if loading succeeds; `echo` prints the selected value. `${UBUNTU_CODENAME:-$VERSION_CODENAME}` uses the Ubuntu codename, falling back to the version codename when empty/unset. |
| `Architectures: $(dpkg --print-architecture)` | `dpkg --print-architecture` prints the package architecture and substitutes it into that field. |
| `Signed-By:` | Path to the public key apt must use to verify this repository's signatures. |
| `dnf install dnf-plugins-core` | Install Fedora's repository-management plugin tools. `dnf install` installs named packages. |
| `dnf config-manager addrepo --from-repofile URL` | `config-manager` manages repositories; `addrepo` adds one; `--from-repofile` takes the URL of its repository definition. |
| `systemctl enable --now docker` | `enable` configures the Docker service to start at boot; `--now` starts it immediately too; `docker` is the system service name. |
| `systemctl status docker` | Show the Docker system service's state and recent status information. |
| `groupadd --force docker` | Create the group named `docker`; `--force` succeeds if it already exists. |
| `usermod -aG docker "$USER"` | `-a` appends; `-G` takes supplementary groups (here `docker`); `$USER` expands to your current username. Together `-aG` adds this group without replacing other memberships. Quotes preserve the value as one argument. Sign out and back in afterward. |

The unprivileged `docker run --rm hello-world` check and every other Docker
command above are broken down in [commands.md](commands.md). Prefix them with
`sudo` on native Linux if that is the access route your administrator selected.

## Optional: run the app without containerizing it

This is a before/after comparison, not a prerequisite for the Docker practical.
You need local Python 3.13 and Redis installed to do it. That host setup is exactly
the dependency work the Dockerfile will later package. A facilitator can demonstrate
it instead if students have only Docker installed.

In one terminal, start an installed Redis server on loopback port 6379:

```sh
redis-server --bind 127.0.0.1 --port 6379
```

`redis-server` is the program; `--bind` takes its listening IP; `--port` takes
the port number. If a local Redis server is already using that address/port,
use that existing service rather than trying to start a second one.

From the repository root, create a Python environment in a second terminal:

```sh
python3 -m venv .venv
```

`-m venv` runs Python's virtual-environment module; `.venv` is its destination.
Activate it on Linux/macOS with `source .venv/bin/activate`; `source` loads that
script into the current shell. On Windows PowerShell, create it with
`py -3.13 -m venv .venv` (`-3.13` selects that installed Python version), then
activate with `.venv\Scripts\Activate.ps1`. Follow local script-execution policy.

Then run:

```sh
python -m pip install -r requirements.txt
python -m flask --app app.app run --host 127.0.0.1 --port 8000
```

The first command runs pip's `install` action, reading `-r`'s filename argument.
The second runs Flask's CLI module: `--app app.app` selects the Python module
containing the app; `run` starts the development server; `--host` and `--port`
select its listening address. Use this development server only for the local
baseline; the Docker image uses Gunicorn.

The app defaults to Redis on localhost; if you already set `REDIS_HOST` in your
shell, ensure it points at this local server. Open http://localhost:8000 and click
Add one. Missing Redis produces a real 503, rather than a fake working counter.
Stop the Flask server with Ctrl+C before beginning the container lab so port
8000 is free. Leave an existing Redis service alone; stop a Redis process you
started for this demonstration when you no longer need it.
