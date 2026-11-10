#!/usr/bin/env python3
"""Пакет из текущих файлов сайта: только автоматический выбор типа в шести отраслевых формах.

python3 tools/deploy/prepare-2026-11-11-industry-default.py <live> <deploy-dir>
"""
import hashlib
import importlib.util
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('required_marks', ROOT / 'tools/site/required_marks.py')
marks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(marks)
SELECT = re.compile(r'<select\b[^>]*name="type"[^>]*>.*?</select>', re.S)
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
NAME = 'pestcontrol-deploy-2026-11-11-industry-default'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    src, dst = map(pathlib.Path, sys.argv[1:3])
    dst.mkdir(parents=True, exist_ok=True)
    order, before, after = [], [], []
    for page, value in marks.INDUSTRY_TYPES.items():
        path = page + '/index.php'
        data = (src / path).read_bytes()
        s = data.decode('utf-8')
        new, _, forms = marks.apply(s)
        assert forms == 1 and new != s, page
        assert SELECT.sub('[TYPE]', s) == SELECT.sub('[TYPE]', new), page
        old_counters, new_counters = COUNTERS.findall(s), COUNTERS.findall(new)
        assert len(old_counters) == 1 and old_counters == new_counters, page
        assert marks.apply(new)[0] == new, page
        assert '<?' not in new and new.rstrip().endswith('</html>'), page
        assert 'name="type" required' in new, page
        b = new.encode('utf-8')
        out = dst / 'pkg' / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b)
        order.append(path)
        before.append(sha(data) + '  ' + path)
        after.append(sha(b) + '  ' + path)
        print(page, '=>', value, ': только select; счётчики без изменений')
    config = (
        '# Только отраслевой автовыбор типа объекта; без редизайна. Пакет из текущих файлов сайта.\n'
        f'NAME="{NAME}"\nBK="before-industry-default_2026-11-11_ftp.zip"\n'
        'ORDER="' + '\n'.join(order) + '"\n'
        'REPLACED="' + ' '.join(order) + '"\n'
        'EXPECTED_BEFORE="' + '\n'.join(before) + '"\n'
        'CHECK_DIRS="' + ' '.join(marks.INDUSTRY_TYPES) + '"\n'
    )
    (dst / 'deploy.conf').write_text(config, encoding='utf-8')
    (dst / 'MANIFEST.sha256').write_text('\n'.join(after) + '\n', encoding='utf-8')
    shutil.copy2(ROOT / 'tools/deploy/run_all.sh', dst / 'run_all.sh')


if __name__ == '__main__':
    main()
