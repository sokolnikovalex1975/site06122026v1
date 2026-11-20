#!/usr/bin/env python3
"""Сборка пакета tools/deploy/home-mobile-2026-11-20 для Timeweb:
Ц-4 (мобильная главная: схема и круг IPM по варианту A, отрасли, цены и подвал по варианту B)
+ Ц-7 (удаление улицы, дома и индекса из JSON-LD главной, остаются Москва и область обслуживания).
"""
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'tools' / 'deploy' / 'home-mobile-2026-11-20'
PUB_SRC = ROOT / 'tools' / 'deploy' / 'publish_home_mobile.py'
HOST = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'


def fetch_live():
    for _ in range(8):
        try:
            return urllib.request.urlopen(HOST, timeout=20).read().decode('utf-8')
        except Exception:
            time.sleep(1.5)
    sys.exit('ERROR: failed to fetch live home page')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    live = fetch_live()
    live2 = fetch_live()
    assert live == live2, 'live home page changed between two reads'
    repo = (ROOT / 'index.html').read_text(encoding='utf-8')

    old_addr = '"address":{"@type":"PostalAddress","streetAddress":"2-й Хорошёвский проезд, д. 7, к. 1, помещ. 1","postalCode":"123007","addressLocality":"Москва","addressCountry":"RU"}'
    new_addr = '"address":{"@type":"PostalAddress","addressLocality":"Москва","addressCountry":"RU"}'
    assert live.count(old_addr) == 1 and repo.count(new_addr) == 1

    old_hz_st = re.search(r'<style id="hz-st">.*?</style>', live, re.S).group(0)
    new_hz_st = re.search(r'<style id="hz-st">.*?</style>', repo, re.S).group(0)
    new_hm_st = re.search(r'<style id="hm-st">.*?</style>', repo, re.S).group(0)

    old_ipm_js = re.search(r'<script id="ipm-pin-js">.*?</script>', live, re.S).group(0)
    new_ipm_js = re.search(r'<script id="ipm-pin-js">.*?</script>', repo, re.S).group(0)

    old_hz_js = re.search(r'<script id="hz-js">.*?</script>', live, re.S).group(0)
    new_hz_js = re.search(r'<script id="hz-js">.*?</script>', repo, re.S).group(0)
    new_hm_js = re.search(r'<script id="hm-js">.*?</script>', repo, re.S).group(0)

    replacements = [
        [old_addr, new_addr, 1],
        [old_hz_st, new_hz_st + '\n' + new_hm_st, 1],
        [old_ipm_js, new_ipm_js, 1],
        [old_hz_js, new_hz_js + '\n' + new_hm_js, 1],
    ]

    after = live
    for o, n, c in replacements:
        assert after.count(o) == c
        after = after.replace(o, n, 1)

    # Reverse check
    rev = after
    for o, n, _ in reversed(replacements):
        assert rev.count(n) == 1
        rev = rev.replace(n, o, 1)
    assert rev == live, 'reverse replacement mismatch'

    # Tracking & contact invariants
    for tok in ('113675622', 'comagic', 'uiscom', 'radist', 'tel:+74951043570', 'mailto:b2b@pestcontrol-center.ru'):
        assert live.count(tok) == after.count(tok), f'invariant changed: {tok}'

    # Validate JSON-LD in resulting HTML
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', after, re.S).group(1))
    assert ld['@graph'][0]['address'] == {'@type': 'PostalAddress', 'addressLocality': 'Москва', 'addressCountry': 'RU'}

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'backup').mkdir(parents=True)
    (OUT / 'pkg').mkdir(parents=True)

    b_old = live.encode('utf-8')
    b_new = after.encode('utf-8')
    (OUT / 'backup' / 'index.php').write_bytes(b_old)
    (OUT / 'pkg' / 'index.php').write_bytes(b_new)
    shutil.copy2(PUB_SRC, OUT / 'publish_home_mobile.py')

    payload = {
        'name': 'home-mobile-2026-11-20',
        'count': 1,
        'files': [{
            'file': 'index.php',
            'before': sha(b_old),
            'after': sha(b_new),
            'replace': replacements,
        }],
    }
    payload_bytes = (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    (OUT / 'deploy_payload.json').write_bytes(payload_bytes)

    pub_sha = sha((OUT / 'publish_home_mobile.py').read_bytes())
    pay_sha = sha(payload_bytes)

    run_once = (
        "#!/bin/sh\n"
        "# Разовая выкладка пакета home-mobile-2026-11-20 заданием Crontab панели Timeweb или из SSH-консоли.\n"
        "cd \"$(dirname \"$0\")\" || exit 1\n"
        "[ -e run_once.done ] && exit 0\n"
        "date '+%Y-%m-%d %H:%M:%S %Z' > run_once.done\n"
        "{\n"
        "  echo \"start: $(date '+%Y-%m-%d %H:%M:%S %Z')\"\n"
        f"  printf '%s  %s\\n%s  %s\\n' \\\n"
        f"    {pub_sha} publish_home_mobile.py \\\n"
        f"    {pay_sha} deploy_payload.json | sha256sum -c - &&\n"
        "  python3 --version &&\n"
        "  python3 publish_home_mobile.py --check &&\n"
        "  python3 publish_home_mobile.py --publish &&\n"
        "  python3 publish_home_mobile.py --check\n"
        "  echo \"exit: $?\"\n"
        "  echo \"end: $(date '+%Y-%m-%d %H:%M:%S %Z')\"\n"
        "} > run_once.log 2>&1\n"
    ).encode('utf-8')
    (OUT / 'run_once.sh').write_bytes(run_once)
    (OUT / 'run_once.sh').chmod(0o755)

    manifest = (
        f"home-mobile-2026-11-20\n"
        f"index.php  {sha(b_old)} -> {sha(b_new)}  ({len(b_old)} -> {len(b_new)} bytes)\n"
        f"publish_home_mobile.py  {pub_sha}\n"
        f"deploy_payload.json     {pay_sha}\n"
        f"run_once.sh             {sha(run_once)}\n"
    )
    (OUT / 'MANIFEST.txt').write_text(manifest, encoding='utf-8')
    print(manifest)


if __name__ == '__main__':
    main()
