<h1>Review: <?= e($session['title']) ?></h1>
<form method="post" action="<?= url('sessions/review') ?>" class="form">
  <?= csrf_field() ?>
  <input type="hidden" name="id" value="<?= (int)$session['id'] ?>">
  <label>Rating
    <select name="rating">
      <option value="5">5 - Excellent</option>
      <option value="4">4 - Good</option>
      <option value="3">3 - Okay</option>
      <option value="2">2 - Poor</option>
      <option value="1">1 - Bad</option>
    </select>
  </label>
  <label>Comment (optional) <textarea name="comment"></textarea></label>
  <button type="submit">Submit review</button>
</form>
