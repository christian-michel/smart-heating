# 🔥 Smart Heating System

> IoT thermostat system for Raspberry Pi with **automatic storage management (USB / Dropbox / Local)**, a **mobile-friendly web UI**, and two deployment modes: **bare-metal (systemd)** or **Docker**.

---

## 📌 Overview

Smart Heating is a thermostat system designed for a Raspberry Pi (3 or later). It controls a heating system using:

- 🌡 A DS18B20 temperature sensor (1-Wire)
- 🔘 A physical button for manual mode
- 🔌 A GPIO-controlled relay

It's built around a separation-of-concerns architecture:

- 🧠 **Core orchestrator** → `AppController` (thread-safe, owns the regulation loop)
- 🌡 **Thermostat logic** → sensor reading + hysteresis + anti-short-cycle protection
- 💾 **Storage system** → USB → Dropbox → local fallback, in that priority order
- 🌐 **API layer** → FastAPI, Bearer-token authenticated
- 🖥 **Web UI** → self-contained mobile page served directly by the API (no separate frontend build)

---

## ⚙️ Key Features

### 🔥 Thermostat
- Automatic heating regulation with configurable tolerance
- Manual / Auto mode switching (button or API)
- **Anti-short-cycle protection** on the relay — enforced identically whether the switch is triggered by the automatic regulation loop *or* by an API call, so the hardware can't be hammered by rapid remote toggling
- Real-time temperature monitoring with sensor CRC validation and fallback to the last known-good reading

### 🧠 System architecture
- Central `AppController` (thread-safe orchestration, single lock discipline across the background loop and API-triggered actions)
- Safe lifecycle management (start / stop / restart), exposed both via systemd and via the API
- Fails loudly rather than silently: if GPIO access can't be established, the app refuses to run in a "simulation" state without saying so (see [Docker deployment](docs/DOCKER.md) for how this is enforced in containers)

### 💾 Data logging & storage
- CSV-based logging, buffered writes
- Storage priority: 🥇 USB (`/mnt/usb_backup`) → 🥈 Dropbox → 🥉 local fallback (`/opt/smart-heating/data`)
- Automatic sync on USB mount, periodic sync to Dropbox, flush on shutdown

### 🌐 Remote control API (FastAPI)
- Bearer-token authentication on every endpoint
- Full system control over HTTP (heating, mode, target temperature, start/stop/restart)
- Configurable CORS, so a browser-based client on another origin can reach it
- See [docs/API.md](docs/API.md) for the full reference

### 📱 Web UI
- A single self-contained page (`backend/api/routes/ui.py`), no build step, no external CDN — served directly by the API at `http://<raspberry-ip>:8000/`
- Circular gauge for the target temperature, live chart (built from polled readings), Auto/Manual toggle, manual heating override, and a collapsible system panel (start/stop/restart, hardware info)
- The API token is entered once and kept in the phone's browser storage — no server-side session needed
- Works from any device on the same network; add it to your phone's home screen for an app-like shortcut

---

## 🧱 Project Structure

```
smart-heating/
├── backend/
│   ├── config.py                 # GPIO pins, sensor ID, tolerances, storage paths
│   ├── main.py                   # Standalone entrypoint (not used by the API/Docker path)
│   ├── core/
│   │   ├── app_controller.py     # 🧠 Main orchestrator (thread-safe)
│   │   ├── thermostat.py         # 🔥 Regulation logic, hysteresis, anti-short-cycle
│   │   ├── heating.py            # GPIO relay control (LED-based)
│   │   ├── switch.py             # Physical button (manual mode)
│   │   └── temperature.py        # DS18B20 sensor reader (CRC + fallback)
│   ├── services/
│   │   ├── logger_service.py     # 📊 CSV logging engine
│   │   ├── storage_manager.py    # 💾 Storage routing logic
│   │   └── storage/
│   │       ├── usb_storage.py
│   │       ├── dropbox_storage.py
│   │       └── local_storage.py
│   ├── api/
│   │   ├── api_server.py         # 🚀 FastAPI entrypoint + CORS
│   │   ├── controller.py         # Singleton AppController wrapper
│   │   ├── dependencies.py       # 🔐 Bearer-token auth
│   │   └── routes/
│   │       ├── status.py         # GET /status
│   │       ├── heating.py        # POST /heating/{state}
│   │       ├── mode.py           # POST /manual/{state}
│   │       ├── temperature.py    # GET/POST /temperature/target
│   │       ├── system.py         # POST /start /stop /restart
│   │       └── ui.py             # GET / — mobile web UI
│   └── tests/                    # pytest unit tests
├── docker/
│   ├── Dockerfile                # Builds liblgpio from source, non-root user
│   └── entrypoint.sh             # Fails loudly if real GPIO access isn't available
├── docker-compose.yml            # GPIO device, 1-Wire mount, USB mount, restart policy
├── install/
│   ├── install.sh                # Bare-metal install (venv + systemd)
│   ├── install_docker.sh         # Docker install (idempotent, safe to re-run)
│   ├── uninstall.sh
│   └── setup_dependencies.sh
├── data/                         # Local fallback storage (bare-metal path)
├── dependencies_apt.txt
├── requirements.txt
└── docs/
    ├── API.md                    # Full endpoint reference
    ├── DOCKER.md                 # Docker deployment guide + troubleshooting log
    └── SECURITY.md               # Threat model, hardening notes, what's NOT covered
```

---

## 🧠 How It Works

### Auto mode
```
if temperature < target - tolerance → heating ON
if temperature > target + tolerance → heating OFF
```
Both transitions are gated by the anti-short-cycle protection (default: 60s minimum between switches).

### Manual mode
Heating is forced ON or OFF via the API or the physical button, still subject to the same anti-short-cycle protection — a rapid sequence of API calls can't bypass it.

