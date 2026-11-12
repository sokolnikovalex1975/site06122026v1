#!/usr/bin/env python3
"""Превью блока «Наши клиенты» (запрос владельца 12.11.2026: «Нужно сделать блок на каждой странице „наши клиенты“.
Предложи, где этот блок нужно разместить, наверное, только на коммерческих страницах… Сделай превью и скрин»).

    preview-klienty.html               — главная: блок 4-м экраном, после прайса #tseny, перед «Этапами»;
    preview-klienty-restorany/         — «Пест-контроль ресторанов и кафе»: блок перед формой заявки,
                                         первыми — логотипы ресторанов и кафе.

Превью лежат на той же глубине, что и исходные страницы, поэтому все относительные ссылки, стили и скрипты
работают без переписывания. Основа — собранные страницы репозитория (index.html, restorany-i-kafe/index.html);
меняется только вставка блока (tools/site/clients_block.py) и заголовок вкладки. Превью закрыты noindex,
в sitemap, поиск, меню и сборку для Timeweb не входят (tools/site/build_prod.PAGES). После согласования блок
включается шагом сборки в tools/site/build_site.py, а превью удаляются.

    python3 tools/klienty/make_logos.py && python3 tools/klienty-preview/build.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import clients_block  # noqa: E402

PREVIEWS = [  # исходная страница, адрес для порядка логотипов, файл превью
    ('index.html', '', 'preview-klienty.html'),
    ('restorany-i-kafe/index.html', 'restorany-i-kafe', 'preview-klienty-restorany/index.html'),
]


def main():
    for src, rel, dst in PREVIEWS:
        s = (ROOT / src).read_text(encoding='utf-8')
        assert '<meta name="robots" content="noindex, nofollow">' in s, src + ': нет noindex превью'
        s = clients_block.patch(s, rel)
        s = re.sub(r'<title>', '<title>Превью «Наши клиенты» · ', s, count=1)
        out = ROOT / dst
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(s, encoding='utf-8')
        print('  превью', out.relative_to(ROOT))


if __name__ == '__main__':
    main()
