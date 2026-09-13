<?php
// =====================================================================
// Front controller. EVERY request enters here (Apache rewrites to it via
// .htaccess; the PHP built-in server uses it as the router script). It boots
// the app, works out the route, and hands off to a controller method.
// =====================================================================

define('ROOT', __DIR__);
define('APP', ROOT . '/app');

// When using PHP's built-in server, let it serve real static files (css, etc.)
// directly instead of routing them through the app.
if (PHP_SAPI === 'cli-server') {
    $file = ROOT . str_replace('/', DIRECTORY_SEPARATOR,
            urldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH)));
    if (is_file($file)) {
        return false;
    }
}

session_start();

require APP . '/Core/helpers.php';
require APP . '/Core/Database.php';

// Autoload classes from Core / Models / Controllers by file name.
spl_autoload_register(function ($class) {
    foreach (['Core', 'Models', 'Controllers'] as $dir) {
        $path = APP . "/$dir/$class.php";
        if (is_file($path)) { require $path; return; }
    }
});

require APP . '/Core/auth.php';

// Work out the route: strip the app's base path, trim slashes.
$base  = base_path();
$uri   = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$route = trim(substr($uri, strlen($base)), '/');
$verb  = $_SERVER['REQUEST_METHOD'];

// Route table: "VERB route" => [Controller, method].
$routes = [
    'GET '                 => ['OfferController', 'index'],
    'GET search'           => ['OfferController', 'search'],
    'GET offer'            => ['OfferController', 'show'],
    'GET offers/create'    => ['OfferController', 'createForm'],
    'POST offers/create'   => ['OfferController', 'store'],
    'GET offers/edit'      => ['OfferController', 'editForm'],
    'POST offers/edit'     => ['OfferController', 'update'],
    'POST offers/delete'   => ['OfferController', 'destroy'],
    'GET login'            => ['AuthController', 'loginForm'],
    'POST login'           => ['AuthController', 'login'],
    'GET register'         => ['AuthController', 'registerForm'],
    'POST register'        => ['AuthController', 'register'],
    'GET logout'           => ['AuthController', 'logout'],
    'GET dashboard'        => ['DashboardController', 'index'],
    'POST dashboard'       => ['DashboardController', 'wishlist'],
    'POST sessions/request'=> ['SessionController', 'request'],
    'POST sessions/action' => ['SessionController', 'action'],
    'GET sessions/review'  => ['SessionController', 'reviewForm'],
    'POST sessions/review' => ['SessionController', 'review'],
    'GET admin'            => ['AdminController', 'index'],
    'GET admin/skills'     => ['AdminController', 'skills'],
    'POST admin/skills'    => ['AdminController', 'skillsPost'],
];

$key = $verb . ' ' . $route;
if (isset($routes[$key])) {
    [$controller, $method] = $routes[$key];
    (new $controller)->$method();
} else {
    http_response_code(404);
    echo 'Page not found: ' . e($route);
}
