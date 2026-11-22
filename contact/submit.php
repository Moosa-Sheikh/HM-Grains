<?php
declare(strict_types=1);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /contact/', true, 303);
    exit;
}

if (!empty($_POST['website'])) {
    header('Location: /contact/?sent=1', true, 303);
    exit;
}

$name = trim((string) ($_POST['name'] ?? ''));
$email = trim((string) ($_POST['email'] ?? ''));
$phone = trim((string) ($_POST['phone'] ?? ''));
$message = trim((string) ($_POST['message'] ?? ''));

if ($name === '' || strlen($name) > 120 || !filter_var($email, FILTER_VALIDATE_EMAIL)
    || strlen($email) > 254 || $phone === '' || strlen($phone) > 50
    || strlen($message) > 10000) {
    header('Location: /contact/?error=invalid', true, 303);
    exit;
}

$recipient = getenv('HM_CONTACT_TO') ?: 'contact@hmgrains.com';
$subject = 'New inquiry from HM Grains website';
$body = "Name: {$name}\nEmail: {$email}\nPhone: {$phone}\n\nMessage:\n{$message}\n";
$headers = ['From: HM Grains <contact@hmgrains.com>', 'Reply-To: ' . $email, 'Content-Type: text/plain; charset=UTF-8'];

if (mail($recipient, $subject, $body, implode("\r\n", $headers))) {
    header('Location: /contact/?sent=1', true, 303);
} else {
    header('Location: /contact/?error=delivery', true, 303);
}
exit;
