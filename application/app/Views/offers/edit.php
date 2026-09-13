<h1>Edit offer</h1>
<form method="post" action="<?= url('offers/edit?id=' . (int)$offer['id']) ?>" class="form">
  <?= csrf_field() ?>
  <label>Skill
    <select name="skill_id">
      <?php foreach ($skills as $s): ?>
        <option value="<?= (int)$s['id'] ?>" <?= $s['id'] == $offer['skill_id'] ? 'selected' : '' ?>>
          <?= e($s['name']) ?> (<?= e($s['category']) ?>)
        </option>
      <?php endforeach; ?>
    </select>
  </label>
  <label>Title <input type="text" name="title" value="<?= e($offer['title']) ?>"></label>
  <label>Description <textarea name="description"><?= e($offer['description']) ?></textarea></label>
  <label>Level
    <select name="level">
      <?php foreach (['Beginner', 'Intermediate', 'Advanced'] as $lv): ?>
        <option <?= $offer['level'] == $lv ? 'selected' : '' ?>><?= $lv ?></option>
      <?php endforeach; ?>
    </select>
  </label>
  <label>Status
    <select name="status">
      <option <?= $offer['status'] == 'active'   ? 'selected' : '' ?>>active</option>
      <option <?= $offer['status'] == 'inactive' ? 'selected' : '' ?>>inactive</option>
    </select>
  </label>
  <button type="submit">Save changes</button>
</form>
