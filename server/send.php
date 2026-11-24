<?php
declare(strict_types=1);

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

// Логирование ошибок без вывода технических данных посетителю.
ini_set('log_errors', '1');
ini_set('display_errors', '0');
error_reporting(E_ALL);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

// Единый формат ответа сервера.
function respond(int $status, array $data): void
{
    http_response_code($status);

    echo json_encode(
        $data,
        JSON_UNESCAPED_UNICODE | JSON_INVALID_UTF8_SUBSTITUTE
    );

    exit;
}

// Принимаем только POST-запросы.
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');

    respond(405, [
        'success' => false,
        'message' => 'Метод не поддерживается.'
    ]);
}

// Проверяем источник запроса, если браузер передал Origin.
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
$httpHost = $_SERVER['HTTP_HOST'] ?? '';

if ($origin !== '') {
    $originHost = parse_url($origin, PHP_URL_HOST);
    $siteHost = parse_url('https://' . $httpHost, PHP_URL_HOST);

    if (
        !$originHost ||
        !$siteHost ||
        strcasecmp($originHost, $siteHost) !== 0
    ) {
        respond(403, [
            'success' => false,
            'message' => 'Запрос отклонён.'
        ]);
    }
}

// Подключаем PHPMailer.
$autoload = __DIR__ . '/vendor/autoload.php';

if (!is_file($autoload)) {
    error_log('Audit form error: vendor/autoload.php not found');

    respond(500, [
        'success' => false,
        'message' => 'Ошибка настройки отправки. Попробуйте позже.'
    ]);
}

require $autoload;

// SMTP-настройки.
$smtpHost = 'smtp.timeweb.ru';
$smtpUsername = 'b2b@pestcontrol-center.ru';
$smtpPassword = 'ПАРОЛЬ_ПОЧТЫ'; // настоящий пароль хранится только на сервере
$smtpPort = 465;

// Отправитель и получатель.
$fromEmail = 'b2b@pestcontrol-center.ru';
$fromName = 'Заявка на аудит объекта';
$toEmail = 'АДРЕС_ДЛЯ_ЗАЯВОК@example.ru'; // настоящий адрес указан только на сервере
// Рабочая почта для заявок (указана на сайте). Письмо уходит на оба адреса.
$toEmailB2b = 'b2b@pestcontrol-center.ru';

// Чтение и ограничение длины полей.
function field(string $key, int $maxLength = 2000): string
{
    $value = $_POST[$key] ?? '';

    if (!is_string($value)) {
        respond(400, [
            'success' => false,
            'message' => 'Некорректные данные формы.'
        ]);
    }

    $value = trim($value);

    $length = function_exists('mb_strlen')
        ? mb_strlen($value, 'UTF-8')
        : strlen($value);

    if ($length > $maxLength) {
        respond(400, [
            'success' => false,
            'message' => 'Одно из полей слишком длинное.'
        ]);
    }

    return $value;
}

// Чтение служебного необязательного поля без прерывания заявки при переполнении.
function optionalMeta(string $key, int $maxLength): string
{
    $value = $_POST[$key] ?? '';

    if (!is_string($value)) {
        return '';
    }

    $value = trim($value);

    if (function_exists('mb_substr')) {
        return mb_substr($value, 0, $maxLength, 'UTF-8');
    }

    return substr($value, 0, $maxLength);
}

