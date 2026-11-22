#!/usr/bin/env python3
"""Génère les schémas d'architecture du guide participant (docs/guide-participant.md).

Produit docs/images/architecture.svg (vue complète) et docs/images/architecture-tache-{2,3,4,5}.svg
(périmètre de chaque tâche : actif, déjà en place, à venir). Des aperçus PNG haute résolution
sont écrits dans .pytest_cache/architecture-previews/ (ignoré par git) pour contrôle visuel.

Les SVG sont modifiés à la main dans ce script : ne pas éditer docs/images/architecture*.svg directement.

Usage (depuis la racine du dépôt) :
    uv run --no-project --with resvg-py python3 scripts/build_architecture_diagrams.py

Après génération, reconstruire le site : python scripts/build_guides_html.py
"""
from pathlib import Path
import html
import resvg_py

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_IMAGES = REPO_ROOT / "docs" / "images"
PREVIEW_DIR = REPO_ROOT / ".pytest_cache" / "architecture-previews"

FONT_SANS = "Roboto, 'Helvetica Neue', Arial, sans-serif"
FONT_MONO = "'Roboto Mono', 'SF Mono', Menlo, monospace"

# Exact official Google Cloud logo SVG fetched from https://raw.githubusercontent.com/gilbarbara/logos/main/logos/google-cloud.svg
OFFICIAL_GOOGLE_CLOUD_SYMBOL = """
    <symbol id="icon-gcp-official" viewBox="0 0 256 206">
      <path d="M170.2517,56.8186 L192.5047,34.5656 L193.9877,25.1956 C153.4367,-11.6774 88.9757,-7.4964 52.4207,33.9196 C42.2667,45.4226 34.7337,59.7636 30.7167,74.5726 L38.6867,73.4496 L83.1917,66.1106 L86.6277,62.5966 C106.4247,40.8546 139.8977,37.9296 162.7557,56.4286 L170.2517,56.8186 Z" fill="#EA4335"/>
      <path d="M224.2048,73.9182 C219.0898,55.0822 208.5888,38.1492 193.9878,25.1962 L162.7558,56.4282 C175.9438,67.2042 183.4568,83.4382 183.1348,100.4652 L183.1348,106.0092 C198.4858,106.0092 210.9318,118.4542 210.9318,133.8052 C210.9318,149.1572 198.4858,161.2902 183.1348,161.2902 L127.4638,161.2902 L121.9978,167.2242 L121.9978,200.5642 L127.4638,205.7952 L183.1348,205.7952 C223.0648,206.1062 255.6868,174.3012 255.9978,134.3712 C256.1858,110.1682 244.2528,87.4782 224.2048,73.9182" fill="#4285F4"/>
      <path d="M71.8704,205.7957 L127.4634,205.7957 L127.4634,161.2897 L71.8704,161.2897 C67.9094,161.2887 64.0734,160.4377 60.4714,158.7917 L52.5844,161.2117 L30.1754,183.4647 L28.2234,191.0387 C40.7904,200.5277 56.1234,205.8637 71.8704,205.7957" fill="#34A853"/>
      <path d="M71.8704,61.4255 C31.9394,61.6635 -0.2366,94.2275 0.0014,134.1575 C0.1344,156.4555 10.5484,177.4455 28.2234,191.0385 L60.4714,158.7915 C46.4804,152.4705 40.2634,136.0055 46.5844,122.0155 C52.9044,108.0255 69.3704,101.8085 83.3594,108.1285 C89.5244,110.9135 94.4614,115.8515 97.2464,122.0155 L129.4944,89.7685 C115.7734,71.8315 94.4534,61.3445 71.8704,61.4255" fill="#FBBC05"/>
    </symbol>
"""

OFFICIAL_GEMINI_SYMBOL = """
    <symbol id="icon-gemini" viewBox="0 0 65 65">
      <path d="M32.4473 0C33.1278 0 33.7197 0.464783 33.8857 1.125C34.3947 3.14441 35.0586 5.11414 35.8848 7.03027C38.0369 12.0299 40.99 16.406 44.7393 20.1553C48.4903 23.9045 52.8647 26.8576 57.8643 29.0098C59.7821 29.8359 61.7502 30.4998 63.7695 31.0088C64.4297 31.1748 64.8944 31.7668 64.8945 32.4473C64.8945 33.1278 64.4298 33.7198 63.7695 33.8857C61.7502 34.3947 59.7803 35.0586 57.8643 35.8848C52.8646 38.037 48.4885 40.99 44.7393 44.7393C40.99 48.4904 38.037 52.8646 35.8848 57.8643C35.0586 59.7822 34.3947 61.7502 33.8857 63.7695C33.7198 64.4298 33.1278 64.8945 32.4473 64.8945C31.7668 64.8944 31.1748 64.4297 31.0088 63.7695C30.4998 61.7502 29.8359 59.7803 29.0098 57.8643C26.8576 52.8647 23.9063 48.4885 20.1553 44.7393C16.4041 40.99 12.0299 38.0369 7.03027 35.8848C5.1123 35.0586 3.14441 34.3947 1.125 33.8857C0.464783 33.7197 0 33.1278 0 32.4473C8.67651e-05 31.7668 0.464826 31.1748 1.125 31.0088C3.14442 30.4998 5.11413 29.836 7.03027 29.0098C12.03 26.8575 16.406 23.9046 20.1553 20.1553C23.9046 16.406 26.8575 12.03 29.0098 7.03027C29.836 5.11229 30.4998 3.14442 31.0088 1.125C31.1748 0.464826 31.7668 8.67651e-05 32.4473 0Z" fill="#4285F4"/>
    </symbol>
"""

