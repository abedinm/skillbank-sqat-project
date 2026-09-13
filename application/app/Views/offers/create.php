<h1>Offer a skill</h1>
<?php foreach (($errors ?? []) as $err): ?><div class="error"><?= e($err) ?></div><?php endforeach; ?>
<form method="post" action="<?= url('offers/create') ?>" class="form">
  <?= csrf_field() ?>
  <label>Skill
    <select name="skill_id">
      <option value="">-- choose --</option>
      <?php foreach ($skills as $s): ?>
        <option value="<?= (int)$s['id'] ?>"><?= e($s['name']) ?> (<?= e($s['category']) ?>)</option>
      <?php endforeach; ?>
    </select>
  </label>
  <label>Title <input type="text" name="title" value="<?= old('title') ?>"></label>
  <label>Description <textarea name="description"><?= old('description') ?></textarea></label>
  <label>Level
    <select name="level">
      <option>Beginner</option><option>Intermediate</option><option>Advanced</option>
    </select>
  </label>
  <button type="submit">Create offer</button>
</form>
