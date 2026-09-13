<h1>Manage skills</h1>
<form method="post" action="<?= url('admin/skills') ?>" class="form-inline">
  <?= csrf_field() ?>
  <input type="text" name="name" placeholder="Skill name">
  <input type="text" name="category" placeholder="Category">
  <button type="submit" name="add" value="1">Add skill</button>
</form>
<table class="table">
  <tr><th>Name</th><th>Category</th><th></th></tr>
  <?php foreach ($skills as $s): ?>
  <tr>
    <td><?= e($s['name']) ?></td>
    <td><?= e($s['category']) ?></td>
    <td>
      <form method="post" action="<?= url('admin/skills') ?>" class="inline-form"
            onsubmit="return confirm('Delete skill?')">
        <?= csrf_field() ?>
        <input type="hidden" name="skill_id" value="<?= (int)$s['id'] ?>">
        <button type="submit" name="delete" value="1">Delete</button>
      </form>
    </td>
  </tr>
  <?php endforeach; ?>
</table>