COMMON_DEFS = f"""
  <defs>
    <style>
      .z-title {{ font-family: {FONT_SANS}; font-size: 13.5px; font-weight: 600; fill: #202124; }}
      .z-sub {{ font-family: {FONT_SANS}; font-size: 11px; font-weight: 500; fill: #5f6368; }}
      .c-title {{ font-family: {FONT_SANS}; font-size: 12.5px; font-weight: 600; fill: #202124; }}
      .c-prod {{ font-family: {FONT_SANS}; font-size: 11px; font-weight: 500; fill: #1a73e8; }}
      .c-body {{ font-family: {FONT_SANS}; font-size: 10.5px; font-weight: 400; fill: #5f6368; }}
      .c-code {{ font-family: {FONT_MONO}; font-size: 9.6px; font-weight: 500; fill: #3c4043; }}
      .badge-txt {{ font-family: {FONT_SANS}; font-size: 9.2px; font-weight: 700; letter-spacing: 0.04em; }}
      .leg-txt {{ font-family: {FONT_SANS}; font-size: 10.8px; font-weight: 400; fill: #3c4043; }}
      .ban-task {{ font-family: {FONT_SANS}; font-size: 11.5px; font-weight: 600; fill: #ffffff; }}
      .ban-title {{ font-family: {FONT_SANS}; font-size: 12px; font-weight: 500; fill: #174ea6; }}
      .state-done {{ opacity: 0.56; }}
      .state-todo {{ opacity: 0.22; }}
    </style>

    <marker id="arr-blue" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
      <path d="M 1 1.5 L 9 5 L 1 8.5 z" fill="#1a73e8"/>
    </marker>
    <marker id="arr-blue-muted" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 1 1.5 L 9 5 L 1 8.5 z" fill="#8ab4f8"/>
    </marker>
    <marker id="arr-grey" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 1 1.5 L 9 5 L 1 8.5 z" fill="#5f6368"/>
    </marker>
    <marker id="arr-grey-faint" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5.5" markerHeight="5.5" orient="auto-start-reverse">
      <path d="M 1 1.5 L 9 5 L 1 8.5 z" fill="#bdc1c6"/>
    </marker>

    {OFFICIAL_GOOGLE_CLOUD_SYMBOL}
    {OFFICIAL_GEMINI_SYMBOL}

    <symbol id="icon-cloud-run" viewBox="0 0 32 32">
      <path fill-rule="evenodd" fill="#aecbfa" d="M 11.87 3.51 L 16.03 16 L 28.51 16 Z"/>
      <path fill-rule="evenodd" fill="#4285f4" d="M 28.51 16 L 16.03 16 L 11.87 28.51 Z"/>
      <path fill-rule="evenodd" fill="#4285f4" d="M 4.59 28.51 L 8.76 26.41 L 11.87 16 L 7.71 16 Z"/>
      <path fill-rule="evenodd" fill="#aecbfa" d="M 4.59 3.51 L 7.71 16 L 11.87 16 L 8.76 5.59 Z"/>
    </symbol>

    <symbol id="icon-cloud-storage" viewBox="0 0 32 32">
      <path fill="#aecbfa" d="M 2.67 5.33 L 29.33 5.33 L 29.33 14.67 L 2.67 14.67 Z"/>
      <path fill="#669df6" d="M 26.67 5.33 L 29.33 5.33 L 29.33 14.67 L 26.67 14.67 Z"/>
      <path fill="#4285f4" d="M 29.33 5.33 L 26.67 5.33 L 26.67 14.67 Z"/>
      <path fill="#669df6" d="M 2.67 5.33 L 5.33 5.33 L 5.33 14.67 L 2.67 14.67 Z"/>
      <path fill="#ffffff" d="M 8 9.33 L 16 9.33 L 16 10.67 L 8 10.67 Z"/>
      <circle cx="22" cy="10" r="2" fill="#ffffff"/>
      <path fill="#aecbfa" d="M 2.67 17.33 L 29.33 17.33 L 29.33 26.67 L 2.67 26.67 Z"/>
      <path fill="#669df6" d="M 26.67 17.33 L 29.33 17.33 L 29.33 26.67 L 26.67 26.67 Z"/>
      <path fill="#4285f4" d="M 29.33 17.33 L 26.67 17.33 L 26.67 26.67 Z"/>
      <path fill="#669df6" d="M 2.67 17.33 L 5.33 17.33 L 5.33 26.67 L 2.67 26.67 Z"/>
      <path fill="#ffffff" d="M 8 21.33 L 16 21.33 L 16 22.67 L 8 22.67 Z"/>
      <circle cx="22" cy="22" r="2" fill="#ffffff"/>
    </symbol>

    <symbol id="icon-ces" viewBox="0 0 32 32">
      <path fill="#aecbfa" d="M 16.87 2.87 L 25.20 7.75 C 25.77 8.06 26.13 8.65 26.13 9.29 L 26.13 20.00 C 26.12 20.64 25.77 21.23 25.20 21.54 L 11.92 29.31 C 11.70 29.44 11.43 29.37 11.30 29.16 C 11.26 29.09 11.24 29.01 11.23 28.93 L 11.23 24.22 L 6.68 21.54 C 6.11 21.23 5.76 20.64 5.75 20.00 L 5.75 9.29 C 5.76 8.65 6.11 8.06 6.68 7.75 L 15.02 2.87 C 15.59 2.54 16.29 2.54 16.87 2.87 Z"/>
      <path fill="#669df6" d="M 10.92 12.64 C 10.65 12.64 10.42 12.86 10.41 13.13 L 10.41 18.45 C 10.43 18.77 10.61 19.06 10.89 19.23 L 13.47 20.70 L 13.47 22.79 C 13.49 23.05 13.71 23.27 13.98 23.27 C 14.06 23.27 14.14 23.24 14.21 23.21 L 21.09 19.23 C 21.36 19.05 21.52 18.75 21.53 18.43 L 21.53 13.15 C 21.53 12.82 21.18 12.60 20.78 12.70 L 16.20 15.33 C 16.05 15.41 15.87 15.40 15.72 15.32 L 11.18 12.71 Z"/>
      <path fill="#185abc" d="M 16.33 6.75 C 16.14 6.64 15.91 6.64 15.71 6.74 L 10.71 9.57 C 10.42 9.76 10.42 10.26 10.70 10.45 L 15.69 13.32 C 15.88 13.43 16.12 13.43 16.33 13.32 L 21.24 10.45 C 21.54 10.26 21.54 9.76 21.24 9.57 Z"/>
    </symbol>

    <symbol id="icon-datastore" viewBox="0 0 32 32">
      <rect x="4" y="5" width="18" height="6" rx="1.5" fill="#aecbfa"/>
      <rect x="4" y="13" width="18" height="6" rx="1.5" fill="#669df6"/>
      <rect x="4" y="21" width="13" height="6" rx="1.5" fill="#4285f4"/>
      <circle cx="7.5" cy="8" r="1.1" fill="#ffffff"/>
      <circle cx="7.5" cy="16" r="1.1" fill="#ffffff"/>
      <circle cx="7.5" cy="24" r="1.1" fill="#ffffff"/>
      <circle cx="22.5" cy="21.5" r="4.5" fill="#ffffff" stroke="#1a73e8" stroke-width="2.2"/>
      <line x1="25.8" y1="24.8" x2="29.2" y2="28.2" stroke="#1a73e8" stroke-width="2.4" stroke-linecap="round"/>
    </symbol>

    <symbol id="icon-user" viewBox="0 0 32 32">
      <circle cx="16" cy="16" r="14.5" fill="#f1f3f4" stroke="#dadce0" stroke-width="1"/>
      <circle cx="16" cy="12.2" r="4.3" fill="#5f6368"/>
      <path d="M 8.5 24.5 C 8.5 20.3 11.8 18.2 16 18.2 C 20.2 18.2 23.5 20.3 23.5 24.5" fill="#5f6368"/>
    </symbol>

    <symbol id="icon-doc" viewBox="0 0 28 28">
      <path d="M7 3h10l5 5v16a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 6 24V4.5A1.5 1.5 0 0 1 7.5 3z" fill="#f1f3f4" stroke="#5f6368" stroke-width="1.4"/>
      <path d="M17 3v5h5" fill="none" stroke="#5f6368" stroke-width="1.4"/>
      <line x1="9.5" y1="13" x2="18.5" y2="13" stroke="#5f6368" stroke-width="1.4"/>
      <line x1="9.5" y1="17" x2="18.5" y2="17" stroke="#5f6368" stroke-width="1.4"/>
      <line x1="9.5" y1="21" x2="15" y2="21" stroke="#5f6368" stroke-width="1.4"/>
    </symbol>

    <symbol id="icon-globe" viewBox="0 0 28 28">
      <circle cx="14" cy="14" r="10.5" fill="#ffffff" stroke="#1a73e8" stroke-width="1.6"/>
      <ellipse cx="14" cy="14" rx="5" ry="10.5" fill="none" stroke="#1a73e8" stroke-width="1.3"/>
      <line x1="3.5" y1="14" x2="24.5" y2="14" stroke="#1a73e8" stroke-width="1.3"/>
      <line x1="5.2" y1="9.2" x2="22.8" y2="9.2" stroke="#aecbfa" stroke-width="1.1"/>
      <line x1="5.2" y1="18.8" x2="22.8" y2="18.8" stroke="#aecbfa" stroke-width="1.1"/>
    </symbol>

    <symbol id="icon-state" viewBox="0 0 28 28">
      <rect x="3" y="4" width="22" height="20" rx="4" fill="#e8f0fe" stroke="#669df6" stroke-width="1.3"/>
      <text x="14" y="18" text-anchor="middle" font-family="{FONT_MONO}" font-size="11.5" font-weight="700" fill="#174ea6">{{ }}</text>
    </symbol>

    <symbol id="icon-check" viewBox="0 0 18 18">
      <circle cx="9" cy="9" r="8" fill="#e6f4ea" stroke="#ceead6" stroke-width="1"/>
      <path d="M 5.3 9.2 L 7.8 11.7 L 12.8 6.5" fill="none" stroke="#188038" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    </symbol>
  </defs>
"""


