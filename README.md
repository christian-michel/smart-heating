# 🔥 Smart Heating System

> IoT thermostat system for Raspberry Pi with **automatic storage management (USB / Dropbox / Local)** and **robust systemd deployment**

---

## 📌 Overview

Smart Heating is a **production-ready thermostat system** designed for Raspberry Pi.

It controls a heating system using:
- 🌡 Temperature sensor (DS18B20)
- 🔘 Physical button (manual mode)
- 💡 GPIO-controlled relay (via LED simulation)

It is built around a **separation of concerns architecture**:

- 🧠 Core system → `AppController`
- 🌡 Thermostat logic → sensor + heating control
- 💾 Storage system → USB / Dropbox / Local fallback
- 🌐 API layer → FastAPI (smartphone / remote control)
- 🖥 Web UI → lightweight interface (mobile-first)

---

## ⚙️ Key Features

✅ Automatic heating control  
✅ Manual override via button  
✅ Robust GPIO handling (lgpio)  
✅ Data logging (CSV)  
✅ Smart storage management:
- 🥇 USB (priority)
- 🥈 Dropbox
- 🥉 Local fallback

✅ Automatic synchronization:
- Local → USB
- Local → Dropbox
- USB → Dropbox

✅ systemd service (auto start on boot)  
✅ Fully automated installation  


---

## ⚙️ Key Features

### 🔥 Thermostat
- Automatic heating regulation
- Manual / Auto mode switching
- Real-time temperature monitoring

### 🧠 System architecture
- Central `AppController` (thread-safe orchestration)
- Safe lifecycle management (start / stop / restart)
- systemd integration (auto boot)

### 💾 Data logging
- CSV-based logging system
- Buffer-based writing (performance safe)
- Session-based file creation

### 📦 Storage management
Priority system:
1. 🥇 USB storage (`/mnt/usb_backup`)
2. 🥈 Dropbox sync
3. 🥉 Local fallback storage

### 🔄 Synchronization
- Automatic flush on USB mount
- Periodic sync to Dropbox
- Safe shutdown flush (critical)

### 🌐 Remote control API (FastAPI)
- Secure token-based authentication
- Full system control via HTTP
- Mobile-ready endpoints

---

## 🧱 Project Structure

```

smart-heating/
│
├── backend/
│ ├── core/
│ │ ├── app_controller.py       # 🧠 Main system orchestrator
│ │ ├── thermostat.py           # 🔥 Thermostat logic
│ │ ├── heating.py              # GPIO relay control
│ │ ├── sensor.py               # Temperature sensor
│ │
│ ├── services/
│ │ ├── logger_service.py       # 📊 CSV logging engine
│ │ ├── storage_manager.py      # 💾 Storage routing logic
│ │ └── storage/
│ │ ├── usb_storage.py
│ │ ├── dropbox_storage.py
│ │ └── local_storage.py
│
│ ├── api/
│ │ ├── api_server.py           # 🚀 FastAPI entrypoint
│ │ ├── controller.py           # Singleton AppController wrapper
│ │ ├── dependencies.py         # 🔐 Auth (Bearer token)
│ │ │
│ │ └── routes/
│ │ ├── status.py               # System status
│ │ ├── heating.py              # Heating control
│ │ ├── mode.py                 # Manual / Auto mode
│ │ ├── system.py               # Start / Stop / Restart
│ │ └── ui.py                   # Web UI (mobile interface)
│
├── install/
│ ├── install.sh
│ ├── uninstall.sh
│ └── setup_dependencies.sh
│
├── data/ # Local fallback storage
└── README.md

```

---

## 🧠 System Architecture

### 🔥 Core Principle

The system is driven by a **single orchestrator**:

```python
AppController

```

It manages:

* Thermostat lifecycle
* Thread execution
* Safe shutdown
* API interactions

---

### 🌡 Heating Logic
#### Auto mode:

