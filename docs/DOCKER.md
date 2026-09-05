# Docker Deployment Guide

This document covers how the Docker setup works, and — because getting GPIO access right inside a
container took real trial and error — a detailed log of the problems we hit and how each one is
handled, so a future rebuild (or a fork on different hardware) doesn't have to rediscover them.

## Quick start

```bash
sudo ./install/install_docker.sh
```

Safe to re-run any time: it never touches `data/` or `.env`, it stops any bare-metal `systemd`
service first (to avoid two processes fighting over the same GPIO pins), and it always ends with
`docker compose build && docker compose up -d`.

```bash
cd /opt/smart-heating
sudo docker compose ps            # should show "Up", not "Restarting"
sudo docker compose logs -f       # look for "[entrypoint] OK"
```

## What the container gets access to, and why

`docker-compose.yml` deliberately avoids `privileged: true`. Instead:

- **`devices: /dev/gpiochip0`** — the actual GPIO controller of a Raspberry Pi 3. This is the
  single device the `lgpio` backend needs; nothing broader is granted.
- **`group_add: ${GPIO_GID}`** — the host's `gpio` group id (auto-detected by
  `install_docker.sh` and written to `.env`), added as a *supplementary* group to the
  container's non-root user. The kernel checks the device's group by numeric GID, so this
  works without needing a matching `/etc/group` entry inside the image.
- **`/sys/bus/w1/devices` mounted read-only** — the 1-Wire sensor's sysfs tree.
- **`/mnt/usb_backup`, mounted with `bind: propagation: rslave`** — so a USB key mounted or
  removed on the *host* after the container has started is still visible inside it. Docker's
  default bind-mount propagation (`rprivate`) would otherwise freeze the container's view of
  that mount point at container-start time.
- **`/opt/smart-heating/data`** — plain bind mount for the local CSV fallback storage.

The container runs as a dedicated non-root user (`appuser`, uid 1000) — mirroring the bare-metal
install's own `smartheating` user + `gpio` group approach — rather than as root.

## The entrypoint's GPIO check (`docker/entrypoint.sh`)

`heating.py` and `thermostat.py` both wrap their GPIO initialization in a `try/except` that falls
back to a `simulation_mode` on failure — useful for developing without hardware, dangerous in
production: the API keeps answering normally, `/status` reports a consistent-looking state, but
the relay never actually moves, with only a quiet log line to say why.

The entrypoint runs a real GPIO probe (opening the actual relay pin with the same non-root user
that will run the app) **before** starting uvicorn. If it fails, the container exits non-zero;
with `restart: unless-stopped` Docker retries it and the failure reason is printed clearly in
`docker compose logs` under an `[entrypoint]` prefix — a loud, visible failure instead of a
heating system that silently never heats.

## Problems we hit building this, in the order we hit them

### 1. `docker-compose-plugin` package not found

Debian's own apt repos don't ship a package with that name — that's the name Docker's *official*
repo (`download.docker.com`) uses, which we deliberately don't add (avoids depending on a
third-party repo, and at the time of writing Docker's official repo didn't even have complete
`trixie` packages yet). Debian's own equivalent package is simply called **`docker-compose`**
(it's still Compose v2, not the old Python v1 tool). `install_docker.sh` tries the
official-repo name first, falls back to the Debian name automatically.

### 2. `docker` command not found after installing `docker.io`

`docker-cli` is a `Recommends` of `docker.io` on Debian, not a hard dependency — so
`--no-install-recommends` (used to keep the image lean) silently skipped it. Fixed by installing
`docker-cli` explicitly alongside `docker.io`.

### 3. A broken `docker compose` symlink (self-inflicted)

An earlier version of our own repair logic searched for the `docker-compose` binary with a
pattern that also matched `/usr/share/doc/docker-compose` (a *directory*), and created a bad
symlink pointing at it. The fix, in order: `apt-get install --reinstall docker-compose` to
restore the package's own files first; only as a last resort does the script search explicit
candidate paths, and only after verifying each one is really an ELF executable (`file`), not
just "a file that exists".

### 4. `liblgpio-dev` not found during `docker compose build`

This package only exists in the **Raspberry Pi Foundation's own apt repo**
(`archive.raspberrypi.com`), not in vanilla Debian — and our Docker base image
(`python:3.13-slim`) only has Debian's own repos. This is a documented, recurring gap on Debian
13 "trixie" in general (confirmed by multiple independent sources, including guides aimed at
bare-metal Raspberry Pi OS trixie users hitting the exact same missing package). Rather than add
the Raspberry Pi repo + its signing key into the image, `docker/Dockerfile` builds `liblgpio`
from its official upstream source (`github.com/joan2937/lg`, `make && make install`) — the same
method the package maintainers themselves use, and one that doesn't depend on any particular
distro's packaging.

### 5. GPIO check failing with `No such file or directory: '.lgd-nfy-3'`

`lgpio` creates its internal notification pipes (`.lgd-nfy<N>`) in the process's *current working
directory* — a documented quirk of the upstream library
(`github.com/joan2937/lg/issues/12`). The container's `WORKDIR` (`/app`) was owned by `root`,
unwritable by the non-root `appuser`. Fixed two ways, belt-and-suspenders, since this couldn't be
tested on real hardware ahead of time:
- `LG_WD=/tmp` — the environment variable the library itself documents for this.
- `chown -R appuser:appuser /app` in the Dockerfile as a fallback, in case `LG_WD` turns out not
  to be honored by the local `lgpio` Python module specifically (only confirmed for the remote
  `rgpio` tools in upstream's own docs).

### 6. `.env` permission denied running `docker compose` without `sudo`

`.env` is `chmod 600`, owned by `root` (it holds the API token) — created that way deliberately.
Any `docker compose` command that reads it (`build`, `up`, `logs`, ...) needs `sudo`, same as the
install script itself uses throughout.

## Updating an already-running deployment

- **Only `.env` or `docker-compose.yml` changed** → `sudo docker compose up -d` (recreates the
  container, no rebuild needed for compose-file-only changes) or `sudo docker compose restart`
  for `.env`-only changes.
- **Anything under `backend/`, `docker/Dockerfile`, or `docker/entrypoint.sh` changed** → needs a
  rebuild: `sudo docker compose build && sudo docker compose up -d`.
- **Simplest, always-correct option**: re-run `sudo ./install/install_docker.sh` — it re-syncs the
  source (excluding `data/` and `.env`), then rebuilds and restarts regardless of what changed.

## Verifying it's actually working, not just "running"

A container reporting `Up` only means the process is alive — it doesn't confirm the entrypoint's
GPIO check passed at that exact moment if it's mid-restart-loop. Check properly:

```bash
sudo docker compose logs --tail=50   # look for "[entrypoint] OK", not "ERREUR CRITIQUE"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/status
```
And, ideally, a physical check once: force the relay via `POST /heating/true` and confirm it
actually clicks/lights up, not just that the API returns success.
