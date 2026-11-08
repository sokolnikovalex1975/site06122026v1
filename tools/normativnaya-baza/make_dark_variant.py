#!/usr/bin/env python3
"""Временная страница для сравнения: «Документы для Роспотребнадзора» с тёмным первым экраном и обложкой чек-листа.

    python3 tools/site/build_site.py                      # сначала обычная сборка
    python3 tools/normativnaya-baza/make_dark_variant.py  # → normativnaya-baza/dokumenty-temnyy-variant/index.html

Первый экран — как в согласованном тексте (блок 1): тёмный фон без фото, как были хаб и проверочные листы до 08.11.2026,
справа карточка «Проверено» с мини-обложкой чек-листа PDF. Остальная страница — байт в байт как у основной: скрипт берёт
собранную страницу и меняет только первый экран, стили первого экрана и заголовок вкладки; предзагрузка фото убрана.
Папка лежит рядом со страницей (та же глубина), поэтому относительные ссылки не меняются.

Страница только для превью на GitHub Pages: в sitemap.xml и в версию для Timeweb (build_prod.py) не входит.
После решения владельца папку normativnaya-baza/dokumenty-temnyy-variant/ и этот скрипт удалить.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SRC = ROOT / 'normativnaya-baza' / 'dokumenty-dlya-rospotrebnadzora' / 'index.html'
OUT = ROOT / 'normativnaya-baza' / 'dokumenty-temnyy-variant' / 'index.html'

CSS = '''<style data-variant="dark">
/* вариант для сравнения: тёмный первый экран с обложкой чек-листа (стили — как у хаба до 08.11.2026) */
.dkv-hero{position:relative;padding:clamp(120px,10vw,190px) 0 clamp(56px,6vw,96px);background:radial-gradient(1100px 620px at 82% 8%,rgba(97,95,255,.15),transparent 64%),radial-gradient(900px 520px at 4% 100%,rgba(124,134,255,.06),transparent 60%)}
.dkv-hero .wrap{display:flex;flex-direction:column}
.dkv-hero .f-crumbs{margin:0 0 clamp(22px,2vw,32px)}
.dkv-grid{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(340px,.8fr);gap:clamp(28px,4vw,80px);align-items:end}
.dkv-copy{min-width:0}
.dkv-hero .eyebrow{margin:0 0 clamp(20px,1.8vw,30px)}
.dkv-hero h1{font-size:clamp(40px,4vw,74px);line-height:1.06;margin:0 0 clamp(22px,2vw,34px)}
.dkv-hero h1 .ln{display:block;padding:0 .08em .08em 0;margin-bottom:-.08em}
.dkv-hero h1 .ln>span{display:inline-block}
.dkv-hero p.lead{font-size:clamp(16px,1.08vw,20px);line-height:1.62;color:#c4c4cc;max-width:900px;margin:0 0 30px}
.dkv-check{display:grid;grid-template-columns:120px minmax(0,1fr);gap:22px;align-items:start;padding:clamp(22px,2vw,32px)}
.dkv-check .dk-cover:hover,.dkv-check .dk-cover:focus-visible{transform:rotate(0) translateY(-2px)}
.dkv-check-k{font-size:12px;font-weight:500;text-transform:uppercase;letter-spacing:.14em;color:var(--acc);margin:0 0 10px}
.dkv-check ul{list-style:none;padding:0;margin:0}
.dkv-check li{display:flex;flex-direction:column;gap:4px;padding:14px 0;border-top:1px solid var(--line2)}
.dkv-check li:first-child{border-top:0;padding-top:4px}
.dkv-check li:last-child{padding-bottom:0}
.dkv-check li span{font-size:13px;color:var(--t3)}
.dkv-check li b{font-weight:500;color:var(--t1);font-size:clamp(15px,1.05vw,18px);line-height:1.4}
.dkv-hero .nb-toc{margin-top:clamp(36px,3.4vw,56px)}
/* планшет и телефон: крошки — внизу первого экрана (на телефоне скрыты правилом m-crumbs), карточка — под кнопками */
@media (max-width:1280px){
  .dkv-check{grid-template-columns:104px minmax(0,1fr);gap:18px}
}
@media (max-width:1180px){
  .dkv-hero .f-crumbs{order:3;margin:22px 0 0}
  .dkv-hero h1 .ln{display:inline}
}
@media (max-width:1100px){
  .dkv-grid{grid-template-columns:minmax(0,1fr);align-items:start}
  .dkv-check{max-width:620px}
}
@media (max-width:860px){
  html .dkv-hero h1{font-size:clamp(28px,7.8vw,36px);line-height:1.08;letter-spacing:-.055em}
  .dkv-hero p.lead{font-size:15px;line-height:1.55;margin-bottom:24px}
}
@media (max-width:760px){
  .dkv-hero{padding:100px 0 48px}
  .dkv-check{grid-template-columns:104px minmax(0,1fr);gap:18px}
  .dkv-check li b{font-size:15px}
}
</style>
'''


def main():
    s = SRC.read_text(encoding='utf-8')
    i = s.index('<section class="d-hero nb-hero dk-hero" id="hero">')
    j = s.index('</section>', i) + len('</section>')
    hero = s[i:j]

    def part(pat):
        m = re.search(pat, hero, re.S)
        assert m, 'первый экран: не найдено ' + pat
        return m.group(0)

    crumbs = part(r'<nav class="f-crumbs".*?</nav>')
    eyebrow = part(r'<div class="eyebrow">.*?</div>')
    h1 = part(r'<h1>.*?</h1>')
    lead = part(r'<p class="lead"[^>]*>.*?</p>')
    # как у тёмного хаба до 08.11.2026: абзац виден сразу, без анимации появления — без фото это самый крупный
    # элемент первого экрана, по нему считается LCP
    lead = lead.replace('<p class="lead" data-h>', '<p class="lead">', 1)
    btns = part(r'<div class="d-btns"[^>]*>.*?</div>')
    pdf_line = part(r'<p class="dk-pdf-line[^"]*"[^>]*>.*?</p>')
    toc = part(r'<nav class="p-toc nb-toc".*?</nav>')
    pdf = re.search(r'href="([^"]+\.pdf)"', pdf_line).group(1)
    img = pdf.split('normativnaya-baza/')[0] + 'img/dok-cover-'
    aside = (
        '<aside class="card dkv-check" aria-label="Чек-лист PDF" data-h>\n'
        f'          <a class="dk-cover" href="{pdf}" download data-dl="pdf" aria-label="Скачать чек-лист PDF, 10 страниц">'
        f'<img src="{img}240.webp" srcset="{img}240.webp 240w, {img}360.webp 360w, {img}480.webp 480w" '
        'sizes="(max-width:1280px) 104px, 120px" width="240" height="339" alt="" decoding="async"></a>\n'
        '          <div>\n'
        '            <p class="dkv-check-k">Проверено</p>\n'
        '            <ul>\n'
        '              <li><span>Сверено с официальными текстами</span><b>07.11.2026</b></li>\n'
        '              <li><span>Подготовила</span><b>Марианна Семерина, санитарный врач</b></li>\n'
        '              <li><span>Чек-лист PDF</span><b>10 страниц, можно распечатать и заполнить</b></li>\n'
        '            </ul>\n'
        '          </div>\n'
        '        </aside>')
    dark = (
        '<section class="p-hero dkv-hero" id="hero">\n'
        '  <div class="wrap">\n'
        f'    {crumbs}\n'
        '    <div class="dkv-grid">\n'
        '      <div class="dkv-copy">\n'
        f'        {eyebrow}\n'
        f'        {h1}\n'
        f'        {lead}\n'
        f'        {btns}\n'
        f'        {pdf_line}\n'
        '      </div>\n'
        f'      {aside}\n'
        '    </div>\n'
        f'    {toc}\n'
        '  </div>\n'
        '</section>')
    s = s[:i] + dark + s[j:]

    # фото на первом экране нет — предзагрузка не нужна
    s, n = re.subn(r'<link rel="preload" as="image"[^>]*dok-hero[^>]*>\n?', '', s)
    assert n == 2, 'предзагрузка фото: ' + str(n)
    s = s.replace('</head>', CSS + '</head>', 1)
    s, n = re.subn(r'<title>', '<title>Вариант: тёмный первый экран — ', s, count=1)
    assert n == 1
    assert 'noindex' in s, 'вариант должен быть закрыт от индексации'
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(s, encoding='utf-8')
    print('ok', OUT.relative_to(ROOT), len(s.encode()), 'байт')


if __name__ == '__main__':
    main()
