#!/bin/bash
#
# install_docker.sh
#
# Installe et lance Smart Heating dans un conteneur Docker, en
# remplacement du mode "bare-metal" (venv + systemd) posé par
# install.sh.
#
# Ce que ça apporte : l'application ne dépend plus des versions de
# paquets système du Raspberry Pi (un apt upgrade ne peut plus casser
# gpiozero/fastapi), et redémarre automatiquement après une coupure de
# courant, exactement comme le service systemd bare-metal — mais via
# la politique de redémarrage de Docker.
#
# Ce que ça NE fait PAS : activer le 1-Wire au niveau noyau. Vérifie
# que /boot/firmware/config.txt (ou /boot/config.txt) contient bien :
#   dtoverlay=w1-gpio
# et que le module est chargé (lsmod | grep w1_gpio) avant de lancer
# ce script — Docker ne peut pas agir à ce niveau.

set -e

echo "============================================="
echo "=== Smart Heating — Installation Docker  ===="
echo "============================================="

# ==========================
# === CHECK ROOT
# ==========================

if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté avec sudo"
    exit 1
fi

# ==========================
# === VARIABLES
# ==========================

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="/opt/smart-heating"
SERVICE_NAME="smart-heating"          # nom de l'ancien service bare-metal
ENV_FILE="$INSTALL_DIR/.env"
USB_MOUNT="/mnt/usb_backup"
DATA_DIR="$INSTALL_DIR/data"

echo "Source : $PROJECT_ROOT"
echo "Installation dans : $INSTALL_DIR"

# ==========================
# === STOP BARE-METAL SERVICE (évite conflit port 8000 / GPIO)
# ==========================

echo "Arrêt de l'éventuel service bare-metal existant..."

systemctl stop "$SERVICE_NAME" 2>/dev/null || true
systemctl disable "$SERVICE_NAME" 2>/dev/null || true

# ==========================
# === CHECK 1-WIRE (avertissement seulement, non bloquant)
# ==========================

if [ ! -d /sys/bus/w1/devices ] || [ -z "$(ls -A /sys/bus/w1/devices 2>/dev/null)" ]; then
    echo "⚠  /sys/bus/w1/devices est vide ou absent."
    echo "   Vérifie que 'dtoverlay=w1-gpio' est actif dans la config"
    echo "   noyau du Raspberry Pi (redémarrage requis après ajout)."
    echo "   Le conteneur démarrera quand même, mais la sonde ne"
    echo "   répondra pas tant que ce n'est pas corrigé côté hôte."
fi

# ==========================
# === INSTALL DOCKER (apt, pas de curl|bash)
# ==========================

install_compose_plugin() {
    # Deux noms de paquet coexistent selon le dépôt utilisé :
    #  - "docker-compose-plugin" : nom utilisé par le dépôt officiel
    #    Docker (download.docker.com), qu'on n'ajoute pas ici pour ne
    #    pas dépendre d'un dépôt tiers.
    #  - "docker-compose" : nom du MÊME plugin (Compose v2, pas
    #    l'ancien binaire Python v1) dans les dépôts Debian natifs —
    #    c'est celui que Debian 13 "trixie" fournit réellement.
    apt-get update
    if apt-get install -y --no-install-recommends docker-compose-plugin 2>/dev/null; then
        return 0
    fi
    echo "Paquet 'docker-compose-plugin' absent de ce dépôt (Debian natif, pas le"
    echo "dépôt officiel Docker) — tentative avec 'docker-compose' (même plugin,"
    echo "nom Debian)..."
    apt-get install -y --no-install-recommends docker-compose
}

# Le CLI docker (docker.io) ne détecte "docker compose" que si le
# binaire est présent dans un de ses dossiers de plugins connus
# (/usr/libexec/docker/cli-plugins en premier). Sur certaines versions
# du paquet Debian "docker-compose", le binaire n'est posé qu'à
# /usr/bin/docker-compose (utilisable en ligne de commande classique
# `docker-compose ...`) sans être relié à `docker compose` (avec un
# espace). On répare ça nous-mêmes plutôt que de dépendre du paquet.
is_valid_compose_binary() {
    local f="$1"
    [ -f "$f" ] && [ -x "$f" ] || return 1
    # Vérifie qu'il s'agit bien d'un binaire réel, pas d'un lien cassé
    # pointant vers un dossier (c'est précisément ce qui s'est produit
    # une fois déjà). Si `file` n'est pas installé, on se contente du
    # test -f/-x ci-dessus.
    if command -v file &>/dev/null; then
        file -L "$f" 2>/dev/null | grep -qi 'ELF'
    else
        return 0
    fi
}