def chip(x: float, y: float, text: str, bg: str = "#f1f3f4", fg: str = "#3c4043", border: str = "#dadce0", mono: bool = True, w: float | None = None, state: str = "normal", highlight: bool = False) -> str:
    char_w = 5.9 if mono else 5.8
    width = w if w is not None else round(len(text) * char_w + 14, 1)
    fam = FONT_MONO if mono else FONT_SANS
    weight = "600" if highlight else ("500" if mono else "600")
    cls = f' class="state-{state}"' if state in ("done", "todo") else ""
    if highlight:
        bg, fg, border = "#e8f0fe", "#174ea6", "#1a73e8"
    sw = "1.5" if highlight else "0.9"
    return (
        f'<g transform="translate({x},{y})"{cls}>'
        f'<rect width="{width}" height="19" rx="4" fill="{bg}" stroke="{border}" stroke-width="{sw}"/>'
        f'<text x="{width/2:.1f}" y="13.2" text-anchor="middle" font-family="{fam}" font-size="9.6px" font-weight="{weight}" fill="{fg}">{html.escape(text)}</text>'
        f'</g>'
    )


def pill_label(cx: float, cy: float, text: str, fg: str = "#174ea6", bg: str = "#ffffff", border: str = "#d2e3fc", w: float | None = None, state: str = "normal") -> str:
    width = w if w is not None else round(len(text) * 5.7 + 14, 1)
    x = cx - width / 2
    y = cy - 9.5
    cls = f' class="state-{state}"' if state in ("done", "todo") else ""
    return (
        f'<g{cls}>'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="19" rx="9.5" fill="{bg}" stroke="{border}" stroke-width="1"/>'
        f'<text x="{cx:.1f}" y="{cy + 3.5:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="9.8px" font-weight="500" fill="{fg}">{html.escape(text)}</text>'
        f'</g>'
    )


