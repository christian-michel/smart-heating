# 🏠 smart-heating
thermostat-iot

## 1️⃣ Présentation

Ce projet a pour objectif de **créer un système domotique pour piloter le chauffage d’une maison** à l’aide d’un Raspberry Pi, d’une sonde de température, d’une LED représentant le chauffage et d’un interrupteur physique.  
Le système est conçu pour être **pilotable à distance via une application web** et pour fonctionner en **logiciel libre**, avec un enregistrement automatique des températures sur une clé USB, rotation journalière, et sauvegarde future sur Dropbox.

Le projet se concentre sur :  

- **Mesure de la température** et pilotage du chauffage  
- **Interface physique** : bouton poussoir pour activer/désactiver le chauffage  
- **Journalisation** des relevés de température en CSV  
- **Démarrage et extinction orchestrés** du Raspberry Pi  

---

## 2️⃣ Arborescence du projet

smart-heating/

├── backend

│   ├── config.py

│   ├── core

│   │   ├── heating.py

│   │   ├── __init__.py

│   │   ├── __pycache__

│   │   │   ├── heating.cpython-313.pyc

│   │   │   ├── __init__.cpython-313.pyc

│   │   │   ├── switch.cpython-313.pyc

│   │   │   ├── temperature.cpython-313.pyc

│   │   │   └── thermostat.cpython-313.pyc

│   │   ├── switch.py

│   │   ├── temperature.py

│   │   └── thermostat.py

│   ├── data

│   │   ├── temperature_2026-03-11_23-31-56.csv

│   │   ├── temperature_2026-03-11_23-34-23.csv

│   │   ├── temperature_2026-03-11_23-54-23.csv

│   │   ├── temperature_2026-03-12_00-04-00.csv

│   │   ├── temperature_2026-03-12_06-06-44.csv

│   │   └── temperature_2026-03-12_13-05-56.csv

│   ├── __init__.py

│   ├── logs

│   │   ├── log_2026-02-20.csv

│   │   └── log_2026-02-21.csv

│   ├── __pycache__

│   │   ├── config.cpython-313.pyc

│   │   └── __init__.cpython-313.pyc

│   ├── pyproject.toml

│   ├── services

│   │   ├── __init__.py

│   │   ├── logger_service.py

│   │   ├── __pycache__

│   │   │   ├── __init__.cpython-313.pyc

│   │   │   ├── logger_service.cpython-313.pyc

│   │   │   └── storage_manager.cpython-313.pyc

│   │   ├── storage

│   │   │   ├── base_storage.py

│   │   │   ├── dropbox_storage.py

│   │   │   ├── __init__.py

│   │   │   ├── local_storage.py

│   │   │   ├── __pycache__

│   │   │   │   ├── base_storage.cpython-313.pyc

│   │   │   │   ├── dropbox_storage.cpython-313.pyc

│   │   │   │   ├── __init__.cpython-313.pyc

│   │   │   │   ├── local_storage.cpython-313.pyc

│   │   │   │   └── usb_storage.cpython-313.pyc

│   │   │   └── usb_storage.py

│   │   └── storage_manager.py

│   ├── smart_heating.egg-info

│   │   ├── dependency_links.txt

│   │   ├── PKG-INFO

│   │   ├── requires.txt

│   │   ├── SOURCES.txt

│   │   └── top_level.txt

│   └── tests

│       ├── __init__.py

│       ├── __pycache__

│       │   ├── __init__.cpython-313.pyc

│       │   ├── test_base_storage.cpython-313-pytest-8.3.5.pyc

│       │   ├── test_dropbox_storage.cpython-313-pytest-8.3.5.pyc

│       │   ├── test_local_storage.cpython-313-pytest-8.3.5.pyc

│       │   ├── test_logger.cpython-313.pyc

│       │   ├── test_logger_flush.cpython-313.pyc

│       │   ├── test_storage_manager.cpython-313-pytest-8.3.5.pyc

│       │   ├── test_switch_heating.cpython-313.pyc

│       │   └── test_usb_storage.cpython-313-pytest-8.3.5.pyc

│       ├── test_base_storage.py

│       ├── test_dropbox_storage.py

│       ├── test_local_storage.py

│       ├── test_logger_flush.py

│       ├── test_logger.py

│       ├── test_storage_manager.py

│       ├── test_switch_heating.py

│       └── test_usb_storage.py

└── frontend

---

## 3️⃣ Besoin et justification du projet

- Permettre à l’utilisateur de **contrôler le chauffage** facilement  
- Avoir un **historique précis** de la température pour analyse  
- Sécuriser la maison avec un **arrêt automatique du chauffage et du Raspberry**  
- Fournir une base solide pour **une future application web avec React**  
- Utiliser uniquement des **logiciels libres** et matériels standards (Raspberry Pi, GPIO, sondes DS18B20)  

---

## 4️⃣ Scénario de fonctionnement

1. **Allumage du Raspberry Pi**  
   - Démarrage à distance via Wake on LAN intégré à la box  
   - Initialisation des GPIO et des modules  

2. **Pilotage du chauffage**  
   - Lecture continue de la sonde de température  
   - Interrupteur physique en mode **toggle**  
   - Chauffage actif si le mode manuel est activé et température < seuil  

3. **Journalisation automatique**  
   - Relevé toutes les X secondes dans un fichier CSV sur la clé USB  
   - Rotation automatique tous les jours à minuit  
   - Sauvegarde future possible sur Dropbox  

4. **Arrêt orchestré**  
   - Bouton ou interface web peut déclencher l’arrêt du programme  
   - Chauffage coupé selon l’état de l’interrupteur  
   - CSV sauvegardé sur la clé USB  
   - Raspberry s’éteint proprement  
   - Interface web affiche “Raspberry éteint”  

---

## 5️⃣ Environnement technique

### Python

- Version recommandée : **Python 3.13.x**  
- Installation sur Raspberry Pi OS :

```bash
sudo apt update
sudo apt install python3 python3-pip
```

- Installer les dépendances du projet :

```bash
pip3 install -r requirements.txt
```

### Clé USB de sauvegarde des températures (fichiers CSV)

- La clé USB doit être montée automatiquement au démarrage.
- Exemple pour la clé nommée SAUVEGARDE :

#### 1. Créer un point de montage :

```bash
sudo mkdir -p /media/maison/SAUVEGARDE
```

#### 2. Ajouter dans /etc/fstab (avec label ou UUID) :

```bash
LABEL=SAUVEGARDE  /media/maison/SAUVEGARDE  ext4  defaults,nofail  0  2
```

#### 3. Monter toutes les partitions :

```bash
sudo mount -a
```

#### 4. Vérifier que la clé est accessible :

```bash
ls /media/maison/SAUVEGARDE
```

### Raspberry Pi

#### GPIO utilisés :

- LED (chauffage) : GPIO 17
- Bouton poussoir : GPIO 27
- Sonde DS18B20 : GPIO 4 (1-Wire)
- Matériel testé : Raspberry Pi 3

#### OS : Raspberry Pi OS