heal_compose_plugin_link() {
    if ! command -v docker &>/dev/null; then
        echo "Le CLI 'docker' est absent — impossible de diagnostiquer le plugin"
        echo "compose avant que ça soit corrigé (voir installation de docker-cli"
        echo "ci-dessus)."
        return 1
    fi

    if docker compose version &>/dev/null; then
        return 0
    fi

    echo "'docker compose' introuvable — réinstallation du paquet docker-compose"
    echo "pour restaurer ses fichiers d'origine (un essai précédent a pu créer"
    echo "un lien incorrect à cet emplacement)..."
    apt-get install --reinstall -y docker-compose

    if docker compose version &>/dev/null; then
        return 0
    fi

    echo "Toujours indisponible après réinstallation — recherche manuelle d'un"
    echo "binaire valide parmi les emplacements connus..."

    local bin=""
    for candidate in \
        /usr/libexec/docker/cli-plugins/docker-compose \
        /usr/bin/docker-compose \
        /usr/lib/docker/cli-plugins/docker-compose \
        /usr/local/lib/docker/cli-plugins/docker-compose
    do
        if is_valid_compose_binary "$candidate"; then
            bin="$candidate"
            break
        fi
    done

    if [ -z "$bin" ]; then
        echo "❌ Aucun binaire docker-compose valide trouvé, même après réinstallation."
        echo "   Le paquet Debian semble incomplet/corrompu sur ce système."
        return 1
    fi

    echo "Binaire trouvé : $bin"
    echo "Création/réparation du lien dans /usr/libexec/docker/cli-plugins/ ..."
    mkdir -p /usr/libexec/docker/cli-plugins
    ln -sf "$bin" /usr/libexec/docker/cli-plugins/docker-compose
    chmod +x /usr/libexec/docker/cli-plugins/docker-compose

    docker compose version &>/dev/null
}

if ! command -v docker &>/dev/null; then
    echo "Installation de Docker (apt)..."
    apt-get update
    # docker-cli n'est qu'une "Recommends" de docker.io sur Debian
    # trixie, pas une dépendance stricte : avec
    # --no-install-recommends elle resterait absente et 'docker'
    # n'existerait pas, même si docker.io (le daemon) est bien
    # installé. On le demande explicitement.
    apt-get install -y --no-install-recommends docker.io docker-cli
    install_compose_plugin
else
    echo "Docker déjà installé ($(docker --version))"
    if ! docker compose version &>/dev/null; then
        echo "Installation du plugin docker compose..."
        install_compose_plugin
    fi
fi

# Le daemon doit tourner avant les vérifications qui suivent.
systemctl enable docker
systemctl start docker

if ! docker compose version &>/dev/null; then
    heal_compose_plugin_link || true
fi

if ! docker compose version &>/dev/null; then
    echo "❌ 'docker compose' reste indisponible après installation et tentative"
    echo "   de réparation. Diagnostique manuellement avec :"
    echo "     dpkg -L docker-compose"
    echo "     ls -la /usr/libexec/docker/cli-plugins/ /usr/lib/docker/cli-plugins/ 2>/dev/null"
    echo "     docker compose version"
    exit 1
fi

echo "✅ docker compose disponible : $(docker compose version --short 2>/dev/null || docker compose version)"

# ==========================
# === STRUCTURE / COPIE
# ==========================

echo "Copie du projet..."

mkdir -p "$INSTALL_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$USB_MOUNT"

# Le conteneur tourne en non-root (uid 1000, voir docker/Dockerfile),
# pas sous l'utilisateur bare-metal "smartheating" (uid différent).
# Sans ce chown, l'appli aurait accès en lecture seule à ces dossiers
# montés et échouerait à écrire ses CSV / sauvegardes — silencieusement,
# comme le piège GPIO décrit plus haut. Sur une clé USB déjà formatée
# en FAT/exFAT, le chown est un no-op (ces filesystems ne portent pas
# de propriétaire par fichier) : les droits dépendent alors des options
# de montage, pas de ce chown.
chown -R 1000:1000 "$DATA_DIR"
chown -R 1000:1000 "$USB_MOUNT" 2>/dev/null || true

if ! command -v rsync &>/dev/null; then
    apt-get update
    apt-get install -y --no-install-recommends rsync
fi

# On ne supprime pas $INSTALL_DIR/data ni .env s'ils existent déjà
# (contrairement à install.sh) : ce script peut être relancé après un
# passage en bare-metal sans perdre l'historique CSV ni le token.
rsync -a --exclude 'data' --exclude '.env' --exclude 'venv' \
    "$PROJECT_ROOT"/ "$INSTALL_DIR"/

echo "Configuration USB..."

