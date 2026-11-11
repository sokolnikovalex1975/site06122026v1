import re
NB = '\u00a0'
SHORT = r'(?:в|во|без|до|из|к|ко|на|по|о|об|обо|от|с|со|у|за|для|и|а|но|или|не|ни|при|под|над|про)'
def _typo_text(s):
    s = s.replace(' —', NB + '—')
    s = re.sub(r'(?<![\w\-])(' + SHORT + r') (?=\S)', lambda m: m.group(1) + NB, s, flags=re.I)
    s = re.sub(r'(?<![\w])(ст|ч|п|пп|г|д|к|корп|лит|ул|помещ|стр|т|тел)\. (?=\S)', lambda m: m.group(1) + '.' + NB, s, flags=re.I)
    s = s.replace('№ ', '№' + NB)
    s = re.sub(r'(?<![\w])(ООО|АО|ИП) (?=«)', lambda m: m.group(1) + NB, s)
    s = re.sub(r'(?<=\d) (?=[а-яёА-ЯЁ])', NB, s)
    # Телефон НЕ склеиваем неразрывными пробелами — ЗАКОН ВЛАДЕЛЬЦА 11.11.2026 (tools/site/tracking_laws.py, п. 4):
    # с &nbsp; внутри номера колл-трекинг UIS (CoMagic) его не находит и не подменяет. Номер не разрывается благодаря
    # стилю a[href^="tel:"]{white-space:nowrap} (<style id="tel-plain">). До 11.11.2026 здесь ставились U+00A0.
    return s
def typo(html):
    parts = re.split(r'(<[^>]+>)', html)
    return ''.join(p if p.startswith('<') else _typo_text(p) for p in parts)
