"""
audit_dependencies.py

Objectif :
Analyser automatiquement le projet Python pour détecter
les dépendances externes utilisées (packages à installer via pip).

Ce script :
1. Parcourt tous les fichiers Python du dossier backend
2. Extrait les imports (import / from ...)
3. Filtre :
   - les modules internes (backend.*)
   - les modules standards Python (os, sys, etc.)
4. Génère une liste des dépendances externes

Sortie :
- Affichage console
- Fichier : requirements_audit.txt

⚠️ Limites :
- Ne détecte pas les imports dynamiques
- Peut inclure des faux positifs (modules internes renommés)
- Ne donne pas les versions (juste les noms)

💡 Utilisation :
python audit_dependencies.py
"""

import os
import re
import sys


# ==========================
# CONFIGURATION
# ==========================

# Dossier du projet à analyser
PROJECT_DIR = "backend"


# ==========================
# MODULES STANDARD PYTHON
# ==========================

# Modules natifs Python (ex: sys, builtins, etc.)
STANDARD_LIBS = set(sys.builtin_module_names)

# On ajoute manuellement les plus courants
COMMON_STDLIB = {
    "os", "sys", "time", "datetime", "csv", "json",
    "re", "math", "threading", "subprocess",
    "pathlib", "logging", "shutil"
}

# Fusion des deux listes
STANDARD_LIBS = STANDARD_LIBS.union(COMMON_STDLIB)


# ==========================
# REGEX POUR EXTRACTION
# ==========================

# Capture les lignes du type :
# import module
# from module import ...
IMPORT_PATTERN = re.compile(r'^\s*(?:import|from)\s+([a-zA-Z0-9_\.]+)')


# ==========================
# EXTRACTION DES IMPORTS D'UN FICHIER
# ==========================

def extract_imports(file_path):
    """
    Lit un fichier Python et extrait les modules importés.

    Exemple :
        import os → "os"
        from time import sleep → "time"
    """

    imports = set()

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:

            # On cherche un import dans la ligne
            match = IMPORT_PATTERN.match(line)

            if match:
                # On récupère le module principal (avant le .)
                module = match.group(1).split('.')[0]
                imports.add(module)

    return imports


# ==========================
# SCAN COMPLET DU PROJET
# ==========================

def scan_project():
    """
    Parcourt tous les fichiers .py du projet
    et agrège tous les imports détectés.
    """

    all_imports = set()

    for root, _, files in os.walk(PROJECT_DIR):
        for file in files:

            if file.endswith(".py"):
                file_path = os.path.join(root, file)

                # Extraction des imports du fichier
                imports = extract_imports(file_path)

                # Ajout à la liste globale
                all_imports.update(imports)

    return all_imports


# ==========================
# FILTRAGE DES DÉPENDANCES EXTERNES
# ==========================

def filter_external(imports):
    """
    Supprime :
    - modules internes (backend)
    - modules standard Python

    Garde uniquement les dépendances externes (pip).
    """

    external = []

    for module in sorted(imports):

        # Ignore ton propre code
        if module.startswith("backend"):
            continue

        # Ignore la stdlib Python
        if module in STANDARD_LIBS:
            continue
