<h1>Register</h1>
<?php foreach (($errors ?? []) as $err): ?><div class="error"><?= e($err) ?></div><?php endforeach; ?>
<form method="post" action="<?= url('register') ?>" class="form">
  <label>Name <input type="text" name="name" value="<?= old('name') ?>"></label>
  <label>Email <input type="email" name="email" value="<?= old('email') ?>"></label>
  <label>Password <input type="password" name="password"></label>
  <button type="submit">Create account</button>
</form>
<p>Already have an account? <a href="<?= url('login') ?>">Login</a></p>
