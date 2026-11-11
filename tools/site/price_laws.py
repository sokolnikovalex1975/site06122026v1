#!/usr/bin/env python3
"""Единые начальные цены на всём сайте (указание владельца 11.11.2026):

  «Цена пест-контроля везде должна быть от 3 900 рублей, на всем сайте, на всех страницах, только на пест-контроль.
   На дератизацию и дезинсекцию, дезинфекцию — от 3 500 руб на всем сайте».

Что делает (последний шаг tools/site/build_site.py; patch() применим и к живым index.php с Timeweb):
  * пест-контроль — постоянное обслуживание по договору (грызуны и насекомые, IPM, абонентское, «комплексное
    обслуживание по договору»): «3 500 ₽ в месяц / ₽/мес» → «3 900 ₽ …», в JSON-LD у предложений «…пест-контрол…» 3500 → 3900;
  * дезинфекция помещений: «от 9 ₽ за м²» → «от 3 500 ₽ за обработку», в JSON-LD lowPrice "9" → "3500";
  * дератизация, дезинсекция по отдельности (в т. ч. по договору) остаются от 3 500 ₽; «Дератизация + дезинсекция»
    (комплекс) — от 4 900 ₽/мес, склады — от 4 500 ₽/мес (выше начальной цены), оснащение точками — от 600 ₽ за точку
    (это оборудование, не обработка) — не меняются.
Повторный запуск ничего не меняет. Запуск: python3 tools/site/price_laws.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
S = r'(?:[ \u00a0]|&nbsp;)'
MONTH = rf'(?={S}*(?:<[^>]+>{S}*)?(?:/{S}*мес|в{S}месяц))'

# страницы, где все «3 500 ₽ в месяц» — это пест-контроль (договор на грызунов и насекомых сразу)
PEST_MONTHLY = [
    'restorany-i-kafe', 'magaziny-i-torgovye-seti', 'biznes-tsentry-torgovye-tsentry-predpriyatiya',
    'materialy/pest-menedzhment-ili-razovaya-obrabotka', 'materialy/programma-pest-kontrolya',
    'materialy/zhurnal-pest-kontrolya', 'materialy/programma-proizvodstvennogo-kontrolya-haccp',
]
SKIP = re.compile(r'<section class="s s-(?:pr|vu)[^"]*" id="[^"]*".*?</section>|<style\b.*?</style>', re.S)
PEST_OFFER = re.compile(r'\{\s*"@type"\s*:\s*"Offer"\s*,\s*"name"\s*:\s*"[^"]*ест-контрол[^"]*"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}')


def _outside(s, fn):
    """Применяет fn только вне блоков прайса/каталога и стилей."""
    out, pos = [], 0
    for m in SKIP.finditer(s):
        out.append(fn(s[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(fn(s[pos:]))
    return ''.join(out)


def _monthly(t):
    return re.sub(rf'3({S})500({S})₽{MONTH}', r'3\g<1>900\g<2>₽', t)


def _offers(t):
    return PEST_OFFER.sub(lambda m: re.sub(r'(:\s*"?)3500\b', r'\g<1>3900', m.group(0)), t)


def _dezinf(t):
    t = re.sub(rf'от({S})9({S})₽({S})за({S})м²', r'от\g<1>3\g<2>500\g<2>₽\g<3>за\g<4>обработку', t)
    return re.sub(r'("lowPrice"\s*:\s*)"9"', r'\g<1>"3500"', t)


def _complex(t):
    # «(комплексное) обслуживание по договору … от 3 500 ₽ в месяц» на страницах отдельных услуг — это пест-контроль
    return re.sub(rf'([Кк]омплексное{S}+обслуживание{S}+по{S}+договору[^₽]{{0,300}}?)3({S})500({S})₽{MONTH}',
                  r'\g<1>3\g<2>900\g<3>₽', t)


def patch(s, rel):
    cur = rel.strip('/')
    def fn(t):
        t = _offers(_dezinf(_complex(t)))
        if cur in PEST_MONTHLY:
            t = _monthly(t)
        if cur == 'dezinfektsiya':
            # «обслуживание по договору от 3 500 ₽ в месяц» в описании и FAQ страницы дезинфекции — то же комплексное
            t = re.sub(rf'(обслуживание{S}+по{S}+договору{S}*(?:—{S}*)?от{S})3({S})500({S})₽{MONTH}',
                       r'\g<1>3\g<2>900\g<3>₽', t)
        return t
    return _outside(s, fn)


def main():
    sys.path.insert(0, str(ROOT / 'tools' / 'menu'))
    from apply_menu import PAGES
    for rel, root, cur in PAGES:
        f = ROOT / rel
        old = f.read_text(encoding='utf-8')
        new = patch(old, rel[:-len('index.html')])
        if new != old:
            f.write_text(new, encoding='utf-8')
            print('ok', rel)


if __name__ == '__main__':
    main()
