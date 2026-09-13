<h1>Login</h1>
<?php if (!empty($error)): ?><div class="error"><?= e($error) ?></div><?php endif; ?>
<form method="post" action="<?= url('login') ?>" class="form">
  <label>Email <input type="email" name="email"></label>
  <label>Password <input type="password" name="password"></label>
  <button type="submit">Login</button>
</form>
<p>No account? <a href="<?= url('register') ?>">Register</a></p>
