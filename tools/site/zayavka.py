#!/usr/bin/env python3
"""«Состав заявки» и длинные блоки на телефоне (команда владельца 20.11.2026 «Делай это на сайте»).

    python3 tools/site/zayavka.py            # правит страницы репозитория, собирает zayavka.min.js и mob-bloki.min.js
    python3 tools/site/zayavka.py --check    # только проверка страниц репозитория

Решение — «Мобильная версия — блоки с выбором и состав заявки» (16.11.2026, листы на согласование в файлах проекта).
На всех 42 страницах сайта (кроме политики и согласия; с 20.11.2026 и на «Дезинфекции автотранспорта») перед <style id="tel-plain"> в <head> ставятся:
  * <style id="zv-css"> — стили состава, шторки, панели блока и длинных блоков (tools/site/zayavka.css);
  * <style id="chk-css"> — стили окна заявки, как у самопроверки (tools/site/samoproverka_forma.py), если их нет;
  * <script src="…zayavka.min.js?v=…" defer> — «Состав заявки»: выбор в блоках, шторка заявки на телефоне, состав в
    основной форме и в поле msg заявки (zayavka.js);
  * <script src="…mob-bloki.min.js?v=…" defer> — длинные блоки на телефоне (mob-bloki.js); на главной не ставится —
    у неё своя мобильная раскладка (tools/home-mobile, решение владельца 19.11.2026).
Тексты, разметка блоков, основная форма, app.js, style.css, send.php, счётчики (Метрика, UIS, Radist), телефон и почта
не меняются: код UIS остаётся прямо перед </head>, Radist — в конце <body> (ЗАКОН ВЛАДЕЛЬЦА 11.11.2026). На телефоне
ничего не затемняется (ЗАКОН ВЛАДЕЛЬЦА 17.11.2026). Повторный запуск ничего не меняет. transform() использует и пакет
для Timeweb (tools/deploy/prepare-2026-11-20-zayavka.py).
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import samoproverka_forma  # noqa: E402

VERSION = '20261120zv'
ANCHOR = '<style id="tel-plain">'
HOME = 'index.html'
PAGES = [
    'index.html', 'dezinfektsiya/index.html', 'dezinfektsiya/avtotransport/index.html', 'deratizatsiya/index.html', 'zashchita-ot-proniknoveniya-gryzunov/index.html',
    'dezinsektsiya/index.html', 'deratizatsiya-i-dezinsektsiya/index.html', 'dogovor-deratizatsiya-dezinsektsiya/index.html',
    'sanitarnyy-audit/index.html', 'razrabotka-ppk/index.html', 'laboratornye-issledovaniya/index.html',
    'ochistka-dezinfektsiya-ventilyatsii/index.html', 'pishchevoe-proizvodstvo/index.html', 'restorany-i-kafe/index.html',
    'magaziny-i-torgovye-seti/index.html', 'gostinitsy/index.html', 'farmatsevticheskie-proizvodstva/index.html',
    'sklady-i-logistika/index.html', 'biznes-tsentry-torgovye-tsentry-predpriyatiya/index.html',
    'materialy/index.html', 'materialy/programma-pest-kontrolya/index.html', 'materialy/zhurnal-pest-kontrolya/index.html',
    'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.html', 'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.html',
    'normativnaya-baza/index.html', 'normativnaya-baza/proverochnye-listy/index.html',
    'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html', 'normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/index.html',
    'materialy/akt-deratizatsii-i-dezinsektsii/index.html', 'materialy/skhema-tochek-pest-kontrolya/index.html',
    'materialy/pest-kontrol-iso-22000-fssc-22000/index.html', 'materialy/litsenziya-na-dezinfektsiyu/index.html',  # статьи, с 24.11.2026
    'dezinsektsiya/restorany-i-kafe/index.html', 'deratizatsiya/restorany-i-kafe/index.html',
    'laboratornye-issledovaniya/analiz-smyvov/index.html', 'laboratornye-issledovaniya/izmerenie-mikroklimata/index.html',
    'laboratornye-issledovaniya/zamer-osveshchennosti/index.html', 'laboratornye-issledovaniya/analiz-vozdukha-rabochey-zony/index.html',
    'laboratornye-issledovaniya/analiz-pishchevykh-produktov/index.html', 'laboratornye-issledovaniya/analiz-vody/index.html',
    'laboratornye-issledovaniya/kontrol-sterilizatorov/index.html', 'materialy/kak-berut-smyvy/index.html',
    'materialy/zamer-osveshchennosti-i-mikroklimata/index.html', 'materialy/kontrol-raboty-sterilizatorov/index.html',
]
JS = ['zayavka', 'mob-bloki']


def css_line():
    src = (ROOT / 'tools' / 'site' / 'zayavka.css').read_text(encoding='utf-8')
    src = re.sub(r'/\*.*?\*/', '', src, flags=re.S)
    src = re.sub(r'\s*\n\s*', '', src)
    src = re.sub(r'\s*([{};,])\s*', r'\1', src).replace(';}', '}')
    return '<style id="zv-css">/* состав заявки и длинные блоки на телефоне (tools/site/zayavka.py) */' + src + '</style>'


def rel_root(page):
    return '../' * page.count('/')


def tags(page):
    r = rel_root(page)
    out = ['<script src="%szayavka.min.js?v=%s" defer></script>' % (r, VERSION)]
    if page != HOME:
        out.append('<script src="%smob-bloki.min.js?v=%s" defer></script>' % (r, VERSION))
    return out


ZV_RE = re.compile(r'<style id="zv-css">.*?</style>\n?', re.S)
TAG_RE = re.compile(r'<script src="(?:\.\./)*(?:zayavka|mob-bloki)\.min\.js\?v=[0-9a-z]+" defer></script>\n?')
CHK_RE = re.compile(r'<style id="chk-css">.*?</style>\n', re.S)


def block(s, page):
    out = '' if CHK_RE.search(s) else samoproverka_forma.CSS
    return out + css_line() + '\n' + '\n'.join(tags(page)) + '\n'


def transform(s, page):
    """Новый текст страницы page (путь к index.html или index.php от корня сайта). Повторный запуск ничего не меняет."""
    page = page.replace('index.php', 'index.html')
    want = block(s, page)
    cur_css = ZV_RE.search(s)
    if cur_css:
        # уже стоит: убрать прежние строки и поставить новые на то же место (перед tel-plain)
        old = s
        s = ZV_RE.sub('', s, count=1)
        s = TAG_RE.sub('', s)
        assert s.count(ANCHOR) == 1, page + ': нет tel-plain'
        out = s.replace(ANCHOR, want + ANCHOR, 1)
        return old if out == old else out
    assert s.count(ANCHOR) == 1, page + ': нет tel-plain'
    assert s.index(ANCHOR) < s.index('</head>'), page + ': tel-plain не в <head>'
    return s.replace(ANCHOR, want + ANCHOR, 1)


def problems(s, page):
    page = page.replace('index.php', 'index.html')
    bad = []
    head = s[:s.index('</head>')]
    if head.count('<style id="zv-css">') != 1 or s.count('<style id="zv-css">') != 1:
        bad.append('zv-css: %d' % s.count('<style id="zv-css">'))
    if s.count('<style id="chk-css">') != 1:
        bad.append('chk-css: %d' % s.count('<style id="chk-css">'))
    for t in tags(page):
        if head.count(t) != 1:
            bad.append('нет ' + t)
    if page == HOME and 'mob-bloki.min.js' in s:
        bad.append('mob-bloki на главной')
    if s.count('zayavka.min.js') != 1:
        bad.append('zayavka.min.js: %d' % s.count('zayavka.min.js'))
    return bad


def minify():
    for name in JS:
        subprocess.run(['npx', '--yes', 'esbuild@0.24.2', name + '.js', '--minify', '--target=es2015', '--charset=utf8',
                        '--outfile=' + name + '.min.js', '--log-level=warning'], cwd=ROOT, check=True)


def main():
    check = '--check' in sys.argv[1:]
    total = 0
    for page in PAGES:
        f = ROOT / page
        s = f.read_text(encoding='utf-8')
        if not check:
            new = transform(s, page)
            if new != s:
                f.write_text(new, encoding='utf-8')
                total += 1
            s = new
        bad = problems(s, page)
        if bad:
            sys.exit('%s: %s' % (page, '; '.join(bad)))
    if not check:
        minify()
        print('zayavka: изменено страниц %d из %d, zayavka.min.js и mob-bloki.min.js собраны' % (total, len(PAGES)))
    else:
        print('zayavka: %d страниц — состав заявки и длинные блоки на телефоне на месте' % len(PAGES))


if __name__ == '__main__':
    main()
