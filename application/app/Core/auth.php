<?php
// Authentication helpers built on top of the User model + the session.

// The logged-in user's row, or null. Cached per request.
function current_user()
{
    static $cached = false;
    if ($cached !== false) {
        return $cached;
    }
    if (empty($_SESSION['user_id'])) {
        return $cached = null;
    }
    return $cached = User::find($_SESSION['user_id']);
}

function is_logged_in() { return current_user() !== null; }

function require_login()
{
    if (!is_logged_in()) {
        set_flash('Please log in first.');
        redirect('login');
    }
}

function is_admin()
{
    $u = current_user();
    return $u && $u['role'] === 'admin';
}

function require_admin()
{
    if (!is_admin()) {
        set_flash('Admins only.');
        redirect('');
    }
}
