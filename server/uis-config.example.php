<?php
declare(strict_types=1);

/**
 * Шаблон конфигурации UIS Data API для серверной передачи заявок.
 *
 * Рабочий файл размещается на сервере ВНЕ public_html:
 *   ~/pestcontrol-center/uis-config.php (права 600, не коммитится в GitHub).
 * send.php подключает его через dirname(__DIR__) . '/uis-config.php'.
 */
return [
    'endpoint'     => 'https://dataapi.uiscom.ru/v2.0',
    'access_token' => 'КЛЮЧ_UIS_DATA_API', // настоящий ключ хранится только на сервере вне public_html
    'site_id'      => 134808,              // пестконтроль-центр.рф
    'timeout'      => 5,
];