```
if temperature < target - threshold → heating ON
if temperature > target + threshold → heating OFF
```

#### Manual mode:
Heating is forced ON or OFF via API or button

---

### 🌐 API (FastAPI)

#### 🔐 Authentication

All endpoints are protected :

```http
Authorization: Bearer <API_TOKEN>
```
Token defined in environment variable :
```bash
API_TOKEN=your_secret_token
```

---

### 📡 Main endpoints
📊 System status
```http
GET /status
```

---

### 🔥 Heating control
```http
POST /heating/on
POST /heating/off
```

---

### 🎛 Mode control
```http
POST /mode/manual
POST /mode/auto
```

---

### 🔄 System control
```http
POST /restart
POST /start
POST /stop
```

---

### 📱 Web UI (Mobile Interface)

Accessible via:
```
http://RASPBERRY_IP:8000
```
Features:

* Temperature display
* Heating ON/OFF control
* Mode switch (Auto / Manual)
* System status view

---

## 🧠 How It Works

### 🔥 Heating Logic

- Manual mode ON → heating forced ON
- Manual mode OFF → thermostat mode:

```

if temp < target - tolerance → ON
if temp > target + tolerance → OFF

````

---

### 💾 Storage Strategy

Priority order:

1. **USB (/mnt/usb_backup)**
2. **Dropbox**
3. **Local (/opt/smart-heating/data)**

---

### 🔄 Synchronization Rules

| Source | Destination | When |
|------|--------|------|
| Local | USB | once when USB appears |
| Local | Dropbox | once |
| USB | Dropbox | every 60s |

---

## 🧰 Installation

### 📦 Run installer

```bash
sudo ./install/install.sh
````

---

### ⚠️ After install

Edit environment file:

```bash
sudo nano /opt/smart-heating/.env
```

Add:

```env
DROPBOX_APP_KEY=
DROPBOX_APP_SECRET=
DROPBOX_REFRESH_TOKEN=
```

Restart service:

```bash
sudo systemctl restart smart-heating
```

---

## 🧹 Uninstall

```bash
sudo ./install/uninstall.sh
```

✔ Removes:

* service
* project files
* user (if safe)

❌ Keeps:

* USB data
* CSV files

---

## 🔌 Hardware Setup

| Component   | GPIO    |
| ----------- | ------- |
| LED / Relay | GPIO 17 |
| Button      | GPIO 27 |
| DS18B20     | GPIO 4  |

---

## 💽 USB Configuration (EXT4)

### Recommended setup

```bash
sudo mkfs.ext4 /dev/sda1
sudo mkdir -p /mnt/usb_backup
```

---

### Manual mount

```bash
sudo mount /dev/sda1 /mnt/usb_backup
sudo chown -R smartheating:smartheating /mnt/usb_backup
```

---

## ☁️ Dropbox Setup

### 1️⃣ Create App

