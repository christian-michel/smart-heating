# API Reference

Base URL: `http://<raspberry-ip>:8000`

All endpoints (except `GET /` and `GET /docs`) require a Bearer token:
```
Authorization: Bearer <API_TOKEN>
```
The token is set in `.env` (`API_TOKEN`). The comparison is a plain string match — see [SECURITY.md](SECURITY.md) for the implications of that if you expose this API beyond your LAN.

Interactive Swagger UI is always available, unauthenticated, at `GET /docs`.

---

## GET /status

Returns the full current state.

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/status
```

```json
{
  "running": true,
  "temperature": 21.5,
  "heating": false,
  "manual_mode": false,
  "target_temperature": 19.0
}
```

- `running`: `false` if the regulation loop has been stopped via `POST /stop` and not yet restarted. When `false`, the other fields are the last known values, not live readings.
- `temperature`: last valid DS18B20 reading (°C), or `null` if the sensor has never returned a valid value.

---

## GET /temperature/target

Returns just the current setpoint.

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/temperature/target
```
```json
{ "target_temperature": 19.0 }
```

## POST /temperature/target

Sets the setpoint. Body: `{"value": <float>}`, validated to `5.0 ≤ value ≤ 30.0`.

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"value": 20.5}' http://localhost:8000/temperature/target
```
Success:
```json
{ "status": "ok", "target_temperature": 20.5 }
```
Failure (out of range, or internal error) returns HTTP 500/422 with a `detail` field — check `res.ok` / HTTP status, not just the JSON body, when scripting against this.

---

## POST /manual/{state}

Switches Auto/Manual mode. `state` is `true` or `false` (part of the URL path, not the body).

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/manual/true
```
Success:
```json
{ "manual_mode": true }
```
Failure (regulation loop not ready, e.g. right after `POST /stop`):
```json
{ "error": "thermostat not ready" }
```
Note: a failure response is still **HTTP 200** — check for the `error` key, not just the status code.

---

## POST /heating/{state}

Forces the relay ON or OFF. `state` is `true` or `false`.

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/heating/true
```
Success:
```json
{ "heating": true }
```
Rejected by the anti-short-cycle protection (relay changed state less than the configured minimum interval ago — same protection the automatic regulation loop itself respects):
```json
{ "error": "switch rejected: anti short-cycle protection active" }
```
Thermostat not initialized:
```json
{ "error": "thermostat not ready" }
```
Again: these are **HTTP 200** responses with an `error` key on failure, not 4xx/5xx — client code must check for the `error` field explicitly rather than relying on `heating`/`manual_mode` being present, or relying on HTTP status alone. This is a real gap we found and fixed in the bundled web UI (`ui.py`) — if you write your own client, replicate the same check.

---

## POST /start / POST /stop / POST /restart

Controls the `AppController`'s background regulation loop — **not** the systemd service or the Docker container process itself.

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/stop
# {"status": "stopped"}
```

- `/stop`: stops the loop, releases GPIO. The API process keeps running and answering requests, but `GET /status` will return `running: false` and frozen values until `/start` is called.
- `/start`: (re)creates the thermostat and resumes the loop.
- `/restart`: `stop` then a 1-second pause then `start`.

---

## GET /

Serves the mobile web UI (`backend/api/routes/ui.py`) — no token required to load the page itself, but every API call the page makes still requires the token (entered once, stored in the browser's `localStorage`).

## GET /docs

FastAPI's Swagger UI — public, no token required. Useful for exploring/testing the API by hand, but also means anyone who can reach the port can see the full API surface. Consider this if exposing the API beyond your LAN (see [SECURITY.md](SECURITY.md)).
