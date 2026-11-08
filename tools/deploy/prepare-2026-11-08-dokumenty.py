#!/usr/bin/env python3
"""Prepare a minimal, checksum-gated release from current live bytes."""
import concurrent.futures
import hashlib
import pathlib
import re
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/site"))
import build_prod

OUT = ROOT.parent / "release-dokumenty-2026-11-08"
LIVE = OUT / "live"
PKG = OUT / "pkg"
SITE = "https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/"
SLUG = "normativnaya-baza/dokumenty-dlya-rospotrebnadzora/"
MARK = "<!-- Yandex.Metrika counter + UIS + Radist"
NAME = "Документы для\u00a0Роспотребнадзора"


def get(rel):
    url = SITE + (rel.removesuffix("index.php") if rel.endswith("index.php") else rel)
    with urllib.request.urlopen(url, timeout=60) as r:
        return rel, r.read()


def save(base, rel, data):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def counter(s):
    return s[s.index(MARK):] if MARK in s else ""


def insert_panel(s, ident, link):
    pattern = r'(<div class="(?:nav-dd-panel|mm-sub)" id="' + ident + r'">)(.*?)(</div>)'
    def change(m):
        assert SLUG not in m[2]
        return m[1] + m[2] + link + m[3]
    result, n = re.subn(pattern, change, s, count=1, flags=re.S)
    assert n == 1, ident
    return result


def insert_footer(s, title, link):
    pattern = r"(<div><h4>" + title + r"</h4><ul>)(.*?)(</ul></div>)"
    def change(m):
        body = m[2]
        if SLUG in body:
            return m[0]
        if title == "Услуги":
            body = re.sub(r'<li><a [^>]*>Документы для[ \u00a0]проверок</a></li>', "", body)
        return m[1] + body + "<li>" + link + "</li>" + m[3]
    result, n = re.subn(pattern, change, s, count=1, flags=re.S)
    assert n == 1, title
    return result


def main():
    paths = [p.replace("index.html", "index.php")
             for p in build_prod.PAGES + build_prod.LEGAL if p != SLUG + "index.html"]
    paths += ["sitemap.xml", "app.min.js"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for rel, data in pool.map(get, paths):
            save(LIVE, rel, data)
    baseline = (LIVE / "index.php").read_text()
    assert counter(baseline) == counter((ROOT / "dist/timeweb/index.php").read_text())
    assert (LIVE / "app.min.js").read_bytes() == (ROOT / "app.min.js").read_bytes(), "shared JS has changed"
    replaced = []
    for rel in paths:
        if not rel.endswith(".php"):
            continue
        original = (LIVE / rel).read_text()
        root = "../" * (len(pathlib.PurePosixPath(rel).parts) - 1)
        link = f'<a href="{root}{SLUG}">{NAME}</a>'
        new = insert_panel(original, "nav-uslugi", link)
        new = insert_panel(new, "mm-uslugi", link)
        new = insert_footer(new, "Услуги", link)
        new = insert_footer(new, "Материалы", link)
        assert counter(original) == counter(new), rel
        old_main = re.search(r"<main\b.*?</main>", original, re.S)
        new_main = re.search(r"<main\b.*?</main>", new, re.S)
        assert (old_main[0] if old_main else "") == (new_main[0] if new_main else ""), rel
        save(PKG, rel, new.encode())
        replaced.append(rel)
    sm = (LIVE / "sitemap.xml").read_text()
    ET.fromstring(sm)
    if SITE + SLUG not in sm:
        sm = sm.replace("</urlset>", f"  <url><loc>{SITE}{SLUG}</loc><lastmod>2026-11-08</lastmod><priority>0.7</priority></url>\n</urlset>")
        save(PKG, "sitemap.xml", sm.encode())
        replaced.append("sitemap.xml")
    new_rel = SLUG + "index.php"
    page = (ROOT / "dist/timeweb" / new_rel).read_bytes()
    assert b'noindex' not in page
    assert counter(page.decode()) == counter(baseline)
    save(PKG, new_rel, page)
    for p in (ROOT / "img").glob("dok-*"):
        if p.suffix == ".webp":
            save(PKG, "img/" + p.name, p.read_bytes())
    for p in (ROOT / SLUG).glob("*.pdf"):
        save(PKG, SLUG + p.name, p.read_bytes())
    all_files = sorted(str(p.relative_to(PKG)) for p in PKG.rglob("*") if p.is_file())
    manifest = "".join(hashlib.sha256((PKG / r).read_bytes()).hexdigest() + "  " + r + "\n" for r in all_files)
    (OUT / "MANIFEST.sha256").write_text(manifest)
    expected = "\n".join(hashlib.sha256((LIVE / r).read_bytes()).hexdigest() + "  " + r for r in replaced)
    conf = (f'NAME="pestcontrol-dokumenty-2026-11-08"\nBK="before-dokumenty-2026-11-08.zip"\n'
            f'ORDER="{" ".join(all_files)}"\nREPLACED="{" ".join(replaced)}"\nEXPECTED_BEFORE="{expected}"\n')
    (OUT / "deploy.conf").write_text(conf)
    shutil.copy2(ROOT / "tools/deploy/run_all.sh", OUT / "run_all.sh")
    print(f"Prepared {len(all_files)} files, {len(replaced)} replacements. Counters and main content unchanged.")
    print(OUT)


if __name__ == "__main__":
    main()