// HTTP POST JSON в UIS Data API (cURL с запасным вариантом через stream_context).
function uisPostJson(string $url, string $token, array $payload, int $timeout): ?array
{
    $body = json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_INVALID_UTF8_SUBSTITUTE);

    if ($body === false) {
        error_log('UIS server send error: json_encode failed');
        return null;
    }

    $headers = [
        'Content-Type: application/json; charset=UTF-8',
        'Authorization: Bearer ' . $token,
    ];

    $raw = false;
    $httpCode = 0;

    if (function_exists('curl_init')) {
        $ch = curl_init($url);

        if ($ch === false) {
            error_log('UIS server send error: curl_init failed');
            return null;
        }

        curl_setopt_array($ch, [
            CURLOPT_POST           => true,
            CURLOPT_POSTFIELDS     => $body,
            CURLOPT_HTTPHEADER     => $headers,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CONNECTTIMEOUT => min(3, max(1, $timeout)),
            CURLOPT_TIMEOUT        => max(2, $timeout),
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_SSL_VERIFYHOST => 2,
        ]);

        $raw = curl_exec($ch);
        $httpCode = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);

        if ($raw === false) {
            error_log('UIS server send cURL error: ' . curl_error($ch));
            curl_close($ch);
            return null;
        }

        curl_close($ch);
    } else {
        $ctx = stream_context_create([
            'http' => [
                'method'        => 'POST',
                'header'        => implode("\r\n", $headers) . "\r\n",
                'content'       => $body,
                'timeout'       => max(2, $timeout),
                'ignore_errors' => true,
            ],
            'ssl' => [
                'verify_peer'      => true,
                'verify_peer_name' => true,
            ],
        ]);

        $raw = @file_get_contents($url, false, $ctx);

        if ($raw === false) {
            error_log('UIS server send stream error: request failed');
            return null;
        }
    }

    $decoded = json_decode((string) $raw, true);

    if (!is_array($decoded)) {
        error_log('UIS server send invalid JSON (HTTP ' . $httpCode . '): ' . substr((string) $raw, 0, 300));
        return null;
    }

    return $decoded;
}

// Серверная передача заявки в UIS Data API (upload.offline_messages).
// Ключ читается только из закрытого файла вне public_html: dirname(__DIR__) . '/uis-config.php'.
function sendToUis(
    string $name,
    string $digits,
    string $email,
    string $company,
    string $type,
    string $msg,
    string $formName,
    string $pageUrl,
    string $uisSessionId
): bool {
    $configPath = dirname(__DIR__) . '/uis-config.php';

    if (!is_file($configPath)) {
        error_log('UIS server send skipped: config file not found outside public_html');
        return false;
    }

    $config = require $configPath;

    if (!is_array($config)) {
        error_log('UIS server send skipped: invalid config format');
        return false;
    }

    $token = trim((string) ($config['access_token'] ?? ''));
    $endpoint = trim((string) ($config['endpoint'] ?? 'https://dataapi.uiscom.ru/v2.0'));
    $siteId = (int) ($config['site_id'] ?? 134808);
    $timeout = (int) ($config['timeout'] ?? 5);

    if ($token === '' || $token === 'КЛЮЧ_UIS_DATA_API' || $siteId <= 0) {
        error_log('UIS server send skipped: access_token or site_id not configured');
        return false;
    }

    // Нормализация телефона РФ к формату E.164 без «+» (7XXXXXXXXXX).
    $uisPhone = $digits;
    if (strlen($uisPhone) === 11 && $uisPhone[0] === '8') {
        $uisPhone[0] = '7';
    }

    // Собираем полный текст заявки для amoCRM (без дублирования строк, которые уже есть в msg).
    $parts = [];
    $hasText = static function (string $haystack, string $needle): bool {
        if ($needle === '') {
            return true;
        }
        return function_exists('mb_stripos')
            ? mb_stripos($haystack, $needle, 0, 'UTF-8') !== false
            : stripos($haystack, $needle) !== false;
    };

    if ($company !== '' && !$hasText($msg, $company)) {
        $parts[] = 'Компания или объект: ' . $company;
    }

    if ($type !== '' && !$hasText($msg, $type)) {
        $parts[] = 'Тип объекта: ' . $type;
    }

    if ($msg !== '') {
        $parts[] = $msg;
    }

    if ($pageUrl !== '' && !$hasText($msg, $pageUrl)) {
        $parts[] = 'Страница: ' . $pageUrl;
    }

    $uisText = implode("\n", $parts);
    if (function_exists('mb_substr')) {
        $uisText = mb_substr($uisText, 0, 3500, 'UTF-8');
    } else {
        $uisText = substr($uisText, 0, 3500);
    }

    try {
        $rand = bin2hex(random_bytes(4));
    } catch (\Throwable $e) {
        $rand = substr(md5((string) microtime(true)), 0, 8);
    }

    $item = [
        'name'      => $name,
        'phone'     => $uisPhone,
        'message'   => $uisText,
        'site_id'   => $siteId,
        'form_name' => $formName !== '' ? $formName : 'Заявка с сайта',
        'ext_id'    => 'pc-' . date('Ymd-His') . '-' . $rand,
    ];

    if ($email !== '') {
        $item['email'] = $email;
    }

    $hasSession = preg_match('/^[1-9]\d{4,18}$/', $uisSessionId) === 1;
    if ($hasSession) {
        $item['visitor_session_id'] = (int) $uisSessionId;
    }

    $buildPayload = static function (array $msgItem) use ($token): array {
        return [
            'jsonrpc' => '2.0',
            'id'      => 1,
            'method'  => 'upload.offline_messages',
            'params'  => [
                'access_token'     => $token,
                'offline_messages' => [$msgItem],
            ],
        ];
    };

    $res = uisPostJson($endpoint, $token, $buildPayload($item), $timeout);

    if (is_array($res) && isset($res['result']['data'][0]['id'])) {
        return true;
    }

    // Если передавали visitor_session_id и UIS отклонил (устаревшая или несовпадающая сессия),
    // повторяем без visitor_session_id — только по site_id, чтобы заявка гарантированно дошла.
    if ($hasSession && is_array($res) && isset($res['error'])) {
        error_log('UIS server send retry without visitor_session_id: ' . json_encode($res['error'], JSON_UNESCAPED_UNICODE));
        unset($item['visitor_session_id']);
        $res2 = uisPostJson($endpoint, $token, $buildPayload($item), $timeout);

        if (is_array($res2) && isset($res2['result']['data'][0]['id'])) {
            return true;
        }

        error_log('UIS server send fallback failed: ' . json_encode($res2, JSON_UNESCAPED_UNICODE));
        return false;
    }

    error_log('UIS server send failed: ' . json_encode($res, JSON_UNESCAPED_UNICODE));
    return false;
}

