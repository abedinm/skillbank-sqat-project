<h1>Admin dashboard</h1>
<div class="stats">
  <div class="stat"><strong><?= (int)$userCount ?></strong><span>Users</span></div>
  <div class="stat"><strong><?= (int)$offerCount ?></strong><span>Offers</span></div>
  <div class="stat"><strong><?= (int)$sessionCount ?></strong><span>Completed sessions</span></div>
</div>
<p><a href="<?= url('admin/skills') ?>">Manage skills &raquo;</a></p>

<h2>All users</h2>
<table class="table">
  <tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Credits</th></tr>
  <?php foreach ($users as $u): ?>
  <tr>
    <td><?= (int)$u['id'] ?></td>
    <td><?= e($u['name']) ?></td>
    <td><?= e($u['email']) ?></td>
    <td><?= e($u['role']) ?></td>
    <td><?= (int)$u['credits'] ?></td>
  </tr>
  <?php endforeach; ?>
</table>
