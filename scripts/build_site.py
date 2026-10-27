"""Convierte los informes de reports/ en páginas HTML dentro de site/informes/.

Uso: uv run --with markdown scripts/build_site.py
"""

import logging
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "informes"

REPORTS = [
    ("ensayo-anuncios.html", "Ensayo para anuncios", "reports/Hackatón de Meta ideas en grande.md"),
    ("jueces.html", "Qué buscan los jueces", "reports/Hackatón de Meta qué buscan jueces.md"),
    ("crowdfunding-v1.html", "Versión crowdfunding", "reports/Hackatón de Meta ideas en grande v1 crowdfunding.md"),
]

NAV_ITEMS = [("../index.html", "← Plan y roadmap")] + [(slug, title) for slug, title, _ in REPORTS]

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700'
    '&amp;family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet">'
)

NAV_CSS = """
.site-nav{background:#1C2333;border-bottom:1px solid #1F2937;font-family:Inter,system-ui,sans-serif}
.site-nav div{max-width:1120px;margin:0 auto;padding:12px 24px;display:flex;flex-wrap:wrap;gap:8px 24px;align-items:center}
.site-nav strong{color:#F9FAFB;font-family:'Space Grotesk',sans-serif;font-size:16px;margin-right:8px}
.site-nav a{color:#D1D5DB;font-size:15px;text-decoration:none;padding:10px 0}
.site-nav a:hover{color:#FFFFFF}
.site-nav a[aria-current="page"]{color:#8FB0FF;font-weight:600}
"""

REPORT_CSS = """
body{margin:0;background:#F7F8FA;color:#3A4152;font-family:Inter,system-ui,sans-serif;font-size:17px;line-height:1.65}
a{color:#2456D6}a:hover{color:#1B44AE}
main{max-width:860px;margin:0 auto;padding:56px 24px 96px}
h1,h2,h3{font-family:'Space Grotesk',sans-serif;color:#1C2333;line-height:1.15}
h1{font-size:clamp(32px,5vw,48px);font-weight:800;margin:0 0 24px}
h2{font-size:30px;font-weight:800;margin:56px 0 16px;padding-top:24px;border-top:1px solid #E5E7EB}
h3{font-size:22px;margin:36px 0 12px}
blockquote{margin:24px 0;padding:16px 20px;background:#FFF7ED;border-left:3px solid #B45309}
blockquote p{margin:0}
.table-wrap{overflow-x:auto;margin:24px 0;border:1px solid #E5E7EB;border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:15px;min-width:640px}
th{background:#F3F4F6;text-align:left;font-weight:600;color:#1C2333}
th,td{padding:10px 14px;border-top:1px solid #E5E7EB;vertical-align:top}
code{font-size:0.9em;background:#F3F4F6;padding:1px 5px;border-radius:4px}
"""


def nav(current: str) -> str:
    links = "".join(
        f'<a href="{slug}"{" aria-current=\"page\"" if slug == current else ""}>{title}</a>'
        for slug, title in NAV_ITEMS
    )
    return f'<nav class="site-nav" aria-label="Documentos"><div><strong>Ensayo · Hackatón Meta</strong>{links}</div></nav>'


def page(title: str, head_extra: str, body: str) -> str:
    return (
        '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="robots" content="noindex, nofollow">\n'
        f"<title>{title}</title>\n{head_extra}\n</head>\n<body>\n{body}\n</body>\n</html>\n"
    )


def build_report(slug: str, title: str, md_path: str) -> None:
    text = (ROOT / md_path).read_text(encoding="utf-8")
    html = markdown.markdown(text, extensions=["tables", "sane_lists"])
    html = re.sub(r"<table>(.*?)</table>", r'<div class="table-wrap"><table>\1</table></div>', html, flags=re.S)
    head = f"{FONTS}\n<style>{REPORT_CSS}{NAV_CSS}</style>"
    body = f"{nav(slug)}\n<main>\n{html}\n</main>"
    (OUT / slug).write_text(page(f"Ensayo · {title}", head, body), encoding="utf-8")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, title, md_path in REPORTS:
        build_report(slug, title, md_path)
    for f in sorted(OUT.glob("*.html")):
        logging.info(f"{f.name}\t{f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
