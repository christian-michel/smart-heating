#!/bin/bash
#
# entrypoint.sh
#
# Le code applicatif (heating.py, thermostat.py) intercepte
# volontairement toute erreur d'initialisation GPIO et bascule en
# "simulation_mode" sans lever d'exception — pratique en développement
# sur une machine sans GPIO, dangereux en production : l'API continue
# de répondre normalement, /status affiche un état de chauffage
# cohérent, mais le relais ne bouge jamais réellement.
#
# Cet entrypoint fait le test AVANT de lancer uvicorn, avec le même
# utilisateur non-root que celui qui exécutera l'application (voir
# Dockerfile: USER appuser), pour vérifier que l'accès GPIO réel
# fonctionne réellement dans ces conditions — pas juste que le module
# s'importe.
#
# S'il échoue : le conteneur s'arrête en erreur (exit 1), Docker le
# redémarre (restart: unless-stopped) et le réessaie en boucle avec un
# message explicite dans `docker compose logs` — un échec bruyant et
# visible plutôt qu'un chauffage silencieusement inerte.

set -e

echo "[entrypoint] Vérification de l'accès GPIO réel (backend lgpio)..."

python3 - <<'PYEOF'
import sys

try:
    from gpiozero import Device, LED
    from gpiozero.pins.lgpio import LGPIOFactory

    Device.pin_factory = LGPIOFactory()

    # Ouvre réellement un pin (celui du relais chauffage) pour
    # provoquer l'éventuelle erreur de permission/device maintenant,
    # pas seulement au premier appel de l'API.
    from backend.config import LED_GPIO
    probe = LED(LED_GPIO)
    probe.close()

    print(f"[entrypoint] OK — pin factory lgpio active, GPIO{LED_GPIO} accessible.")

except Exception as e:
    print("[entrypoint] ERREUR CRITIQUE : accès GPIO réel impossible.", file=sys.stderr)
    print(f"[entrypoint] Détail : {e}", file=sys.stderr)
    print(
        "[entrypoint] Vérifie : device /dev/gpiochip0 monté (docker-compose.yml), "
        "GPIO_GID correct dans .env, et libgpiod-dev/liblgpio-dev présents dans l'image.",
        file=sys.stderr,
    )
    print(
        "[entrypoint] Refus de démarrer en mode simulation pour un système de "
        "chauffage : un crash visible vaut mieux qu'un chauffage qui ne chauffe "
        "jamais sans le signaler.",
        file=sys.stderr,
    )
    sys.exit(1)
PYEOF

echo "[entrypoint] Vérification OK, démarrage de l'application."
exec "$@"