---

## 🚀 Installation

Two ways to run this project. Docker is recommended for anyone who wants the app isolated from Raspberry Pi OS package updates and automatic recovery after a power outage; bare-metal is simpler to inspect/debug directly.

### Option A — Docker (recommended)

```bash
sudo ./install/install_docker.sh
```

This installs Docker + Compose if needed, builds the image (compiling `liblgpio` from source — see [docs/DOCKER.md](docs/DOCKER.md) for why), detects your host's `gpio` group, wires up the GPIO device and 1-Wire sensor into the container without `--privileged`, and starts it with `restart: unless-stopped` so it survives reboots and power cuts.

The script is **idempotent** — re-run it any time after pulling code changes; it never touches `data/` or `.env`.

Useful commands:
```bash
cd /opt/smart-heating
sudo docker compose ps          # check it's "Up", not "Restarting"
sudo docker compose logs -f     # watch it live — look for [entrypoint] OK
sudo docker compose restart     # after an .env change
sudo docker compose build && sudo docker compose up -d   # after a code change
```

If the container keeps restarting, `docker compose logs` will show a `[entrypoint]` line explaining exactly what's blocking (device, permissions, GPIO_GID) instead of silently falling back to a non-functional simulation mode. See [docs/DOCKER.md](docs/DOCKER.md) for the full list of pitfalls we hit building this (Debian package naming, `liblgpio-dev` availability, working-directory permissions) and how they're handled.

### Option B — Bare-metal (venv + systemd)

```bash
sudo ./install/install.sh
```

Then edit `/opt/smart-heating/.env` (Dropbox keys, `API_TOKEN`, `CORS_ALLOWED_ORIGINS`) and:
```bash
sudo systemctl restart smart-heating
```

### Uninstall

```bash
sudo ./install/uninstall.sh
```
Removes the service/container and project files. Keeps USB data and CSV files.

---

## 🔐 Configuration (`.env`)

| Variable | Purpose | Default |
|---|---|---|
| `API_TOKEN` | Bearer token required on every API call | `changeme` — **change this** |
| `CORS_ALLOWED_ORIGINS` | Comma-separated origins allowed to call the API from a browser, or `*` for LAN use | `*` |
| `DROPBOX_APP_KEY` / `DROPBOX_APP_SECRET` / `DROPBOX_REFRESH_TOKEN` | Optional Dropbox sync | empty |
| `GPIO_GID` | (Docker only) host `gpio` group id, auto-detected by `install_docker.sh` | auto |

See [docs/SECURITY.md](docs/SECURITY.md) for what these settings do and don't protect against.

---

## 🔌 Hardware Setup

| Component | GPIO |
|---|---|
| Relay (heating) | GPIO 17 |
| Manual button | GPIO 27 |
| DS18B20 (1-Wire) | GPIO 4 |

1-Wire must be enabled at the OS level (`dtoverlay=w1-gpio` in `/boot/firmware/config.txt`) — this is true whether you run bare-metal or in Docker, since it's a kernel/device-tree setting, not something the app or container can configure.

---

## 💽 USB Configuration

```bash
sudo mkfs.ext4 /dev/sda1
sudo mkdir -p /mnt/usb_backup
sudo mount /dev/sda1 /mnt/usb_backup
sudo chown -R smartheating:smartheating /mnt/usb_backup   # bare-metal
```
`install_docker.sh` detects and mounts a USB key automatically and `chown`s it to the container's uid.

---

## ☁️ Dropbox Setup

1. Create an app at [dropbox.com/developers/apps](https://www.dropbox.com/developers/apps) (scoped access, full Dropbox).
2. Enable refresh tokens, copy `APP_KEY` / `APP_SECRET` / `REFRESH_TOKEN`.
3. Add them to `.env`, then restart the service/container.

---

## 📊 Data Logging

CSV format:
```
timestamp,temperature,heating,switch
2026-04-10 12:00:00,21.5,True,False
```

---

## 🔍 Monitoring

**Bare-metal:**
```bash
sudo systemctl status smart-heating
journalctl -u smart-heating -f
```

**Docker:**
```bash
cd /opt/smart-heating
sudo docker compose ps
sudo docker compose logs -f
```

**Either way**, a quick functional check:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/status
# {"running":true,"temperature":21.5,"heating":false,"manual_mode":false,"target_temperature":19.0}
```

---

## 🛠 Troubleshooting

| Symptom | Likely cause |
|---|---|
| Relay never triggers, but the API says `heating: true` | GPIO backend silently in simulation mode — should no longer happen in Docker (the entrypoint refuses to start), but check `docker compose logs` / journal for `[HeatingSystem] GPIO non disponible` |
| `switch rejected: anti short-cycle protection active` | Expected — the relay changed state less than 60s ago. Wait, or check the tolerance/cycle settings in `config.py` |
| USB not used | Check `lsblk` / `mount \| grep usb_backup` and ownership |
| Dropbox not syncing | Check `.env` values, restart the service/container |
| Docker build fails on `liblgpio-dev` | Expected on a vanilla Debian base image — see [docs/DOCKER.md](docs/DOCKER.md), it's built from source instead |
| `docker compose` not found after installing `docker.io` | See [docs/DOCKER.md](docs/DOCKER.md) — package naming differs between Debian's own repos and Docker's official repo |

Full deployment troubleshooting log: [docs/DOCKER.md](docs/DOCKER.md).

---

## 📈 Future Improvements

- MQTT integration
- OTA updates
- Scheduling / programmable heating periods

---

## 👨‍💻 Author

Built for Raspberry Pi IoT automation.

## 📄 License

GPL v3 — see [LICENSE](LICENSE).
