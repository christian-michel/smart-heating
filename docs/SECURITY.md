# Security Notes

This project is designed for **home LAN use**. This document is an honest account of what's
protected, what isn't, and what to do before exposing it any further than your own network.

## What's in place

- **Bearer token auth** on every state-changing and state-reading endpoint (`GET /status`,
  `POST /heating/{state}`, `POST /manual/{state}`, `POST /temperature/target`,
  `POST /start|stop|restart`). Only `GET /` (the web UI shell) and `GET /docs` are public.
- **Anti-short-cycle protection on the relay**, enforced identically for the automatic
  regulation loop and for API-triggered changes — an attacker (or a buggy client) sending rapid
  `POST /heating/true` / `POST /heating/false` calls can't hammer the physical relay faster than
  the configured minimum interval.
- **Non-root container** (Docker deployment) with GPIO access scoped to a single device
  (`/dev/gpiochip0`) via group membership, not `--privileged`.
- **`.env` permissions**: `chmod 600`, owned by `root` — not readable by the container's uid or
  by a non-privileged user on the host.
- **Configurable CORS** (`CORS_ALLOWED_ORIGINS`) instead of a hardcoded wildcard baked into code.

## What's NOT protected against, if you go beyond your LAN

- **The token comparison is a plain string equality check**, not constant-time. On a LAN this is
  a non-issue; if you expose this API to the internet, that's a (minor, but real) timing-attack
  surface.
- **No rate limiting or lockout on failed auth attempts.** Combined with the default token
  (`changeme`) being an easy guess, this matters a lot if you port-forward the API. **Change
  `API_TOKEN` before doing that, full stop.**
- **No TLS.** The token and all traffic travel in clear HTTP. Fine on a trusted home LAN; not fine
  over the open internet. If you need remote access, put this behind:
  - a reverse proxy with TLS (Caddy, nginx) if you want a stable public endpoint, or
  - a VPN back into your home network (WireGuard, Tailscale) — generally the better default for a
    single-user home automation setup, since it avoids exposing the API's port at all.
- **`GET /docs` is public** and lists the entire API surface. Harmless on a LAN; consider
  disabling it (`FastAPI(docs_url=None)`) if the port is ever reachable from the internet.
- **A stopped regulation loop (`POST /stop`) doesn't stop the API process** — `GET /status` will
  keep returning the last known values with `running: false`, which the bundled web UI surfaces
  as a "Système arrêté" badge, but any script you write against this API should check the
  `running` field explicitly rather than assuming a response means the system is live.

## Recommendations if you plan to expose this beyond your LAN

1. Change `API_TOKEN` to something long and random (e.g. `openssl rand -hex 32`).
2. Restrict `CORS_ALLOWED_ORIGINS` to the exact origin(s) you'll call it from — don't leave `*` set.
3. Put it behind a VPN or a TLS-terminating reverse proxy; don't port-forward port 8000 directly.
4. Disable `/docs` in production if you go the reverse-proxy route.
5. Keep an eye on `docker compose logs` (or `journalctl -u smart-heating`) for repeated auth
   failures — there's currently no automated alerting on that, so it's a manual check.
