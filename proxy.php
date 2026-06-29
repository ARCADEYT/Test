<?php
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Método no permitido, usa POST.']);
    exit;
}

$raw = file_get_contents('php://input');
$payload = json_decode($raw, true);
if (!is_array($payload)) {
    http_response_code(400);
    echo json_encode(['error' => 'JSON inválido.']);
    exit;
}

$link = trim($payload['link'] ?? '');
$quantity = isset($payload['quantity']) ? intval($payload['quantity']) : 0;

if ($link === '') {
    http_response_code(400);
    echo json_encode(['error' => 'Falta el enlace del reel.']);
    exit;
}

if ($quantity < 1) {
    http_response_code(400);
    echo json_encode(['error' => 'Cantidad inválida.']);
    exit;
}

$apiUrl = 'https://smmapi.com/api/v2/';
$apiKey = '6e032cb6cb976d5269408d3c6adb6932373a513ee09783b59a4e526c9bb9eef3';
$serviceId = '7356';

$postFields = http_build_query([
    'key' => $apiKey,
    'action' => 'add',
    'service' => $serviceId,
    'link' => $link,
    'quantity' => $quantity,
]);

$ch = curl_init($apiUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $postFields);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/x-www-form-urlencoded']);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
$response = curl_exec($ch);
$errno = curl_errno($ch);
$error = curl_error($ch);
$status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($errno) {
    http_response_code(502);
    echo json_encode(['error' => 'Error de conexión al API: ' . $error]);
    exit;
}

if ($status >= 400) {
    http_response_code($status);
    echo json_encode(['error' => 'El API respondió con HTTP ' . $status, 'body' => $response]);
    exit;
}

$json = json_decode($response, true);
if ($json === null) {
    echo $response;
    exit;
}

echo json_encode($json);
