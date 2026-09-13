<?php $me = current_user(); $flash = get_flash(); ?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SkillBank</title>
  <link rel="stylesheet" href="<?= url('assets/style.css') ?>">
</head>
<body>
<nav class="nav">
  <a class="brand" href="<?= url('') ?>">SkillBank</a>
  <div class="nav-links">
    <a href="<?= url('') ?>">Browse</a>
    <?php if ($me): ?>
      <a href="<?= url('dashboard') ?>">Dashboard</a>
      <a href="<?= url('offers/create') ?>">Offer a skill</a>
      <?php if ($me['role'] === 'admin'): ?>
        <a href="<?= url('admin') ?>">Admin</a>
      <?php endif; ?>
      <span class="credits">Credits: <?= (int)$me['credits'] ?></span>
      <span class="hi">Hi, <?= e($me['name']) ?></span>
      <a href="<?= url('logout') ?>">Logout</a>
    <?php else: ?>
      <a href="<?= url('login') ?>">Login</a>
      <a href="<?= url('register') ?>">Register</a>
    <?php endif; ?>
  </div>
</nav>
<main class="container">
<?php if ($flash): ?><div class="flash"><?= e($flash) ?></div><?php endif; ?>
