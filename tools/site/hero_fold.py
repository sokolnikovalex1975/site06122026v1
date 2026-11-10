#!/usr/bin/env python3
"""Кнопки первого экрана видны целиком на любом экране — правило владельца сайта для всех страниц.

    python3 tools/site/hero_fold.py

Запрос владельца 09.11.2026: «кнопки должны влезать на любых разрешениях на первом экране». До правки на телефонах
у отраслевых страниц (фото сверху, затем заголовок, длинный абзац и только потом кнопки) кнопки оказывались на 130–400 px
ниже края экрана, на ноутбуках 1280–1536 px по высоте 600–760 px — на 10–230 px ниже края.

Что делает правило (только стили, тексты и порядок в HTML не меняются — для поиска и экранных дикторов всё как было):
  • телефоны и планшеты: кнопки сразу после заголовка, абзац и списки — под кнопками (так уже было на страницах
    нормативной базы); высота фото первого экрана зависит от высоты экрана (на низких экранах фото ниже);
    на совсем низких экранах (до 620 px) прячется плашка над заголовком — её текст дублируется ниже по странице;
  • компьютеры и ноутбуки: кнопки сразу после вводного абзаца, списки «галочек» и пояснения — под кнопками;
    на экранах до 820 px по высоте уменьшены отступы и размер заголовка (зависит от высоты экрана).

Скрипт вставляет (или обновляет) одну строку <style id="hero-fold"> перед </head> на каждой странице с первым экраном
#hero. Запускается из tools/site/build_site.py после tools/site/mobile_crumbs.py; та же функция apply() используется
для точечной правки страниц, взятых с сайта (tools/deploy/prepare-2026-11-09-fold.py).
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SKIP = {'.git', 'tools', 'dist', 'server', 'node_modules', 'preview-audit'}

CSS = r"""
/* ===== телефоны: главная (до 760 px) ===== */
@media (max-width:760px){
#hero.hero:not(.f-hero) .hero-copy{display:flex;flex-direction:column}
#hero.hero:not(.f-hero) .hero-copy>*{order:6}
#hero.hero:not(.f-hero) .hero-copy>.badge{order:1;align-self:flex-start}
#hero.hero:not(.f-hero) .hero-copy>h1{order:2;margin-bottom:0}
#hero.hero:not(.f-hero) .hero-copy>.hero-ctas{order:3;margin-top:22px}
#hero.hero:not(.f-hero) .hero-copy>.lead{order:4;margin-top:24px}
}
@media (max-width:760px) and (max-height:620px){
#hero.hero:not(.f-hero){padding-top:92px}
#hero.hero:not(.f-hero) h1{margin-top:18px}
}
/* ===== телефоны и планшеты: отраслевые страницы с фото сверху (до 900 px) ===== */
@media (max-width:900px){
#hero.f-hero .hero-copy{display:flex;flex-direction:column}
#hero.f-hero .hero-copy>*{order:6}
#hero.f-hero .hero-copy>.f-crumbs{order:0}
#hero.f-hero .hero-copy>.badge{order:1;align-self:flex-start}
#hero.f-hero .hero-copy>h1{order:2;margin-bottom:0}
#hero.f-hero .hero-copy>.hero-ctas{order:3;margin-top:22px}
#hero.f-hero .hero-copy>.lead{order:4;margin-top:24px}
#hero.f-hero .hero-media{aspect-ratio:auto;height:clamp(104px,calc(100vh - 440px),56.25vw);height:clamp(104px,calc(100svh - 440px),56.25vw)}
}
@media (max-width:760px){
#hero.f-hero .hero-media{height:clamp(104px,calc(100vh - 440px),75vw);height:clamp(104px,calc(100svh - 440px),75vw)}
.rp-page #hero.f-hero .hero-media,.lb-page #hero.f-hero .hero-media{height:clamp(104px,calc(100vh - 480px),75vw);height:clamp(104px,calc(100svh - 480px),75vw)}
}
@media (max-width:900px) and (max-height:620px){
#hero.f-hero .hero-copy>.badge{display:none}
#hero.f-hero .hero-media{height:clamp(96px,calc(100vh - 400px),75vw);height:clamp(96px,calc(100svh - 400px),75vw)}
.rp-page #hero.f-hero .hero-copy>h1{font-size:clamp(26px,7.6vw,34px)}
#hero.f-hero .hero-copy>h1{margin-top:30px}
}
/* ===== телефоны и планшеты: страницы с фото под заголовком (до 860 px) ===== */
@media (max-width:860px){
#hero.d-hero .d-hero-media{aspect-ratio:auto;height:clamp(104px,calc(100vh - 380px),56.25vw);height:clamp(104px,calc(100svh - 380px),56.25vw)}
}
@media (max-width:860px) and (max-height:620px){
#hero.d-hero{padding-top:84px}
#hero.d-hero .d-hero-media{margin-top:14px}
#hero.d-hero .d-btns{margin-top:16px}
}
/* ===== очень низкие экраны телефонов (до 520 px: iPhone SE первого поколения, телефон горизонтально) — без фото ===== */
@media (max-width:860px) and (max-height:520px){
#hero.d-hero .d-hero-media{display:none}
#hero.d-hero h1{margin-bottom:0}
}
@media (max-width:900px) and (max-height:520px){
#hero.f-hero{padding-top:76px}
#hero.f-hero .hero-media{display:none}
#hero.f-hero .wrap{margin-top:0}
#hero.f-hero .hero-copy>h1{margin-top:0}
}
/* ===== узкие телефоны (до 400 px): кнопки не шире экрана ===== */
@media (max-width:400px){
#hero .hero-copy{min-width:0}
#hero .hero-ctas .btn{min-width:0;max-width:100%;white-space:normal;padding:0 14px}
#hero .hero-ctas .btn-t{white-space:normal;text-align:center}
}
@media (max-width:860px) and (max-height:620px){
#hero.d-hero .d-hero-media{height:clamp(104px,calc(100vh - 410px),56.25vw);height:clamp(104px,calc(100svh - 410px),56.25vw)}
}
@media (max-height:520px){
#hero.p-hero .p-hero-copy>.d-btns{order:3;margin-top:18px}
#hero.p-hero .p-hero-copy>.p-def{order:4;margin-top:18px}
}
@media (max-width:760px) and (max-height:620px){
#hero.p-hero .p-hero-copy>.d-btns{order:3;margin-top:18px}
#hero.p-hero .p-hero-copy>.p-def{order:4;margin-top:18px}
}
@media (min-width:761px) and (max-height:520px){
#hero.hero:not(.f-hero){padding-top:84px;min-height:0}
#hero.hero:not(.f-hero) .hero-copy{display:flex;flex-direction:column}
#hero.hero:not(.f-hero) .hero-copy>*{order:6}
#hero.hero:not(.f-hero) .hero-copy>.badge{order:1;align-self:flex-start}
#hero.hero:not(.f-hero) .hero-copy>h1{order:2;margin:14px 0 0}
#hero.hero:not(.f-hero) .hero-copy>.hero-ctas{order:3;margin-top:18px}
#hero.hero:not(.f-hero) .hero-copy>.lead{order:4;margin-top:18px}
}
/* ===== компьютеры и ноутбуки: кнопки сразу после вводного абзаца ===== */
@media (min-width:861px){
#hero.d-hero .d-hero-copy{display:flex;flex-direction:column}
#hero.d-hero .d-hero-copy>*{order:6}
#hero.d-hero .d-hero-copy>.d-crumbs{order:0}
#hero.d-hero .d-hero-copy>.eyebrow{order:1}
#hero.d-hero .d-hero-copy>h1{order:2}
#hero.d-hero .d-hero-copy>:is(.lead,.sub,.p-def):not(:is(.lead,.sub,.p-def)~*){order:3}
#hero.d-hero .d-hero-copy>.d-btns:not(.d-btns~*){order:4}
#hero.d-hero .d-hero-copy>.d-ticks{margin-bottom:0}
}
@media (min-width:901px){
#hero.f-hero .hero-copy{display:flex;flex-direction:column}
#hero.f-hero .hero-copy>*{order:6}
#hero.f-hero .hero-copy>.f-crumbs{order:0}
#hero.f-hero .hero-copy>.badge{order:1;align-self:flex-start}
#hero.f-hero .hero-copy>h1{order:2}
#hero.f-hero .hero-copy>.lead{order:3}
#hero.f-hero .hero-copy>.hero-ctas{order:4}
#hero.f-hero .hero-copy>.rp-hero-list{margin-top:26px}
}
/* ===== невысокие экраны компьютеров и ноутбуков (до 820 px по высоте) ===== */
@media (min-width:861px) and (max-height:820px){
#hero.d-hero{padding-top:calc(clamp(68px,6vw,115px) + 8px)}
#hero.d-hero .d-hero-copy>.d-crumbs{margin-bottom:0}
#hero.d-hero .d-hero-copy>.eyebrow{margin:16px 0 0}
#hero.d-hero .d-hero-copy>h1{margin-top:14px;line-height:1.02}
#hero.d-hero .d-hero-copy>:is(.lead,.sub,.p-def){margin-top:16px}
#hero.d-hero .d-btns{margin-top:20px}
}
@media (min-width:901px) and (max-height:820px){
#hero.f-hero{padding-top:80px}
#hero.f-hero .hero-copy>.f-crumbs{margin-bottom:10px}
#hero.f-hero .hero-copy>h1{font-size:min(8.2vh,4.4vw);margin:16px 0 14px}
.rp-page #hero.f-hero .hero-copy>h1,.lb-page #hero.f-hero .hero-copy>h1{font-size:min(8vh,3.4vw)}
#hero.f-hero .hero-copy>.lead{line-height:1.5}
#hero.f-hero .hero-copy>.hero-ctas{margin-top:26px}
}
@media (min-width:761px) and (max-height:820px){
#hero.p-hero h1{font-size:min(8.4vh,4.4vw)}
#hero.p-hero .p-hero-copy>.d-btns{margin-top:20px}
}
@media (min-width:761px) and (max-height:820px){
#hero.hero:not(.f-hero) h1{font-size:min(8.4vh,4.4vw);margin:22px 0 18px}
#hero.hero:not(.f-hero) .hero-ctas{margin-top:28px}
}
"""
RULE = ('<style id="hero-fold">/* кнопки первого экрана видны целиком на любом экране (tools/site/hero_fold.py) */'
        + re.sub(r'\s*\n\s*', '', re.sub(r'/\*.*?\*/', '', CSS, flags=re.S)) + '</style>')
HAS_HERO = re.compile(r'<section[^>]*id="hero"')
OLD = re.compile(r'<style id="hero-fold">.*?</style>\n?', re.S)


def apply(s):
    """Вставить правило в одну страницу (тот же код используется для точечной правки страниц с сайта)."""
    if not HAS_HERO.search(s):
        return s, False
    s = OLD.sub('', s)
    if s.count('</head>') != 1:
        raise SystemExit('ошибка: на странице не один </head>')
    return s.replace('</head>', RULE + '\n</head>', 1), True


def main():
    n = 0
    for f in sorted(ROOT.rglob('index.html')):
        if SKIP & set(f.relative_to(ROOT).parts):
            continue
        s = f.read_text(encoding='utf-8')
        new, ok = apply(s)
        if ok:
            n += 1
            if new != s:
                f.write_text(new, encoding='utf-8')
    print(f'кнопки первого экрана: правило на {n} страницах')


if __name__ == '__main__':
    main()
