<?php
// Plain functions used everywhere (views + controllers). Loaded once in index.php.

// The app's base URL path, detected automatically so links work whether the app
// is served at the site root (built-in server) or under /skillbank/ (XAMPP).
function base_path()
{
    $dir = str_replace('\\', '/', dirname($_SERVER['SCRIPT_NAME']));
    return rtrim($dir, '/');
}

// Build a URL to a route, e.g. url('offers/create') or url('offer?id=5').
function url($path = '')
{
    return base_path() . '/' . ltrim($path, '/');
}

// Escape output to prevent XSS. Wrap EVERY user value printed into HTML.
function e($value)
{
    return htmlspecialchars($value ?? '', ENT_QUOTES, 'UTF-8');
}

// Redirect to a route and stop. Call before any HTML output.
function redirect($path)
{
    header('Location: ' . url($path));
    exit;
}

// One-time flash messages.
function set_flash($m) { $_SESSION['flash'] = $m; }
function get_flash()
{
    if (!empty($_SESSION['flash'])) {
        $m = $_SESSION['flash'];
        unset($_SESSION['flash']);
        return $m;
    }
    return null;
}

// CSRF token helpers (see the Security topic in the course).
function csrf_token()
{
    if (empty($_SESSION['csrf'])) {
        $_SESSION['csrf'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf'];
}
function csrf_field()
{
    return '<input type="hidden" name="csrf" value="' . e(csrf_token()) . '">';
}
function verify_csrf()
{
    if (!isset($_POST['csrf']) || !hash_equals($_SESSION['csrf'] ?? '', $_POST['csrf'])) {
        http_response_code(400);
        die('Invalid or missing security token. Go back, refresh, and try again.');
    }
}

// Re-fill a form field after a validation error.
function old($key) { return e($_POST[$key] ?? ''); }