def pill_2lines(cx: float, cy: float, line1: str, line2: str, fg: str = "#174ea6", bg: str = "#ffffff", border: str = "#1a73e8", w: float = 86, state: str = "normal") -> str:
    x = cx - w / 2
    y = cy - 15
    cls = f' class="state-{state}"' if state in ("done", "todo") else ""
    return (
        f'<g{cls}>'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="30" rx="8" fill="{bg}" stroke="{border}" stroke-width="1"/>'
        f'<text x="{cx:.1f}" y="{cy - 2.5:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="9.6px" font-weight="600" fill="{fg}">{html.escape(line1)}</text>'
        f'<text x="{cx:.1f}" y="{cy + 9.5:.1f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="9.1px" font-weight="400" fill="#5f6368">{html.escape(line2)}</text>'
        f'</g>'
    )


def focus_halo(w: float, h: float, rx: float = 5, color: str = "#d2e3fc") -> str:
    return f'<rect x="-3" y="-3" width="{w+6}" height="{h+6}" rx="{rx+2}" fill="none" stroke="{color}" stroke-width="4"/>'


def build_diagram(mode: str = "full") -> str:
    """
    mode in {"full", "tache2", "tache3", "tache4", "tache5"}
    Uses a crisp 1040px wide canvas so text renders large and readable inside the 860px HTML column.
    """
    is_task = mode != "full"
    y_off = 44 if is_task else 0
    W = 1040
    H = (512 + y_off) if is_task else 548

    # Component states: "active" | "done" | "todo" | "normal"
    if mode == "full":
        st = {k: "normal" for k in [
            "user", "faq_file", "ces_box", "concierge", "faq_chip", "programme",
            "openapi_chips", "py_prog_chip", "state_box", "state_prog", "state_tkt",
            "assistance", "gcs", "datastore", "cloud_run",
            "e_user", "e_prog", "e_assist", "e_state_prog", "e_state_tkt", "e_faq", "e_import", "e_index", "e_api"
        ]}
    elif mode == "tache2":
        st = {
            "user": "active",
            "faq_file": "active",
            "ces_box": "active",
            "concierge": "active",
            "faq_chip": "todo",
            "programme": "active",
            "openapi_chips": "active",
            "py_prog_chip": "todo",
            "state_box": "todo",
            "state_prog": "todo",
            "state_tkt": "todo",
            "assistance": "todo",
            "gcs": "active",
            "datastore": "active",
            "cloud_run": "active",
            "e_user": "active",
            "e_prog": "active",
            "e_assist": "todo",
            "e_state_prog": "todo",
            "e_state_tkt": "todo",
            "e_faq": "todo",
            "e_import": "active",
            "e_index": "active",
            "e_api": "active",
        }
    elif mode == "tache3":
        st = {
            "user": "done",
            "faq_file": "done",
            "ces_box": "normal",
            "concierge": "done",
            "faq_chip": "todo",
            "programme": "active",
            "openapi_chips": "done",
            "py_prog_chip": "active",
            "state_box": "active",
            "state_prog": "active",
            "state_tkt": "todo",
            "assistance": "todo",
            "gcs": "done",
            "datastore": "done",
            "cloud_run": "done",
            "e_user": "done",
            "e_prog": "done",
            "e_assist": "todo",
            "e_state_prog": "active",
            "e_state_tkt": "todo",
            "e_faq": "todo",
            "e_import": "done",
            "e_index": "done",
            "e_api": "active",  # get_session called before add!
        }
    elif mode == "tache4":
        st = {
            "user": "done",
            "faq_file": "done",
            "ces_box": "normal",
            "concierge": "active",
            "faq_chip": "active",
            "programme": "done",
            "openapi_chips": "normal",
            "py_prog_chip": "normal",
            "state_box": "active",
            "state_prog": "done",
            "state_tkt": "active",
            "assistance": "active",
            "gcs": "done",
            "datastore": "active",
            "cloud_run": "done",
            "e_user": "done",
            "e_prog": "done",
            "e_assist": "active",
            "e_state_prog": "done",
            "e_state_tkt": "active",
            "e_faq": "active",
            "e_import": "done",
            "e_index": "done",
            "e_api": "done",
        }
    elif mode == "tache5":
        st = {
            "user": "active",
            "faq_file": "done",
            "ces_box": "active",
            "concierge": "done",
            "faq_chip": "normal",
            "programme": "done",
            "openapi_chips": "normal",
            "py_prog_chip": "normal",
            "state_box": "done",
            "state_prog": "normal",
            "state_tkt": "normal",
            "assistance": "done",
            "gcs": "done",
            "datastore": "done",
            "cloud_run": "done",
            "e_user": "active",
            "e_prog": "active",
            "e_assist": "active",
            "e_state_prog": "active",
            "e_state_tkt": "active",
            "e_faq": "active",
            "e_import": "done",
            "e_index": "done",
            "e_api": "active",
        }

    def g_cls(key: str) -> str:
        s = st[key]
        return f' class="state-{s}"' if s in ("done", "todo") else ""

    def card_stroke(key: str, default_color: str = "#dadce0", active_color: str = "#1a73e8") -> tuple[str, str, str]:
        s = st[key]
        if s == "active":
            halo_c = "#fde293" if active_color == "#f29900" else "#d2e3fc"
            return active_color, "1.9", halo_c
        if s == "todo":
            return "#bdc1c6", "1.2", ""
        return default_color, "1.3", ""

    def done_mark(key: str, x: float, y: float = 8) -> str:
        return f'<use href="#icon-check" x="{x}" y="{y}" width="16" height="16"/>' if st[key] == "done" else ""

    def blue_edge_attrs(key: str, width: float = 2.0) -> str:
        s = st[key]
        if s in ("normal", "active"):
            w = width + (0.3 if s == "active" else 0)
            return f'stroke="#1a73e8" stroke-width="{w:.1f}"'
        if s == "done":
            return 'stroke="#8ab4f8" stroke-width="1.6"'
        return 'stroke="#dadce0" stroke-width="1.3" stroke-dasharray="4,4"'

    def blue_marker(key: str) -> str:
        s = st[key]
        if s in ("normal", "active"):
            return "url(#arr-blue)"
        if s == "done":
            return "url(#arr-blue-muted)"
        return "url(#arr-grey-faint)"

    def grey_edge_attrs(key: str) -> str:
        s = st[key]
        if s == "active":
            return 'stroke="#1a73e8" stroke-width="2.0" stroke-dasharray="5,4"'
        if s == "normal":
            return 'stroke="#5f6368" stroke-width="1.7" stroke-dasharray="5,4"'
        if s == "done":
            return 'stroke="#9aa0a6" stroke-width="1.4" stroke-dasharray="4,4"'
        return 'stroke="#dadce0" stroke-width="1.2" stroke-dasharray="3,4"'

    def grey_marker(key: str) -> str:
        s = st[key]
        if s == "active":
            return "url(#arr-blue)"
        if s == "normal":
            return "url(#arr-grey)"
        return "url(#arr-grey-faint)"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        COMMON_DEFS,
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
    ]

    # Task Spotlight top bar
    if is_task:
        task_banners = {
            "tache2": ("Tâche 2", "Application Concierge, import FAQ et recherche via l’API publique"),
            "tache3": ("Tâche 3", "Outil Python update_personal_program et état personal_program"),
            "tache4": ("Tâche 4", "Branchement du Data Store FAQ et ajout du sous-agent Assistance"),
            "tache5": ("Tâche 5", "Simulation des 5 scénarios dans Evaluate et lecture des traces"),
        }
        t_badge, t_desc = task_banners[mode]
        parts.extend([
            '<rect x="18" y="12" width="1004" height="34" rx="6" fill="#f8f9fa" stroke="#dadce0" stroke-width="1"/>',
            '<rect x="26" y="18" width="68" height="22" rx="11" fill="#1a73e8"/>',
            f'<text x="60" y="33" text-anchor="middle" class="ban-task">{html.escape(t_badge)}</text>',
            f'<text x="104" y="33.5" class="ban-title">{html.escape(t_desc)}</text>',
            # Mini status key on the right
            '<rect x="698" y="22" width="13" height="13" rx="3" fill="#ffffff" stroke="#1a73e8" stroke-width="1.8"/>',
            '<text x="716" y="32.5" class="c-body" style="font-weight:600;fill:#174ea6">Créé / actif ici</text>',
            '<use href="#icon-check" x="806" y="20.5" width="16" height="16"/>',
            '<text x="826" y="32.5" class="c-body">Déjà en place</text>',
            '<rect x="912" y="22" width="13" height="13" rx="3" fill="#ffffff" stroke="#bdc1c6" stroke-width="1.2" stroke-dasharray="3,2"/>',
            '<text x="930" y="32.5" class="c-body">À venir</text>',
        ])

    # Main content group shifted by y_off
    parts.append(f'<g transform="translate(0,{y_off})">')

    # ---------------- COL 1: PARTICIPANT & FICHIER FAQ (x=18..150) ----------------
    u_stroke, u_sw, u_halo = card_stroke("user")
    user_sub1 = "Onglet Evaluate (5 tests)" if mode == "tache5" else "Aperçu & Evaluate"
    user_sub2 = "Simulation & traces" if mode == "tache5" else "Console CX Agent Studio"
    parts.extend([
        f'<g transform="translate(18,142)"{g_cls("user")}>',
        f'  {focus_halo(132, 114, 6, u_halo) if u_halo else ""}',
        f'  <rect width="132" height="114" rx="6" fill="#ffffff" stroke="{u_stroke}" stroke-width="{u_sw}"/>',
        f'  {done_mark("user", 108, 8)}',
        '  <use href="#icon-user" x="46" y="14" width="40" height="40"/>',
        '  <text x="66" y="72" text-anchor="middle" class="c-title">Participant</text>',
        f'  <text x="66" y="89" text-anchor="middle" class="c-prod">{html.escape(user_sub1)}</text>',
        f'  <text x="66" y="104" text-anchor="middle" class="c-body">{html.escape(user_sub2)}</text>',
        '</g>',
    ])

    f_stroke, f_sw, f_halo = card_stroke("faq_file")
    parts.extend([
        f'<g transform="translate(18,402)"{g_cls("faq_file")}>',
        f'  {focus_halo(132, 72, 6, f_halo) if f_halo else ""}',
        f'  <rect width="132" height="72" rx="6" fill="#ffffff" stroke="{f_stroke}" stroke-width="{f_sw}" stroke-dasharray="4,3"/>',
        f'  {done_mark("faq_file", 108, 8)}',
        '  <use href="#icon-doc" x="10" y="12" width="22" height="22"/>',
        '  <text x="36" y="27" class="c-title">Fichier FAQ</text>',
        f'  {chip(8, 42, "faq-devfest-2026.txt", w=116)}',
        '</g>',
    ])

    # ---------------- COL 2: PARTICIPANT GCP PROJECT ZONE (x=176..738, w=562) ----------------
    parts.extend([
        '<rect x="176" y="18" width="562" height="486" rx="6" fill="#f6f8fc" stroke="#4285f4" stroke-width="1.8"/>',
        '<use href="#icon-gcp-official" x="192" y="29" width="25" height="20"/>',
        '<text x="224" y="44" class="z-title">Projet Google Cloud du participant</text>',
        chip(514, 30, "Localisation : eu (région & multi-région)", bg="#e8f0fe", fg="#174ea6", border="#aecbfa", mono=False, w=210),
    ])

    # Sub-zone 2A: CX Agent Studio (x=192, y=60, w=530, h=304)
    ces_border = "#1a73e8" if st["ces_box"] == "active" else "#aecbfa"
    ces_sw = "1.7" if st["ces_box"] == "active" else "1.3"
    parts.extend([
        f'<rect x="192" y="60" width="530" height="304" rx="6" fill="#ffffff" stroke="{ces_border}" stroke-width="{ces_sw}"/>',
        '<rect x="192" y="60" width="530" height="34" rx="6" fill="#e8f0fe"/>',
        '<rect x="192" y="86" width="530" height="8" fill="#e8f0fe"/>',
        '<line x1="192" y1="94" x2="722" y2="94" stroke="#aecbfa" stroke-width="1"/>',
        '<use href="#icon-ces" x="202" y="64" width="26" height="26"/>',
        '<text x="233" y="81" class="z-title">CX Agent Studio</text>',
        '<text x="344" y="81" class="z-sub">concierge-devfest-&lt;prénom&gt;</text>',
        '<use href="#icon-gemini" x="556" y="69" width="15" height="15"/>',
        chip(575, 67, "gemini-3.5-flash", bg="#ffffff", fg="#174ea6", border="#aecbfa", mono=True, w=136),
    ])

    # Root Agent: Concierge (x=204, y=130, w=166, h=148) -> ends at x=370
    c_stroke, c_sw, c_halo = card_stroke("concierge", default_color="#1a73e8", active_color="#1a73e8")
    if st["concierge"] == "done":
        c_stroke, c_sw = "#8ab4f8", "1.4"
    parts.extend([
        f'<g transform="translate(204,130)"{g_cls("concierge")}>',
        f'  {focus_halo(166, 148, 5, c_halo) if c_halo else ""}',
        f'  <rect width="166" height="148" rx="5" fill="#ffffff" stroke="{c_stroke}" stroke-width="{c_sw}"/>',
        f'  {done_mark("concierge", 142, 9)}',
        '  <rect x="10" y="10" width="86" height="17" rx="3" fill="#e8f0fe"/>',
        '  <text x="53" y="22" text-anchor="middle" class="badge-txt" fill="#174ea6">AGENT RACINE</text>',
        '  <text x="10" y="44" class="c-title">Concierge</text>',
        '  <text x="10" y="62" class="c-body">Accueille, répond aux infos</text>',
        '  <text x="10" y="77" class="c-body">pratiques, route en silence</text>',
        '  <line x1="10" y1="89" x2="156" y2="89" stroke="#f1f3f4" stroke-width="1"/>',
        '  <text x="10" y="105" class="c-body" style="font-weight:600;fill:#3c4043">Outils :</text>',
        f'  {chip(10, 114, "faq", bg="#e8f0fe", fg="#174ea6", border="#aecbfa", w=44, state=st["faq_chip"], highlight=(st["faq_chip"]=="active"))}',
        f'  {chip(60, 114, "end_session", w=94)}',
        '</g>',
    ])

    # Sub-agent 1: Programme (x=434, y=104, w=276, h=96) -> 64px corridor x=370..434
    p_stroke, p_sw, p_halo = card_stroke("programme")
    parts.extend([
        f'<g transform="translate(434,104)"{g_cls("programme")}>',
        f'  {focus_halo(276, 96, 5, p_halo) if p_halo else ""}',
        f'  <rect width="276" height="96" rx="5" fill="#ffffff" stroke="{p_stroke}" stroke-width="{p_sw}"/>',
        f'  {done_mark("programme", 252, 9)}',
        '  <rect x="10" y="10" width="76" height="16" rx="3" fill="#f1f3f4"/>',
        '  <text x="48" y="21.5" text-anchor="middle" class="badge-txt" fill="#5f6368">SOUS-AGENT</text>',
        '  <text x="94" y="22.5" class="c-title">Programme</text>',
        '  <text x="10" y="40" class="c-body">Sessions &amp; agenda sans chevauchement</text>',
        f'  {chip(10, 49, "search_sessions", bg="#e8f0fe", fg="#174ea6", border="#aecbfa", w=106, state=st["openapi_chips"], highlight=(st["openapi_chips"]=="active"))}',
        f'  {chip(122, 49, "get_session", bg="#e8f0fe", fg="#174ea6", border="#aecbfa", w=84, state=st["openapi_chips"], highlight=(st["openapi_chips"]=="active"))}',
        f'  <text x="212" y="62" class="c-body{" state-" + st["openapi_chips"] if st["openapi_chips"] in ("done","todo") else ""}">(OpenAPI)</text>',
        f'  {chip(10, 72, "update_personal_program", w=158, state=st["py_prog_chip"], highlight=(st["py_prog_chip"]=="active"))}',
        f'  <text x="174" y="85" class="c-body{" state-" + st["py_prog_chip"] if st["py_prog_chip"] in ("done","todo") else ""}">(outil Python)</text>',
        '</g>',
    ])

    # Session State (x=434, y=218, w=276, h=46)
    s_stroke, s_sw, s_halo = card_stroke("state_box", default_color="#aecbfa")
    parts.extend([
        f'<g transform="translate(434,218)"{g_cls("state_box")}>',
        f'  {focus_halo(276, 46, 5, s_halo) if s_halo else ""}',
        f'  <rect width="276" height="46" rx="5" fill="#f8f9fa" stroke="{s_stroke}" stroke-width="{s_sw}" stroke-dasharray="4,3"/>',
        f'  {done_mark("state_box", 252, 6)}',
        '  <use href="#icon-state" x="8" y="9" width="26" height="26"/>',
        '  <text x="40" y="18" class="c-body" style="font-weight:600;fill:#202124">État de la session (JSON)</text>',
        f'  {chip(40, 23, "personal_program", bg="#ffffff", w=112, state=st["state_prog"], highlight=(st["state_prog"]=="active"))}',
        f'  {chip(158, 23, "support_tickets", bg="#ffffff", w=108, state=st["state_tkt"], highlight=(st["state_tkt"]=="active"))}',
        '</g>',
    ])

    # Sub-agent 2: Assistance (x=434, y=282, w=276, h=70)
    a_stroke, a_sw, a_halo = card_stroke("assistance")
    parts.extend([
        f'<g transform="translate(434,282)"{g_cls("assistance")}>',
        f'  {focus_halo(276, 70, 5, a_halo) if a_halo else ""}',
        f'  <rect width="276" height="70" rx="5" fill="#ffffff" stroke="{a_stroke}" stroke-width="{a_sw}"/>',
        f'  {done_mark("assistance", 252, 9)}',
        '  <rect x="10" y="10" width="76" height="16" rx="3" fill="#f1f3f4"/>',
        '  <text x="48" y="21.5" text-anchor="middle" class="badge-txt" fill="#5f6368">SOUS-AGENT</text>',
        '  <text x="94" y="22.5" class="c-title">Assistance</text>',
        '  <text x="10" y="40" class="c-body">Ticket immédiat sans doublon (réf. TKT-…)</text>',
        f'  {chip(10, 46, "create_support_ticket", w=148, highlight=(st["assistance"]=="active"))}',
        '  <text x="165" y="59" class="c-body">(outil Python)</text>',
        '</g>',
    ])

    # Sub-zone 2B: FAQ Pipeline (x=192, y=378, w=530, h=112)
    parts.extend([
        '<rect x="192" y="378" width="530" height="112" rx="6" fill="#ffffff" stroke="#dadce0" stroke-width="1.3"/>',
        '<text x="206" y="397" class="z-sub" style="font-weight:600;fill:#3c4043">Source documentaire de l’événement (multi-région eu)</text>',
    ])

    g_stroke, g_sw, g_halo = card_stroke("gcs")
    parts.extend([
        f'<g transform="translate(204,406)"{g_cls("gcs")}>',
        f'  {focus_halo(212, 70, 5, g_halo) if g_halo else ""}',
        f'  <rect width="212" height="70" rx="5" fill="#ffffff" stroke="{g_stroke}" stroke-width="{g_sw}"/>',
        f'  {done_mark("gcs", 188, 8)}',
        '  <use href="#icon-cloud-storage" x="10" y="16" width="32" height="32"/>',
        '  <text x="50" y="25" class="c-title">Bucket FAQ</text>',
        '  <text x="50" y="41" class="c-prod">Cloud Storage</text>',
        '  <text x="50" y="56" class="c-code">devfest-faq-&lt;prénom&gt;</text>',
        '</g>',
    ])

    d_stroke, d_sw, d_halo = card_stroke("datastore")
    parts.extend([
        f'<g transform="translate(474,406)"{g_cls("datastore")}>',
        f'  {focus_halo(236, 70, 5, d_halo) if d_halo else ""}',
        f'  <rect width="236" height="70" rx="5" fill="#ffffff" stroke="{d_stroke}" stroke-width="{d_sw}"/>',
        f'  {done_mark("datastore", 212, 8)}',
        '  <use href="#icon-datastore" x="10" y="16" width="32" height="32"/>',
        '  <text x="50" y="25" class="c-title">Data Store FAQ</text>',
        '  <text x="50" y="41" class="c-prod">AI Applications</text>',
        '  <text x="50" y="56" class="c-body">Indexe faq-devfest-2026.txt</text>',
        '</g>',
    ])

    # ---------------- COL 3: INTERNET CORRIDOR (x=738..832, w=94) ----------------
    parts.extend([
        '<line x1="785" y1="24" x2="785" y2="498" stroke="#9aa0a6" stroke-width="1.5" stroke-dasharray="6,5"/>',
        '<rect x="749" y="214" width="72" height="58" rx="6" fill="#ffffff" stroke="#dadce0" stroke-width="1"/>',
        '<use href="#icon-globe" x="771" y="218" width="28" height="28"/>',
        '<text x="785" y="260" text-anchor="middle" class="z-sub" style="font-weight:600;fill:#1a73e8">Internet</text>',
    ])

    # ---------------- COL 4: EXTERNAL PUBLIC GCP PROJECT ZONE (x=832..1022, w=190) ----------------
    cr_stroke, cr_sw, cr_halo = card_stroke("cloud_run", default_color="#f29900", active_color="#f29900")
    ext_cls = g_cls("cloud_run")
    parts.extend([
        f'<g{ext_cls}>',
        '  <rect x="832" y="60" width="190" height="278" rx="6" fill="#fff8e1" stroke="#f29900" stroke-width="1.8"/>',
        '  <rect x="842" y="72" width="170" height="22" rx="4" fill="#fef0c3" stroke="#f9ab00" stroke-width="1"/>',
        '  <text x="927" y="87" text-anchor="middle" class="badge-txt" fill="#b06000">HORS PROJET PARTICIPANT</text>',
        '  <use href="#icon-gcp-official" x="845" y="104" width="21" height="17"/>',
        '  <text x="871" y="117" class="z-title" style="font-size:12.5px">Projet GCP externe</text>',
        '  <text x="927" y="133" text-anchor="middle" class="z-sub">Exposé publiquement</text>',
        f'  <g transform="translate(842,146)">',
        f'    {focus_halo(170, 178, 5, cr_halo) if cr_halo else ""}',
        f'    <rect width="170" height="178" rx="5" fill="#ffffff" stroke="{cr_stroke}" stroke-width="{cr_sw}"/>',
        f'    {done_mark("cloud_run", 146, 8)}',
        '    <use href="#icon-cloud-run" x="10" y="14" width="34" height="34"/>',
        '    <text x="50" y="26" class="c-title">API Sessions</text>',
        '    <text x="50" y="42" class="c-prod">Cloud Run (public)</text>',
        '    <line x1="10" y1="56" x2="160" y2="56" stroke="#f1f3f4" stroke-width="1"/>',
        '    <text x="10" y="73" class="c-body" style="font-weight:600;fill:#202124">Accès lecture seule :</text>',
        '    <text x="10" y="88" class="c-body">Aucune clé requise</text>',
        f'    {chip(10, 99, "GET /sessions", bg="#fef7e0", fg="#b06000", border="#fde293", w=150)}',
        f'    {chip(10, 123, "GET /sessions/{id}", bg="#fef7e0", fg="#b06000", border="#fde293", w=150)}',
        '    <text x="10" y="160" class="c-code" style="font-size:8.6px;fill:#5f6368">devfest-sessions-…run.app</text>',
        '  </g>',
        '</g>',
    ])

    # ---------------- CONNECTORS (100% PLANAR) ----------------
    # 1. Participant <-> Concierge
    parts.append(f'<line x1="150" y1="199" x2="202" y2="199" {blue_edge_attrs("e_user")} marker-start="{blue_marker("e_user")}" marker-end="{blue_marker("e_user")}"/>')

    # 2. Concierge <-> Programme
    parts.append(f'<path d="M 370 170 L 402 170 L 402 152 L 432 152" fill="none" {blue_edge_attrs("e_prog")} marker-start="{blue_marker("e_prog")}" marker-end="{blue_marker("e_prog")}"/>')
    parts.append(pill_label(402, 126, "{@AGENT}", w=58, state=st["e_prog"]))

    # 3. Concierge <-> Assistance
    parts.append(f'<path d="M 370 238 L 402 238 L 402 316 L 432 316" fill="none" {blue_edge_attrs("e_assist")} marker-start="{blue_marker("e_assist")}" marker-end="{blue_marker("e_assist")}"/>')
    parts.append(pill_label(402, 278, "{@AGENT}", w=58, state=st["e_assist"]))

    # 4. Programme -> Session State
    parts.append(f'<line x1="572" y1="200" x2="572" y2="216" {grey_edge_attrs("e_state_prog")} marker-end="{grey_marker("e_state_prog")}"/>')

    # 5. Assistance -> Session State
    parts.append(f'<line x1="572" y1="282" x2="572" y2="266" {grey_edge_attrs("e_state_tkt")} marker-end="{grey_marker("e_state_tkt")}"/>')

    # 6. Concierge -> Data Store FAQ
    parts.append(f'<path d="M 287 278 L 287 370 L 592 370 L 592 404" fill="none" {blue_edge_attrs("e_faq")} marker-end="{blue_marker("e_faq")}"/>')
    parts.append(pill_label(426, 370, "Outil faq (recherche RAG)", w=146, state=st["e_faq"]))

    # 7. Fichier FAQ -> Bucket FAQ -> Data Store FAQ
    parts.append(f'<line x1="150" y1="441" x2="202" y2="441" {grey_edge_attrs("e_import")} marker-end="{grey_marker("e_import")}"/>')
    parts.append(f'<line x1="416" y1="441" x2="472" y2="441" {grey_edge_attrs("e_index")} marker-end="{grey_marker("e_index")}"/>')
    idx_lbl = "Import lancé" if mode == "tache2" else "Indexation"
    idx_fg = "#174ea6" if mode == "tache2" else "#5f6368"
    idx_bd = "#aecbfa" if mode == "tache2" else "#dadce0"
    parts.append(pill_label(444, 421, idx_lbl, fg=idx_fg, border=idx_bd, w=72 if mode == "tache2" else 64, state=st["e_index"]))

    # 8. Programme -> Public Cloud Run across Internet
    parts.append(f'<line x1="710" y1="180" x2="840" y2="180" {blue_edge_attrs("e_api", 2.2)} marker-end="{blue_marker("e_api")}"/>')
    api_l1 = "get_session" if mode == "tache3" else "HTTPS GET"
    api_l2 = "vérifie horaires" if mode == "tache3" else "public · sans clé"
    parts.append(pill_2lines(785, 148, api_l1, api_l2, w=86, state=st["e_api"]))

    # Footer legend ONLY on the full reference diagram (keeps per-task spotlights sleek!)
    if not is_task:
        parts.extend([
            '<g transform="translate(20,518)">',
            '  <line x1="0" y1="10" x2="28" y2="10" stroke="#1a73e8" stroke-width="2.2" marker-end="url(#arr-blue)"/>',
            '  <text x="36" y="14" class="leg-txt">Flux d’exécution (conversation, transfert, appel d’outil / API)</text>',
            '  <line x1="378" y1="10" x2="406" y2="10" stroke="#5f6368" stroke-width="1.7" stroke-dasharray="5,4" marker-end="url(#arr-grey)"/>',
            '  <text x="414" y="14" class="leg-txt">Import / état de session</text>',
            '  <rect x="558" y="2" width="15" height="15" rx="3" fill="#f6f8fc" stroke="#4285f4" stroke-width="1.5"/>',
            '  <text x="579" y="14" class="leg-txt">Projet GCP du participant (eu)</text>',
            '  <rect x="758" y="2" width="15" height="15" rx="3" fill="#fff8e1" stroke="#f29900" stroke-width="1.5"/>',
            '  <text x="779" y="14" class="leg-txt">Projet GCP externe public (hors compte)</text>',
            '</g>',
        ])

    parts.append('</g>')
    parts.append('</svg>')
    return "\n".join(parts)


def main() -> None:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    targets = [
        ("architecture", "full"),
        ("architecture-tache-2", "tache2"),
        ("architecture-tache-3", "tache3"),
        ("architecture-tache-4", "tache4"),
        ("architecture-tache-5", "tache5"),
    ]
    for filename, mode in targets:
        svg = build_diagram(mode)
        svg_dest = DOCS_IMAGES / f"{filename}.svg"
        png_preview = PREVIEW_DIR / f"{filename}.png"
        svg_dest.write_text(svg, encoding="utf-8")
        png_preview.write_bytes(resvg_py.svg_to_bytes(svg, dpi=192))
        print(f"OK {filename}: svg={svg_dest.stat().st_size}B -> {svg_dest.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