Go to:
👉 [https://www.dropbox.com/developers/apps](https://www.dropbox.com/developers/apps)

* Create App
* Scoped access
* Full Dropbox

---

### 2️⃣ Generate Token

* Enable refresh token
* Copy:

```
APP_KEY
APP_SECRET
REFRESH_TOKEN
```

---

### 3️⃣ Add to `.env`

---

## 📊 Data Logging

CSV format:

```
timestamp,temperature,heating,switch
2026-04-10 12:00:00,21.5,True,False
```

---

## 🔍 Monitoring

### Service status

```bash
sudo systemctl status smart-heating
```

### Logs

```bash
journalctl -u smart-heating -f
```

---

## 🧪 To do post-install
```bash
#!/bin/bash

# Au démarrage, juste après l'installation du programme : 
lsblk
# exemple de réponse attendue : 
# NAME        MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
# loop0         7:0    0  905M  0 loop 
# sda           8:0    1 28,9G  0 disk 
# └─sda1        8:1    1 28,9G  0 part /mnt/usb_backup
# mmcblk0     179:0    0 59,5G  0 disk 
# ├─mmcblk0p1 179:1    0  512M  0 part /boot/firmware
# └─mmcblk0p2 179:2    0   59G  0 part /
# zram0       254:0    0  905M  0 disk [SWAP]


# Insertion du token Dropbox et de la clé de connexion à l'API
sudo -u smartheating echo "# Dropbox
DROPBOX_APP_KEY="your_api_key"
DROPBOX_APP_SECRET="your_api_secret"
DROPBOX_REFRESH_TOKEN="your_refresh_token"

# API Token
API_TOKEN=changeme" > /opt/smart-heating/.env

ls -l /opt/smart-heating/ 
sudo -u smartheating cat /opt/smart-heating/.env

# Lancer le service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl restart smart-heating.service

# Faire les vérifications de base pour s'assurer que tout fonctionne bien : 
systemctl status smart-heating.service
# exemple de réponse attendue : 
# ● smart-heating.service - Smart Heating API (FastAPI + Controller)
#      Loaded: loaded (/etc/systemd/system/smart-heating.service; enabled; preset: enabled)
#      Active: active (running) since Sat 2026-04-18 10:15:41 CEST; 7s ago
#  Invocation: 19f79777bd6e4ebbaf9a16fb2ae98b1a
#    Main PID: 7272 (uvicorn)
#       Tasks: 4 (limit: 756)
#         CPU: 5.036s
#      CGroup: /system.slice/smart-heating.service
#              └─7272 /opt/smart-heating/venv/bin/python3 /opt/smart-heating/venv/bin/uvicorn backend.api.api_server:app --host 0.0.0.0 --port 8000
# 
# avril 18 10:15:46 maison uvicorn[7272]: [AppController] Démarrage...
# avril 18 10:15:47 maison uvicorn[7272]: [HeatingSystem] GPIO actif (pin=17)
# avril 18 10:15:47 maison uvicorn[7272]: [StorageManager] Initialisation...
# avril 18 10:15:48 maison uvicorn[7272]: ✅ Dropbox connecté avec succès
# avril 18 10:15:48 maison uvicorn[7272]: [StorageManager] USB disponible ✅
# avril 18 10:15:48 maison uvicorn[7272]: [StorageManager] STOCKAGE ACTIF → USB
# avril 18 10:15:48 maison uvicorn[7272]: [StorageManager] Sync local → USB...
# avril 18 10:15:48 maison uvicorn[7272]: [StorageManager] Sync local → USB OK
# avril 18 10:15:48 maison uvicorn[7272]: [StorageManager] Sync USB → Dropbox...
# avril 18 10:15:48 maison uvicorn[7272]: [Dropbox] Sync depuis : /mnt/usb_backup


ss -tulnp | grep 8000
# réponse attendue : 
# tcp   LISTEN 0      2048         0.0.0.0:8000       0.0.0.0:*  

curl -H "Authorization: Bearer changeme" http://localhost:8000/status
# exemple de réponse attendue : 
# {"running":true,"temperature":22.0,"heating":false,"manual_mode":false}

journalctl -u smart-heating.service -f
```

---

## 🧪 Debug Tips

### GPIO test

```bash
python -c "from gpiozero import LED; LED(17).on()"
```

### Check USB

```bash
lsblk
mount | grep usb_backup
```

---

## 🚀 Run Manually

```bash
cd /opt/smart-heating
source venv/bin/activate
python -m backend.core.thermostat
```

---

## 🛠 Troubleshooting

### ❌ LED not working

* Check GPIO group
* Check pin_factory = lgpio

---

### ❌ USB not used

* Check mount
* Check permissions

---

### ❌ Dropbox not syncing

* Check `.env`
* Restart service

---

## 📈 Future Improvements

* Web dashboard
* MQTT integration
* Remote control API
* OTA updates

---

## 👨‍💻 Author

Built with ❤️ for Raspberry Pi IoT automation

---

## 📄 License

GPL v3 License
