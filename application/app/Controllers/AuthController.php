<?php
class AuthController extends Controller
{
    public function registerForm()
    {
        $this->view('auth/register');
    }

    public function register()
    {
        $errors = [];
        $name     = trim($_POST['name'] ?? '');
        $email    = trim($_POST['email'] ?? '');
        $password = $_POST['password'] ?? '';

        if ($name === '')          $errors[] = 'Name is required.';
        if ($email === '')         $errors[] = 'Email is required.';
        if (strlen($password) < 6) $errors[] = 'Password must be at least 6 characters.';
        if (!$errors && User::emailExists($email)) $errors[] = 'That email is already registered.';

        if ($errors) {
            $this->view('auth/register', ['errors' => $errors]);
            return;
        }
        $id = User::create($name, $email, password_hash($password, PASSWORD_DEFAULT));
        $_SESSION['user_id'] = $id;
        set_flash('Welcome to SkillBank! You start with 3 credits.');
        redirect('dashboard');
    }

    public function loginForm()
    {
        $this->view('auth/login');
    }

    public function login()
    {
        $user = User::findByEmail(trim($_POST['email'] ?? ''));
        if ($user && password_verify($_POST['password'] ?? '', $user['password_hash'])) {
            $_SESSION['user_id'] = $user['id'];
            set_flash('Logged in.');
            redirect('dashboard');
        }
        $this->view('auth/login', ['error' => 'Wrong email or password.']);
    }

    public function logout()
    {
        session_destroy();
        redirect('');
    }
}
