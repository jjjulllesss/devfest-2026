# Concierge DevFest Paris 2026 — atelier Arc

Dépôt de l’atelier de 90 minutes : construire un concierge dans **CX Agent Studio** avec **Arc**.

- **Guide participant (site publié)** : <https://jjjulllesss.github.io/devfest-2026/>
- Source du guide : [docs/guide-participant.md](docs/guide-participant.md)

Les fichiers à télécharger pendant l’atelier se trouvent dans le guide :
[FAQ à importer](docs/datastore/faq-devfest-2026.txt) et [brief à coller dans Arc](docs/brief-arc-concierge.txt).

Document pédagogique non officiel.

## Contenu

| Dossier | Contenu |
|---|---|
| `concierge-cxas/cxas_app/DevFest_Concierge_atelier_simple/` | L’application CX Agent Studio de référence (export SCRAPI) |
| `concierge-cxas/environments/` | Environnement de cette application (URL d’API et Data Store du projet de répétition) |
| `concierge-cxas/evals/simulations/` | Scénarios de simulation de l’application |
| `docs/` | Guide participant, présentation d’introduction (`presentation/`), captures (`images/`), brief Arc, contrat de l’API des sessions (`sessions.openapi.yaml`) et FAQ à importer dans le Data Store (`datastore/`) |
| `data/agenda.json` | Catalogue des sessions, utilisé par les tests locaux |
| `tests/` | Tests locaux des outils Python de l’application |
| `scripts/build_guides_html.py` | Génère le site HTML du guide (style Google Cloud) dans `build/`, dossier non versionné |
| `scripts/check_site.py` | Vérifie le site généré : liens, images, fichiers à télécharger |
| `.github/workflows/pages.yml` | Construit et publie le site sur GitHub Pages à chaque push sur `main` |
| `.agents/` | Compétences de l’assistant de développement (CXAS, SCRAPI) |

## Présentation d’introduction

`docs/presentation/introduction.html` est un diaporama HTML autonome de 8 diapositives sur la place de CX Agent Studio dans l’offre Google. Il est publié avec le guide : le bandeau en haut du guide renvoie vers `presentation/introduction.html` sur le site. Le détail de la structure (ajouter une diapositive, numéros « N / 8 », notes de l’intervenant) est en commentaire en tête du fichier.

## Tests locaux

Depuis la racine du dépôt :

```sh
python -m unittest discover -s tests -q
```

Les tests ne touchent aucun service cloud.

## Guide en HTML

```sh
pip install -r requirements-docs.txt
python scripts/build_guides_html.py
python scripts/check_site.py
```

Le dossier `build/` contient le site à héberger : `index.html` (CSS et JavaScript intégrés), la présentation d’introduction (`presentation/introduction.html`, liée en haut du guide), les captures (`images/`) et les fichiers à télécharger (`brief-arc-concierge.txt`, qui inclut le contrat de l’API, et `datastore/faq-devfest-2026.txt`). Seules les polices Roboto sont chargées en ligne ; hors connexion, une police système les remplace.

## Publication sur GitHub Pages

Le workflow `.github/workflows/pages.yml` publie `build/` avec GitHub Actions. Une seule fois, dans **Settings → Pages**, choisir **Source : GitHub Actions**. Chaque push sur `main` qui modifie `docs/` ou le script de génération redéploie le site ; le workflow peut aussi être lancé à la main (**Actions → Publier le guide sur GitHub Pages → Run workflow**).

## Licence

- **Code** (scripts, tests, configuration de l’application) : [Apache License 2.0](LICENSE).
- **Guide et documentation** (`docs/guide-participant.md`, captures `docs/images/`) : [Creative Commons Attribution 4.0](LICENSE-docs) (CC BY 4.0).
- **Données de l’événement** : la FAQ (`docs/datastore/faq-devfest-2026.txt`), le catalogue des sessions (`data/agenda.json`) et le brief (`docs/brief-arc-concierge.txt`) concernent le DevFest Paris 2026 et ne sont pas couverts par ces licences. Leurs droits appartiennent à leurs organisateurs ; ne les réutilisez qu’avec leur accord.

Document pédagogique non officiel, sans lien avec Google ni avec l’organisateur du DevFest Paris.
