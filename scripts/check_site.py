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
PRESENTATION = "presentation/introduction.html"


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "build")
    index = site / "index.html"
    if not index.is_file():
        print(f"ERREUR : {index} est absent")
        return 1
    page = index.read_text(encoding="utf-8")
    errors = []

    if f'href="{PRESENTATION}"' not in page:
        errors.append(f"le guide ne contient pas de lien vers {PRESENTATION}")
    slides = site / PRESENTATION
    if not slides.is_file():
        errors.append(f"{PRESENTATION} est absent de {site}/")

    for html_file in (index, slides):
        if not html_file.is_file():
            continue
        text = html_file.read_text(encoding="utf-8")
        for attr, url in re.findall(r'\b(href|src)="([^"]+)"', text):
            if url.startswith(("#", "data:", "mailto:")) or urlparse(url).scheme:
                continue
            target = unquote(urlparse(url).path)
            if target in ("", "./"):
                continue
            if not (html_file.parent / target).is_file():
                errors.append(f"{html_file.relative_to(site)} : {attr}=\"{url}\" : fichier absent")

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
