# 🔥 Smart Heating System

> IoT thermostat system for Raspberry Pi with **automatic storage management (USB / Dropbox / Local)** and **robust systemd deployment**

---

## 📌 Overview

Smart Heating is a **production-ready thermostat system** designed for Raspberry Pi.

It controls a heating system using:
- 🌡 Temperature sensor (DS18B20)
- 🔘 Physical button (manual mode)
- 💡 GPIO-controlled relay (via LED simulation)

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

## 🧱 Project Structure

```

smart-heating/
│
├── backend/
│   ├── core/
│   │   ├── thermostat.py      # 🔥 Main logic
│   │   ├── heating.py         # GPIO control
│   │   └── temperature.py     # Sensor reading
│   │
│   ├── services/
│   │   ├── logger_service.py  # CSV logging
│   │   ├── storage_manager.py # Storage orchestration
│   │   └── storage/
│   │       ├── usb_storage.py
│   │       ├── dropbox_storage.py
│   │       └── local_storage.py
│
├── install/
│   ├── install.sh             # 🚀 Installer (PRO)
│   ├── uninstall.sh           # 🧹 Uninstaller (PRO)
│   └── setup_dependencies.sh
│
├── data/                      # Local fallback storage
└── README.md

```

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
