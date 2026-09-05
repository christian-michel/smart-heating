# syntax=docker/dockerfile:1
#
# Image du backend Smart Heating.
#
# Contient uniquement l'application Python (FastAPI + contrôleur +
# accès GPIO/1-Wire). Le matériel lui-même (GPIO, sonde, USB) est
# fourni au conteneur via docker-compose.yml (devices/volumes), pas
# dans cette image.

FROM python:3.13-slim

# Librairies système documentées par le projet
# (dependencies_apt.txt / install/setup_dependencies.sh) — gpiozero
# doit compiler ses extensions C contre les vraies libs lgpio/gpiod,
# sans quoi l'initialisation GPIO échoue et l'appli bascule en mode
# simulation SANS ERREUR VISIBLE (cf. heating.py / thermostat.py :
# try/except → simulation_mode = True).
#
# "liblgpio-dev" n'est PAS repris ici : ce paquet n'existe que dans le
# dépôt propre à Raspberry Pi (archive.raspberrypi.com), absent d'une
# image Docker générique (python:3.13-slim = Debian vanilla). C'est un
# manque documenté et récurrent sur Debian 13 "trixie" en général,
# Raspberry Pi OS y compris — on compile donc liblgpio depuis la
# source officielle juste après, comme le recommande le mainteneur
# amont (méthode "make && make install", identique à celle utilisée
# pour packager la lib sur Debian/Ubuntu/Raspberry Pi OS).
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        swig \
        libgpiod-dev \
        libexpat1-dev \
        zlib1g-dev \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/joan2937/lg.git /tmp/lg \
    && cd /tmp/lg \
    && make \
    && make install \
    && ldconfig \
    && rm -rf /tmp/lg

WORKDIR /app

# Étape séparée pour profiter du cache Docker : les dépendances ne sont
# réinstallées que si requirements.txt change, pas à chaque édition du
# code.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Utilisateur non-root, comme le mode bare-metal (utilisateur
# "smartheating" + groupe gpio dans install.sh). L'accès réel au
# device GPIO de l'hôte est donné à ce process via `group_add` dans
# docker-compose.yml (le GID du groupe "gpio" de l'hôte), pas en
# tournant en root dans le conteneur.
RUN useradd -m -u 1000 -s /usr/sbin/nologin appuser

# Deuxième filet de sécurité pour le point LG_WD ci-dessous : si jamais
# cette variable n'était pas respectée par le module Python "lgpio"
# local (contrairement aux outils rgpio distants, pour lesquels c'est
# documenté), /app doit rester utilisable comme repli.
RUN chown -R appuser:appuser /app

USER appuser

# LG_WD : lgpio crée ses fichiers de notification (.lgd-nfy<N>) dans
# le répertoire de travail courant du process (comportement documenté
# de la bibliothèque, cf. github.com/joan2937/lg/issues/12). WORKDIR
# (/app) appartient à root, illisible en écriture par l'utilisateur
# non-root ci-dessus : on redirige donc explicitement vers /tmp,
# systématiquement accessible en écriture.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    GPIOZERO_PIN_FACTORY=lgpio \
    LG_WD=/tmp

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "backend.api.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
