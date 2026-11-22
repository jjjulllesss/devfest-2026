#!/usr/bin/env python3
"""Vérifie le site généré (build/) : liens relatifs, images et fichiers à télécharger.

Échoue si un lien ou une image locale pointe vers un fichier absent, ou si
l’un des fichiers que les participants doivent télécharger n’est pas proposé
en téléchargement dans la page d’accueil.

Usage : python scripts/check_site.py [build]
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

REQUIRED_DOWNLOADS = ["datastore/faq-devfest-2026.txt", "brief-arc-concierge.txt"]


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "build")
    index = site / "index.html"
    if not index.is_file():
        print(f"ERREUR : {index} est absent")
        return 1
    page = index.read_text(encoding="utf-8")
    errors = []

    for attr, url in re.findall(r'\b(href|src)="([^"]+)"', page):
        if url.startswith(("#", "data:", "mailto:")) or urlparse(url).scheme:
            continue
        target = unquote(urlparse(url).path)
        if target in ("", "./"):
            continue
        if not (site / target).is_file():
            errors.append(f"{attr}=\"{url}\" : fichier absent de {site}/")

    for rel in REQUIRED_DOWNLOADS:
        if f'href="{rel}" download' not in page:
            errors.append(f"{rel} n’est pas proposé en téléchargement dans le guide")
        elif (site / rel).stat().st_size == 0:
            errors.append(f"{rel} est vide")

    for err in errors:
        print("ERREUR :", err)
    if not errors:
        print("site OK :", index)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