// Получаем данные формы.
$name         = field('name', 150);
$company      = field('company', 250);
$phone        = field('phone', 30);
$email        = field('email', 254);
$type         = field('type', 150);
$msg          = field('msg', 3000);
$formName     = optionalMeta('form_name', 150);
$pageUrl      = optionalMeta('page_url', 500);
$uisSessionId = optionalMeta('uis_session_id', 30);
$uisSkip      = optionalMeta('uis_skip', 10);

if ($formName === '') {
    $formName = optionalMeta('page', 150);
}

// Проверяем обязательные поля.
$nameLength = function_exists('mb_strlen')
    ? mb_strlen($name, 'UTF-8')
    : strlen($name);

if ($nameLength < 2) {
    respond(422, [
        'success' => false,
        'message' => 'Проверьте имя.'
    ]);
}

$digits = preg_replace('/\D/', '', $phone);

if (strlen($digits) !== 11) {
    respond(422, [
        'success' => false,
        'message' => 'Проверьте номер телефона.'
    ]);
}

if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    respond(422, [
        'success' => false,
        'message' => 'Проверьте адрес электронной почты.'
    ]);
}

// Разрешённые значения поля «Тип объекта».
$allowedTypes = [
    'Пищевое производство',
    'Фармацевтическое производство',
    'Ресторан или кафе',
    'Гостиница',
    'Магазин или торговая сеть',
    'Склад, логистика',
    'Элеватор, комбикормовый завод',
    'Бизнес-центр или офисное здание',
    'Офис арендатора',
    'Торговый центр',
    'Промышленное предприятие',
    'Несколько объектов',
    'Другое',
];

if (!in_array($type, $allowedTypes, true)) {
    respond(422, [
        'success' => false,
        'message' => 'Выберите тип объекта.'
    ]);
}

// Экранирование пользовательских данных для HTML-письма.
$escape = static function (string $value): string {
    return htmlspecialchars(
        $value,
        ENT_QUOTES | ENT_SUBSTITUTE,
        'UTF-8'
    );
};

