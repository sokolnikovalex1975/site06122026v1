#!/usr/bin/env python3
"""Test the sanitized handler with a fake PHPMailer. Never sends real mail.

python3 tools/bctc/test_types.py [sanitized-send.php] [fixture-directory]
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
MOCK = r'''<?php
namespace PHPMailer\PHPMailer;
#[\AllowDynamicProperties]
class PHPMailer {
    const ENCRYPTION_SMTPS = 'ssl';
    public $ErrorInfo = '';
    public function __construct($exceptions = true) {}
    public function __call($method, $args) {}
    public function send() {
        file_put_contents(getenv('TEST_MAIL_CAPTURE'), json_encode([
            'html'=>$this->Body, 'text'=>$this->AltBody, 'subject'=>$this->Subject
        ], JSON_UNESCAPED_UNICODE));
        return true;
    }
}
class Exception extends \Exception {}
'''


def main():
    source = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'server/send.php'
    fixture = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(tempfile.mkdtemp(prefix='bctc-types-'))
    fixture.mkdir(parents=True, exist_ok=True)
    (fixture / 'vendor').mkdir(exist_ok=True)
    (fixture / 'vendor/autoload.php').write_text(MOCK)
    (fixture / 'send.php').write_bytes(source.read_bytes())
    subprocess.run(['php', '-l', str(fixture / 'send.php')], check=True)
    s = source.read_text()
    block = re.search(r'\$allowedTypes\s*=\s*\[(.*?)\];', s, re.S)[1]
    types = re.findall(r"'([^']+)'", block)
    assert len(types) == 13 and len(set(types)) == 13
    capture = fixture / 'mail.json'
    env = dict(os.environ, TEST_MAIL_CAPTURE=str(capture))
    base = dict(name='Тестовая проверка', phone='+7 (999) 123-45-67', company='Тест',
                email='', msg='Площадь: 100 м²\nВопрос: <проверка>')
    def check(value, success, extra=None, method='POST', origin=''):
        capture.unlink(missing_ok=True)
        post = dict(base, type=value)
        if extra:
            post.update(extra)
        data = dict(post=post, method=method, origin=origin)
        env['TEST_REQUEST'] = json.dumps(data, ensure_ascii=False)
        code = (
            "$x=json_decode(getenv('TEST_REQUEST'),true);$_POST=$x['post'];"
            "$_SERVER['REQUEST_METHOD']=$x['method'];"
            "$_SERVER['HTTP_HOST']='test.local';$_SERVER['HTTP_ORIGIN']=$x['origin'];"
            "require " + json.dumps(str(fixture / 'send.php')) + ";"
        )
        r = subprocess.run(['php', '-r', code], env=env, capture_output=True, text=True, check=True)
        result = json.loads(r.stdout)
        assert result['success'] is success, (value, result, r.stderr)
        assert capture.exists() is success
        if success:
            mail = json.loads(capture.read_text())
            assert '<b>Тип объекта:</b> ' + value + '</p>' in mail['html']
            assert 'Тип объекта: ' + value + '\n' in mail['text']
            assert '&lt;проверка&gt;' in mail['html']
        return result
    for value in types:
        check(value, True)
    for value in ('', 'Несуществующий объект', ['Торговый центр']):
        check(value, False)
    check(types[0], False, extra={'name':''})
    check(types[0], False, extra={'phone':'123'})
    check(types[0], False, method='GET')
    check(types[0], False, origin='https://foreign.example')
    print('PASS: 13 accepted types; correct HTML/text type; 7 invalid/security requests rejected; no real mail')
    print('Fixture for browser integration:', fixture)


if __name__ == '__main__':
    main()