# Nettoyage double montage
while mount | grep "$USB_MOUNT" > /dev/null; do
    umount "$USB_MOUNT" || break
done

# Détection USB fiable (identique à install.sh)
USB_DEVICE=""

if [ -e "/dev/sda1" ]; then
    USB_DEVICE="/dev/sda1"
else
    USB_DEVICE=$(lsblk -rpno NAME,TRAN | grep usb | awk '{print $1}' | head -n 1)
fi

if [ -n "$USB_DEVICE" ]; then
    echo "USB détectée : $USB_DEVICE"
    if mount "$USB_DEVICE" "$USB_MOUNT"; then
        echo "✅ Montage OK"
        chown -R 1000:1000 "$USB_MOUNT" 2>/dev/null || true
    else
        echo "❌ Échec montage"
    fi
else
    echo "⚠ Aucun USB détecté — le conteneur démarrera quand même, "
    echo "  services/storage retombera sur le stockage local/Dropbox."
fi

# ==========================
# === GROUPE GPIO DE L'HÔTE
# ==========================

echo "Détection du groupe gpio de l'hôte..."

GPIO_GID="$(getent group gpio | cut -d: -f3 || true)"

if [ -z "$GPIO_GID" ]; then
    echo "❌ Groupe 'gpio' introuvable sur cet hôte. Le conteneur ne"
    echo "   pourra pas piloter le relais/bouton. Vérifie ton image"
    echo "   Raspberry Pi OS."
    exit 1
fi

echo "GPIO_GID détecté : $GPIO_GID"

# ==========================
# === ENV FILE
# ==========================

echo "Configuration .env..."

if [ ! -f "$ENV_FILE" ]; then
cat > "$ENV_FILE" <<EOF
DROPBOX_APP_KEY=
DROPBOX_APP_SECRET=
DROPBOX_REFRESH_TOKEN=
API_TOKEN=changeme
# Origines autorisées à appeler l'API depuis un navigateur, séparées par
# des virgules. Laisser "*" pour un usage LAN uniquement ; restreindre si
# l'API est exposée sur Internet.
CORS_ALLOWED_ORIGINS=*
# Gid du groupe "gpio" de l'hôte, injecté automatiquement.
# Ne pas éditer à la main sauf si tu sais ce que tu fais.
GPIO_GID=$GPIO_GID
EOF
    echo "Fichier .env créé — pense à changer API_TOKEN avant tout accès distant."
else
    echo ".env existant conservé — mise à jour de GPIO_GID uniquement."
    if grep -q '^GPIO_GID=' "$ENV_FILE"; then
        sed -i "s/^GPIO_GID=.*/GPIO_GID=$GPIO_GID/" "$ENV_FILE"
    else
        echo "GPIO_GID=$GPIO_GID" >> "$ENV_FILE"
    fi
fi

chmod 600 "$ENV_FILE"

# ==========================
# === BUILD & RUN
# ==========================

echo "Construction de l'image Docker..."

cd "$INSTALL_DIR"
docker compose build

echo "Démarrage du conteneur..."

docker compose up -d

# ==========================
# === VALIDATION
# ==========================

sleep 3

if [ "$(docker inspect -f '{{.State.Running}}' smart-heating 2>/dev/null)" = "true" ]; then
    echo "✅ Conteneur actif (API disponible)"
else
    echo "❌ Le conteneur ne tourne pas — logs ci-dessous :"
    docker compose logs --tail=50
fi

# ==========================
# === FIN
# ==========================

echo ""
echo "============================================="
echo "✅ Installation Docker terminée"
echo "============================================="
echo ""
echo "🌐 Accès API : http://<IP_RASPBERRY>:8000/docs"
echo ""
echo "⚠ IMPORTANT :"
echo "- Modifier TOKEN : $ENV_FILE"
echo "- Le conteneur redémarre automatiquement avec Docker (au boot du"
echo "  Raspberry Pi, y compris après une coupure de courant), tant que"
echo "  'systemctl enable docker' reste actif."
echo ""
echo "Commandes utiles :"
echo " cd $INSTALL_DIR && docker compose ps"
echo " cd $INSTALL_DIR && docker compose logs -f"
echo " cd $INSTALL_DIR && docker compose restart"
echo " cd $INSTALL_DIR && docker compose down      # arrêt complet"
echo ""
echo "ℹ Au démarrage, le conteneur vérifie l'accès GPIO réel avant de"
echo "  lancer l'API (docker/entrypoint.sh). Si tu vois le conteneur"
echo "  redémarrer en boucle, regarde 'docker compose logs' : le"
echo "  message [entrypoint] indique précisément ce qui bloque (device,"
echo "  permissions, GPIO_GID) plutôt que de tourner en mode simulation."