// Фиксируем факт согласия на обработку персональных данных (доказательство для оператора, ч. 3 ст. 9 152-ФЗ).
$consentVersion = '22.10.2026';
$consentAt = (new DateTimeImmutable('now', new DateTimeZone('Europe/Moscow')))->format('d.m.Y H:i:s');
$clientIp = (string) ($_SERVER['REMOTE_ADDR'] ?? '');
$consentNote = 'Согласие на обработку персональных данных дано нажатием кнопки «Отправить заявку» '
    . '(текст согласия: https://пестконтроль-центр.рф/soglasie/, редакция от ' . $consentVersion . '). '
    . 'Дата и время: ' . $consentAt . ' (МСК). IP-адрес: ' . ($clientIp !== '' ? $clientIp : 'не определён') . '.';

// Создаём письмо и отправляем через SMTP.
$mail = new PHPMailer(true);

try {
    $mail->isSMTP();
    $mail->SMTPDebug = 0; // 2 — подробный журнал SMTP для диагностики
    $mail->Debugoutput = static function ($str, $level) {
        error_log("PHPMailer [$level]: $str");
    };
    $mail->Host       = $smtpHost;
    $mail->SMTPAuth   = true;
    $mail->Username   = $smtpUsername;
    $mail->Password   = $smtpPassword;
    $mail->Port       = $smtpPort;
    $mail->SMTPSecure = PHPMailer::ENCRYPTION_SMTPS;
    $mail->CharSet    = 'UTF-8';
    $mail->Timeout    = 15;

    $mail->setFrom($fromEmail, $fromName);
    $mail->addAddress($toEmail);
    $mail->addAddress($toEmailB2b);

    // Ответ на заявку можно отправить посетителю.
    if ($email !== '') {
        $mail->addReplyTo($email, $name);
    }

    $mail->isHTML(true);
    $mail->Subject = 'Заявка на аудит объекта';

    $mail->Body =
        '<h2>Новая заявка на аудит объекта</h2>' .
        '<p><b>Имя:</b> ' . $escape($name) . '</p>' .
        '<p><b>Компания или объект:</b> ' .
            $escape($company) . '</p>' .
        '<p><b>Телефон:</b> ' . $escape($phone) . '</p>' .
        '<p><b>E-mail:</b> ' . $escape($email) . '</p>' .
        '<p><b>Тип объекта:</b> ' . $escape($type) . '</p>' .
        '<p><b>Комментарий:</b><br>' .
            nl2br($escape($msg)) . '</p>' .
        '<hr><p style="color:#666;font-size:12px">' . $escape($consentNote) . '</p>';

    $mail->AltBody =
        "Новая заявка на аудит объекта\n\n" .
        "Имя: {$name}\n" .
        "Компания или объект: {$company}\n" .
        "Телефон: {$phone}\n" .
        "E-mail: {$email}\n" .
        "Тип объекта: {$type}\n" .
        "Комментарий: {$msg}\n\n" .
        "{$consentNote}\n";

    // Успех возвращаем только после подтверждения отправки SMTP.
    $mail->send();

    // После успешной отправки письма передаём заявку в UIS с сервера
    // (для 2-й и следующих частей длинного опросного листа передаётся uis_skip=1).
    if ($uisSkip !== '1') {
        try {
            sendToUis($name, $digits, $email, $company, $type, $msg, $formName, $pageUrl, $uisSessionId);
        } catch (\Throwable $uisErr) {
            error_log('UIS server send exception: ' . $uisErr->getMessage());
        }
    }

    respond(200, [
        'success' => true,
        'message' => 'Заявка успешно отправлена.'
    ]);

} catch (\Throwable $e) {
    // Подробности остаются в серверном журнале.
    error_log(
        'Audit form SMTP error: ' .
        $e->getMessage() .
        ' | ' .
        $mail->ErrorInfo
    );

    respond(500, [
        'success' => false,
        'message' => 'Не удалось отправить заявку. Попробуйте позже.'
    ]);
}
